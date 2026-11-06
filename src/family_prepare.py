"""Pick decision dates and write past-only records for the family run.

Usage: python -I src/family_prepare.py [--run fam_v0] [--start 2023-01-03] [--end 2024-12-31] [--step 21] [--capital 1000]
Decision dates: every STEP trading days from START up to END minus 25 trading days (so every hold can finish before END).
Each record contains only closes dated before the decision day and calendar facts known in advance. Validation period only
(2023-2024); the final test (2025 onward) is not touched. Writes results/<run>/days.json and results/<run>/records/<day>.json.
"""
import argparse
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import familydata as fd  # noqa: E402
import datetime as dt    # noqa: E402


def stats(closes_by_date, day, sym_type="price"):
    ds = sorted(d for d in closes_by_date if d < day)
    if len(ds) < 260:
        return None
    c = [closes_by_date[d] for d in ds]
    rets = [(c[i] / c[i - 1] - 1) * 100 for i in range(len(c) - 20, len(c))]
    def r(n):
        return round((c[-1] / c[-1 - n] - 1) * 100, 2)
    ma200 = sum(c[-200:]) / 200
    hi = max(c[-252:])
    return {"last_date": ds[-1], "last": round(c[-1], 3), "ret_1d_pct": r(1), "ret_5d_pct": r(5), "ret_20d_pct": r(20), "ret_60d_pct": r(60),
            "vol_20d_daily_pct": round(st.pstdev(rets), 2), "above_200d_avg": c[-1] > ma200, "from_252d_high_pct": round((c[-1] / hi - 1) * 100, 1)}


def build(day, series, stocks, sel, capital):
    names = fd.names_at(sel, day)
    rec = {"decision_day": day, "weekday": dt.date.fromisoformat(day).strftime("%A"), "information_cutoff": "closes dated before " + day,
           "account": {"capital_usd": capital, "max_long_positions": 3, "round_trip_cost_pct_approx": 0.3, "whole_shares": True},
           "macro": {sym: stats(series[sym], day) for sym, _ in fd.MACRO}, "families": {}}
    for fam in fd.FAMILIES:
        rec["families"][fam] = {
            "label": fd.FAMILY_LABEL[fam],
            "drivers": {name: stats(series[sym], day) for sym, name in fd.DRIVERS[fam]},
            "names": {t: dict(stats(stocks[t], day) or {}, is_leader=(i == 0)) for i, t in enumerate(names[fam]) if t in stocks},
            "leader": names[fam][0]}
    cal = [d for d in sorted(series["CL=F"]) if d < day]
    D = dt.date.fromisoformat(day)
    rec["calendar"] = {"month": D.strftime("%B"), "earnings_season_window": D.month in (1, 2, 4, 5, 7, 8, 10, 11),
                       "known_weekly_events": ["US crude inventories (Wednesday)", "US natural gas storage (Thursday)"],
                       "first_friday_jobs_report_in_next_20_trading_days": True}
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="fam_v0")
    ap.add_argument("--start", default="2023-01-03")
    ap.add_argument("--end", default="2024-12-31")
    ap.add_argument("--step", type=int, default=21)
    ap.add_argument("--capital", type=int, default=1000)
    a = ap.parse_args()
    series, stocks, sel = fd.load_series(), fd.load_stocks(), fd.selections()
    cal = sorted(d for d in series["CL=F"] if a.start <= d <= a.end)
    dates = cal[:-25][::a.step]
    out = ROOT / "results" / a.run
    (out / "records").mkdir(parents=True, exist_ok=True)
    for d in dates:
        rec = build(d, series, stocks, sel, a.capital)
        (out / "records" / (d + ".json")).write_text(json.dumps(rec, indent=1), encoding="utf-8")
    (out / "days.json").write_text(json.dumps(dates), encoding="utf-8")
    print(len(dates), "decision days:", dates[0], "to", dates[-1])
    print(dates)


if __name__ == "__main__":
    main()
