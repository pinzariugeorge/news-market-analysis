"""Add past-only news headlines (Google News RSS search with date filters, free, no key) to the records of a family run.

Usage: python -I src/download_news.py --run fam_post
For each decision day D in results/<run>/days.json it asks six theme queries (market, oil and gas, gold, chips, pharma, copper and uranium) restricted to
after:D-1 before:D+1 and keeps only items whose publication time is earlier than D 12:00 GMT (before the US open on D), top 8 titles per theme, title and source only
(no article text, no links). Writes them under "headlines" in results/<run>/records/<D>.json and a copy in results/<run>/news/<D>.json. Resumable.
Limits: the feed gives day-level dates (many items are stamped 07:00 GMT), so the cutoff is approximate; coverage is thin for narrow queries.
(GDELT was tried first and refused with HTTP 429.)
"""
import argparse
import datetime as dt
import email.utils
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES = {
    "market": '(stocks OR "Wall Street" OR "Federal Reserve" OR tariffs OR inflation OR "Treasury yields")',
    "oil_gas": '("crude oil" OR OPEC OR "oil prices" OR "natural gas" OR Exxon OR Chevron)',
    "gold_miners": '("gold price" OR "gold miners" OR Newmont OR "central bank gold")',
    "chips": '(semiconductor OR Nvidia OR TSMC OR "chip export" OR AMD OR Micron)',
    "pharma": '(FDA OR "drug prices" OR "Eli Lilly" OR Pfizer OR Merck OR Medicare)',
    "copper_uranium": '(copper OR uranium OR Freeport OR Cameco)',
}


def fetch(query, d0, d1):
    q = "{} after:{} before:{}".format(query, d0, d1)
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"})
    txt = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", errors="replace")
    out = []
    for block in re.findall(r"<item>(.*?)</item>", txt, re.S):
        t = re.search(r"<title>(.*?)</title>", block, re.S)
        p = re.search(r"<pubDate>(.*?)</pubDate>", block, re.S)
        if not t or not p:
            continue
        title = re.sub(r"&amp;", "&", re.sub(r"&#39;|&apos;", "'", re.sub(r"&quot;", '"', t.group(1)))).strip()
        src = title.rsplit(" - ", 1)[1] if " - " in title else ""
        out.append((email.utils.parsedate_to_datetime(p.group(1)), title.rsplit(" - ", 1)[0], src))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="fam_post")
    a = ap.parse_args()
    run = ROOT / "results" / a.run
    (run / "news").mkdir(exist_ok=True)
    for day in json.loads((run / "days.json").read_text(encoding="utf-8")):
        nf = run / "news" / (day + ".json")
        if nf.exists():
            continue
        D = dt.date.fromisoformat(day)
        cutoff = dt.datetime(D.year, D.month, D.day, 12, 0, tzinfo=dt.timezone.utc)
        heads, seen = [], set()
        for theme, q in THEMES.items():
            try:
                items = fetch(q, (D - dt.timedelta(days=1)).isoformat(), (D + dt.timedelta(days=1)).isoformat())
            except Exception as e:  # noqa: BLE001
                print(day, theme, "failed", str(e)[:60])
                items = []
            time.sleep(2)
            n = 0
            for pub, title, src in sorted(items, key=lambda x: x[0], reverse=True):
                if pub >= cutoff or title.lower()[:80] in seen:
                    continue
                seen.add(title.lower()[:80])
                heads.append({"theme": theme, "title": title, "source": src, "published_utc": pub.strftime("%Y-%m-%d %H:%M")})
                n += 1
                if n >= 8:
                    break
        nf.write_text(json.dumps(heads, indent=1), encoding="utf-8")
        rf = run / "records" / (day + ".json")
        rec = json.loads(rf.read_text(encoding="utf-8"))
        rec["headlines"] = heads
        rec["information_cutoff"] = "closes dated before {}; headlines published before {} 12:00 GMT".format(day, day)
        rf.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        print(day, len(heads), "headlines")


if __name__ == "__main__":
    main()
