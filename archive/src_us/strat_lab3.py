"""Robustness of cross-sectional momentum against universe hindsight (extends src/strat_lab.py / strat_lab2.py).

The universe is today's large caps, so it contains stocks that became large because they rose (NVDA, TSLA, AMD...). Two checks:
 1. Point-in-time liquidity filter: at each monthly rebalance only the K most liquid names by trailing 250-day median dollar volume (data before that date) are eligible.
 2. Random subsamples: 40 random draws of 100 names; show the distribution of (momentum CAGR - equal-weight CAGR) for build and validation.
Same cut (data ends 2024-12-31), costs, lag. Usage: python -I src/strat_lab3.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import strat_lab as L  # noqa: E402


def main():
    dates, names, D, spx = L.load(L.VALID[1])
    C, V = D["c"], D["v"]
    T, N = C.shape
    R = np.vstack([np.full((1, N), np.nan), C[1:] / C[:-1] - 1])
    me = [i for i in L.month_ends(dates) if i >= 260]
    dv = C * V
    liq = {}
    for t in me:
        med = np.nanmedian(dv[t - 249:t + 1], axis=0)
        liq[t] = med

    def targets(n, lookback, mask_fn):
        tg = {}
        ew = {}
        for t in me:
            s = C[t - 21] / C[t - lookback] - 1
            ok = ~np.isnan(s) & ~np.isnan(C[t]) & mask_fn(t)
            w = np.zeros(N)
            e = np.zeros(N)
            if ok.sum() >= n:
                top = np.argsort(np.where(ok, s, -np.inf))[-n:]
                w[top] = 1.0 / n
            if ok.sum() > 0:
                e[ok] = 1.0 / ok.sum()
            tg[t] = w
            ew[t] = e
        return tg, ew

    def report(label, mask_fn):
        print("\n== {} ==".format(label))
        for lb, lab in ((126, "6-1"), (252, "12-1")):
            for n in (10, 20):
                tg, ew = targets(n, lb, mask_fn)
                rm, im, tm = L.simulate(L.hold(tg, T), R)
                re_, ie, te = L.simulate(L.hold(ew, T), R)
                row = "Mom {} top {:2d}".format(lab, n).ljust(20)
                for wn, (a, b) in (("build", L.BUILD), ("valid", L.VALID)):
                    cm, shm, ddm, _, tn = L.stats(rm, im, tm, a, b, dates)
                    ce, she, dde, _, _ = L.stats(re_, ie, te, a, b, dates)
                    row += " | {} mom {:+6.1%} (Sh {:4.2f}, DD {:4.1%}) vs eligible-EW {:+6.1%} (Sh {:4.2f}, DD {:4.1%})".format(wn, cm, shm, ddm, ce, she, dde)
                print(row)

    for k in (60, 100):
        def mask_fn(t, k=k):
            m = liq[t]
            order = np.argsort(-np.nan_to_num(m, nan=-1))
            mk = np.zeros(N, dtype=bool)
            mk[order[:k]] = True
            return mk
        report("point-in-time liquid top {} names".format(k), mask_fn)

    rng = np.random.default_rng(7)
    print("\n== 40 random subsamples of 100 names: momentum minus equal-weight CAGR (percentage points) ==")
    for lb, lab, n in ((126, "6-1", 10), (252, "12-1", 10), (126, "6-1", 20), (252, "12-1", 20)):
        diffs = {"build": [], "valid": []}
        for _ in range(40):
            pick = np.zeros(N, dtype=bool)
            pick[rng.choice(N, 100, replace=False)] = True
            tg, ew = targets(n, lb, lambda t, pick=pick: pick)
            rm, im, tm = L.simulate(L.hold(tg, T), R)
            re_, ie, te = L.simulate(L.hold(ew, T), R)
            for wn, (a, b) in (("build", L.BUILD), ("valid", L.VALID)):
                diffs[wn].append(100 * (L.stats(rm, im, tm, a, b, dates)[0] - L.stats(re_, ie, te, a, b, dates)[0]))
        print("Mom {} top {:2d}: ".format(lab, n) + "; ".join("{} mean {:+.1f}, median {:+.1f}, 10th pct {:+.1f}, positive in {}/40".format(
            wn, np.mean(v), np.median(v), np.percentile(v, 10), sum(1 for x in v if x > 0)) for wn, v in diffs.items()))


if __name__ == "__main__":
    main()
