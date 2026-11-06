"""Build the news corpus (all years) from the S&P headlines dataset.

Usage: python -I src/build_news_corpus.py
Reads  data/raw/candidates/sp500_headlines/sp500_headlines_2008_2024.csv
       data/raw/sp500_2008_2024_daily.csv
Writes data/processed/news_all.csv  : date, decision_date, split, title
       data/processed/market_days.csv: date, close, ret_pct, split   (ret_pct = close-to-close vs previous day)
Drops CP (S&P close = outcome leak), fixes mojibake, removes exact duplicates (same date + normalized title).
decision_date = next trading day strictly after date (headline may be published after the close); empty if none.
split: handbook = 2008-2019, test = 2020, holdout = 2021 onward.
"""
import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw" / "candidates" / "sp500_headlines" / "sp500_headlines_2008_2024.csv"
PRICES = ROOT / "data" / "raw" / "sp500_2008_2024_daily.csv"
OUT_NEWS = ROOT / "data" / "processed" / "news_all.csv"
OUT_DAYS = ROOT / "data" / "processed" / "market_days.csv"


def split_of(date):
    y = int(date[:4])
    return "handbook" if y <= 2019 else "test" if y == 2020 else "holdout"


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", t.lower())).strip()


def fix_mojibake(t):
    """Source has UTF-8 text mis-decoded as cp1252 (e.g. 'â€™'); undo it when possible."""
    try:
        return t.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return t


def main():
    with open(PRICES, newline="", encoding="utf-8") as f:
        px = [(r["Date"][:10], float(r["Close"])) for r in csv.DictReader(f)]
    px.sort()
    trading_list = [d for d, _ in px]
    trading = set(trading_list)

    import bisect

    def next_trading_day(d):
        i = bisect.bisect_right(trading_list, d)
        return trading_list[i] if i < len(trading_list) else ""

    seen, rows, dupes = set(), [], 0
    csv.field_size_limit(10**8)
    with open(SRC, newline="", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            date = (r.get("Date") or "").strip()
            title = fix_mojibake((r.get("Title") or "").strip())
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", date) or not title:
                continue
            key = (date, norm(title))
            if key in seen:
                dupes += 1
                continue
            seen.add(key)
            rows.append((date, title))
    rows.sort(key=lambda x: x[0])

    OUT_NEWS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_NEWS, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "decision_date", "split", "title"])
        w.writerows((d, next_trading_day(d), split_of(d), t) for d, t in rows)

    with open(OUT_DAYS, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "close", "ret_pct", "split"])
        for i, (d, c) in enumerate(px):
            ret = "" if i == 0 else f"{(c / px[i - 1][1] - 1) * 100:.2f}"
            w.writerow([d, f"{c:.2f}", ret, split_of(d)])

    print(f"{len(rows)} headlines ({dupes} duplicates removed) -> {OUT_NEWS}")
    print("per split:", dict(Counter(split_of(d) for d, _ in rows)))
    print("no decision day:", sum(1 for d, _ in rows if not next_trading_day(d)))
    print("headlines on non-trading days:", sum(1 for d, _ in rows if d not in trading))
    print(f"market days: {len(px)} -> {OUT_DAYS}")


if __name__ == "__main__":
    main()
