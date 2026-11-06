"""Point-in-time universe selection: pick the top N names per family using only data before a given date.

Usage: python -I src/select_universe.py [--asof 2022-12-31 2023-12-31 ...] [--top 4]
Reads universe/candidates.csv (family,ticker). Downloads 10 years of daily bars from Yahoo (standard library only).
Rule (v2): for each family and as-of date D, use only bars dated before D; a name is eligible if it has at least 250 bars
before D; rank eligible names by the MEDIAN daily dollar volume (close x volume) over the last 250 bars (robust to
one-day spikes); take the top N. Performance (returns) is never used.
Writes universe/rule_selections.csv (asof, family, rank, ticker, median_dollar_volume) and prints the sets and turnover.
Limitation: candidates are today's list; names that delisted and are missing from Yahoo cannot appear in past selections
(survivorship bias). Mitigation: add acquired or delisted candidates when Yahoo still serves them.
"""
import argparse
import csv
import datetime as dt
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import build_universe as bu  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", nargs="*", default=["2021-12-31", "2022-12-31", "2023-12-31", "2024-12-31", "2025-12-31"])
    ap.add_argument("--top", type=int, default=4)
    a = ap.parse_args()
    today = dt.date.today().isoformat()
    asofs = list(a.asof) + [today]
    cands = list(csv.DictReader(open(ROOT / "universe" / "candidates.csv", encoding="utf-8")))
    bars = {}
    for r in cands:
        t = r["ticker"]
        try:
            _, b = bu.fetch(t, "10y")
            bars[t] = b
        except Exception as e:  # noqa: BLE001
            print("skip", t, repr(e)[:50])
    rows, sets = [], {}
    for d in asofs:
        for fam in sorted({r["family"] for r in cands}):
            ranked = []
            for r in cands:
                if r["family"] != fam or r["ticker"] not in bars:
                    continue
                past = [x for x in bars[r["ticker"]] if x[0] < d]
                if len(past) < 250:
                    continue
                last = past[-250:]
                ranked.append((st.median(x[1] * x[2] for x in last), r["ticker"]))
            ranked.sort(reverse=True)
            for k, (v, t) in enumerate(ranked[: a.top], 1):
                rows.append({"asof": d, "family": fam, "rank": k, "ticker": t, "median_dollar_volume": round(v)})
            sets[(d, fam)] = [t for _, t in ranked[: a.top]]
    with open(ROOT / "universe" / "rule_selections.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["asof", "family", "rank", "ticker", "median_dollar_volume"])
        w.writeheader()
        w.writerows(rows)
    fams = sorted({r["family"] for r in cands})
    for fam in fams:
        print("\n" + fam)
        prev = None
        for d in asofs:
            s = sets[(d, fam)]
            ch = "" if prev is None else "  changes: " + (", ".join(sorted(set(s) ^ set(prev))) or "none")
            print("  {}: {}{}".format(d, ", ".join(s), ch))
            prev = s


if __name__ == "__main__":
    main()
