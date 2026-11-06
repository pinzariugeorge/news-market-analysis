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

**Next step:** (1) user reviews handbook v0; (2) test it on 2008-2019: for each |move|>=2% day (247), do the handbook plus past-only headlines name the right event type and size? Record hit rates per event type in `handbook/` (never use 2020); (3) design the daily record format (new events, open storylines, past-only market context). Also check why 2020-09-23 has 55 headlines.
