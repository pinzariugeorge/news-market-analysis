"""Daily Donchian breakout with a ratcheting ATR trail (long-only), tested on the whole single-stock universe in data/raw/stocks_cache.json.

Rule (same as the TradingKit 'menu' mode 0): enter at the close when the close is above the highest close of the previous N days; exit at the close
when the close falls below the trailing stop; stop = highest(close - M * ATR) since entry, ratcheting up. Cost 0.15% per side. All-in, long or cash.
Approximation: the cache holds closes only, so ATR is proxied by 1.4 * mean(|close change|) over 14 days and breakouts use closes, not highs.

Time split (CLAUDE.md): build <= 2022-12-31, validation 2023-01-01..2024-12-31. 2025+ is the reserved final test and is NOT evaluated here
(except the optional --sanity flag, which only reproduces the three TradingKit names for 2024-01..2026-11 to check the approximation).
Usage: python -I src/run_donchian_universe.py [--n 55] [--mult 3] [--sanity]
"""
import argparse
import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "raw" / "stocks_cache.json"
COST = 0.0015
FAMILIES = {
    "oil_gas": ["XOM", "CVX", "COP", "OXY", "EOG", "DVN", "FANG", "APA"],
    "gold_miners": ["NEM", "GOLD", "AEM", "KGC", "FNV", "WPM", "AU", "HMY"],
    "chips": ["NVDA", "AVGO", "TSM", "ASML", "AMD", "MU", "QCOM", "INTC", "AMAT", "TXN", "LRCX", "KLAC"],
    "pharma": ["LLY", "NVO", "JNJ", "MRK", "ABBV", "PFE", "AZN", "BMY", "AMGN", "NVS", "GILD"],
    "copper": ["FCX"],
}
WINDOWS = {"build": ("2016-11-07", "2022-12-30"), "valid": ("2023-01-03", "2024-12-31")}


def simulate(closes, n, mult):
    eq = [1.0] * len(closes)
    pos = 0
    trail = None
    e = 1.0
    for i in range(1, len(closes)):
        if pos:
            e *= closes[i] / closes[i - 1]
        a = None
        if i >= 15:
            a = 1.4 * sum(abs(closes[j] - closes[j - 1]) for j in range(i - 13, i + 1)) / 14
        if pos:
            if closes[i] < trail:
                e *= 1 - COST
                pos = 0
                trail = None
            elif a is not None:
                trail = max(trail, closes[i] - mult * a)
        elif a is not None and i >= n and closes[i] > max(closes[i - n:i]):
            e *= 1 - COST
            pos = 1
            trail = closes[i] - mult * a
        eq[i] = e
    return eq


def window_stats(dates, curve, a, b):
    idx = [i for i, d in enumerate(dates) if a <= d <= b]
    if not idx:
        return None
    s, t = idx[0], idx[-1]
    base = curve[s]
    peak = 1.0
    dd = 0.0
    for i in range(s, t + 1):
        v = curve[i] / base
        peak = max(peak, v)
        dd = max(dd, 1 - v / peak)
    return curve[t] / base - 1, dd


def portfolio(curves, dates, a, b):
    idx = [i for i, d in enumerate(dates) if a <= d <= b]
    s, t = idx[0], idx[-1]
    peak = 1.0
    dd = 0.0
    for i in range(s, t + 1):
        v = sum(c[i] / c[s] for c in curves) / len(curves)
        peak = max(peak, v)
        dd = max(dd, 1 - v / peak)
    return sum(c[t] / c[s] for c in curves) / len(curves) - 1, dd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=55)
    ap.add_argument("--mult", type=float, default=3.0)
    ap.add_argument("--sanity", action="store_true")
    a = ap.parse_args()
    cache = json.load(open(CACHE))
    rows = []
    allnames = [t for f in FAMILIES.values() for t in f if t in cache]
    series = {}
    for t in allnames:
        d = cache[t]
        ks = sorted(d)
        cl = [float(d[k][0] if isinstance(d[k], (list, tuple)) else d[k]) for k in ks]
        series[t] = (ks, cl, simulate(cl, a.n, a.mult))
    print("Donchian N={} mult={} cost={:.2%} per side".format(a.n, a.mult, COST))
    for w, (x, y) in WINDOWS.items():
        print("\n== window {} {}..{} ==".format(w, x, y))
        per = {}
        for t in allnames:
            ks, cl, eq = series[t]
            bh = [c / cl[0] for c in cl]
            r = window_stats(ks, eq, x, y)
            h = window_stats(ks, bh, x, y)
            if r is None:
                continue
            per[t] = (r, h)
            rows.append([w, t, round(r[0] * 100, 1), round(r[1] * 100, 1), round(h[0] * 100, 1), round(h[1] * 100, 1)])
        for fam, names in FAMILIES.items():
            ns = [t for t in names if t in per]
            if not ns:
                continue
            sr = [per[t][0][0] for t in ns]
            hr = [per[t][1][0] for t in ns]
            sd = [per[t][0][1] for t in ns]
            hd = [per[t][1][1] for t in ns]
            print("{:12s} n={:2d} strat ret {:+6.1f}% (med {:+6.1f}%, {:2d} pos)  B&H {:+7.1f}%   strat DD {:4.1f}%  B&H DD {:4.1f}%".format(
                fam, len(ns), 100 * statistics.mean(sr), 100 * statistics.median(sr), sum(1 for v in sr if v > 0), 100 * statistics.mean(hr),
                100 * statistics.mean(sd), 100 * statistics.mean(hd)))
        ns = list(per)
        sr = [per[t][0][0] for t in ns]
        hr = [per[t][1][0] for t in ns]
        print("ALL          n={:2d} strat ret {:+6.1f}% (med {:+6.1f}%, {:2d} pos)  B&H {:+7.1f}% (med {:+7.1f}%)  strat DD {:4.1f}%  B&H DD {:4.1f}%".format(
            len(ns), 100 * statistics.mean(sr), 100 * statistics.median(sr), sum(1 for v in sr if v > 0), 100 * statistics.mean(hr),
            100 * statistics.median(hr), 100 * statistics.mean(per[t][0][1] for t in ns), 100 * statistics.mean(per[t][1][1] for t in ns)))
        # equal-weight portfolios on a common date axis (dates identical across the cache)
        ref = series[ns[0]][0]
        ok = [t for t in ns if series[t][0] == ref]
        pr = portfolio([series[t][2] for t in ok], ref, x, y)
        bhc = [[c / series[t][1][0] for c in series[t][1]] for t in ok]
        pb = portfolio(bhc, ref, x, y)
        print("equal-weight basket of {}: strategy {:+.1f}% DD {:.1f}%   buy-and-hold {:+.1f}% DD {:.1f}%".format(len(ok), 100 * pr[0], 100 * pr[1], 100 * pb[0], 100 * pb[1]))
    out = ROOT / "results" / "donchian_universe_N{}_M{}.csv".format(a.n, int(a.mult))
    with open(out, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["window", "ticker", "strat_ret_pct", "strat_dd_pct", "bh_ret_pct", "bh_dd_pct"])
        wr.writerows(rows)
    print("saved", out.name)
    if a.sanity:
        print("\n== sanity: 2024-01-02..2026-11-06 (TradingKit validation numbers: NVDA +66, AMD +73, AVGO +16) ==")
        for t in ("NVDA", "AMD", "AVGO"):
            ks, cl, eq = series[t]
            r = window_stats(ks, eq, "2024-01-02", "2026-11-06")
            print(t, "{:+.1f}% DD {:.1f}%".format(100 * r[0], 100 * r[1]))


if __name__ == "__main__":
    main()
