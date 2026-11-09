"""Feasibility probe for running the paper trading jobs in Claude Code's cloud: can this machine reach the public data sources the jobs need? Research only.
Prints one line per source: HTTP status and a tiny sample. No keys, no secrets. Run: python -I src/cloud_probe.py
"""
import json
import time
import urllib.request

TESTS = [
    ("yahoo chart 5m (SHEL.L)", "https://query1.finance.yahoo.com/v8/finance/chart/SHEL.L?range=1d&interval=5m"),
    ("yahoo chart daily (ASML.AS)", "https://query1.finance.yahoo.com/v8/finance/chart/ASML.AS?range=5d&interval=1d"),
    ("yahoo fx (GBPEUR=X)", "https://query1.finance.yahoo.com/v8/finance/chart/GBPEUR=X?range=5d&interval=1d"),
    ("google news rss", "https://news.google.com/rss/search?q=oil+price+when:1d&hl=en-GB&gl=GB&ceid=GB:en"),
    ("ntfy health", "https://ntfy.sh/v1/health"),
]


def main():
    for name, url in TESTS:
        t0 = time.time()
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20)
            body = r.read()
            extra = ""
            if "yahoo" in url:
                d = json.loads(body)["chart"]["result"][0]
                extra = "bars={} last={}".format(len(d.get("timestamp", [])), d["meta"].get("regularMarketPrice"))
            elif "rss" in url:
                extra = "items={}".format(body.count(b"<item>"))
            print("OK   {:30s} http {} {:.1f}s {}".format(name, r.status, time.time() - t0, extra))
        except Exception as e:  # noqa: BLE001
            print("FAIL {:30s} {}".format(name, str(e)[:120]))


if __name__ == "__main__":
    main()
