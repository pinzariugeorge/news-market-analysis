"""One phone page with ALL paper accounts: the main account and the three idea labs. Research and simulation only, paper money.
Each account's state lives in its own git branch (state_sync); this module reads them (read-only, into temporary folders) and builds a single self-contained page.
Used by `eu_report.py --snapshot` (so every job that already publishes the snapshot now publishes this overview) and by the lab jobs.
Balances use the delayed quotes of the moment the page is built. Per lab idea: status, closed trades, mean net %, mean excess over the luck benchmark (needs closed trades).
Run:  python -I src/eu_overview.py selftest
"""
import html
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import paper_broker as pb  # noqa: E402
import state_sync  # noqa: E402

ACCOUNTS = [("MAIN", "claude/paper-state", False), ("LAB core", "claude/lab-state", True), ("LAB short", "claude/lab-short-state", True), ("LAB news", "claude/lab-news-state", True)]


def e(x):
    return html.escape(str(x if x is not None else ""))


def rj(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def fetch(branch):
    """Read one account's state branch into a temp folder; returns the folder or None when the branch does not exist yet."""
    tmp = Path(tempfile.mkdtemp(prefix="overview_"))
    try:
        ok = state_sync.pull(ROOT, tmp, branch)
    except Exception:  # noqa: BLE001
        ok = False
    return tmp if ok else None


def lab_rows(d, led, cache):
    import lab
    ideas = rj(d / "ideas.json") or []
    tr = lab.closed_trades(led)
    out = []
    for i in ideas:
        t = [x for x in tr if x["idea"] == i["id"]]
        ex = []
        for x in t:
            b = lab.luck_benchmark(x["entered"], x["exited"], cache)
            if b is not None:
                ex.append(x["net_pct"] - b)
        out.append({"id": i["id"], "status": i["status"], "hyp": i["hypothesis"], "n": len(t), "net": (sum(x["net_pct"] for x in t) / len(t)) if t else None, "ex": (sum(ex) / len(ex)) if ex else None})
    return out


def shadow_line(d):
    done = rj(d / "shadow_scores.json") or {}
    f = d / "shadow.jsonl"
    total = len([x for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]) if f.exists() else 0
    if not total:
        return "Shadow calls: none yet."
    s = list(done.values())
    return "Shadow calls: {} logged, {} scored{}.".format(total, len(s), (", {:.0f}% right".format(100 * sum(c["correct"] for c in s) / len(s))) if s else "")


def card(name, is_lab, d, now_day, fx, cache):
    cls = lambda v: "up" if v > 0.004 else "down" if v < -0.004 else ""  # noqa: E731
    if d is None or not (d / "ledger.json").exists():
        return '<div class="card"><h2>{}</h2>No state yet (the first run has not happened).</div>'.format(e(name))
    led = rj(d / "ledger.json")
    eq = pb.equity_now(led, fx)
    prev = next((h["equity"] for h in reversed(led["equity_history"]) if h["date"] < now_day), led["start_cash"])
    day_eur, tot = eq - prev, (eq / led["start_cash"] - 1) * 100
    pos = "; ".join("{} x{}".format(p["symbol"], p["qty"]) for p in led["positions"]) or "none (all cash)"
    pend = ", ".join("{} {} x {}".format(o["side"], o["qty"], o["symbol"]) for o in led["orders"] if o["status"] == "ACCEPTED") or "none"
    fills = "; ".join("{} {} x {} @ {:.2f}".format(x["side"], x["qty"], x["symbol"], x["price"]) for x in led["fills"] if x["time"][:10] == now_day) or "none"
    h = ('<div class="card"><h2>{}{}</h2><div class="big">{:,.2f}</div><div class="row"><span class="{}">Today {:+.2f}</span><span class="{}">Total {:+.2f}%</span></div>'
         '<div class="mute">Cash {:,.2f} | Positions: {}</div><div class="mute">Waiting: {} | Today\'s fills: {}</div>').format(
        "\U0001F9EA " if is_lab else "", e(name), eq, cls(day_eur), day_eur, cls(tot), tot, led["cash"], e(pos), e(pend), e(fills))
    if is_lab:
        rows = lab_rows(d, led, cache)
        if rows:
            h += '<div class="tw"><table><tr><th>Idea</th><th>Status</th><th>Closed</th><th>Net %</th><th>vs luck %</th></tr>' + "".join(
                "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    e(r["id"]), e(r["status"]), r["n"], "-" if r["net"] is None else "{:+.2f}".format(r["net"]), "-" if r["ex"] is None else "{:+.2f}".format(r["ex"])) for r in rows) + "</table></div>"
        else:
            h += '<div class="mute">No ideas registered yet.</div>'
    else:
        h += '<div class="mute">{}</div>'.format(e(shadow_line(d)))
    return h + "</div>"


def build(now=None):
    now = now or pb.utc_now()
    day = now.date().isoformat()
    fx = pb.get_fx()
    cache, cards, tmps = {}, [], []
    for name, branch, is_lab in ACCOUNTS:
        d = fetch(branch)
        if d:
            tmps.append(d)
        cards.append(card(name, is_lab, d, day, fx, cache))
    for t in tmps:
        shutil.rmtree(t, ignore_errors=True)
    import eu_report
    body = '<main><div class="mute">All paper accounts, EUR - updated {} UTC</div>{}<div class="mute">Prices delayed about 15 minutes. "vs luck" = trade result minus the average move of all 22 names over the same days; an idea needs 20 closed trades to be judged. Paper money, research only.</div></main>'.format(now.strftime("%H:%M"), "".join(cards))
    return '<title>Account Snapshot</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<style>{}</style>\n{}'.format(eu_report.SNAP_CSS, body)


def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    base = Path(tempfile.mkdtemp(prefix="ov_test_"))
    (base / "m").mkdir()
    (base / "l").mkdir()
    led = pb.new_ledger()
    led["cash"] = 900.0
    led["positions"] = [{"symbol": "IFX.DE", "qty": 2, "avg_price": 50.0, "currency": "EUR"}]
    led["equity_history"] = [{"date": "2026-11-09", "equity": 1000.0}]
    (base / "m" / "ledger.json").write_text(json.dumps(led), encoding="utf-8")
    (base / "l" / "ledger.json").write_text(json.dumps(pb.new_ledger()), encoding="utf-8")
    (base / "l" / "ideas.json").write_text(json.dumps([{"id": "dip<x>", "status": "testing", "hypothesis": "h"}]), encoding="utf-8")
    old_q, old_fx = pb.get_quote, pb.get_fx
    pb.get_quote = lambda s: {"price": 55.0, "currency": "EUR", "age_minutes": 5}
    pb.get_fx = lambda: {"EUR": 1.0}
    try:
        m = card("MAIN", False, base / "m", "2026-11-10", {"EUR": 1.0}, {})
        l = card("LAB x", True, base / "l", "2026-11-10", {"EUR": 1.0}, {})
        n = card("LAB y", True, None, "2026-11-10", {"EUR": 1.0}, {})
    finally:
        pb.get_quote, pb.get_fx = old_q, old_fx
    check("main card shows equity 1,010.00 (cash 900 + 2 x 55)", "1,010.00" in m and "IFX.DE x2" in m)
    check("lab card carries the lab sign and escapes idea ids", "\U0001F9EA" in l and "dip&lt;x&gt;" in l)
    check("missing branch gives a clear 'no state yet' card", "No state yet" in n)
    shutil.rmtree(base, ignore_errors=True)
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "selftest":
        sys.exit(selftest())
    t0 = time.time()
    s = build()
    print(len(s), "bytes,", round(time.time() - t0, 1), "s")
