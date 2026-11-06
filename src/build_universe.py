"""Measure a candidate trading universe with recent market data (research tool, not a recommendation).

Usage: python -I src/build_universe.py universe/solar_chain.csv [--range 1y]
Input CSV columns: ticker, name, role, notes
Downloads daily bars from Yahoo's public chart endpoint (standard library only) and writes
universe/<input-stem>_metrics.csv with, per ticker:
  last_close, currency, bars, avg_dollar_volume_30d (price x volume, local currency),
  daily_vol_pct (std of daily returns over the range), avg_abs_move_pct, days_ge_5pct (share of days with |move| >= 5%),
  max_drawdown_pct, return_range_pct, data_end (last date)
Metrics describe the past range only: they say nothing about future profit.
"""
import argparse
import csv
import datetime as dt
import json
import statistics as st
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0 (research-script)"}


def fetch(ticker, rng):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range={}&interval=1d".format(urllib.parse.quote(ticker), rng)
    req = urllib.request.Request(url, headers=UA)
    res = json.loads(urllib.request.urlopen(req, timeout=30).read())["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    bars = []
    for i, t in enumerate(res["timestamp"]):
        if q["close"][i] is None:
            continue
        d = (dt.datetime(1970, 1, 1) + dt.timedelta(seconds=t)).date().isoformat()
        bars.append((d, q["close"][i], q["volume"][i] or 0))
    return res["meta"].get("currency", ""), bars


def metrics(bars):
    closes = [b[1] for b in bars]
    rets = [(closes[i] / closes[i - 1] - 1) * 100 for i in range(1, len(closes))]
    peak, mdd = closes[0], 0.0
    for c in closes:
        peak = max(peak, c)
        mdd = min(mdd, c / peak - 1)
    last30 = bars[-30:]
    return {
        "last_close": round(closes[-1], 2), "bars": len(bars),
        "avg_dollar_volume_30d": round(st.mean(b[1] * b[2] for b in last30)),
        "daily_vol_pct": round(st.pstdev(rets), 2), "avg_abs_move_pct": round(st.mean(abs(r) for r in rets), 2),
        "days_ge_5pct": round(sum(1 for r in rets if abs(r) >= 5) / len(rets) * 100, 1),
        "max_drawdown_pct": round(mdd * 100, 1), "return_range_pct": round((closes[-1] / closes[0] - 1) * 100, 1),
        "data_end": bars[-1][0],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--range", default="1y")
    a = ap.parse_args()
    src = ROOT / a.csv
    rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
    out = []
    for r in rows:
        try:
            cur, bars = fetch(r["ticker"], a.range)
            m = metrics(bars)
            m["currency"] = cur
        except Exception as e:  # noqa: BLE001
            m = {"error": repr(e)[:80]}
        out.append({**r, **m})
        print(r["ticker"], {k: v for k, v in m.items() if k in ("last_close", "currency", "daily_vol_pct", "avg_dollar_volume_30d", "error", "data_end")})
    cols = ["ticker", "name", "role", "currency", "last_close", "bars", "avg_dollar_volume_30d", "daily_vol_pct", "avg_abs_move_pct",
            "days_ge_5pct", "max_drawdown_pct", "return_range_pct", "data_end", "notes", "error"]
    dest = src.with_name(src.stem + "_metrics.csv")
    with open(dest, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    print("saved", dest)


if __name__ == "__main__":
    main()
