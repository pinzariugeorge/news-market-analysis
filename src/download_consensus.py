"""Download earnings history with analyst consensus (estimate, actual, surprise) from Alpha Vantage's EARNINGS endpoint.

Usage: python -I src/download_consensus.py [--tickers XOM NVDA ...] [--demo]
Key: ALPHAVANTAGE_API_KEY in .env (free key from alphavantage.co; never paste it in chat). --demo uses Alpha Vantage's public demo key,
which only works for IBM, to test the pipeline. Writes data/raw/consensus/<TICKER>.json (git-ignored, resumable: existing files are
skipped). The free tier is limited (about 25 requests a day, to be confirmed); the script stops at the first rate-limit message and
you rerun it the next day. Each file holds quarterly records: fiscalDateEnding, reportedDate, reportedEPS, estimatedEPS, surprise,
surprisePercentage, reportTime (pre-market / post-market).
"""
import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "consensus"
DEFAULT = ["XOM", "CVX", "COP", "OXY", "NEM", "NVDA", "MU", "AMD", "INTC", "LLY", "JNJ", "ABBV", "MRK", "FCX", "SCCO",
           "AVGO", "QCOM", "AMAT", "PFE", "EOG"]


def key_from_env():
    if os.environ.get("ALPHAVANTAGE_API_KEY"):
        return os.environ["ALPHAVANTAGE_API_KEY"]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("ALPHAVANTAGE_API_KEY="):
                return line.split("=", 1)[1].strip()
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="*", default=DEFAULT)
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    key = "demo" if a.demo else key_from_env()
    tickers = ["IBM"] if a.demo else a.tickers
    if not key:
        sys.exit("No ALPHAVANTAGE_API_KEY in .env. Get a free key at alphavantage.co (instant, by email), add the line ALPHAVANTAGE_API_KEY=... to .env, rerun.")
    OUT.mkdir(parents=True, exist_ok=True)
    for t in tickers:
        f = OUT / (t + ".json")
        if f.exists():
            print(t, "already downloaded")
            continue
        url = "https://www.alphavantage.co/query?function=EARNINGS&symbol={}&apikey={}".format(t, key)
        j = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research-script)"}), timeout=60).read())
        if "quarterlyEarnings" not in j:
            print(t, "no data; message:", str(j)[:160])
            if "call frequency" in str(j) or "rate limit" in str(j).lower() or "25 requests" in str(j):
                print("Rate limit reached: rerun tomorrow (finished files are kept).")
                break
            continue
        f.write_text(json.dumps(j), encoding="utf-8")
        q = j["quarterlyEarnings"]
        print("{:5s} {} quarters, {} to {}".format(t, len(q), q[-1]["reportedDate"], q[0]["reportedDate"]))
        time.sleep(1.5)


if __name__ == "__main__":
    main()
