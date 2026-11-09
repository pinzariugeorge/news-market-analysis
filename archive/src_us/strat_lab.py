"""Portfolio strategy lab on the wide single-stock universe in data/raw/ohlc (long-only, daily bars, whole shares ignored).

Honest-testing rules (CLAUDE.md): data is physically cut at 2024-12-31 (2025+ is the reserved final test; use --final only once, for chosen finalists).
Build window 2016-01..2022-12, validation window 2023-01..2024-12. Parameters are canonical values fixed in advance, not tuned; every variant that is run is
counted in the printed list. Execution: signal at the close of day t, trade at the close of day t+1 (one-day lag), cost 0.15% per side of traded value, cash earns 0.
Benchmarks: S&P 500 price index (^GSPC, buy and hold) and the equal-weight basket of all names (survivor-biased, so overstated).
Usage: python -I src/strat_lab.py [--final]
"""
import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
import os
OHLC = ROOT / "data" / "raw" / os.environ.get("STRAT_OHLC", "ohlc")
COST = 0.0015
BUILD = ("2016-01-04", "2022-12-30")
VALID = ("2023-01-03", "2024-12-31")
FINAL = ("2025-01-02", "2026-11-06")


def load(end):
    idx = {}
    rows = list(csv.reader(open(OHLC / "_GSPC.csv")))[1:]
    dates = [r[0] for r in rows if r[0] <= end]
    pos = {d: i for i, d in enumerate(dates)}
    T = len(dates)
    names = []
    arrs = {k: [] for k in "ohlcv"}
    for f in sorted(OHLC.glob("*.csv")):
        if f.stem.startswith("_"):
            continue
        a = {k: np.full(T, np.nan) for k in "ohlcv"}
        for r in list(csv.reader(open(f)))[1:]:
            i = pos.get(r[0])
            if i is None:
                continue
            for k, v in zip("ohlcv", r[1:6]):
                a[k][i] = float(v)
        if np.isnan(a["c"]).sum() > 0.2 * T:
            continue
        names.append(f.stem)
        for k in "ohlcv":
            arrs[k].append(a[k])
    D = {k: np.array(v).T for k, v in arrs.items()}
    # forward-fill single missing days inside a series
    for k in "ohlc":
        X = D[k]
        for j in range(X.shape[1]):
            col = X[:, j]
            valid = ~np.isnan(col)
            if valid.any():
                first = np.argmax(valid)
                for t in range(first + 1, T):
                    if np.isnan(col[t]):
                        col[t] = col[t - 1]
    spx = np.array([float(r[4]) for r in rows if r[0] <= end])
    return dates, names, D, spx


def sma(X, n):
    out = np.full(X.shape, np.nan)
    c = np.nancumsum(np.nan_to_num(X), axis=0)
    out[n - 1:] = (c[n - 1:] - np.vstack([np.zeros((1, X.shape[1])), c[:-n]])) / n
    out[np.isnan(X)] = np.nan
    return out


def atr(H, L, C, n=14):
    pc = np.vstack([np.full((1, C.shape[1]), np.nan), C[:-1]])
    tr = np.fmax(H - L, np.fmax(np.abs(H - pc), np.abs(L - pc)))
    out = np.full(C.shape, np.nan)
    for t in range(n, C.shape[0]):
        out[t] = np.nanmean(tr[t - n + 1:t + 1], axis=0) if t == n else (out[t - 1] * (n - 1) + tr[t]) / n
    return out


def month_ends(dates):
    return [i for i in range(len(dates) - 1) if dates[i][:7] != dates[i + 1][:7]]


def hold(target_at, T):
    """target_at: dict index->weights vector; forward-fill between rebalance dates."""
    N = len(next(iter(target_at.values())))
    W = np.zeros((T, N))
    cur = np.zeros(N)
    for t in range(T):
        if t in target_at:
            cur = target_at[t]
        W[t] = cur
    return W


def simulate(W, R):
    T, N = W.shape
    held = np.zeros_like(W)
    held[2:] = W[:-2]
    Rz = np.nan_to_num(R)
    gross = (held * Rz).sum(axis=1)
    turn = np.abs(np.diff(held, axis=0, prepend=np.zeros((1, N)))).sum(axis=1)
    return gross - COST * turn, held.sum(axis=1), turn


def stats(r, inv, turn, a, b, dates):
    idx = [i for i, d in enumerate(dates) if a <= d <= b]
    s, t = idx[0], idx[-1] + 1
    x = r[s:t]
    eq = np.cumprod(1 + x)
    yrs = len(x) / 252
    cagr = eq[-1] ** (1 / yrs) - 1
    sh = x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
    peak = np.maximum.accumulate(eq)
    dd = (1 - eq / peak).max()
    return cagr, sh, dd, inv[s:t].mean(), turn[s:t].sum() / yrs


def main():
    final = "--final" in sys.argv
    end = FINAL[1] if final else VALID[1]
    dates, names, D, spx = load(end)
    C, H, L = D["c"], D["h"], D["l"]
    T, N = C.shape
    R = np.vstack([np.full((1, N), np.nan), C[1:] / C[:-1] - 1])
    sm200 = sma(C, 200)
    sm50 = sma(C, 50)
    spx_sma = np.array([np.nan] * 199 + [spx[i - 199:i + 1].mean() for i in range(199, T)])
    regime = spx > spx_sma
    me = [i for i in month_ends(dates) if i >= 260]
    print("universe {} names, {} days {}..{}".format(N, T, dates[0], dates[-1]))
    wins = [("build", BUILD), ("valid", VALID)] if not final else [("FINAL", FINAL)]
    results = []

    def run(name, W):
        r, inv, turn = simulate(W, R)
        results.append((name, [stats(r, inv, turn, a, b, dates) for _, (a, b) in wins], inv, turn))

    # benchmarks
    sr = np.concatenate([[0], spx[1:] / spx[:-1] - 1])
    results.append(("S&P 500 buy and hold (price)", [stats(sr, np.ones(T), np.zeros(T), a, b, dates) for _, (a, b) in wins], None, None))
    ew = {t: np.where(~np.isnan(C[t]), 1.0, 0.0) / max(1, (~np.isnan(C[t])).sum()) for t in me}
    run("Equal-weight basket (monthly, survivor-biased)", hold(ew, T))
    ew_reg = {t: ew[t] * (1.0 if regime[t] else 0.0) for t in me}
    run("Equal-weight basket, only when S&P > 200d", hold(ew_reg, T))

    def mom_targets(n, lookback=252, skip=21, abs_filter=False, use_regime=False, score="mom"):
        tg = {}
        for t in me:
            if t < lookback:
                continue
            if score == "mom":
                s = C[t - skip] / C[t - lookback] - 1
            elif score == "high":
                s = C[t] / np.nanmax(C[t - 251:t + 1], axis=0)
            else:
                m = C[t - skip] / C[t - lookback] - 1
                vol = np.nanstd(R[t - 62:t + 1], axis=0)
                s = np.where(m > np.nanmedian(m), -vol, np.nan)
            ok = ~np.isnan(s)
            if abs_filter:
                ok &= C[t] > sm200[t]
            w = np.zeros(N)
            if ok.sum() >= n and (not use_regime or regime[t]):
                top = np.argsort(np.where(ok, s, -np.inf))[-n:]
                w[top] = 1.0 / n
            tg[t] = w
        return tg

    for n in (10, 20, 40):
        run("XS momentum 12-1, top {}".format(n), hold(mom_targets(n), T))
    for n in (10, 20):
        run("XS momentum 12-1, top {}, above 200d".format(n), hold(mom_targets(n, abs_filter=True), T))
        run("XS momentum 12-1, top {}, S&P>200d regime".format(n), hold(mom_targets(n, use_regime=True), T))
        run("XS momentum 12-1, top {}, 200d + regime".format(n), hold(mom_targets(n, abs_filter=True, use_regime=True), T))
        run("52-week-high proximity, top {}".format(n), hold(mom_targets(n, score="high"), T))
        run("52-week-high proximity, top {}, regime".format(n), hold(mom_targets(n, score="high", use_regime=True), T))
        run("Low-vol among top-half momentum, {}".format(n), hold(mom_targets(n, score="lowvol"), T))

    # trend-follower portfolio: Donchian 55 breakout, 3 ATR ratcheting stop, per name, capital 1/K per active name
    A = atr(H, L, C)
    for lb, mult, K in ((55, 3.0, 20), (100, 3.0, 20), (55, 3.0, 40)):
        pos = np.zeros((T, N))
        for j in range(N):
            inpos = False
            trail = np.nan
            for t in range(lb + 15, T):
                if np.isnan(C[t, j]) or np.isnan(A[t, j]):
                    inpos = False
                    continue
                if inpos:
                    if C[t, j] < trail:
                        inpos = False
                    else:
                        trail = max(trail, C[t, j] - mult * A[t, j])
                elif C[t, j] > np.nanmax(C[t - lb:t, j]):
                    inpos = True
                    trail = C[t, j] - mult * A[t, j]
                pos[t, j] = 1.0 if inpos else 0.0
        cnt = pos.sum(axis=1, keepdims=True)
        W = pos / np.maximum(cnt, K)
        run("Trend portfolio Donchian {} / {} ATR, K={}".format(lb, mult, K), W)
        # same, only when S&P above 200d
        run("Trend portfolio Donchian {} / {} ATR, K={}, regime".format(lb, mult, K), W * regime[:, None])

    # dip-buy in uptrend, hold 10 days
    for thr in (-0.07, -0.10):
        pos = np.zeros((T, N))
        for j in range(N):
            until = -1
            for t in range(205, T - 1):
                if np.isnan(C[t, j]) or np.isnan(sm200[t, j]):
                    continue
                if t <= until:
                    pos[t, j] = 1.0
                elif C[t, j] > sm200[t, j] and C[t, j] / C[t - 5, j] - 1 <= thr:
                    until = t + 10
                    pos[t, j] = 1.0
        cnt = pos.sum(axis=1, keepdims=True)
        run("Dip buy (5d return <= {:.0%}, above 200d), 10d hold, K=20".format(thr), pos / np.maximum(cnt, 20))

    # seasonality on the equal-weight basket: turn of the month (last 2 and first 3 trading days) and sell-in-May
    tom = np.zeros(T)
    mstart = 0
    for t in range(T):
        if t > 0 and dates[t][:7] != dates[t - 1][:7]:
            mstart = t
        mend = t
        while mend + 1 < T and dates[mend + 1][:7] == dates[t][:7]:
            mend += 1
        tom[t] = 1.0 if (t - mstart < 3 or mend - t < 2) else 0.0
    ewall = np.where(~np.isnan(C), 1.0, 0.0)
    ewall = ewall / np.maximum(1, ewall.sum(axis=1, keepdims=True))
    run("Turn-of-month only, equal-weight basket", ewall * tom[:, None])
    may = np.array([1.0 if d[5:7] in ("11", "12", "01", "02", "03", "04") else 0.0 for d in dates])
    run("Nov-Apr only (sell in May), equal-weight basket", ewall * may[:, None])

    hdr = "{:58s}".format("strategy")
    for w, _ in wins:
        hdr += " | {:>5s}: CAGR  Shrp  MaxDD".format(w)
    print(hdr + " | invested turn/yr")
    for name, st, inv, turn in results:
        line = "{:58s}".format(name[:58])
        for c, sh, dd, iv, tn in st:
            line += " | {:>+6.1%} {:5.2f} {:5.1%}".format(c, sh, dd)
        line += " | {:5.0%} {:6.1f}".format(st[0][3], st[0][4])
        print(line)
    print("variants run:", len(results) - 1)


if __name__ == "__main__":
    main()
