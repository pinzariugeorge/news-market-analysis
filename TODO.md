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
- [x] Pilot v0 done: 12 decisions via Sonnet subagents; about 67k tokens per decision (about 0.8M tokens for 12), so 3,000 days (about 200M) is not feasible on the subscription and even 300 days is about 20M. See PROGRESS_LOG.
- [ ] Cut the cost per decision: a smaller handbook extract per day, chronological multi-day runs in one session (the agent keeps the handbook in context and learns day by day, like live), and fewer days. Pick one and re-measure.
- [ ] Decide the test design from that: sampled days (all big-move days plus a few hundred random days) over several sessions, and/or a rule-based Python version of the handbook for all days with the model only reading headlines on sampled days.
- [ ] Live phase: one decision a day as a scheduled Claude Code routine on the subscription (no API); check plan limits first.

- [ ] API cost estimate (asked 2026-11-06, not adopted; prices from the Claude API skill cache dated 2026-10-06, check the pricing page before relying on them): about 9k input and 3k output tokens per decision called directly. Per decision about $0.002 Haiku 5.5, $0.05 Sonnet 5.5, $0.10 Opus 5.5, $0.24 Fable 5.1; batch API is half. Examples with Sonnet 5.5: 300 days about $14 (about $7 batch), all 3,020 dev days about $145 (about $72 batch), a year of live daily decisions about $12. The usage numbers are assumptions, not measured.

## 3a. Plan v2 next actions (see `PLAN.md`)
- [x] Families: five (solar removed); single stocks only; names chosen by a point-in-time rule (`universe/UNIVERSE_RULE.md`); holding period capped at 20 days.
- [ ] User still to give: account size to design for and allowed instruments (US single stocks assumed); add a market value screen and a revenue-purity screen when a reliable data source is chosen; verify tradability of the selected names at IBKR Ireland.
- [x] Phase 1 part 1 (2026-11-06): `src/costs.py` written and `PHASE1_FACTS.md` (official US stock fees verified; tax from Romanian press).
- [x] Baselines on the universe for a 500 USD account (`results/UNIVERSE_BASELINES.md`): noise dominates with two positions; no strategy consistent; 5-day holds cost up to 17% of the account in fees.
- [ ] Next: judge strategies on many decisions (all 20 names in parallel as a paper portfolio, each decision scored separately), add event windows and calendar data, then the agent with the same costs.
- [x] eToro fees and API researched (`PHASE1_FACTS.md`): 1 USD per stock open and close, ETFs free, API free for eligible users; eligibility for Romania, conversion fee and rate limits still open; some stock buys can be executed as CFDs.
- [ ] Phase 1 part 2, open: third-party fee amounts (collapsed IBKR section), currency conversion cost, paper account and API access, US stocks permission for Romanian retail clients, US dividend withholding and W-8BEN, CASS thresholds. Best done in the IBKR application flow and with an accountant.
- [ ] Phase 2: history for chosen names and drivers (2000 onward), scheduled calendars (earnings, EIA, OPEC, FOMC), company-level news source.

## 3b. Universe and company-level work (new direction, 2026-11-06)
- [x] First research list: solar value chain with current metrics (`universe/UNIVERSE.md`).
- [ ] Confirm themes besides solar with the user (lithium, copper, semiconductors, uranium, oil services, ...).
- [ ] Check each candidate: tradable and fee schedule at the chosen broker, status of the company (bankruptcies, delistings), earnings dates.
- [ ] Source company-level news and earnings dates (Benzinga stock-news Kaggle dataset, `fnspid_news` subset, or a current news source) and component price series (polysilicon index, silver, etc.).
- [ ] Extend the handbook with company-level entries (earnings reaction, guidance, tariff and policy news, component price moves) using history only.
- [ ] Rerun baselines on the new universe with realistic fixed fees for 500 EUR and 5,000 EUR accounts; redo the agent pilot on single names.

## 4. Other
- [ ] Check why 2020-09-23 has 55 headlines.
- [ ] Push local commits to `origin/main` when the user says so.
- [ ] Choose broker, scheduler and live research source only when we reach paper trading (see `STRATEGY.md`).
