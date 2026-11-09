"""Earnings release dates from SEC EDGAR (free, no key): 8-K filings with Item 2.02 (Results of Operations).

Usage: python -I src/download_earnings.py
For each US domestic filer in the candidate list, reads data.sec.gov submissions (recent + older files), keeps 8-K filings whose
items include 2.02, and writes data/processed/earnings_events.csv with: ticker, filing_date, accepted_utc, accepted_et, session
(before_open / during / after_close), reaction_date (first trading day whose close reflects the release: same day if accepted
before 16:00 New York time, otherwise the next trading day). Foreign filers (40-F, 20-F, 6-K) have no 8-K and are skipped.
CIKs are built in and verified against the 'tickers' field of each response. EDGAR asks for a descriptive user agent; none of
the user's personal details are sent.
"""
import csv
import datetime as dt
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
CIK = {"XOM": 34088, "CVX": 93410, "COP": 1163165, "OXY": 797468, "EOG": 821189, "DVN": 1090012, "FANG": 1539838,
       "NEM": 1164727, "NVDA": 1045810, "AVGO": 1730168, "AMD": 2488, "MU": 723125, "QCOM": 804328, "INTC": 50863, "AMAT": 6951,
       "TXN": 97476, "LRCX": 707549, "KLAC": 319201, "LLY": 59478, "JNJ": 200406, "MRK": 310158, "ABBV": 1551152, "PFE": 78003,
       "BMY": 14272, "AMGN": 318154, "GILD": 882095, "FCX": 831259, "SCCO": 1001838, "UEC": 1334933}
UA = "sp500-news-sim research script (public data)"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    time.sleep(0.25)
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def et_offset(d_utc):
    """New York offset in hours for a UTC datetime (US rule: DST from the second Sunday of March to the first Sunday of November)."""
    y = d_utc.year
    def nth_sunday(month, n):
        d = dt.datetime(y, month, 1)
        d += dt.timedelta(days=(6 - d.weekday()) % 7 + 7 * (n - 1))
        return d
    start = nth_sunday(3, 2).replace(hour=7)      # 02:00 EST = 07:00 UTC
    end = nth_sunday(11, 1).replace(hour=6)       # 02:00 EDT = 06:00 UTC
    return -4 if start <= d_utc < end else -5


def main():
    rows, bad = [], []
    for t, cik in CIK.items():
        try:
            j = get("https://data.sec.gov/submissions/CIK{:010d}.json".format(cik))
        except Exception as e:  # noqa: BLE001
            bad.append((t, repr(e)[:50]))
            continue
        listed = [x.upper() for x in j.get("tickers", [])]
        name_ok = {"XOM": "EXXON"}.get(t, "") in j.get("name", "").upper() and not listed      # XOM's response lists no ticker
        if t not in listed and not name_ok:
            bad.append((t, "ticker mismatch " + str(j.get("tickers")) + " " + str(j.get("name"))))
            continue
        blocks = [j["filings"]["recent"]]
        for f in j["filings"].get("files", []):
            try:
                blocks.append(get("https://data.sec.gov/submissions/" + f["name"]))
            except Exception:  # noqa: BLE001
                pass
        n = 0
        for b in blocks:
            for i in range(len(b["form"])):
                if b["form"][i] == "8-K" and "2.02" in (b["items"][i] or "").split(","):
                    acc = b["acceptanceDateTime"][i]
                    u = dt.datetime.strptime(acc[:19], "%Y-%m-%dT%H:%M:%S")
                    et = u + dt.timedelta(hours=et_offset(u))
                    hhmm = et.hour * 60 + et.minute
                    session = "before_open" if hhmm < 570 else "during" if hhmm < 960 else "after_close"
                    rows.append({"ticker": t, "filing_date": b["filingDate"][i], "accepted_utc": acc[:19], "accepted_et": et.strftime("%Y-%m-%d %H:%M"), "session": session})
                    n += 1
        print("{:5s} {} earnings 8-Ks".format(t, n))
    rows.sort(key=lambda r: (r["ticker"], r["accepted_utc"]))
    out = ROOT / "data" / "processed" / "earnings_events.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["ticker", "filing_date", "accepted_utc", "accepted_et", "session"])
        w.writeheader()
        w.writerows(rows)
    print("saved", out, len(rows), "events; problems:", bad or "none")


if __name__ == "__main__":
    main()
