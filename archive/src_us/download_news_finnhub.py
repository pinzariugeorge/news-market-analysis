"""Add past-only company news from Finnhub to the records of a family run (replaces the Google News headlines).

Why this endpoint: Finnhub's Market News (`/news?category=...`) has no date parameters (latest items only), so it cannot be used for a backtest. Company News
(`/company-news?symbol=&from=&to=`) takes a date range; free tier = 1 year of history, North American companies only (docs: finnhub.io/docs/api/company-news).
Key: FINNHUB_API_KEY in the project .env or the parent .env (never printed). Create a free key at finnhub.io and add the line `FINNHUB_API_KEY=...`.

Usage: python -I src/download_news_finnhub.py --run fam_post3 --from-run fam_post2
  --from-run copies days.json and the records of an existing run (headlines removed) into results/<run>/ so the same decision days can be re-run with the new news source.
For each decision day D and each family it takes the family's four point-in-time names, asks for news dated D-1..D, keeps items published before 13:30 UTC on D
(US open on D during daylight time; earlier when the clocks are on winter time, so this errs on the side of being past-only), and stores up to 8 items per family
(newest first, deduplicated by headline): headline, source, published time (UTC), related tickers, and the first 160 characters of the summary. Writes "headlines" in
results/<run>/records/<D>.json and a copy in results/<run>/news/<D>.json. Rate limit: free plan 60 calls a minute; the script sleeps 1.1 s between calls. Resumable.
"""
import argparse
import datetime as dt
import json
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import familydata as fd  # noqa: E402

PER_FAMILY = 8


def key():
    for env in (ROOT / ".env", ROOT.parent / ".env"):
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if line.startswith("FINNHUB_API_KEY=") and line.split("=", 1)[1].strip():
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def fetch(sym, d0, d1, k):
    url = "https://finnhub.io/api/v1/company-news?" + urllib.parse.urlencode({"symbol": sym, "from": d0, "to": d1, "token": k})
    for attempt in range(3):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sp500-news-sim research script"}), timeout=60).read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(30)
                continue
            raise
    return []


def pick(items, cutoff_ts, seen):
    out = []
    for it in sorted(items, key=lambda x: x.get("datetime", 0), reverse=True):
        h = (it.get("headline") or "").strip()
        if not h or it.get("datetime", 0) >= cutoff_ts or h.lower()[:80] in seen:
            continue
        seen.add(h.lower()[:80])
        out.append({"title": h, "source": it.get("source", ""), "published_utc": dt.datetime.fromtimestamp(it["datetime"], dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
                    "related": it.get("related", ""), "summary": (it.get("summary") or "")[:160]})
        if len(out) >= PER_FAMILY:
            break
    return out


def selftest():
    items = [{"headline": "A beats", "datetime": 1000, "source": "X", "related": "XOM", "summary": "s" * 300},
             {"headline": "A beats", "datetime": 900, "source": "Y"}, {"headline": "late", "datetime": 5000}, {"headline": "B cut", "datetime": 800}]
    got = pick(items, 2000, set())
    assert [g["title"] for g in got] == ["A beats", "B cut"] and len(got[0]["summary"]) == 160, got
    print("selftest ok")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="fam_post3")
    ap.add_argument("--from-run", default=None)
    a = ap.parse_args()
    k = key()
    if not k:
        sys.exit("No FINNHUB_API_KEY in .env (project or parent). Create a free key at finnhub.io and add FINNHUB_API_KEY=... to .env.")
    run = ROOT / "results" / a.run
    if a.from_run:
        src = ROOT / "results" / a.from_run
        (run / "records").mkdir(parents=True, exist_ok=True)
        shutil.copy(src / "days.json", run / "days.json")
        for f in (src / "records").glob("*.json"):
            rec = json.loads(f.read_text(encoding="utf-8"))
            rec.pop("headlines", None)
            (run / "records" / f.name).write_text(json.dumps(rec, indent=1), encoding="utf-8")
    (run / "news").mkdir(exist_ok=True)
    sel = fd.selections()
    for day in json.loads((run / "days.json").read_text(encoding="utf-8")):
        nf = run / "news" / (day + ".json")
        if nf.exists():
            continue
        D = dt.date.fromisoformat(day)
        cutoff = int(dt.datetime(D.year, D.month, D.day, 13, 30, tzinfo=dt.timezone.utc).timestamp())
        names = fd.names_at(sel, day)
        heads, seen = [], set()
        for fam in fd.FAMILIES:
            fam_items = []
            for sym in names[fam][:4]:
                try:
                    fam_items += fetch(sym, (D - dt.timedelta(days=1)).isoformat(), day, k)
                except Exception as e:  # noqa: BLE001
                    print(day, sym, "failed", str(e)[:60])
                time.sleep(1.1)
            for h in pick(fam_items, cutoff, seen):
                h["theme"] = fam
                heads.append(h)
        nf.write_text(json.dumps(heads, indent=1), encoding="utf-8")
        rf = run / "records" / (day + ".json")
        rec = json.loads(rf.read_text(encoding="utf-8"))
        rec["headlines"] = heads
        rec["information_cutoff"] = "closes dated before {}; company news published before {} 13:30 UTC".format(day, day)
        rf.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        print(day, len(heads), "items")


if __name__ == "__main__":
    main()
