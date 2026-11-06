# Progress Log

Newest entry at the bottom. Each session: read STRATEGY.md and this file first; at the end, add an entry with what was done and the exact next step.

## 2026-11-05 - Session 1
- DONE (step 1): project folder structure, README, STRATEGY, PROGRESS_LOG, JOURNAL, .env.example, .gitignore.
- DONE (step 2): `src/download_prices.py` and `data/raw/sp500_2020_daily.csv` (253 rows, Yahoo). Verified: first close 3257.85 on 2020-01-02, last 3756.07 on 2020-12-31, low 2237.40 on 2020-03-23, dates sorted and unique, no gaps in values. Needed the user to turn on network egress in account settings first.
- Kaggle login: the user created a token and saved it on their laptop in `D:\Projects\Marketing\news-market-analysis\.env` under the name `KAGLE_API_TOKEN` (typo). Only that one file was copied into this workspace, with the name corrected to `KAGGLE_API_TOKEN`, as `.env` here (permissions 600, git-ignored). The token value has never been printed. Dataset downloads from Kaggle work. The user's own copy still has the typo (left untouched).
- Downloaded four small candidate headline datasets to `data/raw/candidates/` and checked 2020 coverage with `src/inspect_news_candidates.py`:
  - `dyutidasmahaptra/s-and-p-500-with-financial-news-headlines-20082024`: 2008 to 2024, 1519 headlines in 2020, covers 249 of 253 trading days (median 5 per day, 15 to 32 on the big March days). Has a `CP` column which is the S&P close for that date: MUST be dropped before any agent sees the data (outcome leak).
  - `notlucasp/financial-news-headlines`: Reuters file has 9214 rows in 2020 with descriptions but stops in July 2020. CNBC (573 rows) and Guardian (4080 rows) are 2017 to July 2020 with other date formats (not yet parsed).
  - `therohk/million-headlines` (ABC News Australia): full year 2020, 40240 general headlines, no description, mostly local Australian news, not finance-focused.
  - `belbino/financial-news-sentiment-vs-market-2020-present`: only 2 rows in 2020, not usable.
- Not downloaded: `miguelaenlle/massive-stock-news-analysis-db-for-nlpbacktests` (220 MB, Benzinga, ends mid 2020).
- Not done yet: any filtering, de-duplication or model summarizing (needs a decision and an ANTHROPIC_API_KEY, see below).

**Next step:** user decides which news sources to use for the 2020 pilot (recommended: S&P headlines dataset as the full-year finance backbone, plus Reuters for Jan to Jul 2020 detail, plus ABC for global and local color; drop the `CP` column on load). Then (1) write `src/build_news_corpus.py` to load, normalize dates, drop outcome columns, de-duplicate with cheap rules and keep only macro-relevant items, saving to `data/processed/`; (2) before any paid model call, ask the user for approval and an `ANTHROPIC_API_KEY` in `.env`, and give a cost estimate first.

## 2026-11-06 - Handoff to local run
- The user wants the project to run on their own laptop (Windows) instead of this cloud workspace. A copy of the project (docs, scripts, 2020 prices) was placed in `D:\Projects\Marketing\news-market-analysis\sp500-news-sim\`. The `.env` was NOT copied (the user's own `.env` in `D:\Projects\Marketing\news-market-analysis\` holds the Kaggle token, saved under the misspelled name `KAGLE_API_TOKEN`; it must be renamed to `KAGGLE_API_TOKEN`).
- The Kaggle candidate datasets were NOT copied (about 100 MB); re-download them locally from the Kaggle refs listed in the 2026-11-05 entry.
- Windows notes: use `python` instead of `python3` (for example `python -I src\download_prices.py`). Scripts use only the standard library so far; check for the user's `requirements.txt` before installing anything.
- The local session should open the `sp500-news-sim` folder, read STRATEGY.md and this log first, then continue from the Next step of the 2026-11-05 entry.

## 2026-11-06 - Session 2 (local, Windows)
- DECISION: use the S&P headlines dataset only (Reuters and ABC dropped for now). Recorded in STRATEGY.md.
- DONE: installed `kaggle` and `kagglehub`. The `kaggle` CLI (1.7.4.5) fails with the new-style token (KeyError 'username'); `kagglehub.dataset_download(..., output_dir=...)` works with `KAGGLE_API_TOKEN` in the environment. `.env` copied into this project (git-ignored).
- DONE: downloaded `data/raw/candidates/sp500_headlines/sp500_headlines_2008_2024.csv` (19,127 rows; columns Title, Date, CP).
- DONE: `src/build_news_corpus.py` -> `data/processed/news_2020.csv` (columns date, title). Drops `CP`, keeps 2020, fixes cp1252 mojibake in titles, removes 5 exact duplicates: 1,514 headlines on 249 of 253 trading days, none on non-trading days. Busiest days: 2020-09-23 (55), 2020-03-09 (32), 2020-03-12 (25).

- DECISION: timing rule = headline dated D is used for the next trading day's decision. `build_news_corpus.py` now adds a `decision_date` column (recorded in STRATEGY.md).

- DECISION: build a handbook of event-to-market effects from multiple years; no anonymization (see STRATEGY.md).
- DONE: `src/download_prices_all.py` -> `data/raw/sp500_2008_2024_daily.csv` (4,110 rows, 2008-01-02 to 2024-04-30). Headlines per year in the dataset: 2008 141, 2009 113, 2010 209, 2011 547, 2012-2018 about 700-860, 2019 1848, 2020 1519, 2021 1303, 2022 2319, 2023 4760, 2024 833 (thin early years).

- DECISION: handbook years = 2008-2019; 2020 = test; 2021-2024 = holdout.
- DONE: `build_news_corpus.py` now covers all years -> `data/processed/news_all.csv` (18,149 headlines: handbook 7,445 / test 1,514 / holdout 9,190; columns date, decision_date, split, title) and `data/processed/market_days.csv` (4,110 days with close and daily % return). `news_2020.csv` is superseded by `news_all.csv`. Handbook split has 247 days with |move| >= 2%; biggest are Oct-Dec 2008 and 2011-08-08.

- DONE: git repo set up and pushed to origin/main (remote's stub README merged, ours kept). Added `ROADMAP.md` (file map) and `CLAUDE.md` (standing rule: keep context files current in the same change). Parent-folder `context\` notes are from an older GDELT/correlation framing and are not authoritative.

**Next step:** draft handbook v0 in `handbook/` (one entry per event type, fields: mechanism, magnitude, horizon, amplifiers, dampeners, sectors, index effect, confidence, no-effect base rate), from general finance knowledge, then check and refine it against the 2008-2019 big-move days and their headlines (never 2020). Also check why 2020-09-23 has 55 headlines.

## 2026-11-06 - Session 2 (continued): handbook v0
- DONE: `handbook/HANDBOOK.md` v0 (principles, base rates from 3,020 handbook-period days, 14 event-type entries, agent usage steps). Checked against 2008-2019 big-move days only. Base rates: daily sd 1.23%, up days 53.9%, |move|>=2% on 8.2% of days; volatility clusters (mean |move| 1.49% after a 2%+ day vs 0.78%); after a 2%+ drop next day up 58%, after a 2%+ rise 49%.
- FINDING: many headlines in the dataset are market recaps ("Dow plunges..."), not causes, so the news layer is thin on explicit causes. The handbook tells agents to ignore recap-only headlines.
- DONE: ROADMAP.md updated with the handbook folder.

- DECISION: end goal is a live trading agent using the handbook to make profitable trades (not "beat the S&P"; baselines still used to judge it). Phases: research -> simulation (2020, then 2021-2024) -> paper -> live. Selectively adopted file-memory loop, guardrails, weekly self-review, decision log, test-before-trust from the analyzed video; recorded in STRATEGY.md.

- DECISION: long-run goal (years of trading days, as profitable as possible), judged over many months and regimes, not 30 days. Calendar events (midterms, Fed meetings, earnings seasons) get handbook entries.
- DONE: handbook entry 3.6b (US midterms) with web research (`handbook/SOURCES.md`) and our own check on 2010/2014/2018: day after the vote +0.37%, +0.57%, +2.12%; 1 year later +2.1%, +4.5%, +12.0%. Finding: after midterms the market has mostly risen, not fallen; 2018 shows a Fed-driven slide can override the post-election bounce. Only 3 cases in the handbook period; 2022 midterm is in the holdout and was not used.
- TODO: more calendar entries (Fed meeting days, earnings seasons, presidential elections 2008/2012/2016, year-end and January patterns).

- DECISION: go further back than 2008 (2008 was only the headlines dataset start). Prices downloaded back to 1950 (18,702 days); `market_days.csv` and `build_news_corpus.py` now use them. News before 2008 not available yet.
- DONE: handbook 3.6b rewritten with all 13 midterms 1970-2018 (day after: mean +0.57%, up 77%; +6 months and +1 year positive in 13 of 13, mean about +13%); new 3.6c presidential elections (9 cases: day after mean -0.84%, +1 year mean +12.6%). Pre-1970 and some 1972-1980 election days were market holidays, so they are missing.
- NOTE: handbook base-rate table (section 2) is still 2008-2019; recompute for 1950-2019 and by regime.

- DONE: handbook section 2 recomputed on 1950-2019 (daily sd 0.96%, up 52.8%, |move|>=2% on 4.3% of days; 1990-2019: sd 1.10%, 6.4%). Corrected an earlier finding: after a 2%+ drop the next day is up 55% and after a 2%+ rise 56% over the long sample, so no direction signal (the 58%/49% from 2008-2019 did not hold). Volatility predicts size, not direction.
- DONE: handbook 3.15 calendar patterns (months, Santa window +1.35% in 78% of years, turn of month, day of week fading since 1990) and 3.16 volatility regime.
- Old-news source work postponed by the user ("another day"); it stays in TODO.md.

- DONE: big-day review. `src/review_big_days.py` labeled all 247 days with a move of 2% or more (2008-2019) by event type -> `handbook/bigday_review.csv`, `handbook/BIGDAY_REVIEW.md`. Findings: 74% of big days sit in 2008, 2009, 2011, 2018; 79% are within a week of another; 34% have no same-day headline and only 24% have a headline naming a cause; credit/banking/sovereign stress is 49% of big days (range -9.0% to +11.6%). Handbook updated: wider ranges (credit, data in recession, elections), new principle 12 (clusters), new section 5. Labels were made with hindsight; this is not a prediction test.

- DONE: agent design v0. `agent/DAILY_RECORD.md`, `agent/AGENT_PROMPT.md`, `agent/DECISION_LOG.md`, `agent/state/storylines.md`, and `src/build_daily_context.py` (past-only daily record: market state, volatility regime, calendar, headlines with decision_date == D). Leak check: the record is identical when all prices on or after D are removed. Decision: index only, long/flat, provisional guardrails, five baselines, headline ablation, phases dev -> freeze -> test 2020 -> holdout 2021-2024 -> paper -> live.

- DECISION: no Anthropic API. Simulation uses subagents inside Claude Code on the user's Pro subscription (usage limits apply, so test on a sample, not all 3,000 days), plus an optional rule-based Python version of the handbook; the live phase uses one daily Claude Code routine on the subscription. A pilot will measure usage per decision. (The API is a separate pay-per-token service; the user does not want it.)
- DONE: baselines on 2008-2019 (`src/run_baselines.py`, `results/BASELINES.md`). Buy and hold 6.8% a year, Sharpe 0.43, max drawdown -54%; volatility rule 7.3%, Sharpe 0.66, drawdown -27%; capped long 7.4%, Sharpe 0.57; 200-day trend 5.8%, Sharpe 0.57, drawdown -17%; random with the same exposure 5.0% (5th-95th percentile 2.2% to 8.0%). The agent must beat these after costs.

- DONE: pilot v0 (`results/pilot_v0/`). 12 days from 2008-2019 (4 big-move, 3 calm, 3 stormy, 1 normal, 1 event = 2010 midterm day after), each decided by an independent Sonnet subagent that read only AGENT_PROMPT.md, HANDBOOK.md and its record (5 tool calls each; I cannot fully verify it read nothing else). Format worked: all 12 returned valid JSON. Result: 8 of 12 no-edge/flat, 4 long calls (2 right, 2 wrong), average confidence 0.54, expected range contained the outcome on 10 of 12 days. Agent return -0.62% summed vs -0.11% buy and hold and -0.35% volatility rule on the same days. Sample far too small to say anything about skill. Behavior: stayed flat in stormy regimes (avoided -3.45% on 2008-10-24) but also missed +2.13% and +2.33% rebound days; long calls on calm days lost on 2014-01-24 (-2.09%) and 2016-12-21 (-0.25%).
- COST FINDING: about 67k tokens per decision (subagent overhead plus about 5.5k handbook tokens), about 0.8M for 12. At that rate 3,000 days is about 200M tokens: not possible on Pro. Options in TODO.md.
- DONE: scoring and dashboard. `src/score_decisions.py` (outcomes joined after decisions; each pilot day independent, cost 0.02% x size) and `src/build_dashboard.py` -> `results/dashboard.html` (self-contained; 3 charts, 9 KPIs, table with reasoning; checked in the built-in browser: renders, no console errors).

- DECISION (user): the S&P 500 was for learning; the goal is to trade current companies and commodities, chosen by theme and supply chain (example: solar, via component costs such as polysilicon and silver). Recorded in STRATEGY.md.
- DONE: broker research (Interactive Brokers Ireland most mature API and the only clearly documented route for an individual in Romania; Trading 212 API in beta; eToro public API exists, availability by country unconfirmed; XTB discontinued its API on 2025-03-14; Alpaca Europe looks B2B; Saxo has OpenAPI, live retail access unconfirmed). Fee finding: a 3 EUR fixed fee is 0.6% of a 500 EUR order, so my earlier baselines (0.02% per change, about 3 EUR on 15,000 EUR) were too optimistic for small accounts.
- DONE: `src/build_universe.py` and `universe/` (solar chain, 17 tickers, data to 2026-11-05/06). Findings: solar names move 3-7% a day with 47-84% drawdowns inside a year and 11 of 14 stocks down over the year; liquidity ranges from 5M to 470M dollars a day.

- DONE: broad screen (`universe/BROAD_SCREEN.md`, 60 tickers: sector and theme ETFs, 11 commodity futures, 27 single stocks) and driver study. Findings: last month was a sharp pullback (Nasdaq 100 -14.6%, semiconductors -28%); leaders over 3-6 months were health care, oil and energy, defensives; commodity-linked stocks follow their commodity on the same day (gold -> miners R-squared 0.5-0.6, oil -> energy 0.3-0.4) but yesterday's driver move has about zero predictive power (lead correlation -0.06 to +0.06), and cost-side links are weak (jet fuel -> airlines 0.07, silver -> solar 0.06).
- DONE: `PLAN.md` (plan v2): IBKR Ireland, theme families, phases 1-6 with gates, new time split for single names, costs inside every test, event-driven decisions. US single stocks on IBKR tiered pricing cost about 0.07% per 500 USD order versus 0.6% for a 3 EUR fixed fee on EU-listed products; futures and currency fee details unconfirmed.

- DONE: holding-horizon test (universe/BROAD_SCREEN.md): over 1, 3, 5, 10, 20 days a trailing-momentum rule did not beat always holding; costs make 1-5 day holds unprofitable net of fees on small orders; bigger movement did not mean more profit (solar moves most, earned nothing; chips earned most, but names were chosen with hindsight). Supports making the holding horizon a tested parameter and favoring days-to-weeks holds and event windows.

- DONE: AI theme check (universe/BROAD_SCREEN.md): chips fell 22-40% in a month, correlated 0.61 among themselves, basket max drawdown -50% over 5 years; longer holds (10-20 days) beat 1-5 day holds on average, momentum helped for platforms but not for chips; strong hindsight caveat.

- DECISION (user): continue with the six theme families, single stocks only (no indexes or ETFs). DONE: holding period test on 20 single stocks (5, 10, 20, 40, 60 days, net of 0.24% per round trip): net return per day held rises from 0.049% at 5 days to about 0.10% at 40-60 days, stable across both halves of the sample; momentum never beat holding; solar lost at every horizon. Hindsight selection caveat; horizon capped at 60 days.

- DECISION (user): fix the names first; holding period capped at 20 trading days (no 40-60). DONE: fixed universe v1 (24 single stocks, 4 per family, top by 30-day dollar volume among eligible candidates), frozen 2026-11-06 in `universe/FIXED_UNIVERSE.md` and `universe/fixed_universe.csv`.

- DECISION (user): remove solar; user asked me to research the better selection solution. DONE: researched index-provider rules (liquidity and size screen, revenue purity, rank by market value, buffers) and backtesting guidance (point-in-time universes; avoid survivorship and look-ahead). Conclusion: freeze the rule, not the list. Built `src/select_universe.py`, `universe/candidates.csv`, `universe/UNIVERSE_RULE.md`: five families x four names by 250-day median dollar volume as of each date; stable except chips; the current selection equals v1 for all families. Pioneer, Marathon Oil and Hess are not on Yahoo, so past universes still lean toward survivors.
- DONE (outside repo): `C:\Users\pinza\.claude\scripts\click_at.py` now brings the Claude app window (claude.exe) to the front before clicking and aborts without clicking if it cannot; the Stop hook in `~/.claude/settings.json` runs it with `--focus-exe claude.exe`.

- DONE: Phase 1 part 1. Read the official IBKR Ireland commissions page in the built-in browser (the fetch tool got 403): US tiered 0.0035 USD per share, min 0.35 USD, max 1%; fixed 0.005 per share, min 1.00 USD; API directed orders cannot use Tiered; FINRA fee holiday to 2026-12-31. Wrote `src/costs.py` and `PHASE1_FACTS.md`. Cost findings: round trip on US stocks about 0.6% on 125 USD, 0.18% on 500 USD, 0.06% on 5,000 USD (whole shares, assumptions flagged); a currency conversion costs about 0.4% each way at a 500 USD size, so hold USD. Romanian tax per press: 16% on net annual gains declared by May 25, dividends 16%. Account size consequence: 500 EUR should be concentrated in one or two names; 5,000 EUR can hold four or five.

- DONE: outcome ranges for a 500 USD account in PHASE1_FACTS.md: two names held 1 month: median +1.5%, 5th to 95th percentile -11% to +17%, 42% chance of a loss; 2 months: median +3.1%, -14.5% to +26.5%, 39% chance of a loss (buy-and-hold, survivor bias, no edge claimed).

- DECISION (user): continue the strategy. DONE: `src/run_universe_baselines.py` and `results/UNIVERSE_BASELINES.md`: 500 USD, 2 positions, whole shares, real costs, point-in-time universe, periods 2022 / 2023-24 / 2025-now. Findings: no strategy consistent across periods (trend +139%, -35%, +4%; momentum -28% to +209%); random pairs span about 60-150 points per period, so two-position results are mostly luck; 5-day holds paid 3-17% of the account in fees (random rotation up to 29%), 20-day holds 1-8%; low volatility never lost much in 2022 and cut drawdowns but lagged in bull runs.

- DONE: eToro research (official fee page and builders FAQ read in the built-in browser): stocks 1 USD on open and 1 USD on close (country and exchange dependent), no spread markup, ETFs free, no inactivity fee, withdrawal free from a EUR account or 5 USD from USD; conversion fee unstated; some stock buys can be executed as CFDs; API free for eligible users, real trading when enabled, demo separate, country eligibility and rate limits not stated. Cost comparison: eToro worse than IBKR below about 3,000 USD per order (0.8% vs 0.3% at 250 USD, 0.4% vs 0.18% at 500 USD).

- DONE: `run_universe_baselines.py` now takes `--positions`; ran 1,000 USD with 3 positions (`results/UNIVERSE_BASELINES.md`): luck spread narrower but still no consistent strategy (trend -17% to +149%, momentum -11% to +119%); 5-day fees 2-11% of the account, 20-day 1-6%.

**Next step:** (1) evaluate on many decisions instead of two positions: run all 20 names as a parallel paper portfolio or score each decision separately, with costs, per period; (2) add scheduled-event windows (earnings, EIA, OPEC, FOMC) which needs calendar data; (3) then the agent on the same harness with the same costs; (4) Phase 1 part 2 in the IBKR application flow. User still to state account size and instruments (500 and 5,000 modelled).
