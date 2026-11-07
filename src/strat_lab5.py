"""Trend-filtered diversified basket, 2004-2024 (history in data/raw/ohlc_long, data stops 2024-12-31).

Rule (fixed in advance): hold an equal-weight basket of the K most liquid names (point-in-time dollar volume, rebalanced monthly) while the S&P 500 price index
is above its 200-day average (checked daily, one-day execution lag), otherwise hold cash (earning 0). Compared with the same basket always invested and with the S&P 500.
Cost 0.15% per side. Also shows the monthly-checked 10-month-average (Faber) version.
Usage: python -I src/strat_lab5.py
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
    C, V = D["c"], D["v"]
    T, N = C.shape
    R = np.vstack([np.full((1, N), np.nan), C[1:] / C[:-1] - 1])
    R[np.abs(R) > 0.6] = np.nan
    me = [i for i in L.month_ends(dates) if i >= 260]
    dv = C * V
    ma200 = np.array([np.nan] * 199 + [spx[i - 199:i + 1].mean() for i in range(199, T)])
    on_daily = (spx > ma200).astype(float)
    on_daily[np.isnan(ma200)] = 0.0
    ma10m = np.full(T, np.nan)
    for t in me:
        mes = [i for i in me if i <= t][-10:]
        if len(mes) == 10:
            ma10m[t] = np.mean([spx[i] for i in mes])
    on_month = np.zeros(T)
    cur = 0.0
    for t in range(T):
        if not np.isnan(ma10m[t]):
            cur = 1.0 if spx[t] > ma10m[t] else 0.0
        on_month[t] = cur
    sp = np.concatenate([[0], spx[1:] / spx[:-1] - 1])
    print("universe {} names {}..{}".format(N, dates[0], dates[-1]))
    print("{:44s}".format("") + "".join(" | {:>8s}: CAGR  Shrp  MaxDD".format(p) for p, _ in L4.PER) + " | all 2004-2024")
    def row(name, r, inv, turn):
        s = "{:44s}".format(name)
        for _, (a, b) in L4.PER:
            c, sh, dd, _, _ = L.stats(r, inv, turn, a, b, dates)
            s += " | {:>+6.1%} {:5.2f} {:5.1%}".format(c, sh, dd)
        c, sh, dd, iv, tn = L.stats(r, inv, turn, "2004-09-01", "2024-12-31", dates)
        print(s + " | {:>+6.1%} {:5.2f} {:5.1%} invested {:.0%}".format(c, sh, dd, iv))
    row("S&P 500 price, buy and hold", sp, np.ones(T), np.zeros(T))
    spf = sp * np.concatenate([[0, 0], on_daily[:-2]])
    row("S&P 500 price, 200d filter", spf, np.ones(T), np.zeros(T))
    for k in (100, 200):
        ew = {}
        for t in me:
            s = C[t - 252] if t >= 252 else None
            have = ~np.isnan(C[t - 252]) & ~np.isnan(C[t])
            med = np.where(have, np.nanmedian(dv[t - 249:t + 1], axis=0), -1)
            order = np.argsort(-med)[:k]
            elig = np.zeros(N, dtype=bool)
            elig[order] = med[order] > 0
            e = np.zeros(N)
            if elig.sum():
                e[elig] = 1.0 / elig.sum()
            ew[t] = e
        W = L.hold(ew, T)
        r, inv, turn = L.simulate(W, R)
        row("EW top {} liquid, always invested".format(k), r, inv, turn)
        r, inv, turn = L.simulate(W * on_daily[:, None], R)
        row("EW top {} liquid, S&P > 200d (daily)".format(k), r, inv, turn)
        r, inv, turn = L.simulate(W * on_month[:, None], R)
        row("EW top {} liquid, S&P > 10-month avg".format(k), r, inv, turn)


if __name__ == "__main__":
    main()
