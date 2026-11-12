"""Daily cycle runner for the European paper account. Every step is idempotent and tolerant of a late start: a missing earlier step is a WARNING in the day state, never an error.

Commands (python -I src/eu_cycle.py <command>):
  status                 one-screen summary: time, trading day, steps done today, account
  due <role>             prints JSON {"run": true|false, "reason": ...} for role researcher | trader | reviewer (agent tasks call this first and stop on false)
  collect                news per theme (Google News RSS, last 2 days, only items already published), commodity/index drivers, quote table -> data/live/<date>/collected.json
  prep <role>            writes the agent's input file under data/paper/run/<date>/ and prints its path (collects first if needed)
  apply trader <json>    validates the decision, stores the handoff note, submits orders through the risk manager (paper_broker.submit)
  apply researcher|reviewer <file>   marks the step done (reviewer file: JSON with "report" and "handoff")
  intraday               cloud hourly check: replay stops/exits, fill, collect, wake the trader only on new information (prints one JSON line)
  apply intraday <json>  submit the intraday decision's orders through the risk manager
  selftest               trigger-detection tests
  fills                  fills pending orders at the first eligible bar
  watch                  stops/exits from the risk manager, then fills (run every 30 minutes in session)
  close                  mark to market, custody, equity point, reconcile, day report
  evening                cloud mode after the close: replay stops/exits from the bars, fills, then close
  summary                the phone notification line: dot, Balance, Bought, Sold, Ordered
  battery                battery drain from the daemon heartbeat log (percent per hour while on battery)
Day state: data/paper/state/<YYYY-MM-DD>.json. Time is UTC inside; a day starts whenever the first command of the day runs.
"""
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import live_feed as lf  # noqa: E402
import paper_broker as pb  # noqa: E402
import notify  # noqa: E402
import shadow  # noqa: E402

PAPER = pb.PAPER
os.environ.setdefault("HANDOFF_DIR", str(PAPER / "handoff"))
import handoff  # noqa: E402,F401  (reads HANDOFF_DIR at import)

QUERIES = {
    "oil_gas": ["oil price OR Brent OR OPEC", "Shell OR TotalEnergies OR BP OR Eni OR Equinor OR Repsol"],
    "gold_miners": ["gold price", "Fresnillo OR \"Endeavour Mining\""],
    "chips": ["semiconductor OR chip stocks Europe", "Infineon OR STMicroelectronics OR BESI OR ASML"],
    "pharma": ["pharma FDA OR EMA approval", "AstraZeneca OR Novartis OR \"Novo Nordisk\" OR Sanofi OR GSK OR Bayer"],
    "copper_uranium": ["copper price", "Glencore OR \"Rio Tinto\" OR Antofagasta OR Boliden OR KGHM"],
    "macro": ["European stocks ECB OR inflation OR tariffs", "markets Iran OR Ukraine OR OPEC OR sanctions"],
}
DRIVERS = ["BZ=F", "CL=F", "GC=F", "HG=F", "NG=F", "EURUSD=X", "^STOXX50E", "^GDAXI", "^FTSE", "^VIX"]
ROLE_MODEL_NOTE = "Opus"


def today(now=None):
    return (now or pb.utc_now()).date()


def state_file(d):
    return PAPER / "state" / (d.isoformat() + ".json")


def state_get(d):
    f = state_file(d)
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"date": d.isoformat(), "steps": {}, "warnings": []}


def state_set(d, step, ok=True, note=""):
    s = state_get(d)
    s["steps"][step] = {"at": pb.iso(pb.utc_now()), "ok": ok, "note": note}
    f = state_file(d)
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, indent=1), encoding="utf-8")
    os.replace(tmp, f)
    return s


def warn(d, text):
    s = state_get(d)
    if text not in s["warnings"]:
        s["warnings"].append(text)
        f = state_file(d)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(s, indent=1), encoding="utf-8")
    print("WARNING:", text)


def main_session(now):
    return pb.session("SAP.DE", now.date())   # the main venues share these hours


# ------------------------------------------------------------------ due
def due(role, now=None):
    now = now or pb.utc_now()
    d = today(now)
    if not pb.is_trading_day(d):
        return {"run": False, "reason": "not a trading day"}
    o, c = main_session(now)
    st = state_get(d)["steps"]
    if role in ("researcher", "trader"):
        if now > c - dt.timedelta(minutes=pb.LIM["cutoff_min"]):
            return {"run": False, "reason": "past the buy cutoff ({} UTC); the next run is the next trading day".format((c - dt.timedelta(minutes=30)).strftime("%H:%M"))}
        if role in st and st[role]["ok"]:
            return {"run": False, "reason": "{} already ran today at {}".format(role, st[role]["at"])}
        late = "started late: market already open since {} UTC".format(o.strftime("%H:%M")) if now > o else ""
        return {"run": True, "reason": late or "on time"}
    if role == "lab":
        if now > c - dt.timedelta(minutes=pb.LIM["cutoff_min"]):
            return {"run": False, "reason": "past the buy cutoff; the next lab run is the next trading day"}
        if "lab" in st and st["lab"]["ok"]:
            return {"run": False, "reason": "lab already ran today at {}".format(st["lab"]["at"])}
        return {"run": True, "reason": "on time"}
    if role == "reviewer":
        if "reviewer" in st and st["reviewer"]["ok"]:
            return {"run": False, "reason": "reviewer already ran today"}
        if now < c:
            return {"run": False, "reason": "the session is still open; the reviewer runs after the close"}
        return {"run": True, "reason": "after the close" + ("" if "close" in st else " (close job not seen yet: will be done first)")}
    return {"run": False, "reason": "unknown role"}


# ------------------------------------------------------------------ collect
def rss(q, now):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q + " when:2d", "hl": "en-GB", "gl": "GB", "ceid": "GB:en"})
    out = []
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read()
        for it in ET.fromstring(data).iter("item"):
            title = (it.findtext("title") or "").strip()
            try:
                t = parsedate_to_datetime(it.findtext("pubDate")).astimezone(dt.timezone.utc)
            except Exception:  # noqa: BLE001
                continue
            if t > now:          # never a headline from the future
                continue
            src = (it.findtext("source") or "").strip()
            out.append({"title": title, "source": src, "published_utc": pb.iso(t)[:16].replace("T", " "), "query": q})
    except Exception as e:  # noqa: BLE001
        print("WARNING: news query failed:", q, str(e)[:60])
    return sorted(out, key=lambda x: x["published_utc"], reverse=True)


def drv(sym):
    b = lf.bars(sym, "5d", "1d")
    c = [x[4] for x in b if x[4] is not None]
    if len(c) < 2:
        return sym, None
    return sym, {"last": round(c[-1], 4), "prev_close": round(c[-2], 4), "chg_pct": round((c[-1] / c[-2] - 1) * 100, 2)}


def quote_row(sym):
    q = pb.get_quote(sym)
    if q:
        q = dict(q)
        try:
            c = [x[4] for x in lf.bars(sym, "5d", "1d") if x[4] is not None]
            q["chg_pct"] = round((c[-1] / c[-2] - 1) * 100, 2) if len(c) >= 2 else None
        except Exception:  # noqa: BLE001
            q["chg_pct"] = None
    return sym, q


def collect(now=None, force=False, mark_seen=True):
    now = now or pb.utc_now()
    d = today(now)
    out = PAPER.parent / "live" / d.isoformat()
    f = out / "collected.json"
    if f.exists() and not force and (now - pb.parse_utc(json.loads(f.read_text(encoding="utf-8"))["collected_at"])).total_seconds() < 3 * 3600:
        print("collected earlier today:", f)
        return f
    news = {}
    for theme, qs in QUERIES.items():
        seen, items = set(), []
        for q in qs:
            for it in rss(q, now):
                k = it["title"].lower()[:80]
                if k not in seen:
                    seen.add(k)
                    items.append(it)
            time.sleep(0.5)
        news[theme] = sorted(items, key=lambda x: x["published_utc"], reverse=True)[:10]
    with ThreadPoolExecutor(6) as ex:
        drivers = {s: v for s, v in ex.map(drv, DRIVERS) if v}
        syms = sorted(pb.ALLOWED)
        quotes = {s: q for s, q in ex.map(quote_row, syms) if q}
    fx = pb.get_fx()
    table = {}
    for s, q in quotes.items():
        pe = pb.to_eur(q["price"], q["currency"], fx)
        if pe:
            table[s] = {"theme": pb.ALLOWED[s], "price": q["price"], "currency": q["currency"], "price_eur": round(pe, 2), "age_min": q["age_minutes"], "chg_pct": q.get("chg_pct"), "entry_cost_pct": pb.entry_cost_pct(s, pe, q["currency"]),
                        "max_shares_35pct": int(0.35 * pb.LIM["start_cash"] // pe)}
    out.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"collected_at": pb.iso(now), "news": news, "drivers": drivers, "table": table}, indent=1), encoding="utf-8")
    try:
        lf.snapshot(sorted(pb.ALLOWED), out / "snapshot.jsonl") if False else None
    except Exception:  # noqa: BLE001
        pass
    if mark_seen:
        seen_add(d, [i["title"] for v in news.values() for i in v])
    state_set(d, "collect", True, "{} headlines, {} drivers, {} quotes".format(sum(len(v) for v in news.values()), len(drivers), len(table)))
    print("collected:", f, "|", sum(len(v) for v in news.values()), "headlines,", len(drivers), "drivers,", len(table), "quotes")
    return f


# ------------------------------------------------------------------ intraday (cloud: hourly check, wakes the trader only on new information)
ALIASES = {"SHEL.L": ["shell"], "TTE.PA": ["totalenergies"], "BP.L": [" bp ", "bp plc"], "ENI.MI": [" eni "], "EQNR.OL": ["equinor"], "REP.MC": ["repsol"], "FRES.L": ["fresnillo"],
           "EDV.L": ["endeavour mining"], "IFX.DE": ["infineon"], "STMPA.PA": ["stmicro"], "BESI.AS": ["besi", "be semiconductor"], "AZN.L": ["astrazeneca"], "NOVN.SW": ["novartis"],
           "NOVO-B.CO": ["novo nordisk"], "SAN.PA": ["sanofi"], "GSK.L": [" gsk "], "BAYN.DE": ["bayer"], "GLEN.L": ["glencore"], "RIO.L": ["rio tinto"], "ANTO.L": ["antofagasta"],
           "BOL.ST": ["boliden"], "KGH.WA": ["kghm"]}
EVENT_WORDS = ["results", "guidance", "profit warning", "outlook", "fda", "ema ", "approval", "approves", "takeover", "bid", "merger", "acquisition", "probe", "lawsuit", "recall", "strike",
               "outage", "explosion", "sanction", "ban ", "downgrade", "upgrade", "cuts", "raises", "plunge", "surge", "halt", "suspend", "investigation", "fine", "dividend", "buyback"]
MOVE_PCT, HELD_MOVE_PCT, MAX_TRIGGERS = 3.0, 2.0, 12
EVENT_RE = re.compile(r"\b(" + "|".join(re.escape(w.strip()) for w in EVENT_WORDS) + r")\b")   # whole words only: 'fine' must not match inside 'Infineon'


def seen_file(d):
    return PAPER / "state" / (d.isoformat() + "_seen.json")


def seen_get(d):
    f = seen_file(d)
    return set(json.loads(f.read_text(encoding="utf-8"))) if f.exists() else set()


def seen_add(d, titles):
    s = seen_get(d) | {t.lower()[:80] for t in titles}
    f = seen_file(d)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(sorted(s)), encoding="utf-8")


def find_triggers(news, table, held, seen):
    """Pure function: which new headlines and price moves deserve waking the trader. news: {theme: [item]}, table: {sym: {chg_pct, ...}}, held: set of symbols, seen: set of title keys.
    Returns (triggers, new_items). Triggers: a traded name plus an event word in a new headline (kind held when we own it; plain news flow about a held name does not wake the trader); price move of 3% (2% on a held name)."""
    out, new_items = [], []
    for theme, items in news.items():
        for it in items:
            k = it["title"].lower()[:80]
            if k in seen:
                continue
            new_items.append(dict(it, theme=theme))
            low = " " + it["title"].lower() + " "
            for sym, al in ALIASES.items():
                if any(a in low for a in al) and EVENT_RE.search(low):
                    out.append({"kind": "held" if sym in held else "event", "symbol": sym, "text": it["title"], "published": it["published_utc"]})
    for sym, row in table.items():
        ch = row.get("chg_pct")
        if ch is not None and abs(ch) >= (HELD_MOVE_PCT if sym in held else MOVE_PCT):
            out.append({"kind": "move", "symbol": sym, "text": "{:+.2f}% versus the previous close".format(ch), "published": ""})
    uniq, seen_t = [], set()
    for t in out:
        key = (t["kind"], t["symbol"], t["text"][:60])
        if key not in seen_t:
            seen_t.add(key)
            uniq.append(t)
    return uniq[:MAX_TRIGGERS], new_items


def intraday(now=None):
    """Hourly cloud check. Always: replay stops and exits, fill pending orders, collect fresh news and quotes. Wakes the trader only if find_triggers says so; prints one JSON line."""
    now = now or pb.utc_now()
    d = today(now)
    if not pb.is_trading_day(d):
        print(json.dumps({"wake": False, "reason": "not a trading day"}))
        return
    o, c = main_session(now)
    if not (o <= now <= c):
        print(json.dumps({"wake": False, "reason": "outside the session"}))
        return
    for r in pb.replay_exits(now):
        print("replayed exit:", r["id"], r["status"], r.get("reasons", ""))
    do_fills(now)
    f = collect(now, force=True, mark_seen=False)
    col = json.loads(Path(f).read_text(encoding="utf-8"))
    led = pb.load()
    held = {p["symbol"] for p in led["positions"]}
    seen = seen_get(d)
    if not seen_file(d).exists():      # no baseline yet today (the morning run did not mark its headlines): treat what is on the page now as already seen, so only price moves can wake the trader
        seen = {i["title"].lower()[:80] for v in col["news"].values() for i in v}
    trig, new_items = find_triggers(col["news"], col["table"], held, seen)
    seen_add(d, [i["title"] for v in col["news"].values() for i in v])
    log = PAPER / "state" / (d.isoformat() + "_intraday.json")
    runs = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    cutoff = c - dt.timedelta(minutes=pb.LIM["cutoff_min"])
    wake = bool(trig) and now <= c - dt.timedelta(minutes=10)
    runs.append({"at": pb.iso(now), "wake": wake, "triggers": len(trig), "new_headlines": len(new_items), "can_buy": now <= cutoff})
    log.write_text(json.dumps(runs, indent=1), encoding="utf-8")
    if not wake:
        print(json.dumps({"wake": False, "reason": "no trigger ({} new headlines, {} open positions)".format(len(new_items), len(held))}))
        return
    rd = run_dir(d)
    hhmm = now.strftime("%H%M")
    ho, hw = handoff.latest(handoff.DIR, d)
    dec = rd / "trader_decision.json"
    morning = ""
    if dec.exists():
        try:
            m = json.loads(dec.read_text(encoding="utf-8"))
            morning = "Morning view: {} Orders this morning: {}".format(m.get("market_view", ""), json.dumps(m.get("orders", [])))
        except Exception:  # noqa: BLE001
            pass
    L = ["# Intraday input, decision day {} (now {} UTC; buys {})".format(d, now.strftime("%H:%M"), "allowed" if now <= cutoff else "NOT allowed any more (last 30 minutes), sells only"),
         "Output file to write: " + str(rd / "intraday_{}_decision.json".format(hhmm)), "", morning, "", "## What triggered this run (new information only)"]
    L += ["- [{}] {}: {} {}".format(t["kind"], t["symbol"], t["text"], ("(" + t["published"] + ")") if t["published"] else "") for t in trig]
    L += ["", handoff.render(ho, hw), "", pb.outcomes_block(), "", account_text(led), "", "## New headlines since the last check (not seen before)"]
    L += ["- [{}] [{}] {} ({})".format(i["theme"], i["published_utc"], i["title"], i["source"]) for i in new_items[:40]] or ["- (none; the trigger is a price move)"]
    L += ["", "## Traded names: price EUR, change today %, quote age min, entry cost %, max whole shares under the 35% cap"]
    L += ["- {} [{}] {} EUR, {} %, age {} min, entry cost {}%, max {} shares".format(k, v["theme"], v["price_eur"], v.get("chg_pct"), v["age_min"], v["entry_cost_pct"], v["max_shares_35pct"]) for k, v in col["table"].items()]
    L += ["", "Limits: " + json.dumps({k: v for k, v in pb.LIM.items()})]
    p = rd / "intraday_{}_input.md".format(hhmm)
    p.write_text("\n".join(L), encoding="utf-8")
    print(json.dumps({"wake": True, "reason": "{} triggers".format(len(trig)), "input": str(p)}))


def apply_intraday(path, now=None):
    now = now or pb.utc_now()
    d = today(now)
    try:
        dec = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print("NO ACTION: decision file unreadable ({})".format(str(e)[:80]))
        return 1
    themes, results = dec.get("themes", {}), []
    for o in dec.get("orders", []):
        sym = o.get("symbol")
        th = pb.ALLOWED.get(sym)
        t = themes.get(th, {}) if th else {}
        req = {"symbol": sym, "side": str(o.get("side", "")).upper(), "qty": o.get("qty", 0), "type": "MARKET", "confidence": t.get("confidence", o.get("confidence", 0)),
               "catalyst": t.get("catalyst", o.get("catalyst", "")), "horizon": t.get("horizon_days", o.get("horizon", 0)), "agent": "A-opus-intraday", "tag": "intra" + now.strftime("%H")}
        r = pb.submit(req, "agent", now)
        results.append(r)
        print("{} {} {} x{}: {} {}".format(r["id"], r["side"], r["symbol"], r["qty"], r["status"], "; ".join(r.get("reasons", []))))
    if not results:
        print("no action (valid decision)")
    pb.add_note("intraday", "{} orders. {}".format(len(results), dec.get("note", ""))[:500])
    state_set(d, "intraday" + now.strftime("%H%M"), True, "{} orders".format(len(results)))
    return 0


def selftest():
    news = {"pharma": [{"title": "Bayer wins FDA approval for new drug", "source": "x", "published_utc": "2026-11-10 10:00"}, {"title": "Bayer old story", "source": "x", "published_utc": "2026-11-10 06:00"}],
            "oil_gas": [{"title": "Shell chair says nothing", "source": "x", "published_utc": "2026-11-10 10:05"}, {"title": "Equinor halts Troll field after outage", "source": "x", "published_utc": "2026-11-10 10:06"}],
            "chips": [{"title": "Infineon CEO keynote tomorrow", "source": "x", "published_utc": "2026-11-10 10:07"}, {"title": "Infineon issues profit warning", "source": "x", "published_utc": "2026-11-10 10:09"}]}
    table = {"SHEL.L": {"chg_pct": 0.4}, "BP.L": {"chg_pct": -3.4}, "IFX.DE": {"chg_pct": 2.3}, "ENI.MI": {"chg_pct": 2.4}}
    seen = {"bayer old story"}
    trig, new = find_triggers(news, table, {"IFX.DE"}, seen)
    kinds = {(t["kind"], t["symbol"]) for t in trig}
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    check("event word plus traded name triggers (Bayer FDA)", ("event", "BAYN.DE") in kinds)
    check("outage headline triggers for Equinor", ("event", "EQNR.OL") in kinds)
    check("a seen headline does not trigger", len(new) == 5 and not any("old story" in t["text"] for t in trig))
    check("a traded name without an event word does not trigger (Shell)", ("event", "SHEL.L") not in kinds)
    check("held name with an event word triggers; without one it does not", ("held", "IFX.DE") in kinds and not any(t["text"] == "Infineon CEO keynote tomorrow" for t in trig))
    check("3% move triggers (BP), 2.4% on an unheld name does not, 2.3% on a held name does", ("move", "BP.L") in kinds and ("move", "ENI.MI") not in kinds and ("move", "IFX.DE") in kinds)
    check("no news, no moves means no trigger", find_triggers({}, {"SHEL.L": {"chg_pct": 0.5}}, set(), set())[0] == [])
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


# ------------------------------------------------------------------ prep
def run_dir(d):
    p = PAPER / "run" / d.isoformat()
    p.mkdir(parents=True, exist_ok=True)
    return p


def account_text(led):
    fx = pb.get_fx()
    eq = pb.equity_now(led, fx)
    L = ["Account: equity {:.2f} EUR, cash {:.2f} EUR, start {:.2f} EUR, total {:+.2f}%.".format(eq, led["cash"], led["start_cash"], (eq / led["start_cash"] - 1) * 100)]
    if led["positions"]:
        L.append("Open positions:")
        for p in led["positions"]:
            q = pb.get_quote(p["symbol"])
            last = pb.to_eur(q["price"], p["currency"], fx) if q else None
            cost = pb.to_eur(p["avg_price"], p["currency"], fx)
            L.append("- {} {} x{} entry {:.2f} EUR now {} EUR, opened {}, exit by {}, theme {}, catalyst quoted: {}".format(
                p["symbol"], p["name"], p["qty"], cost, "{:.2f}".format(last) if last else "n/a", p["opened"], p["exit_by"], p.get("theme"), str(p.get("catalyst", ""))[:100]))
    else:
        L.append("Open positions: none.")
    pend = [o for o in led["orders"] if o["status"] == "ACCEPTED"]
    L.append("Pending orders: " + (", ".join("{} {} x{}".format(o["side"], o["symbol"], o["qty"]) for o in pend) if pend else "none"))
    return "\n".join(L)


def prep(role, now=None):
    now = now or pb.utc_now()
    d = today(now)
    st = state_get(d)["steps"]
    if "collect" not in st or not (PAPER.parent / "live" / d.isoformat() / "collected.json").exists():
        # collected.json lives in data/live, which is not synced between machines: the step flag can say done
        # (restored from the state branch) while the file only exists on the machine that collected.
        collect(now, force=True)
        st = state_get(d)["steps"]
    col = json.loads((PAPER.parent / "live" / d.isoformat() / "collected.json").read_text(encoding="utf-8"))
    led = pb.load()
    rd = run_dir(d)
    if role == "researcher":
        L = ["# Researcher input, decision day {} (now {} UTC)".format(d, now.strftime("%H:%M")), "Output file to write: " + str(rd / "brief.md"), "", "## Headlines per theme (already published, newest first)"]
        for th, items in col["news"].items():
            L.append("### " + th)
            L += ["- [{}] {} ({})".format(i["published_utc"], i["title"], i["source"]) for i in items] or ["- (none found)"]
        L += ["", "## Drivers (last, previous close, % change)"] + ["- {}: {} (prev {}, {:+.2f}%)".format(k, v["last"], v["prev_close"], v["chg_pct"]) for k, v in col["drivers"].items()]
        L += ["", "## Traded names (theme, price EUR, quote age min)"] + ["- {} [{}] {} EUR, age {} min".format(k, v["theme"], v["price_eur"], v["age_min"]) for k, v in col["table"].items()]
        L += ["", account_text(led)]
        p = rd / "researcher_input.md"
    elif role == "trader":
        br = rd / "brief.md"
        if not br.exists():
            warn(d, "no researcher brief today (researcher did not run); the trader works from the raw headlines")
        ho, hw = handoff.latest(handoff.DIR, today(now))
        L = ["# Trader input, decision day {} (now {} UTC; {} warnings from the day state: {})".format(d, now.strftime("%H:%M"), len(state_get(d)["warnings"]), "; ".join(state_get(d)["warnings"]) or "none"),
             "Output file to write: " + str(rd / "trader_decision.json"), "", handoff.render(ho, hw), "", pb.outcomes_block(), "", shadow.block(), "", account_text(led), "", "## Researcher brief"]
        L += [br.read_text(encoding="utf-8")] if br.exists() else ["(no brief today; use the headlines below)"]
        if not br.exists():
            for th, items in col["news"].items():
                L += ["### " + th] + ["- [{}] {} ({})".format(i["published_utc"], i["title"], i["source"]) for i in items[:6]]
        L += ["", "## Drivers"] + ["- {}: {:+.2f}%".format(k, v["chg_pct"]) for k, v in col["drivers"].items()]
        L += ["", "## Traded names: price EUR, quote age min, entry cost % (commission, FX, tax, slippage), max whole shares under the 35% cap"]
        L += ["- {} [{}] {} EUR, age {} min, entry cost {}%, max {} shares".format(k, v["theme"], v["price_eur"], v["age_min"], v["entry_cost_pct"], v["max_shares_35pct"]) for k, v in col["table"].items()]
        L += ["", "Limits: " + json.dumps({k: v for k, v in pb.LIM.items()})]
        p = rd / "trader_input.md"
    elif role == "lab":
        import lab
        lab.require_lab()
        for r in pb.replay_exits(now):
            print("replayed exit:", r["id"], r["status"], r.get("reasons", ""))
        do_fills(now)
        pb.accrue_custody(now)
        pb.mark_to_market(now)
        lab.sync_status(d)
        led = pb.load()
        L = ["# Lab input, decision day {} (now {} UTC)".format(d, now.strftime("%H:%M")), "Output file to write: " + str(rd / "lab_output.json"), "",
             "## This lab: {} | focus: {} | allowed horizons: {}".format(os.environ.get("LAB_NAME", "lab"), os.environ.get("LAB_FOCUS", "any idea family"), list(pb.LIM["horizons"])), "",
             "## Registered ideas (registry)"] + (["- [{}] {}: {} | rule: {} | source: {} | note: {}".format(i["status"], i["id"], i["hypothesis"], i["rule"], i["source"], i["note"]) for i in lab.load_ideas()] or ["(none yet: propose your first ideas)"])
        L += ["", lab.results_block(led), "", account_text(led), "", "## Per-name features (daily closes up to now; last, 1/5/20-day move %, % below the 3-month high)"]
        L += ["- {}: last {} d1 {:+.2f} d5 {:+.2f} d20 {:+.2f} below_3m_high {:+.2f}".format(k, v["last"], v["d1"], v["d5"], v["d20"], v["below_3m_high"]) for k, v in lab.features().items()]
        L += ["", "## Headlines per theme (newest first)"]
        for th, items in col["news"].items():
            L += ["### " + th] + ["- [{}] {} ({})".format(i["published_utc"], i["title"], i["source"]) for i in items[:6]]
        L += ["", "## Drivers"] + ["- {}: {:+.2f}%".format(k, v["chg_pct"]) for k, v in col["drivers"].items()]
        L += ["", "## Traded names: price EUR, quote age min, entry cost % (commission, FX, tax, slippage), max whole shares under the {:.0f}% lab cap".format(100 * pb.LIM["max_pos_pct"])]
        L += ["- {} [{}] {} EUR, age {} min, entry cost {}%, max {} shares".format(k, v["theme"], v["price_eur"], v["age_min"], v["entry_cost_pct"], int(pb.LIM["max_pos_pct"] * pb.LIM["start_cash"] // v["price_eur"])) for k, v in col["table"].items()]
        L += ["", "Lab limits: " + json.dumps({k: v for k, v in pb.LIM.items()})]
        p = rd / "lab_input.md"
    elif role == "reviewer":
        if "close" not in st:
            close(now)
        rep = PAPER / "reports" / (d.isoformat() + ".json")
        ho, hw = handoff.latest(handoff.DIR, today(now))
        L = ["# Reviewer input, day {}".format(d), "Output file to write: " + str(rd / "reviewer_output.json"), "", handoff.render(ho, hw), "", pb.outcomes_block(), "", shadow.block(), "", account_text(led), "",
             "## Day report (from the close job)", rep.read_text(encoding="utf-8") if rep.exists() else "(no report)", "",
             "## Orders and fills today"] + [json.dumps(o) for o in led["orders"] if o["time"][:10] == d.isoformat()] + [json.dumps(x) for x in led["fills"] if x["time"][:10] == d.isoformat()]
        p = rd / "reviewer_input.md"
    else:
        print("unknown role")
        return None
    p.write_text("\n".join(L), encoding="utf-8")
    print(p)
    return p


# ------------------------------------------------------------------ apply
def apply_trader(path, now=None):
    now = now or pb.utc_now()
    d = today(now)
    try:
        dec = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        state_set(d, "trader", False, "malformed decision file: " + str(e)[:80])
        print("NO TRADE: decision file unreadable ({})".format(str(e)[:80]))
        return 1
    ho = dec.get("handoff")
    if ho:
        probs = handoff.validate(ho)
        if probs:
            warn(d, "handoff rejected: " + "; ".join(probs[:2]))
        else:
            print("handoff stored:", handoff.store(ho))
    else:
        warn(d, "decision has no handoff note")
    try:
        tbl = json.loads((PAPER.parent / "live" / d.isoformat() / "collected.json").read_text(encoding="utf-8"))["table"]
        n, sp = shadow.record(dec.get("shadow", []), tbl, d)
        print("shadow calls stored: {}".format(n))
        for p in sp:
            warn(d, "shadow: " + p)
    except Exception as e:  # noqa: BLE001
        warn(d, "shadow calls not stored: " + str(e)[:60])
    results = []
    themes = dec.get("themes", {})
    for o in dec.get("orders", []):
        sym = o.get("symbol")
        th = pb.ALLOWED.get(sym)
        t = themes.get(th, {}) if th else {}
        req = {"symbol": sym, "side": str(o.get("side", "")).upper(), "qty": o.get("qty", 0), "type": "MARKET", "confidence": t.get("confidence", o.get("confidence", 0)),
               "catalyst": t.get("catalyst", o.get("catalyst", "")), "horizon": t.get("horizon_days", o.get("horizon", 0)), "agent": "A-opus-learning"}
        r = pb.submit(req, "agent", now)
        results.append(r)
        print("{} {} {} x{}: {} {}".format(r["id"], r["side"], r["symbol"], r["qty"], r["status"], "; ".join(r.get("reasons", []))))
    if not results:
        print("no orders (no trade is a valid decision)")
    mv = dec.get("market_view", "")
    pb.add_note("trader", "{} orders. {}".format(len(results), mv)[:500])
    state_set(d, "trader", True, "{} orders: {}".format(len(results), ", ".join(r["status"] for r in results)))
    notify.send(("Trader: " + "; ".join("{} {} x{} {}".format(r["side"], r["symbol"], r["qty"], r["status"]) for r in results)) if results else "Trader: no trade today.", "Paper trading decision", 3 if not results else 4)
    return 0


def apply_lab(path, now=None):
    """Lab run: update the idea registry, then send the lab orders (each tagged with its idea). Only ever touches the lab directory (the broker enforces LAB=1)."""
    import lab
    lab.require_lab()
    now = now or pb.utc_now()
    d = today(now)
    try:
        dec = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        state_set(d, "lab", False, "malformed output: " + str(e)[:80])
        print("LAB: output unreadable ({})".format(str(e)[:80]))
        return 1
    for p in lab.merge_ideas(dec.get("ideas", []), d):
        warn(d, p)
    known = {i["id"]: i for i in lab.load_ideas()}
    results = []
    for o in dec.get("orders", []):
        iid = str(o.get("idea", ""))
        if iid not in known or known[iid]["status"] not in ("testing", "proposed"):
            print("lab order skipped: idea '{}' is not registered as testing".format(iid))
            continue
        req = {"symbol": o.get("symbol"), "side": str(o.get("side", "")).upper(), "qty": o.get("qty", 0), "type": "MARKET", "confidence": o.get("confidence", 0.5),
               "catalyst": "lab idea {}: {}".format(iid, str(o.get("rationale", ""))[:120]), "horizon": o.get("horizon", 0), "agent": "lab:" + iid}
        prev = next((x for x in pb.load()["orders"] if x["id"] == pb.order_id(now.date(), req["symbol"], req["side"])), None)
        if prev and prev["status"] == "REJECTED":
            req["tag"] = "retry{}".format(sum(1 for x in pb.load()["orders"] if x["id"].startswith(prev["id"])))   # a rejected order does not block a corrected one
        r = pb.submit(req, "agent", now)
        results.append(r)
        print("{} {} {} x{}: {} {}".format(r["id"], r["side"], r["symbol"], r["qty"], r["status"], "; ".join(r.get("reasons", []))))
    pb.add_note("lab", str(dec.get("lab_notes", ""))[:500])
    state_set(d, "lab", True, "{} orders".format(len(results)))
    return 0


def apply_simple(role, path):
    d = today()
    if role == "reviewer":
        try:
            out = json.loads(Path(path).read_text(encoding="utf-8"))
            if out.get("handoff"):
                probs = handoff.validate(out["handoff"])
                print("handoff stored:", handoff.store(out["handoff"]) if not probs else "REJECTED " + "; ".join(probs[:2]))
            pb.add_note("reviewer", str(out.get("report", ""))[:500])
        except Exception as e:  # noqa: BLE001
            state_set(d, "reviewer", False, "malformed output: " + str(e)[:80])
            print("reviewer output unreadable")
            return 1
    state_set(d, role, True, "")
    if role == "reviewer":
        notify.send("Day report ready. Tap to open it, then ask Claude about the day.", "Paper trading report", 3, notify.REPORT_URL)
    return 0


# ------------------------------------------------------------------ fills, watch, close
def do_fills(now=None):
    now = now or pb.utc_now()
    msgs = pb.process_fills(now)
    for m in msgs:
        print(m)
    if any(m.startswith("FILLED") for m in msgs):
        state_set(today(now), "fills", True, "; ".join(m for m in msgs if m.startswith("FILLED"))[:200])
    return msgs


def watch(now=None):
    now = now or pb.utc_now()
    d = today(now)
    if not pb.is_trading_day(d):
        print("not a trading day")
        return
    o, c = main_session(now)
    if not (o - dt.timedelta(minutes=5) <= now <= c + dt.timedelta(minutes=20)):
        print("outside the session; nothing to watch")
        return
    for r in pb.system_orders(now):
        print("system order:", r["id"], r["status"], r.get("reasons"))
    do_fills(now)
    state_set(d, "watch", True, pb.iso(now))


def close(now=None):
    now = now or pb.utc_now()
    d = today(now)
    if not pb.is_trading_day(d):
        print("not a trading day")
        return
    do_fills(now)
    fee = pb.accrue_custody(now)
    eq = pb.mark_to_market(now)
    bad = pb.reconcile()
    led = pb.load()
    prev = pb.equity_on(led, d)
    rep = {"date": d.isoformat(), "equity": eq, "day_pnl_eur": round(eq - prev, 2), "day_pnl_pct": round((eq / prev - 1) * 100, 2), "total_pnl_pct": round((eq / led["start_cash"] - 1) * 100, 2),
           "cash": led["cash"], "custody_today": fee, "positions": [{"symbol": p["symbol"], "qty": p["qty"], "exit_by": p["exit_by"]} for p in led["positions"]],
           "fills_today": [x for x in led["fills"] if x["time"][:10] == d.isoformat()], "reconcile": bad or "consistent", "warnings": state_get(d)["warnings"]}
    f = PAPER / "reports" / (d.isoformat() + ".json")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    state_set(d, "close", not bad, "equity {:.2f}, reconcile {}".format(eq, "ok" if not bad else "MISMATCH"))
    print("close: equity {:.2f} day {:+.2f}% reconcile {}".format(eq, rep["day_pnl_pct"], "ok" if not bad else bad))


def summary(now=None):
    """The phone notification line (fixed template): <colored dot> Balance: X EUR | Bought: ... | Sold: ... | Ordered: ...
    Dot: green when equity is above the last recorded close, red below, white when unchanged. Bought/Sold are only the fills booked in this run (last 50 minutes), Ordered the accepted orders still waiting to fill."""
    now = now or pb.utc_now()
    d = today(now)
    led = pb.load()
    eq = pb.equity_now(led)
    prev = pb.equity_on(led, d)
    dot = "\U0001F7E2" if eq > prev + 0.005 else "\U0001F534" if eq < prev - 0.005 else "\u26AA"
    # Only fills booked in THIS run (recorded within the last 50 minutes) count as news; an earlier fill is not repeated in every later notification.
    fills = [x for x in led["fills"] if x.get("recorded_at") and (now - pb.parse_utc(x["recorded_at"])).total_seconds() <= 50 * 60]

    def fmt(side):
        s = ", ".join("{} x {} @ {:.2f}".format(x["qty"], x["symbol"], x["price"]) for x in fills if x["side"] == side)
        return s or "nothing"

    pend = [o for o in led["orders"] if o["status"] == "ACCEPTED"]
    ordered = ", ".join("{} {} x {}".format(o["side"], o["qty"], o["symbol"]) for o in pend) or "nothing"
    tag = "🧪 LAB {} | ".format(os.environ.get("LAB_NAME", "lab")) if pb.LAB else ""     # a lab notification always carries the lab tag
    return "{}{} Balance: {:.2f} EUR | Bought: {} | Sold: {} | Ordered: {}".format(tag, dot, eq, fmt("BUY"), fmt("SELL"), ordered)


def battery():
    import re
    rows = []
    for ln in (PAPER / "daemon.log").read_text(encoding="utf-8").splitlines():
        m = re.match(r"(\S+) heartbeat .*battery=(\d+|None)% ac=(\w+)", ln)
        if m and m.group(2) != "None":
            rows.append((pb.parse_utc(m.group(1)), int(m.group(2)), m.group(3) == "True"))
    if not rows:
        print("no battery data yet (heartbeats before the update carry none)")
        return
    seg = [r for r in rows if not r[2]]
    print("{} heartbeats with battery data; now {}% ({})".format(len(rows), rows[-1][1], "on AC" if rows[-1][2] else "on battery"))
    if len(seg) >= 2:
        # drain over the latest unbroken stretch on battery
        i = len(rows) - 1
        while i > 0 and not rows[i - 1][2]:
            i -= 1
        a, b = rows[i], rows[-1]
        h = (b[0] - a[0]).total_seconds() / 3600
        if not b[2] and h >= 0.05:
            print("on battery since {} UTC: {}% -> {}% in {:.1f} h = {:.1f} % per hour; full day (11 h) would use about {:.0f}%".format(a[0].strftime("%H:%M"), a[1], b[1], h, (a[1] - b[1]) / h, (a[1] - b[1]) / h * 11))


def evening(now=None):
    """Cloud mode, one call after the close: replay stops and horizon exits from the bars, fill everything pending, then the close job."""
    now = now or pb.utc_now()
    d = today(now)
    if not pb.is_trading_day(d):
        print("not a trading day")
        return
    for r in pb.replay_exits(now):
        print("replayed exit:", r["id"], r["status"], r.get("reasons", ""))
    do_fills(now)
    close(now)
    try:
        print("shadow calls scored: {}".format(shadow.score(now)))
    except Exception as e:  # noqa: BLE001
        warn(d, "shadow scoring failed: " + str(e)[:60])


def status():
    now = pb.utc_now()
    d = today(now)
    o, c = main_session(now)
    print("now {} UTC | trading day: {} | main session {}-{} UTC".format(now.strftime("%Y-%m-%d %H:%M"), pb.is_trading_day(d), o.strftime("%H:%M"), c.strftime("%H:%M")))
    for k, v in state_get(d)["steps"].items():
        print("  {:10s} {} {} {}".format(k, v["at"][11:16], "ok " if v["ok"] else "FAIL", v["note"]))
    for w in state_get(d)["warnings"]:
        print("  warning:", w)
    pb.status()


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else ""
    if cmd == "status":
        status()
    elif cmd == "due":
        print(json.dumps(due(a[1])))
    elif cmd == "collect":
        collect(force="--force" in a)
    elif cmd == "prep":
        prep(a[1])
    elif cmd == "apply" and a[1] == "intraday":
        sys.exit(apply_intraday(a[2]))
    elif cmd == "apply" and a[1] == "trader":
        sys.exit(apply_trader(a[2]))
    elif cmd == "apply" and a[1] == "lab":
        sys.exit(apply_lab(a[2]))
    elif cmd == "apply":
        sys.exit(apply_simple(a[1], a[2] if len(a) > 2 else ""))
    elif cmd == "fills":
        do_fills()
    elif cmd == "intraday":
        intraday()
    elif cmd == "selftest":
        sys.exit(selftest())
    elif cmd == "apply" and a[1] == "intraday":
        sys.exit(apply_intraday(a[2]))
    elif cmd == "watch":
        watch()
    elif cmd == "close":
        close()
    elif cmd == "evening":
        evening()
    elif cmd == "battery":
        battery()
    elif cmd == "summary":
        sys.stdout.reconfigure(encoding="utf-8")
        print(summary())
    else:
        print(__doc__)
