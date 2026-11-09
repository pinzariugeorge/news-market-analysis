"""Add past-only company news from Massive (formerly Polygon) to the records of a family run (alternative to Google News and Finnhub).

Endpoint: GET https://api.massive.com/v2/reference/news?ticker.any_of=A,B,C,D&published_utc.gte=&published_utc.lte=&limit=100 (one call per family and day).
Free plan: about 5 calls a minute (script sleeps 13 s); history found from about 2022. Key: MASSIVE_POLYGON_API_KEY in the project or parent .env (never printed).
Same rules as download_news_finnhub.py: items published before 13:30 UTC on decision day D, from D-1, up to 8 per family, newest first, deduplicated.
Usage: python -I src/download_news_massive.py --run fam_post4 --from-run fam_post2
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
BASE = "https://api.massive.com/v2/reference/news"


def key():
    for env in (ROOT / ".env", ROOT.parent / ".env"):
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if line.startswith("MASSIVE_POLYGON_API_KEY=") and line.split("=", 1)[1].strip():
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def fetch(syms, d0, d1, k):
    q = {"ticker.any_of": ",".join(syms), "published_utc.gte": d0, "published_utc.lte": d1 + "T13:30:00Z", "limit": 100, "order": "desc", "apiKey": k}
    url = BASE + "?" + urllib.parse.urlencode(q)
    for attempt in range(4):
        try:
            res = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sp500-news-sim research script"}), timeout=60).read()).get("results", [])
            return [{"headline": r.get("title"), "datetime": int(dt.datetime.strptime(r["published_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()),
                     "source": (r.get("publisher") or {}).get("name", ""), "related": ",".join(r.get("tickers", [])[:6]), "summary": r.get("description") or ""} for r in res]
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
    ap.add_argument("--run", default="fam_post4")
    ap.add_argument("--from-run", default=None)
    a = ap.parse_args()
    k = key()
    if not k:
        sys.exit("No MASSIVE_POLYGON_API_KEY in .env (project or parent). Create a free key at finnhub.io and add MASSIVE_POLYGON_API_KEY=... to .env.")
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
            try:
                fam_items = fetch(names[fam][:4], (D - dt.timedelta(days=1)).isoformat(), day, k)
            except Exception as e:  # noqa: BLE001
                print(day, fam, "failed", str(e)[:60])
            time.sleep(13)
            for h in pick(fam_items, cutoff, seen):
                h["theme"] = fam
                heads.append(h)
        nf.write_text(json.dumps(heads, indent=1), encoding="utf-8")
        rf = run / "records" / (day + ".json")
        rec = json.loads(rf.read_text(encoding="utf-8"))
        rec["headlines"] = heads
        rec["information_cutoff"] = "closes dated before {}; Massive news published before {} 13:30 UTC".format(day, day)
        rf.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        print(day, len(heads), "items")


if __name__ == "__main__":
    main()
