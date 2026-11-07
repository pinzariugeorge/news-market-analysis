"""Do insider open-market purchases predict returns? (SEC Forms 4, data/raw/insider/purchases.csv from src/download_insider.py)

Events (fixed in advance):
  A = first officer/director purchase of at least 50,000 USD in a ticker after 90 days without one;
  B = cluster: at least 2 distinct officers/directors buy within 21 days with a combined value of at least 100,000 USD (counted once per ticker per 90 days).
Purchases by ten-percent owners only (corporate holders) are excluded. Event date = SEC filing date; entry at the close of the second trading day on or after the filing date
(one extra day of lag), exit H = 20 or 60 trading days later; cost 0.15% per side. Abnormal return = the stock's return minus the equal-weight average return of all names in the
universe over the same dates. Months are used as the unit for the t-statistic (events overlap). Periods: build 2014-2020, validation 2021-2024 (data stops 2024-12-31; 2025+ reserved).
Pre-registered pass rule: mean abnormal 20-day return after cost >= +1.0% with t >= 2.5 in build, and the same sign with at least half the size in validation.
Usage: python -I src/run_insider_test.py
"""
import csv
import datetime as dt
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import os  # noqa: E402
os.environ.setdefault("STRAT_OHLC", "ohlc_long")
import strat_lab as L  # noqa: E402

COST = 0.0015


def pdate(s):
    return dt.datetime.strptime(s, "%d-%b-%Y").date().isoformat()


def main():
    dates, names, D, spx = L.load("2024-12-31")
    C = D["c"]
    T, N = C.shape
    col = {n: j for j, n in enumerate(names)}
    didx = {d: i for i, d in enumerate(dates)}
    rows = []
    for r in csv.DictReader(open(ROOT / "data" / "raw" / "insider" / "purchases.csv", encoding="utf-8")):
        try:
            fd, td = pdate(r["filing_date"]), pdate(r["trans_date"])
        except ValueError:
            continue
        rel = r["relationship"].lower()
        if "officer" not in rel and "director" not in rel:
            continue
        if fd > "2024-12-31" or r["ticker"] not in col:
            continue
        rows.append((fd, r["ticker"], r["owner"], float(r["value"] or 0)))
    rows.sort()
    print("{} officer/director purchase rows after filters, {} tickers".format(len(rows), len({r[1] for r in rows})))
    by = defaultdict(list)
    for fd, t, o, v in rows:
        by[t].append((fd, o, v))
    events = {"A": [], "B": []}
    for t, lst in by.items():
        last_a = None
        for fd, o, v in lst:
            if v >= 50000 and (last_a is None or (dt.date.fromisoformat(fd) - dt.date.fromisoformat(last_a)).days > 90):
                events["A"].append((fd, t))
                last_a = fd
        last_b = None
        for k, (fd, o, v) in enumerate(lst):
            f0 = dt.date.fromisoformat(fd)
            win = [(x, y, z) for x, y, z in lst[k:] if (dt.date.fromisoformat(x) - f0).days <= 21]
            owners = {y for _, y, _ in win}
            if len(owners) >= 2 and sum(z for _, _, z in win) >= 100000:
                end = max(dt.date.fromisoformat(x) for x, _, _ in win).isoformat()  # known once the second purchase is filed
                if last_b is None or (dt.date.fromisoformat(end) - dt.date.fromisoformat(last_b)).days > 90:
                    events["B"].append((end, t))
                    last_b = end
    print("events: A {}  B {}".format(len(events["A"]), len(events["B"])))
    R_all = np.full((T, N), np.nan)
    R_all[1:] = C[1:] / C[:-1] - 1
    for H in (20, 60):
        print("\n=== hold {} trading days ===".format(H))
        print("{:5s} {:11s} {:>6s} {:>10s} {:>9s} {:>9s} {:>7s}".format("event", "period", "n", "mean abn.", "t (month)", "hit rate", "mean raw"))
        for ev, lst in events.items():
            res = defaultdict(list)
            for fd, t in lst:
                i = next((k for k, d in enumerate(dates) if d >= fd), None)
                if i is None:
                    continue
                s, e = i + 2, i + 2 + H
                j = col[t]
                if e >= T or np.isnan(C[s, j]) or np.isnan(C[e, j]):
                    continue
                r = C[e, j] / C[s, j] - 1 - 2 * COST
                valid = ~np.isnan(C[s]) & ~np.isnan(C[e])
                ew = np.mean(C[e, valid] / C[s, valid] - 1)
                per = "build" if dates[s] <= "2020-12-31" else "valid"
                res[per].append((dates[s][:7], r - ew, r))
            for per in ("build", "valid"):
                x = res.get(per, [])
                if len(x) < 5:
                    print("{:5s} {:11s} {:>6d}  too few".format(ev, per, len(x)))
                    continue
                bym = defaultdict(list)
                for m, a, _ in x:
                    bym[m].append(a)
                mm = np.array([np.mean(v) for v in bym.values()])
                t = mm.mean() / (mm.std(ddof=1) / np.sqrt(len(mm))) if len(mm) > 2 else float("nan")
                print("{:5s} {:11s} {:>6d} {:>+9.2%} {:>9.2f} {:>9.0%} {:>+7.2%}".format(ev, per, len(x), np.mean([a for _, a, _ in x]), t, np.mean([a > 0 for _, a, _ in x]), np.mean([r for _, _, r in x])))


if __name__ == "__main__":
    main()
