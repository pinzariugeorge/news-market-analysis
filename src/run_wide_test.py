"""Wide test: judge selection rules on many decisions, not on one 2-3 position account.

Usage: python -I src/run_wide_test.py [--sims 300]
Universe: the point-in-time rule-selected names (5 families x 4 = 20) at each decision date (universe/rule_selections.csv).
At each decision date d (every H trading days, H = 5, 10, 20) every name gets its features from closes up to d; each rule
selects a subset of names; the subset is held equal-weight from the close of d+1 to the close of d+1+H (one day signal delay).
Each position is charged a full round-trip cost (default 0.25%) for every decision, i.e. conservative (no netting of repeats).
Rules: all (equal-weight basket, the benchmark), momentum (top half by 20-day return), reversal (bottom half by 20-day return),
lowvol (lowest half by 60-day volatility), trend (above the 200-day average), oversold (RSI(14) < 30), random half (mean of many runs).
Per decision date the rule's basket return is compared with the benchmark basket ("excess"); statistics are over decision dates,
which do not overlap in time. Periods: 2022 (reference), 2023-2024 (validation), 2025 to now (final test). Nothing is tuned.
Writes results/wide_test.csv.
"""
import argparse
import csv
import math
import random
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import build_universe as bu          # noqa: E402
import run_indicator_tests as rit    # noqa: E402

COST = 0.25
PERIODS = (("2022", "2022-01-03", "2022-12-30"), ("2023-24", "2023-01-03", "2024-12-31"), ("2025-now", "2025-01-02", "2026-11-05"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", type=int, default=300)
    a = ap.parse_args()
    cands = [r["ticker"] for r in csv.DictReader(open(ROOT / "universe" / "candidates.csv", encoding="utf-8"))]
    close = {}
    for t in cands:
        try:
            _, b = bu.fetch(t, "10y")
            close[t] = {x[0]: x[1] for x in b}
        except Exception:  # noqa: BLE001
            pass
    sel = {}
    for r in csv.DictReader(open(ROOT / "universe" / "rule_selections.csv", encoding="utf-8")):
        sel.setdefault(r["asof"], []).append(r["ticker"])
    cal = sorted(close["XOM"])
    idx = {d: i for i, d in enumerate(cal)}
    # aligned close lists with forward fill, RSI per name
    arr, rsis = {}, {}
    for t, cd in close.items():
        last, lst = None, []
        for d in cal:
            last = cd.get(d, last)
            lst.append(last)
        arr[t] = lst
        first = next((k for k, v in enumerate(lst) if v is not None), None)
        if first is not None:
            seg = lst[first:]
            r = rit.rsi(seg)
            rsis[t] = [None] * first + r

    def universe_at(d):
        ok = [x for x in sel if x <= d]
        return sel[max(ok)] if ok else sel[min(sel)]

    rows = []
    rnd = random.Random(11)
    for H in (5, 10, 20):
        print("\n=== H = {} trading days, cost {}% per position per decision ===".format(H, COST))
        print("{:10s} {:9s} {:>5s} {:>9s} {:>9s} {:>6s} {:>7s} {:>6s}".format("period", "rule", "n", "mean%", "excess%", "t", "win%", "names"))
        for pname, d0, d1 in PERIODS:
            i0 = next(i for i, d in enumerate(cal) if d >= d0)
            i1 = max(i for i, d in enumerate(cal) if d <= d1)
            res = {k: [] for k in ("all", "momentum", "reversal", "lowvol", "trend", "oversold", "random_half")}
            counts = {k: [] for k in res}
            rand_means = []
            for i in range(max(i0, 201), i1 - H - 1, H):
                d = cal[i]
                names = [t for t in universe_at(d) if t in arr and arr[t][i] is not None and arr[t][i + 1] is not None and arr[t][i + 1 + H] is not None and arr[t][i - 200] is not None]
                if len(names) < 8:
                    continue
                fwd = {t: (arr[t][i + 1 + H] / arr[t][i + 1] - 1) * 100 - COST for t in names}
                mom = {t: arr[t][i] / arr[t][i - 20] - 1 for t in names}
                vol = {}
                for t in names:
                    w = [arr[t][k] for k in range(i - 60, i + 1)]
                    r = [w[k] / w[k - 1] - 1 for k in range(1, len(w))]
                    vol[t] = st.pstdev(r)
                ma200 = {t: sum(arr[t][i - 199:i + 1]) / 200 for t in names}
                half = len(names) // 2
                by_mom = sorted(names, key=lambda t: mom[t], reverse=True)
                by_vol = sorted(names, key=lambda t: vol[t])
                subsets = {
                    "all": names,
                    "momentum": by_mom[:half],
                    "reversal": by_mom[-half:],
                    "lowvol": by_vol[:half],
                    "trend": [t for t in names if arr[t][i] > ma200[t]],
                    "oversold": [t for t in names if rsis.get(t) and rsis[t][i] is not None and rsis[t][i] < 30]}
                for k, s in subsets.items():
                    if s:
                        res[k].append(st.mean(fwd[t] for t in s))
                        counts[k].append(len(s))
                    else:
                        res[k].append(None)     # no position: counts as 0 excess handled below
                        counts[k].append(0)
                ms = []
                for _ in range(a.sims):
                    ms.append(st.mean(fwd[t] for t in rnd.sample(names, half)))
                rand_means.append(st.mean(ms))
                res["random_half"].append(rand_means[-1]); counts["random_half"].append(half)
            base = res["all"]
            for k in res:
                pairs = [(x, b) for x, b in zip(res[k], base) if x is not None]
                if len(pairs) < 3:
                    continue
                ex = [x - b for x, b in pairs]
                t_stat = st.mean(ex) / (st.pstdev(ex) / math.sqrt(len(ex))) if st.pstdev(ex) > 0 else 0.0
                win = 100 * sum(1 for e in ex if e > 0) / len(ex)
                rows.append({"H": H, "period": pname, "rule": k, "n_dates": len(pairs), "mean_pct": round(st.mean(x for x, _ in pairs), 3),
                             "excess_pct": round(st.mean(ex), 3), "t": round(t_stat, 2), "win_pct": round(win, 1),
                             "avg_names": round(st.mean(c for c in counts[k] if c), 1)})
                print("{:10s} {:9s} {:5d} {:9.2f} {:9.2f} {:6.2f} {:7.1f} {:6.1f}".format(pname, k, len(pairs), st.mean(x for x, _ in pairs), st.mean(ex), t_stat, win, st.mean(c for c in counts[k] if c)))
    with open(ROOT / "results" / "wide_test.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("\nsaved results/wide_test.csv")


if __name__ == "__main__":
    main()
