"""Three further anomalies with literature support, tested on 2004-2024 with a point-in-time liquid universe (pre-registered thresholds, see below).

H2 residual momentum: rank by the 12-1 month sum of residual returns (market-beta removed over the prior 36 months) divided by residual volatility.
H5 same-calendar-month seasonality: rank by the stock's average return in the coming calendar month over the previous 5 years (Heston-Sadka).
H6 industry momentum: hold the equal-weight eligible members of the 3 sectors with the best 6-1 month return (Moskowitz-Grinblatt).
Eligible = top K (100 and 200) names by trailing 250-day median dollar volume, data before each month-end; monthly rebalance, signal at close, trade next day, 0.15% per side.
Pre-registered pass rule (written before running): excess return over the eligible equal-weight basket with t >= 2.5 over 2004-2024 AND positive excess in at least 3 of 4 periods AND not driven only by K=200.
Usage: python -I src/strat_lab6.py
"""
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("STRAT_OHLC", "ohlc_long")
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import strat_lab as L  # noqa: E402
import strat_lab4 as L4  # noqa: E402

SECT = ["tech", "comm", "disc", "staples", "health", "fin", "industrial", "energy", "materials", "utilities", "realestate", "goldmin", "foreign"]


def sectors(names):
    txt = open(L.ROOT / "src" / "download_ohlc.py", encoding="utf-8").read()
    block = re.search(r'TICKERS = """(.*?)"""', txt, re.S).group(1).strip().splitlines()
    m = {}
    for i, line in enumerate(block):
        for t in line.split():
            m[t.replace("^", "_")] = SECT[min(i, len(SECT) - 1)] if not t.startswith("^") else "idx"
    return np.array([m.get(n, "other") for n in names])


def main():
    dates, names, D, spx = L.load("2024-12-31")
    C, V = D["c"], D["v"]
    T, N = C.shape
    R = np.vstack([np.full((1, N), np.nan), C[1:] / C[:-1] - 1])
    R[np.abs(R) > 0.6] = np.nan
    ME = L.month_ends(dates)
    me = [i for i in ME if i >= 260]
    dv = C * V
    sec = sectors(names)
    # monthly return matrix at month-ends
    Cm = C[ME]
    Mr = np.vstack([np.full((1, N), np.nan), Cm[1:] / Cm[:-1] - 1])
    mk = np.array([np.nan] + list(spx[ME][1:] / spx[ME][:-1] - 1))
    pos_of = {t: k for k, t in enumerate(ME)}

    def eligible(t, k):
        have = ~np.isnan(C[t - 252]) & ~np.isnan(C[t])
        med = np.where(have, np.nanmedian(dv[t - 249:t + 1], axis=0), -1)
        order = np.argsort(-med)[:k]
        e = np.zeros(N, dtype=bool)
        e[order] = med[order] > 0
        return e

    def resid_score(t):
        k = pos_of[t]
        if k < 40:
            return None
        s = np.full(N, np.nan)
        x = mk[k - 35:k + 1]
        X = np.vstack([np.ones(36), x]).T
        for i in range(N):
            y = Mr[k - 35:k + 1, i]
            if np.isnan(y).any():
                continue
            beta = np.linalg.lstsq(X, y, rcond=None)[0]
            e = y - X @ beta
            s[i] = e[-12:-1].sum() / (e.std() + 1e-9)
        return s

    def season_score(t):
        k = pos_of[t]
        s = np.full(N, np.nan)
        rows = [Mr[k + 1 - 12 * j] for j in range(1, 6) if k + 1 - 12 * j >= 1]
        if len(rows) >= 3:
            s = np.nanmean(np.vstack(rows), axis=0)
        return s

    def build(kind, n, K):
        tg, ew = {}, {}
        for t in me:
            el = eligible(t, K)
            w = np.zeros(N)
            e = np.zeros(N)
            if el.sum() >= max(n, 20):
                e[el] = 1.0 / el.sum()
                if kind == "resid":
                    s = resid_score(t)
                elif kind == "season":
                    s = season_score(t)
                else:
                    s = None
                if kind in ("resid", "season"):
                    if s is not None:
                        ok = el & ~np.isnan(s)
                        if ok.sum() >= n:
                            top = np.argsort(np.where(ok, s, -np.inf))[-n:]
                            w[top] = 1.0 / n
                else:  # industry momentum
                    mom = C[t - 21] / C[t - 126] - 1
                    best = []
                    for sname in set(sec[el]):
                        mem = el & (sec == sname) & ~np.isnan(mom)
                        if mem.sum() >= 4:
                            best.append((np.mean(mom[mem]), sname))
                    best.sort(reverse=True)
                    chosen = [b[1] for b in best[:3]]
                    mem = el & np.isin(sec, chosen)
                    if mem.sum() > 0:
                        w[mem] = 1.0 / mem.sum()
            tg[t], ew[t] = w, e
        return L.hold(tg, T), L.hold(ew, T)

    def monthly(r, a, b):
        out = {}
        for i, d in enumerate(dates):
            if a <= d <= b:
                out[d[:7]] = out.get(d[:7], 1.0) * (1 + r[i])
        return np.array([v - 1 for v in out.values()])

    print("universe {} names, sectors: {}".format(N, {s: int((sec == s).sum()) for s in set(sec)}))
    for K in (100, 200):
        print("\n=== eligible top {} ===".format(K))
        print("{:26s}".format("") + "".join(" | {:>8s}: CAGR  Shrp  MaxDD".format(p) for p, _ in L4.PER) + " | monthly excess vs EW")
        first = True
        for kind, n, label in (("resid", 10, "Residual mom top 10"), ("resid", 20, "Residual mom top 20"), ("season", 10, "Seasonality top 10"),
                               ("season", 20, "Seasonality top 20"), ("industry", 0, "Industry mom, top 3 sectors")):
            Wm, We = build(kind, n, K)
            rm, im, tm = L.simulate(Wm, R)
            re_, ie, te = L.simulate(We, R)
            if first:
                row = "{:26s}".format("EW eligible")
                for _, (a, b) in L4.PER:
                    c, sh, dd, _, _ = L.stats(re_, ie, te, a, b, dates)
                    row += " | {:>+6.1%} {:5.2f} {:5.1%}".format(c, sh, dd)
                print(row)
                first = False
            row = "{:26s}".format(label)
            pos_periods = 0
            for _, (a, b) in L4.PER:
                c, sh, dd, _, _ = L.stats(rm, im, tm, a, b, dates)
                ce = L.stats(re_, ie, te, a, b, dates)[0]
                pos_periods += c > ce
                row += " | {:>+6.1%} {:5.2f} {:5.1%}".format(c, sh, dd)
            ex = monthly(rm, "2004-09-01", "2024-12-31") - monthly(re_, "2004-09-01", "2024-12-31")
            row += " | {:+.2%}/month t={:.2f}, beats EW in {}/4 periods".format(ex.mean(), ex.mean() / (ex.std(ddof=1) / np.sqrt(len(ex))), pos_periods)
            print(row)


if __name__ == "__main__":
    main()
