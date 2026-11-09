"""Local replica of the TradingKit catalogue test: daily Donchian 55 / 3 ATR ratchet, long-only, all-in per name, window 2020-11-02..2024-12-31.

Stocks from data/raw/ohlc_long (cost 0.15% per side); commodities from the futures files (silver, platinum, palladium via SI/PL, Brent, gold, WTI; cost 0.03% per side).
Signal at the close, trade next day. Prints strategy return, drawdown, trades vs buy and hold. (Palladium has no futures file here, so it is skipped.)
Usage: python -I src/run_catalogue_local.py
"""
import csv
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
A, B = "2020-11-02", "2024-12-31"
STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NFLX", "TSLA", "PLTR", "JPM", "BAC", "SAP", "AZN", "NVDA", "AMD", "AVGO"]
COMM = {"GC_F": "Gold", "SI_F": "Silver", "PL_F": "Platinum", "CL_F": "WTI", "BZ_F": "Brent"}


def read(path):
    rows = [r for r in list(csv.reader(open(path)))[1:] if r[4] != "" and r[0] <= B]
    return [r[0] for r in rows], np.array([[float(x) for x in r[1:5]] for r in rows])  # o h l c


def run(dates, X, cost, lb=55, mult=3.0):
    h, l, c = X[:, 1], X[:, 2], X[:, 3]
    n = len(c)
    pc = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    atr = np.full(n, np.nan)
    for t in range(14, n):
        atr[t] = tr[1:15].mean() if t == 14 else (atr[t - 1] * 13 + tr[t]) / 14
    pos = np.zeros(n)
    inpos, trail = False, np.nan
    for t in range(lb + 15, n):
        if inpos:
            if c[t] < trail:
                inpos = False
            else:
                trail = max(trail, c[t] - mult * atr[t])
        elif c[t] > c[t - lb:t].max():
            inpos, trail = True, c[t] - mult * atr[t]
        pos[t] = 1.0 if inpos else 0.0
    held = np.concatenate([[0, 0], pos[:-2]])
    r = np.concatenate([[0], c[1:] / c[:-1] - 1])
    r[abs(r) > 0.25] = 0
    net = held * r - cost * abs(np.diff(held, prepend=0))
    idx = [i for i, d in enumerate(dates) if A <= d <= B]
    s, e = idx[0], idx[-1] + 1
    out = []
    for series in (net[s:e], r[s:e]):
        eq = np.cumprod(1 + series)
        out.append((eq[-1] - 1, (1 - eq / np.maximum.accumulate(eq)).max()))
    trades = int(np.sum(np.diff(held[s:e], prepend=0) > 0))
    return out[0], out[1], trades


def main():
    print("{:10s} {:>9s} {:>7s} {:>7s} | {:>9s} {:>7s}".format("name", "strat", "DD", "trades", "buy&hold", "DD"))
    res = []
    for t in STOCKS:
        f = ROOT / "data" / "raw" / "ohlc_long" / (t + ".csv")
        if not f.exists():
            print(t, "missing")
            continue
        d, X = read(f)
        res.append((t,) + run(d, X, 0.0015))
    for f, name in COMM.items():
        d, X = read(ROOT / "data" / "raw" / "commodities" / (f + ".csv"))
        res.append((name,) + run(d, X, 0.0003))
    for name, s, b, tr in res:
        print("{:10s} {:>+8.0%} {:>7.0%} {:>7d} | {:>+8.0%} {:>7.0%}".format(name, s[0], s[1], tr, b[0], b[1]))
    print("\nstrategy positive in {} of {}; beats buy-and-hold in {} of {}; lower drawdown in {} of {}".format(
        sum(1 for x in res if x[1][0] > 0), len(res), sum(1 for x in res if x[1][0] > x[2][0]), len(res), sum(1 for x in res if x[1][1] < x[2][1]), len(res)))


if __name__ == "__main__":
    main()
