"""Test standard indicators and candlestick patterns as long-entry signals on the candidate stocks (research, not advice).

Usage: python -I src/run_indicator_tests.py
Data: 10 years of daily open/high/low/close/volume from Yahoo for every name in universe/candidates.csv (standard library only).
For each signal: signal computed with data up to the close of day t; entry at the close of day t+1; exit H trading days later
(H = 5, 10, 20); one cost of 0.25% per round trip (small US order, see src/costs.py). To limit overlap, a name's signals within
H days of its previous signal are skipped. Compared with the unconditional mean forward return of the same names and period
("excess" = signal mean minus unconditional mean, so the stocks' own uptrend is removed).
Periods by entry date: build up to 2022-12-31, validation 2023-2024, final test 2025 onward. Nothing is tuned.
Writes results/indicator_tests.csv.
"""
import csv
import datetime as dt
import json
import math
import statistics as st
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COST = 0.25
HS = (5, 10, 20)
PERIODS = (("build", "0000", "2022-12-31"), ("valid", "2023-01-01", "2024-12-31"), ("test", "2025-01-01", "9999"))


def fetch_ohlc(t):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range=10y&interval=1d".format(t)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research-script)"})
    res = json.loads(urllib.request.urlopen(req, timeout=30).read())["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    rows = []
    for i, ts in enumerate(res["timestamp"]):
        if None in (q["open"][i], q["high"][i], q["low"][i], q["close"][i]):
            continue
        d = (dt.datetime(1970, 1, 1) + dt.timedelta(seconds=ts)).date().isoformat()
        rows.append((d, q["open"][i], q["high"][i], q["low"][i], q["close"][i]))
    return rows


def sma(x, n):
    out, s = [None] * len(x), 0.0
    for i, v in enumerate(x):
        s += v
        if i >= n:
            s -= x[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def ema(x, n):
    k, out, e = 2 / (n + 1), [], None
    for v in x:
        e = v if e is None else v * k + e * (1 - k)
        out.append(e)
    return out


def rsi(x, n=14):
    out = [None] * len(x)
    if len(x) <= n:
        return out
    gains = [max(x[i] - x[i - 1], 0) for i in range(1, n + 1)]
    losses = [max(x[i - 1] - x[i], 0) for i in range(1, n + 1)]
    ag, al = sum(gains) / n, sum(losses) / n
    out[n] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n + 1, len(x)):
        g, l = max(x[i] - x[i - 1], 0), max(x[i - 1] - x[i], 0)
        ag, al = (ag * (n - 1) + g) / n, (al * (n - 1) + l) / n
        out[i] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def signals(rows):
    d = [r[0] for r in rows]; o = [r[1] for r in rows]; h = [r[2] for r in rows]; l = [r[3] for r in rows]; c = [r[4] for r in rows]
    n = len(c)
    s20, s50, s200, r14 = sma(c, 20), sma(c, 50), sma(c, 200), rsi(c)
    e12, e26 = ema(c, 12), ema(c, 26)
    macd = [a - b for a, b in zip(e12, e26)]
    sig9 = ema(macd, 9)
    sd20 = [None] * n
    for i in range(19, n):
        w = c[i - 19:i + 1]
        sd20[i] = st.pstdev(w)
    S = {k: [False] * n for k in ("rsi_below_30", "rsi_above_70", "macd_cross_up", "golden_cross_50_200", "close_above_sma20_cross",
                                    "bollinger_lower_touch", "breakout_20d_high", "bullish_engulfing", "hammer_in_downtrend", "three_white_soldiers")}
    for i in range(201, n):
        S["rsi_below_30"][i] = r14[i] is not None and r14[i] < 30
        S["rsi_above_70"][i] = r14[i] is not None and r14[i] > 70
        S["macd_cross_up"][i] = macd[i - 1] <= sig9[i - 1] and macd[i] > sig9[i]
        S["golden_cross_50_200"][i] = s50[i - 1] <= s200[i - 1] and s50[i] > s200[i]
        S["close_above_sma20_cross"][i] = c[i - 1] <= s20[i - 1] and c[i] > s20[i]
        S["bollinger_lower_touch"][i] = c[i] < s20[i] - 2 * sd20[i]
        S["breakout_20d_high"][i] = c[i] > max(h[i - 20:i])
        body, prev_body = abs(c[i] - o[i]), abs(c[i - 1] - o[i - 1])
        S["bullish_engulfing"][i] = (c[i - 1] < o[i - 1] and c[i] > o[i] and o[i] <= c[i - 1] and c[i] >= o[i - 1] and body > prev_body)
        rng = h[i] - l[i]
        lower = min(o[i], c[i]) - l[i]
        upper = h[i] - max(o[i], c[i])
        S["hammer_in_downtrend"][i] = rng > 0 and lower >= 2 * max(body, 1e-9) and upper <= 0.3 * max(body, 1e-9) + 0.05 * rng and c[i] < s20[i]
        S["three_white_soldiers"][i] = all(c[i - k] > o[i - k] and c[i - k] > c[i - k - 1] for k in (0, 1, 2))
    return d, c, S


def period_of(d):
    for name, a, b in PERIODS:
        if a <= d <= b:
            return name
    return None


def main():
    cands = [r["ticker"] for r in csv.DictReader(open(ROOT / "universe" / "candidates.csv", encoding="utf-8"))]
    data = {}
    for t in cands:
        try:
            rows = fetch_ohlc(t)
            if len(rows) > 500:
                data[t] = signals(rows)
        except Exception as e:  # noqa: BLE001
            print("skip", t, repr(e)[:40])
    names = list(SIGNAL_NAMES(data))
    out = []
    print("{} stocks, signals long only, entry next close, cost {}% per round trip. Excess = signal mean minus unconditional mean (same H).".format(len(data), COST))
    print("{:24s} {:>3s} {:>6s} {:>8s} {:>8s} {:>6s} {:>6s} | excess by period: {:>8s} {:>8s} {:>8s} {:>6s}".format(
        "signal", "H", "n", "mean%", "excess%", "t", "win%", "build", "valid", "test", "consis"))
    for H in HS:
        # unconditional per period
        uncond = {p[0]: [] for p in PERIODS}
        for t, (d, c, S) in data.items():
            for i in range(201, len(c) - 1 - H):
                p = period_of(d[i + 1])
                if p:
                    uncond[p].append((c[i + 1 + H] / c[i + 1] - 1) * 100 - COST)
        um = {p: st.mean(v) for p, v in uncond.items() if v}
        allm = st.mean(x for v in uncond.values() for x in v)
        for name in names:
            per = {p[0]: [] for p in PERIODS}
            for t, (d, c, S) in data.items():
                last = -10**9
                for i in range(201, len(c) - 1 - H):
                    if S[name][i] and i - last >= H:
                        last = i
                        p = period_of(d[i + 1])
                        if p:
                            per[p].append((c[i + 1 + H] / c[i + 1] - 1) * 100 - COST)
            allv = [x for v in per.values() for x in v]
            if len(allv) < 30:
                continue
            ex = {p: (st.mean(v) - um[p]) if len(v) >= 10 else None for p, v in per.items()}
            exall = st.mean(allv) - allm
            t_stat = exall / (st.pstdev(allv) / math.sqrt(len(allv))) if st.pstdev(allv) > 0 else 0
            consis = sum(1 for v in ex.values() if v is not None and v > 0)
            win = 100 * sum(1 for x in allv if x > 0) / len(allv)
            out.append({"signal": name, "H": H, "n": len(allv), "mean_pct": round(st.mean(allv), 3), "excess_pct": round(exall, 3), "t": round(t_stat, 2),
                        "win_pct": round(win, 1), "excess_build": None if ex["build"] is None else round(ex["build"], 2),
                        "excess_valid": None if ex["valid"] is None else round(ex["valid"], 2), "excess_test": None if ex["test"] is None else round(ex["test"], 2),
                        "periods_positive": consis})
            fmt = lambda v: "   n/a" if v is None else "{:8.2f}".format(v)
            print("{:24s} {:3d} {:6d} {:8.2f} {:8.2f} {:6.2f} {:6.1f} | {} {} {} {:6d}".format(name, H, len(allv), st.mean(allv), exall, t_stat, win,
                  fmt(ex["build"]), fmt(ex["valid"]), fmt(ex["test"]), consis))
        print("   (unconditional mean net return, H={}: {:.2f}%)".format(H, allm))
    with open(ROOT / "results" / "indicator_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    print("saved results/indicator_tests.csv")


def SIGNAL_NAMES(data):
    first = next(iter(data.values()))
    return first[2].keys()


if __name__ == "__main__":
    main()
