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
| `TODO.md` | Open items: pre-2008 news source options, handbook work, other tasks |
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
| `handbook/BIGDAY_REVIEW.md` | Review of the 247 big-move days of 2008-2019 by event type: findings and observed ranges |
| `handbook/bigday_review.csv` | One row per big day: date, return, event type (hand-labeled with hindsight), headline counts |
| `handbook/SOURCES.md` | Web sources used for handbook entries (currently midterm elections) |
| `handbook/HANDBOOK.md` | v0 draft: principles, 2008-2019 base rates, 16 event-type entries (incl. 3.6b US midterms, 3.6c presidential elections), agent usage steps, known limits. Built from 2008-2019 + general knowledge only (never 2020) |

## Trading universe (`universe/`)
| File | Content |
|---|---|
| `universe/UNIVERSE.md` | Method (criteria) and the solar value-chain list with 1-year volatility, liquidity and drawdown, dated 2026-11-05; research list, not recommendations |
| `universe/solar_chain.csv` | Input list: ticker, name, role in the chain, notes |
| `universe/solar_chain_metrics.csv` | Output of `src/build_universe.py` (current market metrics per ticker) |

## Results (`results/`)
| File | Content |
|---|---|
| `results/BASELINES.md` | Baseline results on 2008-2019 and what the agent must beat |
| `results/baselines_2008_2019.csv` | Same numbers as CSV |
| `results/dashboard.html` | Dashboard: where the agent acted on the S&P chart, cumulative return vs baselines, expected range vs outcome, and a table with the agent's reasoning per day. Open it in a browser |
| `results/pilot_v0/` | First pilot run: `days.json`, `records/` (inputs), `decisions_raw/` (agent JSON), `decisions.csv`, `summary.json`, `dashboard_data.json` |

## Agent design (`agent/`)
| File | Content |
|---|---|
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
