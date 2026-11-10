"""The idea lab: a second, fully separate paper account that tests NEW trading ideas, so the main account keeps running exactly as pre-registered. Research and simulation only.
Isolation (enforced in paper_broker.py): the lab runs with LAB=1 PAPER_DIR=data/paper_lab and its own state branch claude/lab-state; the broker refuses LAB=1 without a separate
directory, and refuses the lab directory without LAB=1. The lab never reads or writes data/paper, and the main agents never read anything from the lab. Nothing moves into the main
rules except by a decision of the user, logged in PREREG_EU.md.
Lab limits (LIM in paper_broker when LAB=1): 1,000 EUR, 5 positions, 25% each, no confidence bar, horizons 1/2/3/5/10/20, 5 new buys a day; costs, slippage, stop and fills identical to main.
Files in data/paper_lab/: ledger.json, orders.jsonl, ideas.json (the registry), run/<day>/lab_input.md and lab_output.json.
Honest scoring: every closed lab trade is compared with the mean move of the whole universe over the same holding days (the 'luck' benchmark). An idea needs at least 20 closed trades
and a positive mean excess over that benchmark, after costs, before it is called promising; promising is only a candidate for the user to review.
"""
import datetime as dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import paper_broker as pb  # noqa: E402
import live_feed as lf  # noqa: E402

MIN_CLOSED = 20
MAX_TESTING = 4
STATUS = ("proposed", "testing", "promising", "rejected", "retired")


def require_lab():
    if not pb.LAB:
        raise SystemExit("lab commands need LAB=1 PAPER_DIR=data/paper_lab")


def ideas_file():
    return pb.PAPER / "ideas.json"


def load_ideas():
    f = ideas_file()
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []


def merge_ideas(updates, day):
    """Apply the agent's idea list (new or changed ideas) to the registry. Returns problems."""
    ideas = {i["id"]: i for i in load_ideas()}
    probs = []
    for u in updates or []:
        try:
            iid = str(u["id"]).strip()[:40]
            if not iid or not str(u.get("rule", "")).strip() or not str(u.get("hypothesis", "")).strip():
                raise ValueError("id, hypothesis and rule are required")
            st = u.get("status", "proposed")
            if st not in STATUS:
                raise ValueError("bad status " + str(st))
        except Exception as e:  # noqa: BLE001
            probs.append("idea rejected: " + str(e)[:60])
            continue
        old = ideas.get(iid)
        if st == "promising":                                    # only the script sets this, from the numbers
            probs.append("{}: 'promising' is set by the script from results, not by the agent".format(iid))
            st = old["status"] if old else "testing"
        ideas[iid] = {"id": iid, "hypothesis": str(u["hypothesis"])[:300], "rule": str(u["rule"])[:600], "source": str(u.get("source", ""))[:200], "status": st,
                      "created": old["created"] if old else str(day), "note": str(u.get("note", ""))[:300]}
    testing = [i for i in ideas.values() if i["status"] == "testing"]
    if len(testing) > MAX_TESTING:
        probs.append("more than {} ideas in testing: extra ones set back to proposed".format(MAX_TESTING))
        for i in sorted(testing, key=lambda x: x["created"], reverse=True)[:len(testing) - MAX_TESTING]:
            i["status"] = "proposed"
    ideas_file().parent.mkdir(parents=True, exist_ok=True)
    ideas_file().write_text(json.dumps(list(ideas.values()), indent=1), encoding="utf-8")
    return probs


def closed_trades(led=None):
    """Closed round trips (FIFO per symbol) with the idea id taken from the buy fill's agent tag 'lab:<id>'."""
    led = led or pb.load()
    lots, out = {}, []
    for f in led["fills"]:
        if f["side"] == "BUY":
            lots.setdefault(f["symbol"], []).append(dict(f))
        else:
            b = lots.get(f["symbol"], [])
            if b:
                e = b[0]
                net = (f["gross_eur"] - f["fee_eur"]) - (e["gross_eur"] + e["fee_eur"]) * f["qty"] / e["qty"]
                out.append({"idea": str(e.get("agent", "")).replace("lab:", "", 1), "symbol": f["symbol"], "entered": e["time"][:10], "exited": f["time"][:10],
                            "net_pct": round(net / (e["gross_eur"] * f["qty"] / e["qty"]) * 100, 2), "net_eur": round(net, 2)})
                b[0]["qty"] -= f["qty"]
                if b[0]["qty"] <= 0:
                    b.pop(0)
    return out


def luck_benchmark(entered, exited, cache):
    """Mean move of every universe name from the close on the entry day to the close on the exit day (daily closes)."""
    rets = []
    for s in pb.ALLOWED:
        if s not in cache:
            try:
                cache[s] = {b[0][:10]: b[4] for b in lf.bars(s, "6mo", "1d") if b[4] is not None}
            except Exception:  # noqa: BLE001
                cache[s] = {}
        a, z = cache[s].get(entered), cache[s].get(exited)
        if a and z:
            rets.append((z / a - 1) * 100)
    return sum(rets) / len(rets) if rets else None


def results_block(led=None, cache=None):
    cache = cache if cache is not None else {}
    tr = closed_trades(led)
    ideas = load_ideas()
    if not ideas:
        return "# Lab results\nNo ideas registered yet."
    L = ["# Lab results per idea (closed trades only; excess = net trade % minus the mean move of the whole universe over the same days, i.e. the luck benchmark)"]
    for i in ideas:
        t = [x for x in tr if x["idea"] == i["id"]]
        ex = []
        for x in t:
            b = luck_benchmark(x["entered"], x["exited"], cache)
            if b is not None:
                ex.append(x["net_pct"] - b)
        s = "- [{}] {} ({}): {} closed".format(i["status"], i["id"], i["hypothesis"][:90], len(t))
        if t:
            s += ", {} won, mean net {:+.2f}%".format(sum(x["net_eur"] > 0 for x in t), sum(x["net_pct"] for x in t) / len(t))
        if ex:
            s += ", mean excess {:+.2f}% over {} benchmarked".format(sum(ex) / len(ex), len(ex))
        if len(t) >= MIN_CLOSED and ex and sum(ex) / len(ex) > 0 and sum(x["net_pct"] for x in t) / len(t) > 0:
            s += "  => PROMISING (candidate for the user to review)"
        elif len(t) < MIN_CLOSED:
            s += "  => too few closed trades ({} needed) to judge".format(MIN_CLOSED)
        L.append(s)
    return "\n".join(L)


def sync_status(day):
    """The script, not the agent, marks ideas promising once the numbers say so (and back to testing if they fall)."""
    ideas = load_ideas()
    if not ideas:
        return
    tr, cache, changed = closed_trades(), {}, False
    for i in ideas:
        t = [x for x in tr if x["idea"] == i["id"]]
        if len(t) < MIN_CLOSED or i["status"] in ("rejected", "retired"):
            continue
        ex = [x["net_pct"] - b for x in t for b in [luck_benchmark(x["entered"], x["exited"], cache)] if b is not None]
        good = bool(ex) and sum(ex) / len(ex) > 0 and sum(x["net_pct"] for x in t) / len(t) > 0
        new = "promising" if good else "testing"
        if new != i["status"]:
            i["status"], changed = new, True
    if changed:
        ideas_file().write_text(json.dumps(ideas, indent=1), encoding="utf-8")


def features(cache=None):
    """Per name: last close, 1/5/20-day move and distance below the 3-month high, from daily bars (point in time: bars up to now)."""
    out = {}
    for s in sorted(pb.ALLOWED):
        try:
            c = [b[4] for b in lf.bars(s, "3mo", "1d") if b[4] is not None]
        except Exception:  # noqa: BLE001
            c = []
        if len(c) >= 21:
            out[s] = {"last": round(c[-1], 2), "d1": round((c[-1] / c[-2] - 1) * 100, 2), "d5": round((c[-1] / c[-6] - 1) * 100, 2), "d20": round((c[-1] / c[-21] - 1) * 100, 2),
                      "below_3m_high": round((c[-1] / max(c) - 1) * 100, 2)}
    return out


def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    check("lab flag is on in this self-test run", pb.LAB)
    check("lab directory is not the main account directory", pb.PAPER.resolve() != (ROOT / "data" / "paper").resolve())
    day = dt.date(2026, 11, 10)
    pr = merge_ideas([{"id": "a", "hypothesis": "h", "rule": "r", "status": "testing"}, {"id": "b", "hypothesis": "h", "rule": "", "status": "testing"},
                      {"id": "c", "hypothesis": "h", "rule": "r", "status": "promising"}], day)
    ids = {i["id"]: i["status"] for i in load_ideas()}
    check("idea without a rule is rejected", "b" not in ids and any("rule" in p for p in pr))
    check("the agent cannot set promising by itself", ids.get("c") == "testing")
    for k in "defg":
        merge_ideas([{"id": k, "hypothesis": "h", "rule": "r", "status": "testing"}], day)
    check("at most {} ideas in testing".format(MAX_TESTING), sum(i["status"] == "testing" for i in load_ideas()) <= MAX_TESTING)
    led = pb.load()
    led["fills"] = [{"side": "BUY", "symbol": "SHEL.L", "qty": 10, "gross_eur": 100.0, "fee_eur": 1.0, "time": "2026-11-02T09:00:00Z", "agent": "lab:a"},
                    {"side": "SELL", "symbol": "SHEL.L", "qty": 10, "gross_eur": 110.0, "fee_eur": 1.0, "time": "2026-11-09T09:00:00Z", "agent": "x"}]
    t = closed_trades(led)
    check("closed trade carries the idea id and net percent", t and t[0]["idea"] == "a" and abs(t[0]["net_pct"] - (110 - 1 - 101) / 100 * 100) < 0.01)
    check("results block flags too few trades", "too few closed trades" in results_block(led, {s: {} for s in pb.ALLOWED}))
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "selftest":
        sys.exit(selftest())      # run as: LAB=1 PAPER_DIR=<temporary directory> python -I src/lab.py selftest
    elif c == "results":
        require_lab()
        sys.stdout.reconfigure(encoding="utf-8")
        print(results_block())
    else:
        print(__doc__)
