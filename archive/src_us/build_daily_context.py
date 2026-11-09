"""Build the past-only daily context record for one decision day D.

Usage: python -I src/build_daily_context.py 2018-12-26 [--max-headlines 40] [--out file.json]
Reads  data/processed/market_days.csv  (date, close, ret_pct, split)
       data/processed/news_all.csv     (date, decision_date, split, title)
Prints / writes a JSON record with ONLY information available before the open of day D:
  - market state from closes dated before D (never D's own close or later)
  - calendar facts known in advance
  - headlines whose decision_date == D (published after the previous trading day's date through D-1)
The record never contains D's return or any later price. See agent/DAILY_RECORD.md.
"""
import argparse
import bisect
import csv
import datetime as dt
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAYS = ROOT / "data" / "processed" / "market_days.csv"
NEWS = ROOT / "data" / "processed" / "news_all.csv"


def load_days():
    rows = []
    with open(DAYS, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((r["date"], float(r["close"]), float(r["ret_pct"]) if r["ret_pct"] else None))
    return rows


def election_day(year):
    d = dt.date(year, 11, 1)
    while d.weekday() != 0:
        d += dt.timedelta(1)
    return d + dt.timedelta(1)


def cycle_info(d):
    """US election-cycle facts known in advance (dates are statutory)."""
    y = d.year
    kind = {0: "presidential", 2: "midterm"}.get(y % 4, "pre-election" if y % 4 == 3 else "post-presidential")
    nxt = None
    for yy in (y, y + 1, y + 2):
        if yy % 2 == 0 and election_day(yy) >= d:
            nxt = (yy, election_day(yy))
            break
    return {"cycle_year_type": kind, "next_us_election": nxt[1].isoformat() if nxt else None,
            "days_to_next_us_election": (nxt[1] - d).days if nxt else None}


def vol_regime(vols_hist, cur):
    """Quartile (1 calm .. 4 stormy) of current 20d vol among the previous <=2520 values (past only)."""
    hist = vols_hist[-2520:]
    if len(hist) < 250:
        return None
    rank = sum(v <= cur for v in hist) / len(hist)
    return 1 + min(3, int(rank * 4))


def build(day, max_headlines=40):
    days = load_days()
    dates = [d for d, _, _ in days]
    D = dt.date.fromisoformat(day)
    i = bisect.bisect_left(dates, day)          # first index with date >= day
    if i >= len(dates) or dates[i] != day:
        raise SystemExit(f"{day} is not a trading day in the data")
    past = days[:i]                              # strictly before D
    if len(past) < 260:
        raise SystemExit("not enough history before this day")
    closes = [c for _, c, _ in past]
    rets = [r for _, _, r in past if r is not None]
    last_date, last_close = past[-1][0], closes[-1]

    def ret_n(n):
        return round((closes[-1] / closes[-1 - n] - 1) * 100, 2)

    vol20 = st.pstdev(rets[-20:])
    vols_hist = [st.pstdev(rets[k - 20:k]) for k in range(20, len(rets) + 1, 1)]
    hi252 = max(closes[-252:])
    ma200 = sum(closes[-200:]) / 200
    streak, sign = 0, 0
    for r in reversed(rets):
        s = 1 if r > 0 else -1
        if sign in (0, s):
            sign, streak = s, streak + 1
        else:
            break
    big_recent = [(d, r) for d, _, r in past[-10:] if r is not None and abs(r) >= 2]

    # headlines usable on D: decision_date == D
    heads = []
    with open(NEWS, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["decision_date"] == day:
                heads.append({"published": r["date"], "title": r["title"]})
    n_heads = len(heads)

    first_days_of_month = sorted(d for d in dates if d[:7] == day[:7])
    rec = {
        "decision_day": day,
        "weekday": D.strftime("%A"),
        "information_cutoff": f"close of {last_date} (previous trading day); headlines published before {day}",
        "market_state": {
            "last_trading_day": last_date,
            "last_close": round(last_close, 2),
            "return_last_day_pct": round(rets[-1], 2),
            "return_5d_pct": ret_n(5), "return_20d_pct": ret_n(20), "return_60d_pct": ret_n(60),
            "realized_vol_20d_daily_pct": round(vol20, 2),
            "vol_regime_1calm_to_4stormy": vol_regime(vols_hist, vol20),
            "drawdown_from_252d_high_pct": round((last_close / hi252 - 1) * 100, 2),
            "distance_from_200d_avg_pct": round((last_close / ma200 - 1) * 100, 2),
            "consecutive_up_or_down_days": streak * sign,
            "big_moves_2pct_last_10_days": [{"date": d, "ret_pct": r} for d, r in big_recent],
        },
        "calendar": {
            "month": D.strftime("%B"),
            "trading_day_of_month": first_days_of_month.index(day) + 1,
            "turn_of_month_window": first_days_of_month.index(day) < 3,
            "year_end_window": (D.month == 12 and D.day >= 23) or (D.month == 1 and D.day <= 5),
            **cycle_info(D),
        },
        "headlines": heads[:max_headlines],
        "headlines_total": n_heads,
        "headlines_truncated": n_heads > max_headlines,
    }
    return rec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("day")
    ap.add_argument("--max-headlines", type=int, default=40)
    ap.add_argument("--out")
    a = ap.parse_args()
    rec = build(a.day, a.max_headlines)
    txt = json.dumps(rec, indent=2, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(txt, encoding="utf-8")
    else:
        print(txt)
