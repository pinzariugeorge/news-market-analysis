# Roadmap: where everything is

Lookup table for humans and agents. Check here before searching the repo. Keep it current: any time a file is added, moved, renamed or changes meaning, update this file in the same change.

Last updated: 2026-11-06

## Start-of-session reading order
1. `ROADMAP.md` (this file)
2. `STRATEGY.md` (rules and decisions)
3. `PROGRESS_LOG.md` (what was done, exact next step)

## Context files (repo root)
| File | What it holds |
|---|---|
| `README.md` | One-page overview of the project |
| `STRATEGY.md` | Goal, core rules, decisions (news source, handbook, timing rule), pipeline steps |
| `PROGRESS_LOG.md` | Dated session entries, newest at the bottom, each ends with "Next step" |
| `JOURNAL.md` | Plain-language notes, surprises, open questions |
| `ROADMAP.md` | This file map |
| `todo_suggestions.md` | Ideas that came up but were NOT adopted (user decision); move to `TODO.md` only when decided |
| `TODO.md` | Open items: pre-2008 news source options, handbook work, other tasks |
| `PLAN.md` | Plan v2: what we learned, theme families, phases 1-6 with gates, open decisions (trade current companies and commodities via Interactive Brokers Ireland) |
| `PHASE1_FACTS.md` | Phase 1 facts: IBKR Ireland fees (verified vs reported vs open), access and onboarding, Romanian tax, what they mean for the cost model |
| `CLAUDE.md` | Standing instructions for Claude sessions in this repo |
| `.env.example` | Names of the secrets needed; the real `.env` is git-ignored and never printed |

## Data (`data/`)
| Path | Content | Git |
|---|---|---|
| `data/raw/sp500_1950_2024_daily.csv` | Daily S&P 500 OHLCV, 1950-01-03 to 2024-04-30 (Date,Open,High,Low,Close,Volume,Source). Use this one | ignored |
| `data/raw/sp500_2008_2024_daily.csv` | Same, 2008 onward (older file, superseded) | ignored |
| `data/raw/sp500_2020_daily.csv` | Same, 2020 only (older file, superseded by the one above) | ignored |
| `data/raw/candidates/sp500_headlines/sp500_headlines_2008_2024.csv` | Kaggle headlines (Title, Date, CP). `CP` = S&P close = outcome leak, never show to agents | ignored |
| `data/processed/news_all.csv` | Cleaned headlines: date, decision_date, split, title. Use this one | tracked |
| `data/processed/market_days.csv` | Per trading day 1950-2024: date, close, ret_pct, split (handbook = up to 2019, test = 2020, holdout = 2021+) | tracked |
| `data/processed/news_2020.csv` | Superseded by `news_all.csv` | tracked |

Note: headlines only exist from 2008; prices from 1950. Splits: `handbook` = up to 2019 (news 2008-2019) (used to build the handbook), `test` = 2020 (never used to write the handbook), `holdout` = 2021 onward (second test).
Timing rule: a headline dated D is only usable from `decision_date` (next trading day after D).

## Handbook (`handbook/`)
| File | Content |
|---|---|
| `handbook/AGENT_HANDBOOK.md` | Lean handbook for agent runs (about 1,400 tokens): rules of thumb and the five families; every number traced to the two full handbooks by `src/verify_handbook.py` |
| `handbook/HANDBOOK_COMPANIES.md` | Handbook v1 for single stocks: how to use, driver links, entries for the five families (base rates, drivers, catalysts, event reactions), limits. Numbers from history to 2022, checked on 2023-24; 2025+ not used |
| `handbook/family_stats.csv` | Statistics behind it (driver R-squared and beta, base rates, volume-shock events, weekday ratios, correlations) |
| `handbook/BIGDAY_REVIEW.md` | Review of the 247 big-move days of 2008-2019 by event type: findings and observed ranges |
| `handbook/bigday_review.csv` | One row per big day: date, return, event type (hand-labeled with hindsight), headline counts |
| `handbook/SOURCES.md` | Web sources used for handbook entries (currently midterm elections) |
| `handbook/HANDBOOK.md` | v0 draft: principles, 2008-2019 base rates, 16 event-type entries (incl. 3.6b US midterms, 3.6c presidential elections), agent usage steps, known limits. Built from 2008-2019 + general knowledge only (never 2020) |

## Trading universe (`universe/`)
| File | Content |
|---|---|
| `universe/COMMODITY_DATA.md` | Free commodity and driver price series (symbols, coverage from 2000, sources that failed, caveats) |
| `universe/UNIVERSE_RULE.md` | Universe rule v2: research behind it, the point-in-time rule, selections by date, limits, change log (five families x four single stocks; solar removed 2026-11-06) |
| `universe/candidates.csv` | Candidate companies per family (input of the rule) |
| `universe/rule_selections.csv` | Output of `src/select_universe.py`: top names per family at each as-of date |
| `universe/fixed_universe.csv` | Earlier v1 liquidity table (30-day average); kept for reference |
| `universe/BROAD_SCREEN.md` | Broad screen of what has traded well (sectors, themes, commodities, single stocks, to 2026-11-06) plus driver-to-asset correlations |
| `universe/broad_screen.csv`, `universe/broad_screen_metrics.csv` | Input list and metrics (returns 1m/3m/6m/1y, volatility, liquidity, drawdown, 200-day flag) |
| `universe/UNIVERSE.md` | Archived (solar removed 2026-11-06): method (criteria) and the solar value-chain list with 1-year volatility, liquidity and drawdown, dated 2026-11-05; research list, not recommendations |
| `universe/solar_chain.csv` | Input list: ticker, name, role in the chain, notes |
| `universe/solar_chain_metrics.csv` | Output of `src/build_universe.py` (current market metrics per ticker) |

## Results (`results/`)
| File | Content |
|---|---|
| `results/FAMILY_RUN.md` | Family agent run fam_v0 (validation 2023-2024): setup, result (all calls flat, portfolio stayed cash), counterfactuals, options |
| `results/dashboard_family.html` | Dashboard of the family run: every stock, commodity and driver price with the agent's calls, portfolio vs leaders basket, decision table with reasoning. Open in a browser |
| `results/fam_lean_check/` | Two decision days rerun with the lean handbook for comparison with `fam_v0` |
| `results/fam_v0/` | Records (inputs), decisions_raw (agent JSON), decisions.csv, summary.json, dashboard_data.json |
| `results/WIDE_TEST.md` | Wide test: momentum, reversal, low volatility, trend, oversold and random rules scored on the whole 20-name basket per decision date, by period and holding period; findings |
| `results/wide_test.csv` | Same numbers as CSV |
| `results/INDICATOR_TESTS.md` | Test of 10 standard indicator and candlestick signals on 45 stocks by period and holding period; no reliable edge; findings |
| `results/indicator_tests.csv` | Same numbers as CSV |
| `results/UNIVERSE_BASELINES.md` | Baselines on the rule-selected single-stock universe for a 500 USD account (whole shares, 2 positions, real costs), by period and holding period; findings |
| `results/universe_baselines.csv` | Same numbers as CSV (500 USD, 2 positions); `results/universe_baselines_1000_3pos.csv` for 1,000 USD with 3 positions |
| `results/BASELINES.md` | Baseline results on 2008-2019 and what the agent must beat |
| `results/baselines_2008_2019.csv` | Same numbers as CSV |
| `results/dashboard.html` | Dashboard: where the agent acted on the S&P chart, cumulative return vs baselines, expected range vs outcome, and a table with the agent's reasoning per day. Open it in a browser |
| `results/pilot_v0/` | First pilot run: `days.json`, `records/` (inputs), `decisions_raw/` (agent JSON), `decisions.csv`, `summary.json`, `dashboard_data.json` |

## Agent design (`agent/`)
| File | Content |
|---|---|
| `agent/FAMILY_AGENT_PROMPT_LEAN.md` | Same rules as the family prompt, pointing at the lean handbook only |
| `agent/FAMILY_AGENT_PROMPT.md` | Prompt for the family run: long or flat per family with horizon and confidence; leader chosen by rule; JSON output |
| `agent/DAILY_RECORD.md` | What the agent sees on decision day D (past-only market state, calendar, headlines) and the timing rule |
| `agent/AGENT_PROMPT.md` | Agent prompt template v0: rules, provisional guardrails, procedure, JSON output format |
| `agent/DECISION_LOG.md` | Decision log columns, baselines, metrics, run phases, weekly review |
| `agent/state/storylines.md` | Template for the open-storylines state file the agent updates |

## Code (`src/`)
| Script | Purpose |
|---|---|
| `download_prices.py` | Yahoo prices, 2020 only (old) |
| `download_prices_all.py` | Yahoo prices 1950 to 2024-04 -> `data/raw/sp500_1950_2024_daily.csv` |
| `inspect_news_candidates.py` | Reports columns, date range and 2020 rows per month for candidate CSVs |
| `verify_handbook.py` | Checks a lean handbook against its sources: size, required keywords, every number found in the sources, and family numbers in the matching family text |
| `familydata.py` | Shared data access for the family run (stocks cache, commodity CSVs, point-in-time names and leaders) |
| `family_prepare.py` | Picks decision days and writes past-only family records into `results/<run>/records/` |
| `score_family_run.py` | Scores family calls (counterfactual for flat) and a 1,000 USD whole-share portfolio vs benchmarks; writes decisions.csv, summary.json, dashboard_data.json |
| `build_dashboard_family.py` | Builds `results/dashboard_family.html` |
| `download_commodities.py` | Downloads free daily commodity and driver series from Yahoo (2000 on) into `data/raw/commodities/` (git-ignored) |
| `build_family_stats.py` | Computes the per-family handbook statistics from history to 2024 (build and validation); writes `handbook/family_stats.csv` |
| `run_wide_test.py` | Scores selection rules on the whole point-in-time basket per decision date (many decisions, costs, periods); writes `results/wide_test.csv` |
| `run_indicator_tests.py` | Tests RSI, MACD, golden cross, Bollinger, breakout and candlestick patterns as long signals with costs and period splits; writes `results/indicator_tests.csv` |
| `run_universe_baselines.py` | Baselines on the rule-selected universe for a small account: cash, hold two, random rotation, momentum, low volatility, trend; writes `results/universe_baselines.csv` |
| `costs.py` | Cost model for IBKR Ireland US stocks (commission, pass-through assumptions, spread, FX, tax); `python -I src\costs.py` prints round-trip cost tables; import it in every backtest |
| `select_universe.py` | Point-in-time universe rule: top 4 names per family by 250-day median dollar volume using only data before each as-of date; writes `universe/rule_selections.csv` |
| `build_universe.py` | For a ticker CSV (`universe/*.csv`), downloads the last year of daily bars from Yahoo and writes `<name>_metrics.csv` (volatility, liquidity, drawdown): `python -I src\build_universe.py universe/solar_chain.csv` |
| `pilot_prepare.py` | Picks pilot decision days (2008-2019 only, by category) and writes their past-only records to `results/<run>/records/` |
| `score_decisions.py` | Joins stored agent decisions (`results/<run>/decisions_raw/`) with outcomes; writes `decisions.csv`, `summary.json`, `dashboard_data.json` |
| `build_dashboard.py` | Builds `results/dashboard.html` (self-contained, no network): `python -I src\build_dashboard.py --run pilot_v0` |
| `run_baselines.py` | Computes the no-model baselines (buy and hold, cash, volatility rule, capped long, 200-day trend, random) for a period; writes `results/baselines_<years>.csv` |
| `build_daily_context.py` | Builds the past-only daily record JSON for one day: `python -I src\build_daily_context.py 2018-12-26` |
| `review_big_days.py` | Labels 2008-2019 days with a move of 2% or more by event type, writes `handbook/bigday_review.csv`, prints per-type stats |
| `build_news_corpus.py` | Raw headlines + prices -> `data/processed/news_all.csv` and `market_days.csv` (drops CP, fixes encoding, de-duplicates, adds decision_date and split) |

Run with `python -I src\<script>.py` on Windows.

## Planned, not created yet

- `cache/`: cached model outputs (git-ignored).

## Outside this repo
- `D:\Projects\Marketing\news-market-analysis\.env`: the user's own env file with the Kaggle token. A copy lives in this folder's git-ignored `.env`.
- `D:\Projects\Marketing\news-market-analysis\context\` (Romanian) and `requirements.txt`: notes from an earlier, different framing (GDELT news-vs-S&P correlation study, no trading). Not authoritative for this project; STRATEGY.md wins.

## How to get things
- Kaggle download: `kagglehub.dataset_download(ref, output_dir=...)` with `KAGGLE_API_TOKEN` in the environment (the `kaggle` CLI fails with this token type).
- Remote: `origin` = git@github.com:pinzariugeorge/news-market-analysis.git, branch `main`.
