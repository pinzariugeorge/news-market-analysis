"""Forward log of the mechanical screens S1-S3 (PREREG_SCREEN.md) on the traded names. No tokens, no money, no orders, no effect on the account.
Each trading evening: evaluate the screens on today's daily bar for every traded stock, append triggers to data/paper/screen_log.jsonl, and score older triggers
at 10 and 20 trading days (entry = next day's open, exit = close H bars later, excess = minus the mean of all traded names over the same bars).
S1 = close > 200-day mean, volume >= 2x its prior-20-day mean, day return >= +2%.  S2 = close > 200-day mean, 3-day return <= -5%.
S3 = close > 200-day mean, volume >= 2x prior-20 mean, day return <= -4%.
Commands:  python -I src/screen_log.py run | score | report | selftest.  Research and simulation only."""
import datetime as dt
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import paper_broker as pb  # noqa: E402
import live_feed as lf  # noqa: E402

HS = (10, 20)


def _log():
    return pb.PAPER / "screen_log.jsonl"


def _scores():
    return pb.PAPER / "screen_scores.json"


def signals(bars):
    """bars: [(ts, o, h, l, c, v), ...] daily, oldest first. Returns (day, [screens]) for the last bar, or None when there is too little history."""
    b = [x for x in bars if x[1] is not None and x[4] is not None and x[5] is not None]
    n = len(b)
    if n < 205:
        return None
    cl = [x[4] for x in b]
    vo = [x[5] for x in b]
    i = n - 1
    ma = sum(cl[i - 199:i + 1]) / 200
    v20 = sum(vo[i - 20:i]) / 20
    up = cl[i] > ma
    vshock = v20 > 0 and vo[i] >= 2 * v20
    r1 = (cl[i] / cl[i - 1] - 1) * 100
    r3 = (cl[i] / cl[i - 3] - 1) * 100
    hits = []
    if up and vshock and r1 >= 2:
        hits.append("S1")
    if up and r3 <= -5:
        hits.append("S2")
    if up and vshock and r1 <= -4:
        hits.append("S3")
    return b[i][0][:10], hits


def _daily(sym):
    return [x for x in lf.bars(sym, "2y", "1d") if x[4] is not None]


def load_log():
    f = _log()
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()] if f.exists() else []


def run(now=None, fetch=None):
    """Evaluate today's bar for every traded name; append one record per day (idempotent). Returns the record or None."""
    now = now or pb.utc_now()
    day = now.date().isoformat()
    if any(r["day"] == day for r in load_log()):
        return None
    fetch = fetch or _daily
    trig, ev = [], 0
    for sym in sorted(pb.ALLOWED):
        try:
            res = signals(fetch(sym))
        except Exception:  # noqa: BLE001
            continue
        if not res or res[0] != day:
            continue
        ev += 1
        if res[1]:
            trig.append({"symbol": sym, "screens": res[1]})
    if ev == 0:
        return None
    rec = {"day": day, "evaluated": ev, "triggers": trig}
    _log().parent.mkdir(parents=True, exist_ok=True)
    with open(_log(), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


def _fwd(bars, entry_day, H):
    """(entry open, exit close) for the first bar dated after entry_day... bars oldest first; entry bar = first bar with date > entry_day."""
    d = [(x[0][:10], x[1], x[4]) for x in bars if x[1] is not None and x[4] is not None]
    for k, (dd, o, c) in enumerate(d):
        if dd > entry_day:
            if k + H < len(d):
                return dd, o, d[k + H][2]
            return None
    return None


def score(now=None, fetch=None):
    """Score every logged trigger whose horizon has passed. Returns the number of newly scored (screen, symbol, H) cases."""
    fetch = fetch or _daily
    f = _scores()
    done = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    cache = {}

    def bars_of(s):
        if s not in cache:
            cache[s] = fetch(s)
        return cache[s]

    n = 0
    for rec in load_log():
        for t in rec["triggers"]:
            for H in HS:
                cid = "{}-{}-{}".format(rec["day"], t["symbol"], H)
                if cid in done:
                    continue
                fw = _fwd(bars_of(t["symbol"]), rec["day"], H)
                if not fw:
                    continue
                ed, o, c = fw
                ret = (c / o - 1) * 100
                allr = []
                for s in sorted(pb.ALLOWED):
                    try:
                        x = _fwd(bars_of(s), rec["day"], H)
                    except Exception:  # noqa: BLE001
                        x = None
                    if x and x[0] == ed:
                        allr.append((x[2] / x[1] - 1) * 100)
                if len(allr) < 5:
                    continue
                done[cid] = {"day": rec["day"], "symbol": t["symbol"], "screens": t["screens"], "H": H, "entry_date": ed, "ret_pct": round(ret, 2),
                             "basket_pct": round(sum(allr) / len(allr), 2), "excess_pct": round(ret - sum(allr) / len(allr), 2)}
                n += 1
    if n:
        f.write_text(json.dumps(done, indent=1), encoding="utf-8")
    return n


def report():
    f = _scores()
    done = list(json.loads(f.read_text(encoding="utf-8")).values()) if f.exists() else []
    recs = load_log()
    L = ["Screen log: {} days logged, {} triggers, {} scored cases.".format(len(recs), sum(len(r["triggers"]) for r in recs), len(done))]
    for sc in ("S1", "S2", "S3"):
        for H in HS:
            xs = [c["excess_pct"] for c in done if sc in c["screens"] and c["H"] == H]
            if xs:
                m = sum(xs) / len(xs)
                L.append("{} {}d: n={} mean excess {:+.2f}% gross, {:+.2f}% net of 0.3%, {:+.2f}% net of 1.5%".format(sc, H, len(xs), m, m - 0.3, m - 1.5))
    return "\n".join(L)


def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    def mk(n, last_close, last_vol, last_prev=100.0):
        out = []
        for k in range(n):
            d = (dt.date(2025, 1, 1) + dt.timedelta(days=k)).isoformat()
            c = 100.0 if k < n - 1 else last_close
            if k == n - 2:
                c = last_prev
            out.append((d + "T07:00:00Z", c, c, c, c, 1000.0 if k < n - 1 else last_vol))
        return out

    check("too little history gives None", signals(mk(100, 103, 5000)) is None)
    s = signals(mk(260, 103, 5000))
    check("S1 on +3% with 5x volume above the 200-day mean", s and s[1] == ["S1"])
    check("quiet volume gives no S1", signals(mk(260, 103, 1000))[1] == [])
    old = pb.PAPER
    pb.PAPER = Path(tempfile.mkdtemp(prefix="screen_test_"))
    oa = dict(pb.ALLOWED)
    try:
        pb.ALLOWED.clear()
        for k in range(6):
            pb.ALLOWED["T%d.X" % k] = "chips"
        base = mk(260, 103, 5000)
        day = base[-1][0][:10]
        series = {"T0.X": base}
        for k in range(1, 6):
            series["T%d.X" % k] = mk(260, 100, 1000)
        now = dt.datetime.combine(dt.date.fromisoformat(day), dt.time(17), dt.timezone.utc)
        rec = run(now, fetch=lambda s: series[s])
        check("one trigger logged for T0.X", rec and rec["evaluated"] == 6 and rec["triggers"] == [{"symbol": "T0.X", "screens": ["S1"]}])
        check("run is idempotent per day", run(now, fetch=lambda s: series[s]) is None)
        ext = {}
        for s_, b in series.items():
            e = list(b)
            for j in range(1, 23):
                d = (dt.date.fromisoformat(day) + dt.timedelta(days=j)).isoformat()
                px = 110.0 if (s_ == "T0.X" and j >= 2) else 100.0
                e.append((d + "T07:00:00Z", px, px, px, px, 1000.0))
            ext[s_] = e
        check("not scored before the horizon exists", score(now, fetch=lambda s: series[s]) == 0)
        check("scored at 10 and 20 days", score(now, fetch=lambda s: ext[s]) == 2)
        sc = json.loads(_scores().read_text(encoding="utf-8"))
        c10 = sc[day + "-T0.X-10"]
        check("excess is the move minus the basket move", abs(c10["ret_pct"] - 10.0) < 0.01 and abs(c10["excess_pct"] - 8.33) < 0.05)
        check("report mentions S1", "S1 10d" in report())
    finally:
        pb.PAPER = old
        pb.ALLOWED.clear()
        pb.ALLOWED.update(oa)
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.stdout.reconfigure(encoding="utf-8")
    if c == "run":
        print(run())
    elif c == "score":
        print("scored:", score())
    elif c == "report":
        print(report())
    elif c == "selftest":
        sys.exit(selftest())
    else:
        print(__doc__)
