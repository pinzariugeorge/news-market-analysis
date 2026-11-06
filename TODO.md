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
- [x] Base-rate table recomputed on 1950-2019 and by volatility regime (2026-11-06); calendar patterns added as 3.15, volatility regime as 3.16.
- [ ] More calendar entries still open: Fed meeting days (needs the FOMC date list), earnings seasons, quarter-end and options expiration, holidays, 2008/2012/2016 election detail, crisis episodes (1987, 2000-2002).
- [x] Reviewed the 247 big-move days of 2008-2019 by event type (`handbook/BIGDAY_REVIEW.md`); ranges updated. Still open: a true predictive test (news before day D vs move on D).
- [ ] Better causal news source: the S&P headlines name a cause on fewer than 1 in 4 big days. Candidates are in section 1, plus event calendars (FOMC, jobs report, CPI dates).
- [x] Daily record format, agent prompt v0, decision log and storylines template written (`agent/`); `src/build_daily_context.py` builds the past-only record (leak check passed).
- [ ] Build the simulation harness: loop over days, call the agent (subagents or API, decide later), store decisions, reveal outcomes, score vs baselines. Baselines on 2008-2019 are done (`results/BASELINES.md`).

## 3. Simulation harness and model use (no extra API cost planned)
- [ ] Run a 20-30 day pilot of the agent as subagents inside Claude Code (uses the Pro subscription, not the API) to measure how much usage one decision takes.
- [ ] Decide the test design from that: sampled days (all big-move days plus a few hundred random days) over several sessions, and/or a rule-based Python version of the handbook for all days with the model only reading headlines on sampled days.
- [ ] Live phase: one decision a day as a scheduled Claude Code routine on the subscription (no API); check plan limits first.

## 4. Other
- [ ] Check why 2020-09-23 has 55 headlines.
- [ ] Push local commits to `origin/main` when the user says so.
- [ ] Choose broker, scheduler and live research source only when we reach paper trading (see `STRATEGY.md`).
