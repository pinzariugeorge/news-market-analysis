"""Download daily S&P 500 prices for 2020 and save them locally.

Tries Yahoo Finance's public chart endpoint first (symbol ^GSPC), then Stooq
(symbol ^spx) as a fallback. Uses only the Python standard library so no
package installs are needed.

Usage: python3 -I src/download_prices.py
Output: data/raw/sp500_2020_daily.csv  (Date,Open,High,Low,Close,Volume,Source)
"""
import csv
import datetime as dt
import io
import json
import sys
import urllib.request
from pathlib import Path

START = dt.date(2020, 1, 1)
END = dt.date(2020, 12, 31)
OUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "sp500_2020_daily.csv"
UA = {"User-Agent": "Mozilla/5.0 (research-script)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def from_yahoo():
    p1 = int(dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).timestamp())
    p2 = int(dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc).timestamp())
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
        f"?period1={p1}&period2={p2}&interval=1d&events=history"
    )
    data = json.loads(fetch(url))
    res = data["chart"]["result"][0]
    ts = res["timestamp"]
    q = res["indicators"]["quote"][0]
    rows = []
    for i, t in enumerate(ts):
        d = dt.datetime.fromtimestamp(t, dt.timezone.utc).date()
        if q["close"][i] is None:
            continue
        rows.append([d.isoformat(), q["open"][i], q["high"][i], q["low"][i],
                     q["close"][i], q["volume"][i], "yahoo"])
    return rows


def from_stooq():
    url = "https://stooq.com/q/d/l/?s=%5Espx&d1=20200101&d2=20201231&i=d"
    text = fetch(url).decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for r in reader:
        rows.append([r["Date"], r["Open"], r["High"], r["Low"], r["Close"],
                     r.get("Volume", ""), "stooq"])
    return rows


def from_local_csv(path):
    """Normalize a Yahoo-style CSV the user downloaded by hand (Date,Open,High,Low,Close,Adj Close,Volume)."""
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            d = dt.datetime.strptime(r["Date"], "%Y-%m-%d").date() if "-" in r["Date"] \
                else dt.datetime.strptime(r["Date"], "%m/%d/%Y").date()
            if not (START <= d <= END):
                continue
            rows.append([d.isoformat(), r["Open"], r["High"], r["Low"], r["Close"],
                         r.get("Volume", ""), "manual-yahoo"])
    rows.sort()
    return rows


def main():
    rows, errors = None, []
    if len(sys.argv) > 1:
        rows = from_local_csv(sys.argv[1])
        print(f"Read {len(rows)} 2020 rows from {sys.argv[1]}")
    sources = () if rows else (("yahoo", from_yahoo), ("stooq", from_stooq))
    for name, fn in sources:
        try:
            rows = fn()
            if rows:
                print(f"Got {len(rows)} rows from {name}")
                break
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {e!r}")
            print(f"{name} failed: {e!r}", file=sys.stderr)
    if not rows:
        print("ALL SOURCES FAILED", errors, file=sys.stderr)
        sys.exit(1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Open", "High", "Low", "Close", "Volume", "Source"])
        w.writerows(rows)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
