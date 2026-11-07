"""Post-earnings behavior test: reaction size, and what the stock does afterwards (no data after 2024-12-31 is used).

Usage: python -I src/run_earnings_test.py
Events: data/processed/earnings_events.csv (SEC 8-K Item 2.02). Reaction day R = filing day if accepted before 16:00 New York time,
otherwise the next trading day; reaction = close(R) / close(R-1) - 1. A decision is made after seeing the reaction: buy at the close
of R+1, sell H trading days later (H = 5, 10, 20), cost 0.3% round trip. Excess = the event group's mean net return minus the same
stock's unconditional mean H-day net return in the same period (removes the stock's own drift).
Buckets: strong up (reaction >= +3%), strong down (<= -3%), small (|reaction| < 3%). Periods: build (up to 2022), validation (2023-2024).
The final test period (2025 onward) is not used. Writes results/earnings_test.csv.
"""
import csv
import math
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import familydata as fd  # noqa: E402

COST = 0.3
LAST = "2024-12-31"
PER = {"build": ("0000", "2022-12-31"), "valid": ("2023-01-01", LAST)}


def per_of(d):
    for p, (a, b) in PER.items():
        if a <= d <= b:
            return p


def main():
    stocks = fd.load_stocks()
    ev = list(csv.DictReader(open(ROOT / "data" / "processed" / "earnings_events.csv", encoding="utf-8")))
    data = {}
    for t, cd in stocks.items():
        d = sorted(x for x in cd if x <= LAST)
        data[t] = (d, [cd[x] for x in d], {x: i for i, x in enumerate(d)})
    out, rows = [], []
    for H in (5, 10, 20):
        uncond = {}
        for t, (d, c, ix) in data.items():
            for i in range(1, len(d) - H - 2):
                p = per_of(d[i])
                if p:
                    uncond.setdefault((t, p), []).append((c[i + 1 + H] / c[i + 1] - 1) * 100 - COST)
        um = {k: st.mean(v) for k, v in uncond.items()}
        groups = {}
        reactions = []
        for e in ev:
            t = e["ticker"]
            if t not in data:
                continue
            d, c, ix = data[t]
            day = e["filing_date"]
            if e["session"] == "after_close":
                nxt = [x for x in d if x > day]
                if not nxt:
                    continue
                day = nxt[0]
            if day not in ix or ix[day] < 2 or ix[day] + 1 + H >= len(d):
                continue
            i = ix[day]
            p = per_of(day)
            if not p or (t, p) not in um:
                continue
            react = (c[i] / c[i - 1] - 1) * 100
            ret = (c[i + 1 + H] / c[i + 1] - 1) * 100 - COST
            b = "strong_up" if react >= 3 else "strong_down" if react <= -3 else "small"
            groups.setdefault((b, p), []).append((ret - um[(t, p)], ret))
            if H == 5:
                reactions.append((p, react))
        for (b, p), v in sorted(groups.items()):
            ex = [x[0] for x in v]
            t_stat = st.mean(ex) / (st.pstdev(ex) / math.sqrt(len(ex))) if len(ex) > 2 and st.pstdev(ex) > 0 else 0.0
            rows.append({"H": H, "bucket": b, "period": p, "n": len(v), "mean_excess_pct": round(st.mean(ex), 2), "t": round(t_stat, 2),
                         "mean_net_pct": round(st.mean(x[1] for x in v), 2), "win_pct": round(100 * sum(1 for x in ex if x > 0) / len(ex), 1)})
        if H == 5:
            for p in PER:
                r = [x for q, x in reactions if q == p]
                out.append((p, len(r), st.mean(abs(x) for x in r), 100 * sum(1 for x in r if x > 0) / len(r), 100 * sum(1 for x in r if abs(x) >= 3) / len(r)))
    print("reaction day move after earnings (all names): period, n, mean |move| %, share up %, share with |move| >= 3 %")
    for o in out:
        print("  {:6s} n={:4d} mean |move| {:.2f}  up {:.1f}  |move|>=3%: {:.1f}".format(*o))
    print("\nH  bucket        period   n   mean excess %   t    mean net %   win %")
    for r in rows:
        print("{:2d} {:12s} {:6s} {:4d} {:8.2f} {:8.2f} {:10.2f} {:8.1f}".format(r["H"], r["bucket"], r["period"], r["n"], r["mean_excess_pct"], r["t"], r["mean_net_pct"], r["win_pct"]))
    with open(ROOT / "results" / "earnings_test.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("saved results/earnings_test.csv")


if __name__ == "__main__":
    main()
