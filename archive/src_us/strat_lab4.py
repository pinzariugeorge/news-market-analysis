"""Cross-sectional momentum over 2004-2024 (history from data/raw/ohlc_long, includes the 2008 crisis), point-in-time liquid universe, with significance.

Run: STRAT_OHLC=ohlc_long python -I src/strat_lab4.py   (the script sets the variable itself if missing).
At each month-end the eligible names are the K most liquid by trailing 250-day median dollar volume (data before that date) among names with a full lookback.
Momentum: top n by 6-1 or 12-1 return, equal weight, monthly, signal at close, trade next day, 0.15% per side. Benchmark: equal weight of the same eligible set.
Periods: 2004-2009, 2010-2015, 2016-2022, 2023-2024 (data stops 2024-12-31; 2025+ reserved). Also monthly excess return over the eligible equal-weight basket with t-statistic.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("STRAT_OHLC", "ohlc_long")
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import strat_lab as L  # noqa: E402

PER = [("2004-09", ("2004-09-01", "2009-12-31")), ("2010-15", ("2010-01-04", "2015-12-31")), ("2016-22", ("2016-01-04", "2022-12-30")), ("2023-24", ("2023-01-03", "2024-12-31"))]


def monthly(r, dates, a, b):
    out = {}
    for i, d in enumerate(dates):
        if a <= d <= b:
            out[d[:7]] = out.get(d[:7], 1.0) * (1 + r[i])
    return np.array([v - 1 for v in out.values()])


def main():
    dates, names, D, spx = L.load("2024-12-31")
    C, V = D["c"], D["v"]
    T, N = C.shape
    R = np.vstack([np.full((1, N), np.nan), C[1:] / C[:-1] - 1])
    R[np.abs(R) > 0.6] = np.nan  # guard against bad ticks
    me = [i for i in L.month_ends(dates) if i >= 260]
    dv = C * V
    print("universe {} names, {} days {}..{}".format(N, T, dates[0], dates[-1]))

    def build(n, lb, k):
        tg, ew = {}, {}
        for t in me:
            s = C[t - 21] / C[t - lb] - 1
            have = ~np.isnan(s) & ~np.isnan(C[t])
            med = np.nanmedian(dv[t - 249:t + 1], axis=0)
            med = np.where(have, med, -1)
            order = np.argsort(-med)[:k]
            elig = np.zeros(N, dtype=bool)
            elig[order] = med[order] > 0
            w = np.zeros(N)
            e = np.zeros(N)
            if elig.sum() >= n:
                top = np.argsort(np.where(elig, s, -np.inf))[-n:]
                w[top] = 1.0 / n
                e[elig] = 1.0 / elig.sum()
            tg[t], ew[t] = w, e
        return L.hold(tg, T), L.hold(ew, T)

    sp = np.concatenate([[0], spx[1:] / spx[:-1] - 1])
    for k in (100, 200):
        print("\n=== eligible: top {} by point-in-time dollar volume ===".format(k))
        print("{:22s}".format("") + "".join(" | {:>8s}: CAGR  Shrp  MaxDD".format(p) for p, _ in PER) + " | monthly excess vs EW (all periods)")
        for lb, lab in ((126, "6-1"), (252, "12-1")):
            for n in (10, 20):
                Wm, We = build(n, lb, k)
                rm, im, tm = L.simulate(Wm, R)
                re_, ie, te = L.simulate(We, R)
                if (lb, n) == (126, 10):
                    row = "{:22s}".format("EW eligible")
                    for _, (a, b) in PER:
                        c, sh, dd, _, _ = L.stats(re_, ie, te, a, b, dates)
                        row += " | {:>+6.1%} {:5.2f} {:5.1%}".format(c, sh, dd)
                    print(row)
                    row = "{:22s}".format("S&P 500 price")
                    for _, (a, b) in PER:
                        c, sh, dd, _, _ = L.stats(sp, np.ones(T), np.zeros(T), a, b, dates)
                        row += " | {:>+6.1%} {:5.2f} {:5.1%}".format(c, sh, dd)
                    print(row)
                row = "{:22s}".format("Mom {} top {}".format(lab, n))
                for _, (a, b) in PER:
                    c, sh, dd, _, _ = L.stats(rm, im, tm, a, b, dates)
                    row += " | {:>+6.1%} {:5.2f} {:5.1%}".format(c, sh, dd)
                ex = monthly(rm, dates, "2004-09-01", "2024-12-31") - monthly(re_, dates, "2004-09-01", "2024-12-31")
                row += " | mean {:+.2%}/month, t = {:.2f}, n = {}".format(ex.mean(), ex.mean() / (ex.std(ddof=1) / np.sqrt(len(ex))), len(ex))
                print(row)


if __name__ == "__main__":
    main()
