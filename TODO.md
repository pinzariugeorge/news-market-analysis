# To-do (open items we must not forget)

Last updated: 2026-11-06

## 1. News source for 2000-2007 (pre-2008)
Why: the S&P headlines dataset starts in 2008, but prices go back to 1950. We want news for the dot-com crash, the 2001 attacks, the 2002 lows, the 2003 war and the 2006 midterms so the handbook and agents have informed context. Nothing is downloaded yet. 2020 stays the test year and 2021+ the holdout.

### Options found (2026-11-06)
| Option | Coverage and content | Needs from the user |
|---|---|---|
| NYT Archive API | Headlines and abstracts by month from 1851 (all of 2000-2007, 96 months). General news, not finance-only. Free for non-commercial use; rate limits not verified. Endpoint: `https://api.nytimes.com/svc/archive/v1/<year>/<month>.json?api-key=...` | Create a free key at developer.nytimes.com and put it in `.env` (never in chat). Cache each month locally. |
| HF `Brianferrell787/financial-news-multisource` (https://huggingface.co/datasets/Brianferrell787/financial-news-multisource) | 24 subsets, 57M+ rows, parquet, about 21 GB in total (low-confidence figure). Columns: date, text (title + body), extra_fields (JSON; `date_trading` = next NYSE session open, recommended for backtests). Gated; license "other", non-commercial research only. | Log in to Hugging Face and request access, then token in `.env`. Download only the chosen subsets via `data_files="data/<subset>/*.parquet"`. |
| ABC News Australia (`therohk/million-headlines`) | From about 2003 (start date not verified), general and local, not finance-focused. | Nothing (Kaggle access already works). |

### Relevant HF subsets (ranges are the dataset card's own approximate descriptions; file sizes and row counts could not be seen because the dataset is gated)
- `fnspid_news`: 1999-2023, financial news. Recommended first choice for finance coverage.
- `nyt_headlines_1990_2020`: covers 2000-2007.
- `nyt_articles_2000_present`: 2000-2025.
- `gold_news_kaggle`: 2000-2021.
- `djia_stock_headlines`: card says 2000-2016 (the well-known Kaggle "Daily News for Stock Market Prediction" set is Reddit WorldNews 2008-2016, so verify).
- `benzinga_6000stocks`: "2000s-2010s", undated.
- `bloomberg_reuters`: Bloomberg 2006-2013, Reuters 2007-2013.
- `headlines_10sites_2007_2022`, `finsen_us_2007_2023`: start 2007.
- Not useful for this window: `cnbc_headlines` (2017-2020), `huffpost_news` (2012-2018), `mind_news_2019`, `yahoo_finance_*`, `frontpage_news`, `all_the_news_2`.

### Agreed next actions
- [ ] User picks the source(s). Current recommendation: `fnspid_news` (HF) for finance coverage plus the NYT Archive API for major world events.
- [ ] Download, normalize to `date, decision_date, split, title` like `news_all.csv`, drop any price/outcome columns, apply the next-trading-day timing rule, de-duplicate.
- [ ] Extend `src/build_news_corpus.py` and document the new files in `ROADMAP.md`.
- [ ] Also write a small event calendar for 2000-2007 from general knowledge if news coverage stays thin.

## 2. Handbook work
- [ ] Recompute the base-rate table (section 2 of `handbook/HANDBOOK.md`) on 1950-2019 and by regime (still 2008-2019).
- [ ] More calendar entries: Fed meeting days, earnings seasons, year-end and January patterns, 2008/2012/2016 election detail, crisis episodes (1987, 2000-2002).
- [ ] Test the handbook on the 247 big-move days of 2008-2019 and record hit rates per event type (never on 2020).
- [ ] Design the daily record format (new events, open storylines, past-only market context).

## 3. Other
- [ ] Check why 2020-09-23 has 55 headlines.
- [ ] Push local commits to `origin/main` when the user says so.
- [ ] Choose broker, scheduler and live research source only when we reach paper trading (see `STRATEGY.md`).
