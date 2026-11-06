"""Single-stock handbook statistics per family, from history only (no data after 2024-12-31 is used).

Usage: python -I src/build_family_stats.py
Periods: build = up to 2022-12-31 (writes the handbook numbers), validation = 2023-01-01 to 2024-12-31 (checks stability).
The final test period (2025 onward) is NOT used here.
Per family: driver link (R-squared, beta, next-day lead) against a driver series; base rates (daily volatility, share of days
with a 3% / 5% move, up-day share); volume-shock days (volume at least 2.5x the previous 60-day mean and a close-to-close move of
at least 3%; a proxy for earnings and news days) with frequency, size, direction and the following 10-day excess return; weekday
and first-Friday activity ratios; average correlations within and between families.
Writes handbook/family_stats.csv. Names: the current rule-selected universe (universe/UNIVERSE_RULE.md).
"""
import csv
import statistics as st
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import build_universe as bu  # noqa: E402

FAM = {"oil_gas": ["XOM", "CVX", "COP", "OXY"], "gold_miners": ["NEM", "AEM", "WPM", "AU"], "chips": ["NVDA", "MU", "AMD", "INTC"],
       "pharma": ["LLY", "JNJ", "ABBV", "MRK"], "copper_uranium": ["FCX", "CCJ", "SCCO", "TECK"]}
DRIVER = {"XOM": "CL=F", "CVX": "CL=F", "COP": "CL=F", "OXY": "CL=F", "NEM": "GC=F", "AEM": "GC=F", "WPM": "GC=F", "AU": "GC=F",
          "NVDA": "SMH", "MU": "SMH", "AMD": "SMH", "INTC": "SMH", "LLY": "XLV", "JNJ": "XLV", "ABBV": "XLV", "MRK": "XLV",
          "FCX": "HG=F", "SCCO": "HG=F", "TECK": "HG=F", "CCJ": "URA"}
LAST = "2024-12-31"
PER = {"build": ("0000", "2022-12-31"), "valid": ("2023-01-01", LAST)}


def corr(x, y):
    mx, my = st.mean(x), st.mean(y)
    sx = sum((a - mx) ** 2 for a in x) ** .5
    sy = sum((b - my) ** 2 for b in y) ** .5
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def main():
    names = [t for v in FAM.values() for t in v]
    px, vol = {}, {}
    for t in set(names) | set(DRIVER.values()):
        _, b = bu.fetch(t, "10y")
        px[t] = {x[0]: x[1] for x in b if x[0] <= LAST}
        vol[t] = {x[0]: x[2] for x in b if x[0] <= LAST}
    cal = sorted(px["XOM"])
    ret = {}
    for t in px:
        d = sorted(px[t])
        ret[t] = {d[i]: (px[t][d[i]] / px[t][d[i - 1]] - 1) * 100 for i in range(1, len(d)) if px[t][d[i - 1]] > 0 and px[t][d[i]] > 0}
        if t.endswith("=F"):                       # drop the 2020-04 negative-price oil roll anomaly (returns beyond 25%)
            ret[t] = {k: v for k, v in ret[t].items() if abs(v) < 25}
    rows = []

    def per_of(d):
        for p, (a, b) in PER.items():
            if a <= d <= b:
                return p

    print("== driver link (daily returns): R-squared / beta / next-day lead correlation, build -> validation")
    for fam, ts in FAM.items():
        for t in ts:
            line = []
            for p in PER:
                ds = [d for d in ret[t] if d in ret[DRIVER[t]] and per_of(d) == p]
                x = [ret[DRIVER[t]][d] for d in ds]; y = [ret[t][d] for d in ds]
                c = corr(x, y)
                lead = corr(x[:-1], y[1:])
                line.append((c * c, c * st.pstdev(y) / st.pstdev(x), lead))
                rows.append({"family": fam, "ticker": t, "period": p, "stat": "driver_" + DRIVER[t], "r2": round(c * c, 3), "beta": round(line[-1][1], 3), "lead_corr": round(lead, 3)})
            print("{:15s} {:5s} vs {:6s} build R2 {:.2f} beta {:.2f} lead {:+.2f} | valid R2 {:.2f} beta {:.2f} lead {:+.2f}".format(
                fam, t, DRIVER[t], *line[0], *line[1]))

    print("\n== base rates per family (pooled over names): daily vol %, avg |move| %, days >=3%, days >=5%, up-day share")
    for fam, ts in FAM.items():
        for p in PER:
            r = [v for t in ts for d, v in ret[t].items() if per_of(d) == p]
            row = {"family": fam, "ticker": "pooled", "period": p, "stat": "base", "daily_vol": round(st.pstdev(r), 2), "avg_abs": round(st.mean(abs(x) for x in r), 2),
                   "ge3": round(100 * sum(1 for x in r if abs(x) >= 3) / len(r), 1), "ge5": round(100 * sum(1 for x in r if abs(x) >= 5) / len(r), 1),
                   "up": round(100 * sum(1 for x in r if x > 0) / len(r), 1)}
            rows.append(row)
            print("{:15s} {:6s} vol {:.2f} abs {:.2f} >=3% {:4.1f} >=5% {:4.1f} up {:4.1f}".format(fam, p, row["daily_vol"], row["avg_abs"], row["ge3"], row["ge5"], row["up"]))

    print("\n== volume-shock days (volume >= 2.5x prior 60-day mean and |move| >= 3%): per name per year, mean |move|, share up, 10-day excess return after")
    for fam, ts in FAM.items():
        for p in PER:
            ev = []; years = 0.0; base10 = []
            for t in ts:
                d = sorted(px[t])
                v = [vol[t].get(x, 0) for x in d]
                c = [px[t][x] for x in d]
                for i in range(61, len(d) - 11):
                    if per_of(d[i]) != p:
                        continue
                    base10.append((c[i + 10] / c[i] - 1) * 100)
                    m = st.mean(v[i - 60:i])
                    r = ret[t].get(d[i])
                    if m > 0 and v[i] >= 2.5 * m and r is not None and abs(r) >= 3:
                        ev.append((r, (c[i + 10] / c[i] - 1) * 100))
                yrs = len([x for x in d if per_of(x) == p]) / 252
                years += yrs
            if len(ev) < 5:
                continue
            b10 = st.mean(base10)
            after_up = [x[1] for x in ev if x[0] > 0]; after_dn = [x[1] for x in ev if x[0] < 0]
            row = {"family": fam, "ticker": "pooled", "period": p, "stat": "shock", "events_per_name_year": round(len(ev) / years, 2), "mean_abs_move": round(st.mean(abs(x[0]) for x in ev), 2),
                   "share_up": round(100 * sum(1 for x in ev if x[0] > 0) / len(ev), 1), "excess10_after_up": round(st.mean(after_up) - b10, 2) if after_up else "",
                   "excess10_after_down": round(st.mean(after_dn) - b10, 2) if after_dn else "", "n": len(ev)}
            rows.append(row)
            print("{:15s} {:6s} n={:3d} per name-year {:.2f} |move| {:.1f}% up {:4.1f}% | 10d excess after up {} after down {}".format(
                fam, p, len(ev), row["events_per_name_year"], row["mean_abs_move"], row["share_up"], row["excess10_after_up"], row["excess10_after_down"]))

    print("\n== weekday activity: mean |move| on the weekday / mean |move| other days (pooled names), build period")
    names_d = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    import datetime as dt
    for fam, ts in FAM.items():
        out = []
        for wd in range(5):
            a = [abs(v) for t in ts for d, v in ret[t].items() if per_of(d) == "build" and dt.date.fromisoformat(d).weekday() == wd]
            o = [abs(v) for t in ts for d, v in ret[t].items() if per_of(d) == "build" and dt.date.fromisoformat(d).weekday() != wd]
            out.append(st.mean(a) / st.mean(o))
            rows.append({"family": fam, "ticker": "pooled", "period": "build", "stat": "weekday_" + names_d[wd], "ratio": round(out[-1], 3)})
        ff = [abs(v) for t in ts for d, v in ret[t].items() if per_of(d) == "build" and dt.date.fromisoformat(d).weekday() == 4 and dt.date.fromisoformat(d).day <= 7]
        ot = [abs(v) for t in ts for d, v in ret[t].items() if per_of(d) == "build" and not (dt.date.fromisoformat(d).weekday() == 4 and dt.date.fromisoformat(d).day <= 7)]
        rows.append({"family": fam, "ticker": "pooled", "period": "build", "stat": "first_friday", "ratio": round(st.mean(ff) / st.mean(ot), 3)})
        print("{:15s} ".format(fam) + " ".join("{} {:.2f}".format(n, x) for n, x in zip(names_d, out)) + "  first Friday {:.2f}".format(st.mean(ff) / st.mean(ot)))

    print("\n== average pairwise daily correlation, build period: within family / between families")
    allc = {}
    for t in names:
        for d, v in ret[t].items():
            if per_of(d) == "build":
                allc.setdefault(t, {})[d] = v
    def pc(a, b):
        ds = sorted(set(allc[a]) & set(allc[b]))
        return corr([allc[a][d] for d in ds], [allc[b][d] for d in ds])
    for fam, ts in FAM.items():
        w = [pc(a, b) for a, b in combinations(ts, 2)]
        o = [pc(a, b) for g, os_ in FAM.items() if g != fam for a in ts for b in os_]
        print("{:15s} within {:.2f} between {:.2f}".format(fam, st.mean(w), st.mean(o)))
        rows.append({"family": fam, "ticker": "pooled", "period": "build", "stat": "corr", "within": round(st.mean(w), 3), "between": round(st.mean(o), 3)})

    cols = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("family", "ticker", "period", "stat"), k))
    with open(ROOT / "handbook" / "family_stats.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(rows)
    print("\nsaved handbook/family_stats.csv")


if __name__ == "__main__":
    main()
