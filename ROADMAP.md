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
| `build_daily_context.py` | Builds the past-only daily record JSON for one day: `python -I src\build_daily_context.py 2018-12-26` |
| `review_big_days.py` | Labels 2008-2019 days with a move of 2% or more by event type, writes `handbook/bigday_review.csv`, prints per-type stats |
| `build_news_corpus.py` | Raw headlines + prices -> `data/processed/news_all.csv` and `market_days.csv` (drops CP, fixes encoding, de-duplicates, adds decision_date and split) |

Run with `python -I src\<script>.py` on Windows.

## Planned, not created yet
- `results/`: simulation decisions and scores (one folder per run).
- `cache/`: cached model outputs (git-ignored).

## Outside this repo
- `D:\Projects\Marketing\news-market-analysis\.env`: the user's own env file with the Kaggle token. A copy lives in this folder's git-ignored `.env`.
- `D:\Projects\Marketing\news-market-analysis\context\` (Romanian) and `requirements.txt`: notes from an earlier, different framing (GDELT news-vs-S&P correlation study, no trading). Not authoritative for this project; STRATEGY.md wins.

## How to get things
- Kaggle download: `kagglehub.dataset_download(ref, output_dir=...)` with `KAGGLE_API_TOKEN` in the environment (the `kaggle` CLI fails with this token type).
- Remote: `origin` = git@github.com:pinzariugeorge/news-market-analysis.git, branch `main`.
