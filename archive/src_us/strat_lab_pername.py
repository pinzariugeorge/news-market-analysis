"""Per-stock Donchian N / 3 ATR ratchet (long-only, all-in per name), on every name in data/raw/ohlc_long, same rule as the TradingKit tests.

Signal at the close, trade next day (one-day lag), cost 0.15% per side, data ends 2024-12-31. Periods: 2004-09..2009, 2010..2015, 2016..2022, 2023..2024.
Prints, per period, the number of names, the share with a positive return, mean/median strategy return vs buy and hold, and mean drawdown vs buy and hold,
for N = 55 and 100 (fixed in advance). Writes results/donchian_pername.csv. Usage: python -I src/strat_lab_pername.py
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("STRAT_OHLC", "ohlc_long")
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import strat_lab as L  # noqa: E402
import strat_lab4 as L4  # noqa: E402


def main():
    dates, names, D, spx = L.load("2024-12-31")
    C, H, Lo = D["c"], D["h"], D["l"]
    T, N = C.shape
    A = L.atr(H, Lo, C)
    rows = []
    for lb in (55, 100):
        pos = np.zeros((T, N))
        for j in range(N):
            inpos, trail = False, np.nan
            for t in range(lb + 15, T):
                if np.isnan(C[t, j]) or np.isnan(A[t, j]):
                    inpos = False
                    continue
                if inpos:
                    if C[t, j] < trail:
                        inpos = False
                    else:
                        trail = max(trail, C[t, j] - 3.0 * A[t, j])
                elif C[t, j] > np.nanmax(C[t - lb:t, j]):
                    inpos, trail = True, C[t, j] - 3.0 * A[t, j]
                pos[t, j] = 1.0 if inpos else 0.0
        R = np.vstack([np.full((1, N), np.nan), C[1:] / C[:-1] - 1])
        R[np.abs(R) > 0.6] = np.nan
        held = np.zeros_like(pos)
        held[2:] = pos[:-2]
        gross = np.nan_to_num(R) * held
        turn = np.abs(np.diff(held, axis=0, prepend=np.zeros((1, N))))
        net = gross - L.COST * turn
        bh = np.nan_to_num(R) * (~np.isnan(C))
        print("\nDonchian {} / 3 ATR per stock (all-in per name), {} names".format(lb, N))
        for pname, (a, b) in L4.PER:
            idx = [i for i, d in enumerate(dates) if a <= d <= b]
            s, t1 = idx[0], idx[-1] + 1
            sr, hr, sd, hd = [], [], [], []
            for j in range(N):
                if np.isnan(C[s, j]) or np.isnan(C[t1 - 1, j]):
                    continue
                x = np.cumprod(1 + net[s:t1, j])
                y = np.cumprod(1 + bh[s:t1, j])
                sr.append(x[-1] - 1)
                hr.append(y[-1] - 1)
                sd.append((1 - x / np.maximum.accumulate(x)).max())
                hd.append((1 - y / np.maximum.accumulate(y)).max())
                rows.append([lb, pname, names[j], round(100 * sr[-1], 1), round(100 * sd[-1], 1), round(100 * hr[-1], 1), round(100 * hd[-1], 1)])
            sr, hr, sd, hd = map(np.array, (sr, hr, sd, hd))
            print("{:8s} n={:3d} positive {:4.0%} | strat mean {:+7.1%} median {:+7.1%} | B&H mean {:+8.1%} median {:+8.1%} | beats B&H {:4.0%} | DD strat {:4.1%} B&H {:4.1%}".format(
                pname, len(sr), (sr > 0).mean(), sr.mean(), np.median(sr), hr.mean(), np.median(hr), (sr > hr).mean(), sd.mean(), hd.mean()))
    out = L.ROOT / "results" / "donchian_pername.csv"
    import csv
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n_lookback", "period", "ticker", "strat_ret_pct", "strat_dd_pct", "bh_ret_pct", "bh_dd_pct"])
        w.writerows(rows)
    print("saved", out.name)


if __name__ == "__main__":
    main()
