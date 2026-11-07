"""Trend following on 7 commodity futures (gold, silver, platinum, copper, WTI, Brent, natural gas), 2000-2024, local Yahoo continuous front-month data.

Data limitation: front-month continuous series are not roll-adjusted, so roll gaps appear as price jumps (daily moves beyond +-25%, such as WTI on 2020-04-20, are dropped).
Rules (fixed in advance): per market a long-only (or long/short) position from time-series momentum 252 and 126 days (monthly decision), Donchian 100 / 3 ATR ratchet,
50/200 moving-average cross, and the average of the four. Equal weight across markets (gross <= 1), signal at the close, trade one day later, cost 0.05% per side.
Windows: 2001-09..2010 (early), 2011-2022 (late), 2023-2024 (validation). Data stops at 2024-12-31 (2025+ reserved).
Usage: python -I src/strat_lab_cmd.py
"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import strat_lab as L  # noqa: E402

COM = L.ROOT / "data" / "raw" / "commodities"
MK = ["GC_F", "SI_F", "PL_F", "HG_F", "CL_F", "BZ_F", "NG_F"]
WIN = [("2001-09..2010", ("2001-09-04", "2010-12-31")), ("2011..2022", ("2011-01-03", "2022-12-30")), ("valid 23-24", ("2023-01-03", "2024-12-31"))]


def main():
    L.COST = 0.0005
    data = {}
    for m in MK:
        data[m] = {r[0]: [float(x) for x in r[1:6]] for r in list(csv.reader(open(COM / (m + ".csv"))))[1:] if r[0] <= "2024-12-31" and r[4] != ""}
    dates = sorted(set(d for m in MK for d in data[m]))
    T, N = len(dates), len(MK)
    O = np.full((T, N), np.nan)
    H = O.copy()
    Lo = O.copy()
    C = O.copy()
    for j, m in enumerate(MK):
        for i, d in enumerate(dates):
            v = data[m].get(d)
            if v:
                O[i, j], H[i, j], Lo[i, j], C[i, j] = v[0], v[1], v[2], v[3]
    for X in (O, H, Lo, C):
        for j in range(N):
            for t in range(1, T):
                if np.isnan(X[t, j]) and not np.isnan(X[t - 1, j]):
                    X[t, j] = X[t - 1, j]
    R = np.vstack([np.full((1, N), np.nan), C[1:] / C[:-1] - 1])
    R[np.abs(R) > 0.25] = np.nan
    me = [i for i in L.month_ends(dates) if i >= 260]

    def tsmom(lb):
        tg = {}
        for t in me:
            sig = (C[t - 21] / C[t - lb] - 1 > 0).astype(float)  # skip last month, as in equity momentum
            sig[np.isnan(C[t]) | np.isnan(C[t - lb])] = 0
            tg[t] = sig
        return L.hold(tg, T)

    def donchian(lb=100, mult=3.0):
        A = L.atr(H, Lo, C)
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
        return pos

    def macross():
        s50, s200 = L.sma(C, 50), L.sma(C, 200)
        return np.where(np.isnan(s200), 0.0, (s50 > s200).astype(float))

    sigs = {"TS momentum 252": tsmom(252), "TS momentum 126": tsmom(126), "Donchian 100 / 3 ATR": donchian(), "MA 50/200 cross": macross()}
    sigs["Ensemble (average of four)"] = sum(sigs.values()) / 4
    sigs["Gold only, TS momentum 252"] = sigs["TS momentum 252"] * np.array([1, 0, 0, 0, 0, 0, 0])
    sigs["Gold + WTI + Brent, ensemble"] = sigs["Ensemble (average of four)"] * np.array([1, 0, 0, 0, 1, 1, 0])

    bh = np.where(np.isnan(C), 0.0, 1.0)
    bh = bh / np.maximum(1, bh.sum(axis=1, keepdims=True))
    results = [("Buy and hold, equal weight 7", L.simulate(bh, R))]
    for name, S in sigs.items():
        # equal weight across the 7 markets (gross <= 1): each market gets 1/7 of capital when its signal is on
        W = S / N if name not in ("Gold only, TS momentum 252", "Gold + WTI + Brent, ensemble") else S / (1 if name.startswith("Gold only") else 3)
        results.append((name, L.simulate(W, R)))
    print("7 commodity futures, {} days {}..{}, cost 0.05% per side".format(T, dates[0], dates[-1]))
    print("{:34s}".format("strategy") + "".join(" | {:>13s}: CAGR  Shrp  MaxDD".format(w) for w, _ in WIN) + " | invested")
    for name, (r, inv, turn) in results:
        row = "{:34s}".format(name)
        for _, (a, b) in WIN:
            c, sh, dd, iv, tn = L.stats(r, inv, turn, a, b, dates)
            row += " | {:>+6.1%} {:5.2f} {:5.1%}".format(c, sh, dd)
        c, sh, dd, iv, tn = L.stats(r, inv, turn, WIN[0][1][0], WIN[1][1][1], dates)
        row += " | {:4.0%}".format(iv)
        print(row)
    # per-market buy-and-hold vs ensemble contribution in the late window
    print("\nper-market TS momentum 252 (own capital, long-only) vs buy and hold, 2011..2022 and valid 23-24:")
    for j, m in enumerate(MK):
        one = np.zeros((T, N))
        one[:, j] = sigs["TS momentum 252"][:, j]
        r, inv, turn = L.simulate(one, R)
        b1 = np.zeros((T, N))
        b1[:, j] = np.where(np.isnan(C[:, j]), 0.0, 1.0)
        rb, ib, tb = L.simulate(b1, R)
        row = m.ljust(6)
        for _, (a, b) in WIN[1:]:
            c, sh, dd, _, _ = L.stats(r, inv, turn, a, b, dates)
            cb, shb, ddb, _, _ = L.stats(rb, ib, tb, a, b, dates)
            row += " | trend {:>+6.1%} Sh {:5.2f} DD {:5.1%}  hold {:>+6.1%} Sh {:5.2f} DD {:5.1%}".format(c, sh, dd, cb, shb, ddb)
        print(row)


if __name__ == "__main__":
    main()
