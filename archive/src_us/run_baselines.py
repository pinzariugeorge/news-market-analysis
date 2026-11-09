"""Compute the simple baselines the agent must beat, on a chosen period (default 2008-2019 = handbook/dev period).

Usage: python -I src/run_baselines.py [--start 2008-01-01] [--end 2019-12-31] [--cost 0.02] [--sims 1000]
Reads data/processed/market_days.csv. Writes results/baselines_<start-year>_<end-year>.csv and prints a table.
No model, no news. Every position for day t uses only information up to the close of day t-1.

Baselines
  buy_hold      size 100% every day
  cash          size 0%
  vol_rule      100% when the volatility regime (quartile of past-20-day vol vs previous 2520 values) is 1-3, else 0%
  capped_long   100% in regime 1-3, 50% in regime 4
  trend_200d    100% when the previous close is above its 200-day average, else 0%
  random_long   random long/flat each day with the same average exposure as capped_long (mean over sims, 5th-95th percentile)
Costs: --cost percent of the traded fraction when the position changes (default 0.02% per 100% change).
"""
import argparse
import bisect
import csv
import random
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load():
    rows = []
    with open(ROOT / "data" / "processed" / "market_days.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((r["date"], float(r["close"]), float(r["ret_pct"]) if r["ret_pct"] else None))
    return rows


def signals(rows):
    """Per day t: (regime, above_200d) using data strictly before t."""
    n = len(rows)
    closes = [c for _, c, _ in rows]
    rets = [r if r is not None else 0.0 for _, _, r in rows]
    regime = [None] * n
    trend = [None] * n
    hist = []            # sorted vol history (up to 2520 values)
    window = []          # chronological vols to evict from hist
    for t in range(n):
        if t >= 21:
            vol = st.pstdev(rets[t - 20:t])          # returns of days t-20..t-1
            if len(hist) >= 250:
                rank = bisect.bisect_right(hist, vol) / len(hist)
                regime[t] = 1 + min(3, int(rank * 4))
            bisect.insort(hist, vol)
            window.append(vol)
            if len(window) > 2520:
                old = window.pop(0)
                hist.pop(bisect.bisect_left(hist, old))
        if t >= 201:
            ma = sum(closes[t - 200:t]) / 200       # closes up to t-1
            trend[t] = 1 if closes[t - 1] > ma else 0
    return regime, trend


def run(sizes, rets, cost_pct):
    equity, peak, mdd, prev = 1.0, 1.0, 0.0, 0.0
    daily, turnover = [], 0.0
    for s, r in zip(sizes, rets):
        c = abs(s - prev) * cost_pct
        turnover += abs(s - prev)
        prev = s
        d = s * r - c
        daily.append(d)
        equity *= 1 + d / 100
        peak = max(peak, equity)
        mdd = min(mdd, equity / peak - 1)
    n = len(daily)
    yrs = n / 252
    mean, sd = st.mean(daily), st.pstdev(daily)
    return {
        "total_return_pct": (equity - 1) * 100,
        "annualized_pct": (equity ** (1 / yrs) - 1) * 100,
        "ann_vol_pct": sd * (252 ** 0.5),
        "sharpe": (mean / sd * (252 ** 0.5)) if sd > 0 else 0.0,
        "max_drawdown_pct": mdd * 100,
        "exposure_pct": 100 * sum(1 for s in sizes if s > 0) / n,
        "avg_size_pct": 100 * st.mean(sizes),
        "turnover_per_year": turnover / yrs,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2008-01-01")
    ap.add_argument("--end", default="2019-12-31")
    ap.add_argument("--cost", type=float, default=0.02)
    ap.add_argument("--sims", type=int, default=1000)
    a = ap.parse_args()
    rows = load()
    regime, trend = signals(rows)
    idx = [i for i, (d, _, r) in enumerate(rows) if a.start <= d <= a.end and r is not None and regime[i] and trend[i] is not None]
    rets = [rows[i][2] for i in idx]
    sz = {
        "buy_hold": [1.0] * len(idx),
        "cash": [0.0] * len(idx),
        "vol_rule": [1.0 if regime[i] <= 3 else 0.0 for i in idx],
        "capped_long": [1.0 if regime[i] <= 3 else 0.5 for i in idx],
        "trend_200d": [float(trend[i]) for i in idx],
    }
    res = {k: run(v, rets, a.cost) for k, v in sz.items()}
    p = st.mean(sz["capped_long"])
    rnd = random.Random(42)
    sims = [run([1.0 if rnd.random() < p else 0.0 for _ in idx], rets, a.cost) for _ in range(a.sims)]
    def pct(key, q):
        v = sorted(s[key] for s in sims)
        return v[int(q * (len(v) - 1))]
    res["random_long"] = {k: st.mean(s[k] for s in sims) for k in sims[0]}
    print("period {} to {}  ({} days)  cost {}% per 100% change".format(rows[idx[0]][0], rows[idx[-1]][0], len(idx), a.cost))
    cols = ["total_return_pct", "annualized_pct", "ann_vol_pct", "sharpe", "max_drawdown_pct", "exposure_pct", "avg_size_pct", "turnover_per_year"]
    print("{:13s}".format("baseline") + "".join("{:>14s}".format(c[:13]) for c in cols))
    for k, v in res.items():
        print("{:13s}".format(k) + "".join("{:14.2f}".format(v[c]) for c in cols))
    print("random_long annualized 5th-95th pct: {:.2f} to {:.2f};  sharpe {:.2f} to {:.2f}".format(
        pct("annualized_pct", .05), pct("annualized_pct", .95), pct("sharpe", .05), pct("sharpe", .95)))
    out = ROOT / "results" / "baselines_{}_{}.csv".format(a.start[:4], a.end[:4])
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["baseline"] + cols)
        for k, v in res.items():
            w.writerow([k] + [round(v[c], 3) for c in cols])
    # per-year buy and hold vs vol_rule vs trend
    print("\nper year annual return % (buy_hold / vol_rule / trend_200d):")
    years = sorted({rows[i][0][:4] for i in idx})
    for y in years:
        ii = [j for j, i in enumerate(idx) if rows[i][0][:4] == y]
        r_y = [rets[j] for j in ii]
        out_y = []
        for k in ("buy_hold", "vol_rule", "trend_200d"):
            out_y.append(run([sz[k][j] for j in ii], r_y, a.cost)["total_return_pct"])
        print(y, " / ".join("{:7.1f}".format(v) for v in out_y))
    print("saved", out)


if __name__ == "__main__":
    main()
