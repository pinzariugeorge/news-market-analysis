"""Download free daily commodity and macro-driver series from Yahoo Finance's public chart endpoint (standard library only).

Usage: python -I src/download_commodities.py [--start 2000-01-01]
Writes data/raw/commodities/<symbol>.csv (Date,Open,High,Low,Close,Volume) and prints a coverage table.
data/raw is git-ignored: rerun this script to rebuild. Series are Yahoo's continuous front-month futures (unadjusted: roll
jumps exist; the 2020-04 WTI negative-price day is in the data) or ETFs/trusts used as proxies. See universe/COMMODITY_DATA.md.
"""
import argparse
import csv
import datetime as dt
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "commodities"
SERIES = [
    ("CL=F", "WTI crude oil futures", "oil and gas"), ("BZ=F", "Brent crude futures", "oil and gas"),
    ("NG=F", "Natural gas futures (Henry Hub)", "oil and gas"),
    ("GC=F", "Gold futures", "gold miners"), ("SI=F", "Silver futures", "gold miners"), ("PL=F", "Platinum futures", "gold miners"),
    ("^TNX", "US 10-year Treasury yield", "gold miners (rates)"), ("DX-Y.NYB", "US dollar index", "gold miners (dollar)"),
    ("TIP", "TIPS ETF (real-rate proxy)", "gold miners (real rates)"),
    ("HG=F", "Copper futures", "copper and uranium"), ("U-UN.TO", "Sprott Physical Uranium Trust (CAD, uranium proxy)", "copper and uranium"),
    ("URA", "Global X Uranium ETF (proxy)", "copper and uranium"),
    ("SMH", "Semiconductor ETF (sector driver)", "chips"), ("XLV", "Health care sector ETF (sector driver)", "pharma"),
    ("^VIX", "VIX volatility index", "market regime"),
]


def fetch(sym, start):
    p1 = int((dt.datetime.fromisoformat(start) - dt.datetime(1970, 1, 1)).total_seconds())
    p2 = int((dt.datetime.utcnow() - dt.datetime(1970, 1, 1)).total_seconds()) + 86400
    url = "https://query1.finance.yahoo.com/v8/finance/chart/{}?period1={}&period2={}&interval=1d&events=history".format(urllib.parse.quote(sym), p1, p2)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research-script)"})
    res = json.loads(urllib.request.urlopen(req, timeout=60).read())["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    rows = []
    for i, t in enumerate(res["timestamp"]):
        if q["close"][i] is None:
            continue
        d = (dt.datetime(1970, 1, 1) + dt.timedelta(seconds=t)).date().isoformat()
        rows.append([d, q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i] or 0])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2000-01-01")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    print("{:10s} {:52s} {:>6s} {:>11s} {:>11s} {:>10s}".format("symbol", "series", "bars", "first", "last", "last close"))
    for sym, name, fam in SERIES:
        try:
            rows = fetch(sym, a.start)
            with open(OUT / (sym.replace("^", "").replace("=", "_").replace(".", "_") + ".csv"), "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
                w.writerows(rows)
            print("{:10s} {:52s} {:6d} {:>11s} {:>11s} {:10.2f}".format(sym, name[:52], len(rows), rows[0][0], rows[-1][0], rows[-1][4]))
        except Exception as e:  # noqa: BLE001
            print("{:10s} {:52s} FAILED {}".format(sym, name[:52], repr(e)[:50]))


if __name__ == "__main__":
    main()
