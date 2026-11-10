"""Shadow predictions: the main trader logs a call for every name it has a view on, whether or not it buys. A script scores each call at its horizon from daily closes.
No money, no orders, no effect on the account. It only makes the sample of scored calls grow much faster than the few real trades. Research and simulation only.
File: data/paper/shadow.jsonl (one JSON per call, appended; scored results in data/paper/shadow_scores.json).
Scoring (point in time, no look-ahead): entry = the price the trader saw (collected table, native currency); exit = the daily close on the horizon date; the horizon date is
entry day + horizon trading days. 'up' is right when the move beats twice the entry cost percent (the real hurdle); 'down' is right when the move is negative.
Commands:  python -I src/shadow.py score | block | selftest
"""
import datetime as dt
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import paper_broker as pb  # noqa: E402
import live_feed as lf  # noqa: E402

HOR = (5, 10, 20)
MAX_PER_DAY = 14


def _file():
    return pb.PAPER / "shadow.jsonl"


def _scores_file():
    return pb.PAPER / "shadow_scores.json"


def load_calls():
    f = _file()
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()] if f.exists() else []


def record(calls, table, day):
    """Validate and append the trader's shadow calls. Returns (stored, problems). Idempotent per day, symbol and horizon."""
    have = {c["id"] for c in load_calls()}
    stored, probs = 0, []
    for c in (calls or [])[:MAX_PER_DAY]:
        try:
            sym, dr, h = c["symbol"], str(c["direction"]).lower(), int(c["horizon_days"])
            conf = float(c.get("confidence", 0))
        except Exception as e:  # noqa: BLE001
            probs.append("malformed call: " + str(e)[:40])
            continue
        if sym not in pb.ALLOWED or dr not in ("up", "down") or h not in HOR or not (0 <= conf <= 1) or sym not in table:
            probs.append("rejected call {} {} {}".format(sym, dr, h))
            continue
        cid = "{}-{}-{}".format(day, sym, h)
        if cid in have:
            continue
        row = {"id": cid, "day": str(day), "symbol": sym, "direction": dr, "horizon_days": h, "confidence": conf, "catalyst": str(c.get("catalyst", ""))[:160],
               "entry_price": table[sym]["price"], "currency": table[sym]["currency"], "entry_cost_pct": table[sym]["entry_cost_pct"]}
        _file().parent.mkdir(parents=True, exist_ok=True)
        with open(_file(), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        have.add(cid)
        stored += 1
    return stored, probs


def _close_on(sym, d, cache):
    if sym not in cache:
        cache[sym] = {b[0][:10]: b[4] for b in lf.bars(sym, "6mo", "1d") if b[4] is not None}
    return cache[sym].get(d)


def score(now=None):
    """Score every call whose horizon date has passed and has a daily close. Returns the number newly scored."""
    now = now or pb.utc_now()
    f = _scores_file()
    done = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    cache, n = {}, 0
    for c in load_calls():
        if c["id"] in done:
            continue
        end = pb.add_trading_days(dt.date.fromisoformat(c["day"]), c["horizon_days"])
        if end >= now.date():
            continue
        px = _close_on(c["symbol"], end.isoformat(), cache)
        if px is None:
            continue
        ret = (px / c["entry_price"] - 1) * 100
        ok = ret > 2 * c["entry_cost_pct"] if c["direction"] == "up" else ret < 0
        done[c["id"]] = dict(c, exit_date=end.isoformat(), exit_price=px, ret_pct=round(ret, 2), correct=bool(ok))
        n += 1
    if n:
        f.write_text(json.dumps(done, indent=1), encoding="utf-8")
    return n


def block():
    """Facts for the trader and reviewer prompts."""
    f = _scores_file()
    done = list(json.loads(f.read_text(encoding="utf-8")).values()) if f.exists() else []
    pend = len(load_calls()) - len(done)
    if not done:
        return "# Shadow call results (scored calls, no money)\nNone scored yet ({} calls waiting for their horizon). Nothing to learn from yet.".format(pend)
    L = ["# Shadow call results (scored calls, no money; {} still waiting)".format(pend)]
    for c in sorted(done, key=lambda x: x["exit_date"])[-20:]:
        L.append("- {} {} {} {}d (conf {:.2f}): {:+.2f}% by {} -> {}. Catalyst: {}".format(c["day"], c["symbol"], c["direction"], c["horizon_days"], c["confidence"], c["ret_pct"], c["exit_date"],
                                                                                    "right" if c["correct"] else "wrong", c["catalyst"][:100] or "(none)"))
    for dr in ("up", "down"):
        s = [c for c in done if c["direction"] == dr]
        if s:
            L.append("Tally {}: {} calls, {} right ({:.0f}%), mean move {:+.2f}%".format(dr, len(s), sum(c["correct"] for c in s), 100 * sum(c["correct"] for c in s) / len(s), sum(c["ret_pct"] for c in s) / len(s)))
    hi = [c for c in done if c["confidence"] >= 0.6]
    lo = [c for c in done if c["confidence"] < 0.6]
    if hi and lo:
        L.append("Confidence check: calls at 0.60+ were right {:.0f}% of {}; below 0.60 {:.0f}% of {}.".format(100 * sum(c["correct"] for c in hi) / len(hi), len(hi), 100 * sum(c["correct"] for c in lo) / len(lo), len(lo)))
    return "\n".join(L)


def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    old = pb.PAPER
    pb.PAPER = Path(tempfile.mkdtemp(prefix="shadow_test_"))
    tbl = {"SHEL.L": {"price": 2500.0, "currency": "GBp", "entry_cost_pct": 1.0}, "AZN.L": {"price": 10000.0, "currency": "GBp", "entry_cost_pct": 1.0}}
    day = dt.date(2026, 11, 2)
    try:
        n, pr = record([{"symbol": "SHEL.L", "direction": "up", "horizon_days": 5, "confidence": 0.6, "catalyst": "x"}, {"symbol": "AZN.L", "direction": "down", "horizon_days": 5, "confidence": 0.55},
                        {"symbol": "ZZZ", "direction": "up", "horizon_days": 5, "confidence": 0.6}, {"symbol": "SHEL.L", "direction": "up", "horizon_days": 7, "confidence": 0.6}], tbl, day)
        check("two valid calls stored, two invalid rejected", n == 2 and len(pr) == 2)
        check("idempotent per day, symbol and horizon", record([{"symbol": "SHEL.L", "direction": "up", "horizon_days": 5, "confidence": 0.6}], tbl, day)[0] == 0)
        end = pb.add_trading_days(day, 5)
        closes = {"SHEL.L": 2600.0, "AZN.L": 9500.0}
        orig = lf.bars
        lf.bars = lambda s, r, i: [[end.isoformat() + "T16:00:00Z", 0, 0, 0, closes[s]]]
        check("a call is not scored before its horizon date", score(dt.datetime.combine(end, dt.time(12), dt.timezone.utc)) == 0)
        check("both calls scored after the horizon", score(dt.datetime.combine(end + dt.timedelta(days=1), dt.time(12), dt.timezone.utc)) == 2)
        lf.bars = orig
        sc = json.loads(_scores_file().read_text(encoding="utf-8"))
        check("up +4% beats the 2% hurdle; down -5% is right", sc[day.isoformat() + "-SHEL.L-5"]["correct"] and sc[day.isoformat() + "-AZN.L-5"]["correct"])
        check("block shows tallies", "Tally up: 1 calls, 1 right" in block())
        check("scoring again changes nothing", score(dt.datetime.combine(end + dt.timedelta(days=2), dt.time(12), dt.timezone.utc)) == 0)
    finally:
        pb.PAPER = old
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "score":
        print("scored:", score())
    elif c == "block":
        sys.stdout.reconfigure(encoding="utf-8")
        print(block())
    elif c == "selftest":
        sys.exit(selftest())
    else:
        print(__doc__)
