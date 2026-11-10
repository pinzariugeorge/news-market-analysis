"""Local paper broker for European stocks (1,000 EUR account). Research and simulation only; no real money.

Everything is UTC inside; exchange hours use a hand-coded EU summer-time rule (no tz database on this machine). Prices come from `src/live_feed.py`.
State lives in `data/paper/` (override with env PAPER_DIR; the self-tests use a temp folder): `ledger.json` (dashboard v0 shape, mode PAPER, written atomically),
`orders.jsonl` (append-only event log: request, accepted, rejected, filled), `state/<date>.json` (which cycle steps ran, written by `src/eu_cycle.py`).
Agents never write the ledger: they hand order requests to `submit()`, which applies the risk checks and logs the result.

Rules (see PREREG_EU.md, defaults not all confirmed by the user): 3 positions, at most 35% of equity each, whole shares, cash only, holds 5/10/20 trading days, stop -8%,
daily loss cap 3%, weekly 6%, at most 3 new buys a day, buy only with a catalyst and confidence >= 0.52, no new buys in the last 30 minutes, a fixed fee above 1% of the order rejects it.
Fills: first 5-minute bar starting at or after the order time and at least 15 minutes after the open, at that bar's open, adverse spread/slippage, fees, FX, purchase taxes.
Usage: python -I src/paper_broker.py selftest | status | reconcile
"""
import datetime as dt
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import live_feed as lf  # noqa: E402

PAPER = Path(os.environ["PAPER_DIR"]) if os.environ.get("PAPER_DIR") else ROOT / "data" / "paper"
THEMES = {
    "oil_gas": ["SHEL.L", "TTE.PA", "BP.L", "ENI.MI", "EQNR.OL", "REP.MC"],
    "gold_miners": ["FRES.L", "EDV.L"],
    "chips": ["IFX.DE", "STMPA.PA", "BESI.AS"],
    "pharma": ["AZN.L", "NOVN.SW", "NOVO-B.CO", "SAN.PA", "GSK.L", "BAYN.DE"],
    "copper_uranium": ["GLEN.L", "RIO.L", "ANTO.L", "BOL.ST", "KGH.WA"],
}
ALLOWED = {s: t for t, l in THEMES.items() for s in l}
NAMES = {"SHEL.L": "Shell", "TTE.PA": "TotalEnergies", "BP.L": "BP", "ENI.MI": "Eni", "EQNR.OL": "Equinor", "REP.MC": "Repsol", "FRES.L": "Fresnillo", "EDV.L": "Endeavour Mining",
         "IFX.DE": "Infineon", "STMPA.PA": "STMicroelectronics", "BESI.AS": "BE Semiconductor", "AZN.L": "AstraZeneca", "NOVN.SW": "Novartis", "NOVO-B.CO": "Novo Nordisk",
         "SAN.PA": "Sanofi", "GSK.L": "GSK", "BAYN.DE": "Bayer", "GLEN.L": "Glencore", "RIO.L": "Rio Tinto", "ANTO.L": "Antofagasta", "BOL.ST": "Boliden", "KGH.WA": "KGHM"}
LIM = dict(start_cash=1000.0, max_positions=3, max_pos_pct=0.35, min_conf=0.52, horizons=(5, 10, 20), max_new_buys_day=3, stop_pct=-8.0, daily_loss_pct=-3.0, weekly_loss_pct=-6.0,
           max_fee_pct=1.0, cutoff_min=30, open_delay_min=15)
LAB = os.environ.get("LAB") == "1"
# Isolation guard: the lab limits run only against a separate directory (data/paper_lab), and the main account never runs with the lab flag or against the lab directory.
if LAB and (not os.environ.get("PAPER_DIR") or PAPER.resolve() == (ROOT / "data" / "paper").resolve()):
    raise SystemExit("lab isolation: LAB=1 needs PAPER_DIR=<a separate lab directory>, never data/paper")
if not LAB and PAPER.name == "paper_lab":
    raise SystemExit("lab isolation: the lab directory needs LAB=1")
if LAB:
    LIM.update(max_positions=5, max_pos_pct=0.25, min_conf=0.0, horizons=(1, 2, 3, 5, 10, 20), max_new_buys_day=5, max_fee_pct=1.5)
TAX_BUY = {".L": 0.005, ".PA": 0.004, ".MI": 0.001, ".MC": 0.002}   # UK stamp duty, French FTT, Italian and Spanish taxes: approximate, to verify
FX_COST, CUSTODY_YEAR = 0.0025, 0.0012
HOLIDAYS = {"2026-12-24", "2026-12-25", "2026-12-31", "2027-01-01", "2027-03-26", "2027-03-29", "2027-05-03"}   # approximate common closures; extend yearly; a symbol with no bars is also treated as closed
FXSYM = {"GBp": "GBPEUR=X", "CHF": "CHFEUR=X", "DKK": "DKKEUR=X", "NOK": "NOKEUR=X", "SEK": "SEKEUR=X", "PLN": "PLNEUR=X", "USD": "USDEUR=X"}
LIQ = {}


# ---------------------------------------------------------------- time
def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def parse_utc(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _last_sunday(y, m):
    d = dt.date(y, m, 31)
    while d.weekday() != 6:
        d -= dt.timedelta(days=1)
    return d


def is_summer(t):
    y = t.year
    a = dt.datetime.combine(_last_sunday(y, 3), dt.time(1, 0), dt.timezone.utc)
    b = dt.datetime.combine(_last_sunday(y, 10), dt.time(1, 0), dt.timezone.utc)
    return a <= t < b


def suffix(sym):
    return "." + sym.rsplit(".", 1)[1] if "." in sym else ""


def is_trading_day(d):
    return d.weekday() < 5 and d.isoformat() not in HOLIDAYS


def session(sym, d):
    """(open, close) in UTC for date d (a date) on the symbol's exchange. Main venues 09:00-17:30 CET; Oslo 16:20; Copenhagen and Warsaw 17:00."""
    noon = dt.datetime.combine(d, dt.time(12, 0), dt.timezone.utc)
    shift = -1 if is_summer(noon) else 0
    close_h = {".OL": 15 + 20 / 60, ".CO": 16.0, ".WA": 16.0}.get(suffix(sym), 16.5)
    o = dt.datetime.combine(d, dt.time(8, 0), dt.timezone.utc) + dt.timedelta(hours=shift)
    c = dt.datetime.combine(d, dt.time(0, 0), dt.timezone.utc) + dt.timedelta(hours=close_h + shift)
    return o, c


def add_trading_days(d, n):
    while n > 0:
        d += dt.timedelta(days=1)
        if is_trading_day(d):
            n -= 1
    return d


# ---------------------------------------------------------------- costs
def liq_value(sym):
    if not LIQ:
        try:
            import csv
            for r in csv.DictReader(open(ROOT / "universe" / "eu_candidates.csv", encoding="utf-8")):
                v = r.get("median_value_eur_m_per_day_250d")
                if v:
                    LIQ[r["ticker"]] = float(v)
        except Exception:  # noqa: BLE001
            pass
        for k, v in (("SHEL.L", 342), ("TTE.PA", 271), ("BP.L", 237), ("ENI.MI", 193)):
            LIQ.setdefault(k, v)
    return LIQ.get(sym, 20.0)


def slippage(sym):
    v = liq_value(sym)
    return 0.0003 if v >= 200 else 0.0005 if v >= 50 else 0.0008 if v >= 20 else 0.0012


def to_eur(price, cur, fx):
    if cur == "EUR":
        return price
    r = fx.get(cur)
    return None if r is None else price * (r / 100 if cur == "GBp" else r)


def costs(sym, side, value_eur, cur):
    c = {"commission": round(max(2.5, 0.0008 * value_eur), 2), "fx": round(FX_COST * value_eur, 2) if cur != "EUR" else 0.0,
         "tax": round(TAX_BUY.get(suffix(sym), 0.0) * value_eur, 2) if side == "BUY" else 0.0}
    c["total"] = round(c["commission"] + c["fx"] + c["tax"], 2)
    return c


def entry_cost_pct(sym, price_eur, cur):
    q = max(1, int(333 // price_eur)) if price_eur else 1
    v = price_eur * q
    return round(costs(sym, "BUY", v, cur)["total"] / v * 100 + slippage(sym) * 100, 2)


# ---------------------------------------------------------------- ledger
def new_ledger():
    return {"mode": "PAPER", "currency": "EUR", "start_cash": LIM["start_cash"], "cash": LIM["start_cash"], "positions": [], "orders": [], "fills": [], "equity_history": [], "notes": [],
            "custody_paid": 0.0, "started": iso(utc_now())}


class Lock:
    def __init__(self):
        self.p = PAPER / ".lock"

    def __enter__(self):
        PAPER.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        while True:
            try:
                os.close(os.open(str(self.p), os.O_CREAT | os.O_EXCL))
                return self
            except FileExistsError:
                if time.time() - self.p.stat().st_mtime > 60:   # stale lock of a crashed run
                    self.p.unlink(missing_ok=True)
                elif time.time() - t0 > 30:
                    raise TimeoutError("ledger lock held for more than 30 s")
                time.sleep(0.2)

    def __exit__(self, *a):
        self.p.unlink(missing_ok=True)


def load():
    f = PAPER / "ledger.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else new_ledger()


def save(led):
    PAPER.mkdir(parents=True, exist_ok=True)
    tmp = PAPER / "ledger.json.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(led, indent=1))
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, PAPER / "ledger.json")


def log_event(ev):
    PAPER.mkdir(parents=True, exist_ok=True)
    with open(PAPER / "orders.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev) + "\n")


def add_note(agent, text, led=None):
    with Lock():
        led = load()
        led["notes"].append({"time": iso(utc_now()), "agent": agent, "text": text[:600]})
        led["notes"] = led["notes"][-60:]
        save(led)


# ---------------------------------------------------------------- market data (patched in tests)
_FX = [0.0, {}]


def get_fx():
    """FX rates to EUR (GBp: price of one pound in EUR, converted per 100 pence by to_eur). Cached for 2 minutes."""
    if time.time() - _FX[0] < 120 and _FX[1]:
        return _FX[1]
    out = {"EUR": 1.0}
    for cur, s in FXSYM.items():
        q = lf.quote(s)
        if q:
            out[cur] = q["price"]
    _FX[0], _FX[1] = time.time(), out
    return out


def get_quote(sym):
    return lf.quote(sym)


def get_bars(sym):
    return lf.bars(sym, "1mo", "5m")   # a month of 5-minute bars, so a skipped day (no tokens, outage) can still be replayed


# ---------------------------------------------------------------- account
def equity_now(led, fx=None, quotes=None):
    fx = fx or get_fx()
    mv = 0.0
    for p in led["positions"]:
        q = (quotes or {}).get(p["symbol"]) or get_quote(p["symbol"])
        if q:
            mv += to_eur(q["price"], p["currency"], fx) * p["qty"]
        else:
            mv += to_eur(p["avg_price"], p["currency"], fx) * p["qty"]   # no quote: carry at cost
    return led["cash"] + mv


def equity_on(led, d):
    """last recorded equity strictly before date d (start cash if none)."""
    prev = [h for h in led["equity_history"] if h["date"] < d.isoformat()]
    return prev[-1]["equity"] if prev else led["start_cash"]


# ---------------------------------------------------------------- orders and risk
def order_id(day, sym, side, tag=""):
    return "{}-{}-{}{}".format(day.strftime("%Y%m%d"), sym, side, ("-" + tag) if tag else "")


def risk_check(led, req, now, fx, quote):
    """Return (ok, reasons, qty). Buys get the full check; sells only need a holding. May shrink the quantity to fit the position cap."""
    sym, side, qty = req["symbol"], req["side"], int(req.get("qty", 0))
    why = []
    if sym not in ALLOWED:
        return False, ["symbol not in the traded universe"], 0
    if qty < 1:
        return False, ["quantity below one share"], 0
    held = next((p for p in led["positions"] if p["symbol"] == sym), None)
    if side == "SELL":
        if not held or held["qty"] < qty:
            return False, ["no such holding to sell"], 0
        return True, [], qty
    if side != "BUY":
        return False, ["side must be BUY or SELL"], 0
    d = now.date()
    if not is_trading_day(d):
        return False, ["not a trading day; decide on the next one"], 0
    o, c = session(sym, d)
    if now > c - dt.timedelta(minutes=LIM["cutoff_min"]):
        return False, ["after the buy cutoff (last 30 minutes or closed)"], 0
    if float(req.get("confidence", 0)) < LIM["min_conf"]:
        why.append("confidence below 0.52")
    if not str(req.get("catalyst", "")).strip():
        why.append("no named catalyst")
    if int(req.get("horizon", 0)) not in LIM["horizons"]:
        why.append("horizon must be one of {}".format(list(LIM["horizons"])))
    if quote is None:
        why.append("no quote")
    else:
        if o <= now <= c and quote.get("age_minutes", 0) > 45:
            why.append("quote older than 45 minutes during the session")
    if why:
        return False, why, 0
    px = to_eur(quote["price"], quote["currency"], fx)
    if px is None:
        return False, ["no fx rate"], 0
    eq = equity_now(led, fx)
    if not held and len(led["positions"]) >= LIM["max_positions"]:
        why.append("already 3 open positions")
    if sum(1 for x in led["orders"] if x["side"] == "BUY" and x["status"] in ("ACCEPTED", "FILLED") and x["time"][:10] == d.isoformat()) >= LIM["max_new_buys_day"]:
        why.append("3 new buys already today")
    day_pnl = (eq / equity_on(led, d) - 1) * 100
    if day_pnl <= LIM["daily_loss_pct"]:
        why.append("daily loss cap reached")
    wk = [h for h in led["equity_history"] if h["date"] >= (d - dt.timedelta(days=7)).isoformat() and h["date"] < d.isoformat()]
    if wk and (eq / wk[0]["equity"] - 1) * 100 <= LIM["weekly_loss_pct"]:
        why.append("weekly loss cap reached")
    if why:
        return False, why, 0
    cap = LIM["max_pos_pct"] * eq - (px * held["qty"] if held else 0.0)
    q = min(qty, int(cap // px))
    while q >= 1 and (px * q + costs(sym, "BUY", px * q, quote["currency"])["total"]) > led["cash"] * 0.998:
        q -= 1
    if q < 1:
        return False, ["no whole share fits the position cap and cash"], 0
    v = px * q
    if costs(sym, "BUY", v, quote["currency"])["commission"] / v * 100 > LIM["max_fee_pct"]:
        return False, ["fixed fee would exceed 1% of the order (order too small)"], 0
    return True, (["quantity shrunk from {} to {}".format(qty, q)] if q != qty else []), q


def submit(req, source="agent", now=None, quote=None):
    """Request an order. Idempotent per day, symbol and side. Returns the stored order dict (status ACCEPTED or REJECTED)."""
    now = now or utc_now()
    with Lock():
        led = load()
        oid = order_id(now.date(), req["symbol"], req["side"], req.get("tag", ""))
        for o in led["orders"]:
            if o["id"] == oid:
                return dict(o, duplicate=True)
        fx = get_fx()
        q = quote if quote is not None else get_quote(req["symbol"])
        ok, reasons, qty = risk_check(led, req, now, fx, q)
        o = {"id": oid, "time": iso(now), "symbol": req["symbol"], "side": req["side"], "qty": qty if ok else int(req.get("qty", 0)), "type": req.get("type", "MARKET"), "limit": req.get("limit"),
             "status": "ACCEPTED" if ok else "REJECTED", "reasons": reasons, "source": source, "theme": ALLOWED.get(req["symbol"]), "catalyst": req.get("catalyst", ""),
             "confidence": req.get("confidence"), "horizon": req.get("horizon"), "agent": req.get("agent", source)}
        log_event(dict(o, event="request"))
        led["orders"].append(o)
        save(led)
        return o


# ---------------------------------------------------------------- fills
def process_fills(now=None):
    """Fill pending accepted orders at the open of the first eligible 5-minute bar. Returns a list of messages. Orders without a visible bar yet stay pending."""
    now = now or utc_now()
    msgs = []
    with Lock():
        led = load()
        fx = get_fx()
        changed = False
        for o in led["orders"]:
            if o["status"] != "ACCEPTED":
                continue
            sym, side = o["symbol"], o["side"]
            t_o = parse_utc(o["time"])
            bars = get_bars(sym)
            pick = None
            for b in bars:
                bt = parse_utc(b[0])
                op, cl = session(sym, bt.date())
                if bt >= t_o and bt >= op + dt.timedelta(minutes=LIM["open_delay_min"]) and bt < cl and bt <= now:
                    pick = b
                    break
            if not pick:
                msgs.append("{} {} {}: waiting for a bar".format(o["id"], side, sym))
                continue
            qd = get_quote(sym)
            cur = qd["currency"] if qd else ("GBp" if sym.endswith(".L") else "EUR")
            px = pick[1] * (1 + slippage(sym)) if side == "BUY" else pick[1] * (1 - slippage(sym))
            unit = to_eur(px, cur, fx)
            if unit is None:
                msgs.append("{}: no fx rate yet".format(o["id"]))
                continue
            gross = unit * o["qty"]
            c = costs(sym, side, gross, cur)
            if side == "BUY":
                if led["cash"] < gross + c["total"]:
                    o["status"], o["reasons"] = "REJECTED", o.get("reasons", []) + ["cash too low at fill time"]
                    log_event(dict(o, event="rejected"))
                    changed = True
                    continue
                led["cash"] = round(led["cash"] - gross - c["total"], 2)
                p = next((x for x in led["positions"] if x["symbol"] == sym), None)
                d0 = parse_utc(pick[0]).date()
                if p:
                    tot = p["qty"] + o["qty"]
                    p["avg_price"] = (p["avg_price"] * p["qty"] + px * o["qty"]) / tot
                    p["qty"] = tot
                    p["exit_by"] = max(p["exit_by"], add_trading_days(d0, int(o["horizon"])).isoformat())
                else:
                    led["positions"].append({"symbol": sym, "name": NAMES.get(sym, sym), "qty": o["qty"], "avg_price": px, "currency": cur, "opened": d0.isoformat(),
                                             "exit_by": add_trading_days(d0, int(o["horizon"])).isoformat(), "catalyst": o["catalyst"], "confidence": o["confidence"], "horizon": o["horizon"],
                                             "agent": o["agent"], "theme": o["theme"]})
                realized = None
            else:
                p = next(x for x in led["positions"] if x["symbol"] == sym)
                cost_eur = to_eur(p["avg_price"], cur, fx) * o["qty"]
                led["cash"] = round(led["cash"] + gross - c["total"], 2)
                realized = round(gross - c["total"] - cost_eur, 2)
                p["qty"] -= o["qty"]
                if p["qty"] <= 0:
                    led["positions"].remove(p)
            o["status"] = "FILLED"
            fill = {"id": len(led["fills"]) + 1, "order_id": o["id"], "time": pick[0], "symbol": sym, "side": side, "qty": o["qty"], "price": round(px, 4), "currency": cur, "fee_eur": c["total"],
                    "gross_eur": round(gross, 2), "costs": c, "realized_eur": realized, "catalyst": o.get("catalyst", ""), "agent": o["agent"], "source": o["source"], "theme": o["theme"]}
            led["fills"].append(fill)
            log_event(dict(fill, event="filled"))
            msgs.append("FILLED {} {} {} @ {:.4f} {} (costs {} EUR)".format(side, o["qty"], sym, px, cur, c["total"]))
            changed = True
        if changed:
            save(led)
    return msgs


# ---------------------------------------------------------------- watchers, close, reconcile
def system_orders(now=None):
    """Exit requests from the risk manager: horizon reached (placed in the last 45 minutes of the session) and the -8% stop (any time in session)."""
    now = now or utc_now()
    out = []
    led = load()
    if not is_trading_day(now.date()):
        return out
    for p in led["positions"]:
        o, c = session(p["symbol"], now.date())
        if not (o <= now <= c - dt.timedelta(minutes=10)):
            continue
        q = get_quote(p["symbol"])
        if q and p["avg_price"] and (q["price"] / p["avg_price"] - 1) * 100 <= LIM["stop_pct"]:
            out.append(submit({"symbol": p["symbol"], "side": "SELL", "qty": p["qty"], "tag": "stop"}, "system:stop", now))
        elif p["exit_by"] <= now.date().isoformat() and now >= c - dt.timedelta(minutes=45):
            out.append(submit({"symbol": p["symbol"], "side": "SELL", "qty": p["qty"], "tag": "horizon"}, "system:horizon", now))
    return out


def replay_exits(now=None):
    """Cloud mode (no always-on watcher): find, from the 5-minute bars since each entry, when the -8% stop or the horizon exit WOULD have fired, and submit the sell with that
    historical trigger time (the sell then fills at the first bar after it, exactly as the live watcher would have). Idempotent per day, symbol and tag. Returns the orders."""
    now = now or utc_now()
    out = []
    led = load()
    for p in led["positions"]:
        sym = p["symbol"]
        ft = next((f["time"] for f in reversed(led["fills"]) if f["symbol"] == sym and f["side"] == "BUY"), None)
        if not ft:
            continue
        t0 = parse_utc(ft)
        stop_px = p["avg_price"] * (1 + LIM["stop_pct"] / 100)
        trig, tag = None, None
        for b in get_bars(sym):
            bt = parse_utc(b[0])
            if bt <= t0:
                continue                         # never the entry bar itself
            op, cl = session(sym, bt.date())
            end = bt + dt.timedelta(minutes=5)
            if not (op <= bt < cl) or end > now:
                continue
            if b[4] is not None and b[4] <= stop_px:
                trig, tag = end, "stop"           # the bar closed at or below the stop: the order exists from the bar's end
                break
        ex = dt.date.fromisoformat(p["exit_by"])
        _, cl = session(sym, ex)
        th = cl - dt.timedelta(minutes=45)
        if th <= now and (trig is None or th < trig):
            trig, tag = th, "horizon"
        if trig and trig <= now:
            out.append(submit({"symbol": sym, "side": "SELL", "qty": p["qty"], "tag": tag}, "system:" + tag, trig))
    return out


def mark_to_market(now=None, write=True):
    now = now or utc_now()
    with Lock():
        led = load()
        fx = get_fx()
        eq = equity_now(led, fx)
        if write:
            d = now.date().isoformat()
            led["equity_history"] = [h for h in led["equity_history"] if h["date"] != d] + [{"date": d, "equity": round(eq, 2)}]
            save(led)
    return round(eq, 2)


def accrue_custody(now=None):
    now = now or utc_now()
    with Lock():
        led = load()
        d = now.date().isoformat()
        if led.get("custody_day") == d or not led["positions"]:
            return 0.0
        fx = get_fx()
        mv = sum(to_eur((get_quote(p["symbol"]) or {"price": p["avg_price"]})["price"], p["currency"], fx) * p["qty"] for p in led["positions"])
        fee = round(mv * CUSTODY_YEAR / 365, 4)
        led["cash"] = round(led["cash"] - fee, 4)
        led["custody_paid"] = round(led.get("custody_paid", 0) + fee, 4)
        led["custody_day"] = d
        save(led)
        return fee


def reconcile():
    """Recompute cash and positions from the fills; return a list of mismatches (empty means consistent)."""
    led = load()
    cash = led["start_cash"] - led.get("custody_paid", 0.0)
    qty = {}
    for f in led["fills"]:
        cash += (-f["gross_eur"] - f["fee_eur"]) if f["side"] == "BUY" else (f["gross_eur"] - f["fee_eur"])
        qty[f["symbol"]] = qty.get(f["symbol"], 0) + (f["qty"] if f["side"] == "BUY" else -f["qty"])
    bad = []
    if abs(cash - led["cash"]) > 0.05:
        bad.append("cash ledger {:.2f} vs recomputed {:.2f}".format(led["cash"], cash))
    have = {p["symbol"]: p["qty"] for p in led["positions"]}
    for s in set(qty) | set(have):
        if qty.get(s, 0) != have.get(s, 0):
            bad.append("position {} ledger {} vs fills {}".format(s, have.get(s, 0), qty.get(s, 0)))
    return bad


def outcomes_block():
    """Closed round trips (FIFO per symbol) as facts for the agent, plus the tally. Point-in-time: only filled sells count."""
    led = load()
    lots, closed = {}, []
    for f in led["fills"]:
        if f["side"] == "BUY":
            lots.setdefault(f["symbol"], []).append(dict(f))
        else:
            b = lots.get(f["symbol"], [])
            if b:
                e = b[0]
                net = (f["gross_eur"] - f["fee_eur"]) - (e["gross_eur"] + e["fee_eur"]) * f["qty"] / e["qty"]
                closed.append({"symbol": f["symbol"], "theme": e.get("theme"), "entered": e["time"][:10], "exited": f["time"][:10], "net_eur": round(net, 2),
                               "net_pct": round(net / (e["gross_eur"] * f["qty"] / e["qty"]) * 100, 2), "catalyst": str(e.get("catalyst", ""))[:140], "confidence": None, "exit": f["source"]})
                b[0]["qty"] -= f["qty"]
                if b[0]["qty"] <= 0:
                    b.pop(0)
    if not closed:
        return "# Outcomes of your past trades\nNo trade has closed yet. Nothing to learn from yet; do not invent lessons."
    L = ["# Outcomes of your past trades (facts from the broker ledger; closed trades only)"]
    for c in closed[-30:]:
        L.append("- {} {}: in {} out {} ({}): net {:+.2f} EUR ({:+.2f}%). Catalyst quoted: {}".format(c["theme"], c["symbol"], c["entered"], c["exited"], c["exit"], c["net_eur"], c["net_pct"], c["catalyst"] or "(none)"))
    L.append("Tally: {} closed trades, {} won, mean net {:+.2f}%".format(len(closed), sum(c["net_eur"] > 0 for c in closed), sum(c["net_pct"] for c in closed) / len(closed)))
    return "\n".join(L)


# ---------------------------------------------------------------- self-test
def selftest():
    global PAPER
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    PAPER = Path(tempfile.mkdtemp(prefix="paper_test_"))     # never the real ledger
    # time rules
    check("DST: 2026-03-28 winter, 03-29 02:00 UTC summer", not is_summer(dt.datetime(2026, 3, 28, 12, tzinfo=dt.timezone.utc)) and is_summer(dt.datetime(2026, 3, 29, 2, tzinfo=dt.timezone.utc)))
    check("DST: 2026-10-24 summer, 10-25 02:00 UTC winter", is_summer(dt.datetime(2026, 10, 24, 12, tzinfo=dt.timezone.utc)) and not is_summer(dt.datetime(2026, 10, 25, 2, tzinfo=dt.timezone.utc)))
    o, c = session("SAP.DE", dt.date(2026, 11, 9))
    check("winter session 08:00-16:30 UTC", (o.hour, o.minute, c.hour, c.minute) == (8, 0, 16, 30))
    o, c = session("SAP.DE", dt.date(2026, 7, 9))
    check("summer session 07:00-15:30 UTC", (o.hour, c.hour, c.minute) == (7, 15, 30))
    check("Oslo closes 15:20 UTC in winter", session("EQNR.OL", dt.date(2026, 11, 9))[1].minute == 20)
    check("weekend and holiday closed", not is_trading_day(dt.date(2026, 11, 14)) and not is_trading_day(dt.date(2026, 12, 25)))
    check("5 trading days from Fri 2026-11-06 skips the weekend", add_trading_days(dt.date(2026, 11, 6), 5) == dt.date(2026, 11, 13))
    # costs
    c = costs("SHEL.L", "BUY", 333.0, "GBp")
    check("UK buy: commission 2.5 + fx + 0.5% tax", c["commission"] == 2.5 and abs(c["tax"] - 1.67) < 0.01 and c["fx"] > 0)
    check("sell has no purchase tax", costs("SHEL.L", "SELL", 333.0, "GBp")["tax"] == 0)
    # fake market
    FX = {"EUR": 1.0, "GBp": 1.15, "CHF": 1.08}
    Q = {"SAN.PA": {"symbol": "SAN.PA", "price": 86.0, "currency": "EUR", "age_minutes": 3}, "SHEL.L": {"symbol": "SHEL.L", "price": 3700.0, "currency": "GBp", "age_minutes": 3},
         "IFX.DE": {"symbol": "IFX.DE", "price": 47.0, "currency": "EUR", "age_minutes": 3}, "BP.L": {"symbol": "BP.L", "price": 480.0, "currency": "GBp", "age_minutes": 3},
         "BAYN.DE": {"symbol": "BAYN.DE", "price": 55.0, "currency": "EUR", "age_minutes": 3}}
    global get_fx, get_quote, get_bars
    g0 = (get_fx, get_quote, get_bars)
    get_fx = lambda: FX                       # noqa: E731
    get_quote = lambda s: Q.get(s)            # noqa: E731
    day = dt.datetime(2026, 11, 9, 13, 0, tzinfo=dt.timezone.utc)
    BARS = {"SAN.PA": [[iso(day.replace(hour=13, minute=m)), 86.0 + m / 100, 87, 85, 86, 100] for m in range(0, 60, 5)]}
    get_bars = lambda s: BARS.get(s, [])      # noqa: E731
    try:
        o1 = submit({"symbol": "SAN.PA", "side": "BUY", "qty": 4, "confidence": 0.6, "catalyst": "x", "horizon": 10}, "agent", day, Q["SAN.PA"])
        check("buy accepted (4 x 86 = 344 EUR fits the 350 cap)", o1["status"] == "ACCEPTED" and o1["qty"] == 4)
        big = risk_check(new_ledger(), {"symbol": "SAN.PA", "side": "BUY", "qty": 6, "confidence": 0.6, "catalyst": "x", "horizon": 10}, day, FX, Q["SAN.PA"])
        check("oversized quantity is shrunk to the cap", big[0] and big[2] == 4 and big[1])
        o1b = submit({"symbol": "SAN.PA", "side": "BUY", "qty": 4, "confidence": 0.6, "catalyst": "x", "horizon": 10}, "agent", day, Q["SAN.PA"])
        check("same order twice is idempotent", o1b.get("duplicate") is True)
        lowc = submit({"symbol": "IFX.DE", "side": "BUY", "qty": 5, "confidence": 0.4, "catalyst": "x", "horizon": 10}, "agent", day, Q["IFX.DE"])
        check("low confidence rejected", lowc["status"] == "REJECTED")
        nocat = submit({"symbol": "BAYN.DE", "side": "BUY", "qty": 5, "confidence": 0.6, "catalyst": "", "horizon": 10}, "agent", day, Q["BAYN.DE"])
        check("missing catalyst rejected", nocat["status"] == "REJECTED")
        late = submit({"symbol": "BP.L", "side": "BUY", "qty": 50, "confidence": 0.6, "catalyst": "x", "horizon": 10}, "agent", day.replace(hour=16, minute=10), Q["BP.L"])
        check("buy in the last 30 minutes rejected", late["status"] == "REJECTED" and "cutoff" in " ".join(late["reasons"]))
        wk = submit({"symbol": "BP.L", "side": "BUY", "qty": 50, "confidence": 0.6, "catalyst": "x", "horizon": 10}, "agent", dt.datetime(2026, 11, 14, 10, 0, tzinfo=dt.timezone.utc), Q["BP.L"])
        check("buy on a Saturday rejected", wk["status"] == "REJECTED")
        out = submit({"symbol": "GSK.L", "side": "BUY", "qty": 1, "confidence": 0.6, "catalyst": "x", "horizon": 10}, "agent", day, {"symbol": "GSK.L", "price": 1700.0, "currency": "GBp", "age_minutes": 3})
        check("order too small for the 1% fee rule rejected", out["status"] == "REJECTED")
        offu = submit({"symbol": "AAPL", "side": "BUY", "qty": 1, "confidence": 0.9, "catalyst": "x", "horizon": 10}, "agent", day, None)
        check("symbol outside the universe rejected", offu["status"] == "REJECTED")
        # fill
        msgs = process_fills(day + dt.timedelta(minutes=30))
        led = load()
        check("fill uses a bar at or after the order time", any("FILLED" in m for m in msgs) and led["fills"][0]["time"] >= o1["time"])
        check("fill price is above the bar open (adverse slippage)", led["fills"][0]["price"] > 86.0)
        check("cash fell by gross + costs", abs(led["cash"] - (1000 - led["fills"][0]["gross_eur"] - led["fills"][0]["fee_eur"])) < 0.01)
        check("reconcile is clean after a buy", reconcile() == [])
        # exits
        p = led["positions"][0]
        check("exit_by is 10 trading days after the fill date", p["exit_by"] == add_trading_days(dt.date(2026, 11, 9), 10).isoformat())
        Q["SAN.PA"]["price"] = 78.0
        so = system_orders(day.replace(hour=14, minute=0))
        check("stop at -8% creates a sell", so and so[0]["side"] == "SELL" and so[0]["status"] == "ACCEPTED")
        BARS["SAN.PA"] = BARS["SAN.PA"] + [[iso(day.replace(hour=14, minute=m)), 78.0, 78, 77, 78, 10] for m in range(0, 30, 5)]
        process_fills(day.replace(hour=14, minute=40))
        led = load()
        check("position closed and reconcile clean", not led["positions"] and reconcile() == [] and led["fills"][-1]["realized_eur"] < 0)
        check("outcomes block lists the closed trade", "Tally: 1 closed trades, 0 won" in outcomes_block())
        # replay (cloud mode): a stop that fired while nobody was watching is found from the bars
        led0 = load()
        led0["positions"].append({"symbol": "BAYN.DE", "name": "Bayer", "qty": 3, "avg_price": 90.0, "currency": "EUR", "opened": "2026-11-09", "exit_by": "2026-11-30", "catalyst": "x", "confidence": 0.6,
                                  "horizon": 10, "agent": "t", "theme": "pharma"})
        led0["fills"].append({"id": 99, "order_id": "t-buy", "time": iso(day.replace(hour=13, minute=0)), "symbol": "BAYN.DE", "side": "BUY", "qty": 3, "price": 90.0, "currency": "EUR", "fee_eur": 2.5,
                              "gross_eur": 270.0, "costs": {}, "realized_eur": None, "catalyst": "x", "agent": "t", "source": "agent", "theme": "pharma"})
        led0["cash"] -= 272.5
        save(led0)
        BARS["BAYN.DE"] = [[iso(day.replace(hour=15, minute=m)), 90.0, 90, 89, 90.0 if m < 20 else 82.0, 10] for m in range(0, 60, 5)] + [[iso(day.replace(hour=16, minute=0)), 82.0, 82, 81, 82.0, 10]]
        rs = replay_exits(day.replace(hour=16, minute=20))
        check("replay finds the stop from the bars and uses the bar end as the order time", rs and rs[0]["status"] == "ACCEPTED" and rs[0]["time"] == iso(day.replace(hour=15, minute=25)) and "stop" in rs[0]["id"])
        check("replay is idempotent", replay_exits(day.replace(hour=16, minute=20))[0].get("duplicate") is True)
        process_fills(day.replace(hour=16, minute=20))
        check("replayed stop fills at the next bar after the trigger", load()["fills"][-1]["symbol"] == "BAYN.DE" and load()["fills"][-1]["time"] == iso(day.replace(hour=15, minute=25)) and not any(x["symbol"] == "BAYN.DE" for x in load()["positions"]))
        led1 = load()
        led1["cash"], led1["fills"] = 1000.0, []
        led1["positions"], led1["orders"] = [], []
        save(led1)
        led1["equity_history"] = []
        # loss cap
        led["equity_history"] = [{"date": "2026-11-06", "equity": 1000.0}]
        led["cash"] = 960.0
        save(led)
        Q["RIO.L"] = {"symbol": "RIO.L", "price": 5000.0, "currency": "GBp", "age_minutes": 3}
        cap = submit({"symbol": "RIO.L", "side": "BUY", "qty": 5, "confidence": 0.6, "catalyst": "x", "horizon": 10}, "agent", day, Q["RIO.L"])
        check("daily loss cap blocks buys", cap["status"] == "REJECTED" and "daily loss" in " ".join(cap["reasons"]))
        # atomic write: no temp file left, valid JSON
        check("ledger written atomically", not (PAPER / "ledger.json.tmp").exists() and json.loads((PAPER / "ledger.json").read_text(encoding="utf-8"))["mode"] == "PAPER")
        check("event log has entries", len((PAPER / "orders.jsonl").read_text(encoding="utf-8").splitlines()) >= 8)
    finally:
        get_fx, get_quote, get_bars = g0
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


def status():
    led = load()
    eq = equity_now(led)
    print("mode {} cash {:.2f} equity {:.2f} positions {} orders {} fills {}".format(led["mode"], led["cash"], eq, len(led["positions"]), len(led["orders"]), len(led["fills"])))
    for p in led["positions"]:
        print("  {} x{} avg {:.2f} {} exit_by {}".format(p["symbol"], p["qty"], p["avg_price"], p["currency"], p["exit_by"]))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "selftest":
        sys.exit(selftest())
    elif cmd == "status":
        status()
    elif cmd == "reconcile":
        b = reconcile()
        print("\n".join(b) or "consistent")
        sys.exit(1 if b else 0)
    else:
        print(__doc__)
