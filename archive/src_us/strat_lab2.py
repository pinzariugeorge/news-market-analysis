"""Cross-sectional momentum, year by year, with a few pre-registered variants (extends src/strat_lab.py; same data cut, costs and lag).

Variants (fixed in advance): lookback 126 (6-1) and 252 (12-1) days, skip 21; top 10 / 20; equal weight or inverse-volatility weight;
optional volatility-target overlay (scale to 20% annual volatility from the strategy's own trailing 60-day volatility, never above 1x).
Prints calendar-year returns for each variant, the S&P 500 price index and the equal-weight basket, plus build/validation summary lines.
Usage: python -I src/strat_lab2.py [--final]
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import strat_lab as L  # noqa: E402


def main():
    final = "--final" in sys.argv
    end = L.FINAL[1] if final else L.VALID[1]
    dates, names, D, spx = L.load(end)
    C = D["c"]
    T, N = C.shape
    R = np.vstack([np.full((1, N), np.nan), C[1:] / C[:-1] - 1])
    me = [i for i in L.month_ends(dates) if i >= 260]

    def targets(n, lookback, invvol):
        tg = {}
        for t in me:
            s = C[t - 21] / C[t - lookback] - 1
            ok = ~np.isnan(s) & ~np.isnan(C[t])
            w = np.zeros(N)
            if ok.sum() >= n:
                top = np.argsort(np.where(ok, s, -np.inf))[-n:]
                if invvol:
                    v = np.nanstd(R[t - 62:t + 1, top], axis=0)
                    v = np.where(np.isnan(v) | (v <= 0), np.nanmean(v), v)
                    w[top] = (1 / v) / (1 / v).sum()
                else:
                    w[top] = 1.0 / n
            tg[t] = w
        return tg

    def with_voltarget(W):
        r, _, _ = L.simulate(W, R)
        sc = np.ones(T)
        for t in range(61, T):
            sd = r[t - 60:t].std() * np.sqrt(252)
            sc[t] = min(1.0, 0.20 / sd) if sd > 0 else 1.0
        return W * sc[:, None]

    ew = {t: np.where(~np.isnan(C[t]), 1.0, 0.0) / max(1, (~np.isnan(C[t])).sum()) for t in me}
    curves = {}
    sr = np.concatenate([[0], spx[1:] / spx[:-1] - 1])
    curves["S&P 500 (price)"] = (sr, np.ones(T), np.zeros(T))
    curves["Equal-weight basket"] = L.simulate(L.hold(ew, T), R)
    variants = []
    for lb, lab in ((252, "12-1"), (126, "6-1")):
        for n in (10, 20):
            for iv in (False, True):
                variants.append(("Mom {} top {}{}".format(lab, n, " invvol" if iv else ""), n, lb, iv, False))
    variants.append(("Mom 12-1 top 20 + vol target", 20, 252, False, True))
    variants.append(("Mom 12-1 top 10 + vol target", 10, 252, False, True))
    for name, n, lb, iv, vt in variants:
        W = L.hold(targets(n, lb, iv), T)
        if vt:
            W = with_voltarget(W)
        curves[name] = L.simulate(W, R)

    years = sorted(set(d[:4] for d in dates if "2016" <= d[:4]))
    print("universe {} names {}..{}  variants {}".format(N, dates[0], dates[-1], len(variants)))
    print("{:34s}".format("calendar-year return") + "".join("{:>8s}".format(y) for y in years))
    for name, (r, inv, turn) in curves.items():
        row = "{:34s}".format(name)
        for y in years:
            idx = [i for i, d in enumerate(dates) if d[:4] == y]
            row += "{:>+8.1%}".format(np.prod(1 + r[idx[0]:idx[-1] + 1]) - 1)
        print(row)
    print()
    wins = [("build", L.BUILD), ("valid", L.VALID)] if not final else [("FINAL", L.FINAL)]
    print("{:34s}".format("summary") + "".join(" | {:>5s}: CAGR  Shrp  MaxDD".format(w) for w, _ in wins))
    for name, (r, inv, turn) in curves.items():
        row = "{:34s}".format(name)
        for _, (a, b) in wins:
            c, sh, dd, iv_, tn = L.stats(r, inv, turn, a, b, dates)
            row += " | {:>+6.1%} {:5.2f} {:5.1%}".format(c, sh, dd)
        print(row)
    # excess over the equal-weight basket by year (how often the momentum variant wins)
    ewr = curves["Equal-weight basket"][0]
    print("\nyears beating the equal-weight basket (2016..):")
    for name, (r, inv, turn) in curves.items():
        if name.startswith("Mom"):
            wins_n = 0
            tot = 0
            for y in years:
                idx = [i for i, d in enumerate(dates) if d[:4] == y]
                a_ = np.prod(1 + r[idx[0]:idx[-1] + 1]) - 1
                b_ = np.prod(1 + ewr[idx[0]:idx[-1] + 1]) - 1
                wins_n += a_ > b_
                tot += 1
            print("{:34s} {} of {}".format(name, wins_n, tot))


if __name__ == "__main__":
    main()
