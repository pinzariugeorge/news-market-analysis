"""Check how well candidate headline files cover 2020.

Usage: python3 -I src/inspect_news_candidates.py <csv> [<csv> ...]
Prints columns, total rows, date range, and 2020 rows per month. Reads only; changes nothing.
"""
import csv
import re
import sys
from collections import Counter

csv.field_size_limit(10**8)
DATE_NAMES = ("date", "datetime", "time", "published", "timestamp", "time_published", "publishedat")


def parse_month(s):
    s = (s or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})", s)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r"^(\d{4})(\d{2})\d{2}$", s)          # 20200315
    if m:
        return m.group(1), m.group(2)
    m = re.match(r"^(\d{1,2})-([A-Za-z]{3})-(\d{4})$", s)  # 15-Mar-2020
    if m:
        mon = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"].index(m.group(2).lower()) + 1
        return m.group(3), f"{mon:02d}"
    m = re.match(r"^([A-Za-z]{3}) (\d{1,2}) (\d{4})", s)   # Mar 15 2020
    if m:
        mon = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"].index(m.group(1).lower()) + 1
        return m.group(3), f"{mon:02d}"
    return None


def main(paths):
    for p in paths:
        print("=" * 70)
        print(p)
        with open(p, newline="", encoding="utf-8", errors="replace") as f:
            r = csv.DictReader(f)
            cols = r.fieldnames or []
            print("columns:", cols)
            dcol = next((c for c in cols if c.strip().lower() in DATE_NAMES), None) or \
                   next((c for c in cols if "date" in c.lower() or "time" in c.lower()), None)
            print("date column:", dcol)
            n, months, bad, first, last, sample = 0, Counter(), 0, None, None, None
            for row in r:
                n += 1
                pm = parse_month(row.get(dcol)) if dcol else None
                if pm is None:
                    bad += 1
                    continue
                key = pm[0] + "-" + pm[1]
                first = key if first is None or key < first else first
                last = key if last is None or key > last else last
                if pm[0] == "2020":
                    months[key] += 1
                    if sample is None:
                        sample = row
            print(f"rows: {n}  unparsed dates: {bad}  range: {first} to {last}")
            print("2020 rows per month:", dict(sorted(months.items())))
            print("2020 total:", sum(months.values()))
            if sample:
                print("sample 2020 row:", {k: (v[:90] if isinstance(v, str) else v) for k, v in list(sample.items())[:6]})


if __name__ == "__main__":
    main(sys.argv[1:])
