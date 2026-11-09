"""Save a dated snapshot of analyst estimates (Alpha Vantage EARNINGS_ESTIMATES) for the tracked names.

Why: estimate revisions predict earnings surprises but no free history exists, so we build our own point-in-time history.
Usage: python -I src/snapshot_estimates.py [--tickers XOM ...] [--demo]
Writes data/raw/estimates/<TICKER>/<YYYY-MM-DD>.json (git-ignored). One request per name (20 names, free limit about 25 a day).
Skips names already saved today; stops at a rate-limit message. Key handling as in download_consensus.py (never printed).
"""
import argparse
import datetime
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from download_consensus import DEFAULT, ROOT, key_from_env

OUT = ROOT / "data" / "raw" / "estimates"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="*", default=DEFAULT)
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    key = "demo" if a.demo else key_from_env()
    tickers = ["IBM"] if a.demo else a.tickers
    if not key:
        sys.exit("No ALPHAVANTAGE_API_KEY found.")
    today = datetime.date.today().isoformat()
    for t in tickers:
        f = OUT / t / (today + ".json")
        if f.exists():
            print(t, "already saved today")
            continue
        url = "https://www.alphavantage.co/query?function=EARNINGS_ESTIMATES&symbol={}&apikey={}".format(t, key)
        j = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research-script)"}), timeout=60).read())
        if "estimates" not in j:
            msg = str(j)[:160]
            print(t, "no data; message:", msg)
            if "call frequency" in msg or "rate limit" in msg.lower() or "25 requests" in msg:
                print("Rate limit reached; rerun tomorrow.")
                break
            continue
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(j), encoding="utf-8")
        print("{:5s} {} estimate rows, keys: {}".format(t, len(j["estimates"]), ",".join(j["estimates"][0].keys())))
        time.sleep(1.5)


if __name__ == "__main__":
    main()
