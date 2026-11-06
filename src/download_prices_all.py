"""Download daily S&P 500 prices for 1950-01-01 to 2024-04-30 (matches the headlines dataset range).

Uses Yahoo's public chart endpoint (^GSPC), standard library only.
Usage: python -I src/download_prices_all.py
Output: data/raw/sp500_1950_2024_daily.csv (Date,Open,High,Low,Close,Volume,Source)
"""
import csv
import datetime as dt
import json
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "sp500_1950_2024_daily.csv"
p1 = int((dt.datetime(1950, 1, 1) - dt.datetime(1970, 1, 1)).total_seconds())
p2 = int(dt.datetime(2024, 5, 1, tzinfo=dt.timezone.utc).timestamp())
url = f"https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?period1={p1}&period2={p2}&interval=1d&events=history"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research-script)"})
res = json.loads(urllib.request.urlopen(req, timeout=60).read())["chart"]["result"][0]
q = res["indicators"]["quote"][0]
rows = []
for i, t in enumerate(res["timestamp"]):
    if q["close"][i] is None:
        continue
    d = (dt.datetime(1970, 1, 1) + dt.timedelta(seconds=t)).date().isoformat()
    rows.append([d, q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i], "yahoo"])
rows.sort()
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Date", "Open", "High", "Low", "Close", "Volume", "Source"])
    w.writerows(rows)
print(f"{len(rows)} rows, {rows[0][0]} to {rows[-1][0]}, saved {OUT}")
