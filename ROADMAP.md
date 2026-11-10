# Roadmap: where everything is

Lookup table for humans and agents. Check here before searching the repo. Keep it current: any time a file is added, moved, renamed or changes meaning, update this file in the same change.

Last updated: 2026-11-09 (European pivot and cleanup). The folder is still called `sp500-news-sim` (renaming would break session paths); the project is now European: see `STRATEGY.md`.

## Start-of-session reading order
1. `ROADMAP.md` (this file)
2. `STRATEGY.md` (current decisions and rules)
3. `PROGRESS_LOG.md` (what was done, exact next step; newest entry at the bottom)
Then `PLAN_EU.md` for the design and `TODO.md` for open items.

## Status labels used below
- **ACTIVE**: part of the European project, works as is.
- **PORT**: from the US era, still in the working tree because the European work will reuse it; reads US data or assumes IBKR/US conventions until ported.
- **ARCHIVE**: moved to `archive/` (see `archive/README.md`); not part of the working tree.

## Root files
| File | Status | What it holds |
|---|---|---|
| `README.md` | ACTIVE | One-page overview |
| `STRATEGY.md` | ACTIVE | Goal, decisions, rules (European era; the old file is `archive/docs_us/STRATEGY_sp500_era.md`) |
| `PLAN_EU.md` | ACTIVE | Plan: decisions of 2026-11-09, free price feed, Saxo facts, paper broker design, daily cycle, phases and gates |
| `DAILY_PLAN_EU.md` | ACTIVE | A trading day end to end: roles (collector, researcher, trader, risk manager, broker, reviewer, baseline bots), timetable in CET, risk limits, cost model, accounts and pass bar, failure handling, scheduling, build order. Design only |
| `PREREG_EU.md` | ACTIVE | Pre-registration written before the first live decision: setup, limits (defaults), baselines, pass bar, what may not change during the test |
| `PROGRESS_LOG.md` | ACTIVE | Dated session entries (whole history), each ends with "Next step" |
| `TODO.md` | ACTIVE | Open items (the US-era list is `archive/docs_us/TODO_us_era.md`) |
| `JOURNAL.md` | ACTIVE | Plain-language notes, surprises, open questions |
| `todo_suggestions.md` | ACTIVE | Ideas that were NOT adopted; move to `TODO.md` only when decided |
| `CLAUDE.md` | ACTIVE | Standing instructions for Claude sessions |
| `.env.example` | ACTIVE | Names of secrets; the real `.env` is git-ignored and never printed |
| `.gitignore` | ACTIVE | Ignores `.env`, `data/raw/`, `data/live/`, `archive/data_us/`, caches |

## Results (`results/`)
| File | Status | What it holds |
|---|---|---|
| `results/US_LESSONS.md` | ACTIVE | Condensed lessons from the whole US era: what was tested, that nothing beat random or a basket, rules that carry over. Read this instead of the archived results |

## Universe (`universe/`)
| File | Status | What it holds |
|---|---|---|
| `universe/EU_UNIVERSE.md` | ACTIVE | European candidates per theme family with liquidity and volatility, what is verified and what is not (Saxo tradability is not), open points |
| `universe/eu_candidates.csv` | ACTIVE | The same table: ticker, exchange, currency, first date, days, median traded value (EUR m, 250 days), volatility, drawdown. Written by `src/eu_probe.py` |
| `universe/eu_screen.csv` | ACTIVE | Broad European screen output of `src/eu_screen.py` (see `universe/EU_SCREEN.md` once written) |
| `universe/UNIVERSE_RULE.md` | PORT | Point-in-time liquidity rule (250-day median value, quarterly rebalance with buffer); method is reusable, numbers are US |
| `universe/COMMODITY_DATA.md` | PORT | Free commodity and driver series (symbols, coverage from 2000, sources that failed) |

## Agent design (`agent/`)
| File | Status | What it holds |
|---|---|---|
| `agent/EU_INTRADAY_PROMPT.md` | ACTIVE | Intraday trader prompt: woken by new information only; default no action; sells only when a catalyst breaks; at most 1 new buy per run; output with orders and a note, no handoff |
| `agent/CLOUD_TASKS.md` | ACTIVE | The two cloud task prompts (morning, evening) as created, with the schedule and the state-branch steps |
| `agent/EU_TRADER_PROMPT.md` | ACTIVE | Live trader prompt (Opus with learning): universe, rules, costs, learning rules, exact JSON and handoff shape |
| `agent/EU_RESEARCHER_PROMPT.md` | ACTIVE | Researcher prompt: morning brief per theme from the collected headlines, no recommendations |
| `agent/EU_REVIEWER_PROMPT.md` | ACTIVE | Reviewer prompt: plain-language day conclusion for the phone, three discussion questions, tomorrow's handoff and lessons |
| `agent/FAMILY_AGENT_PROMPT_CATALYST.md` | ARCHIVE-CANDIDATE | Current agent prompt: long or flat per theme family, long only with a named catalyst and confidence >= 0.52, JSON output, live-mode handoff section with the exact handoff shape |
| `agent/FAMILY_AGENT_PROMPT_LEARN.md` | PORT | Same plus outcome feedback and the lessons ledger (a lesson needs >= 5 supporting closed trades to change a call) |
| `agent/HANDOFF.md` | ACTIVE | Handoff rule between stateless runs (note shape, stale, pending orders, overlap) |
| `agent/DECISION_LOG.md` | PORT | Decision log columns, baselines, metrics, weekly review |
| `agent/state/storylines.md` | ACTIVE | Template for the open-storylines state file |
| `agent/state/handoff/` | ACTIVE | Live handoff notes (empty until paper trading starts) |

## Handbook (`handbook/`)
All three are US-era text (US names, US drivers) written for the old agent; they must be rewritten for the European universe before the agent trades Europe.
| File | Status | What it holds |
|---|---|---|
| `handbook/AGENT_HANDBOOK.md` | PORT | Lean handbook the agent reads (about 1,400 tokens): rules of thumb and the five families |
| `handbook/HANDBOOK_COMPANIES.md` | PORT | Full single-stock handbook: driver links, base rates, catalysts, event reactions for the five families |
| `handbook/family_stats.csv` | PORT | Statistics behind it (driver R-squared and beta, base rates, volume-shock events) |

## Code (`src/`)
Run with `python -I src\<script>.py` on Windows.
| Script | Status | Purpose |
|---|---|---|
| `live_feed.py` | ACTIVE | Live (about 15 min delayed) quotes and 5-minute bars for European stocks and ETCs from Yahoo, free; `quote`, `bars`, `snapshot` (appends to `data/live/`), self-test |
| `paper_broker.py` | ACTIVE | The paper broker: ledger (atomic JSON, dashboard shape), order log, idempotent orders, risk checks, next-bar fills, fees/FX/taxes, hours and holidays (UTC, hand-coded EU summer time), stops and horizon exits, custody, reconcile, outcomes block; 29 self-tests on a temp folder (`python -I src\paper_broker.py selftest`) |
| `eu_cycle.py` | ACTIVE | Daily cycle runner: `due`, `collect` (Google News RSS per theme, drivers, quote table), `prep`, `apply`, `fills`, `watch`, `close`, `status`, `battery` (drain from the daemon heartbeat); per-day state file; late starts produce warnings, never errors |
| `eu_daemon.py` | ACTIVE | Always-on Python scheduler and keep-awake (heartbeat log with battery percent and AC state, fills, 30-minute watchers, close job); started at logon by the Windows task `EuPaperDaemon` |
| `state_sync.py` | ACTIVE | Git-backed state for cloud runs: `pull` restores data/paper/ from the branch claude/paper-state, `push` commits it back (temporary worktree, never touches the checked-out branch); self-test against a temporary bare remote |
| `cloud_probe.py` | ACTIVE | Feasibility probe: can the machine reach Yahoo, Google News and ntfy (used once for the cloud environment) |
| `notify.py` | ACTIVE | Phone notifications via ntfy.sh (topic in `.env` as NTFY_TOPIC, never printed; silent if missing): alive each morning, fills, errors, close result, low battery, trader decision, report ready with a link to the cloud report |
| `eu_report.py` | ACTIVE | Builds the end-of-day report page for the phone (`data/paper/reports/artifact.html`, published to Claude cloud by the reviewer task) |
| `dashboard_server.py` | ACTIVE | Local server for the dashboard (`python -I src\dashboard_server.py --cloud`, port 8765): with `--cloud` it pulls the ledger from the cloud state branch into `data/paper_view/` once at start and when you press the Sync button (no timer) (read-only, never touches `data/paper/`) and shows live delayed prices; without it, reads `data/paper/ledger.json`, or a DEMO ledger with `--demo`, live delayed quotes, FX to EUR; `--selftest` checks the account maths |
| `eu_screen.py` | ACTIVE | Screens about 400 European large and mid caps across sectors: price at most 333 EUR, liquidity, volatility, returns, trend; writes `universe/eu_screen.csv` |
| `eu_probe.py` | ACTIVE | Downloads true daily history for the European candidates into `data/raw/eu/daily/` and writes `universe/eu_candidates.csv` (liquidity, volatility) |
| `handoff.py` | ACTIVE | Handoff note validator, reader, writer, overlap lock, optional `lessons` ledger; 13 self-tests (`python -I src\handoff.py selftest`) |
| `learn_prep.py` | PORT | Builds the agent input for a learning run: handoff text plus outcomes of closed past calls (point-in-time) |
| `score_family_run.py` | PORT | Scores family calls (counterfactual for flat) and a whole-share portfolio vs random-call and basket benchmarks |
| `family_prepare.py` | PORT | Picks decision days and writes past-only records into `results/<run>/records/` |
| `familydata.py` | PORT | Shared data access for the family harness (stocks cache, commodity CSVs, point-in-time names and leaders) |
| `build_universe.py` | PORT | Downloads a year of daily bars for a ticker list and writes volatility, liquidity, drawdown (imported by `familydata.py`, `select_universe.py`) |
| `select_universe.py` | PORT | Point-in-time universe rule: top names per family by median dollar volume before each as-of date |
| `costs.py` | PORT | Cost model for IBKR Ireland US stocks; to be replaced by a Saxo European model |
| `download_commodities.py` | PORT | Free daily commodity and driver series from Yahoo (2000 on) into `data/raw/commodities/` |
| `download_news.py` | PORT | Google News RSS headlines per theme and date into a run's records (date-filtered, macro and commodity rich, noisy) |
| `verify_handbook.py` | PORT | Checks a lean handbook against its sources (numbers and keywords) |

## Dashboard (`dashboard/`)
| File | Status | What it holds |
|---|---|---|
| `dashboard/index.html` | ACTIVE | Broker-style page (account, watchlist, chart with fills, positions, orders, trades, equity, agent notes); talks to `src/dashboard_server.py` |

## Data (`data/`, git-ignored)
| Path | Status | Content |
|---|---|---|
| `data/raw/eu/daily/<TICKER>.csv` | ACTIVE | Daily OHLCV for the 47 European candidates, up to about 35 years (from `src/eu_probe.py`) |
| `data/live/` | ACTIVE | Forward quote snapshots (`YYYY-MM-DD.jsonl`) written by `live_feed.snapshot`; created on first use |
| `data/paper/` | ACTIVE | Runtime state: `ledger.json` (the real paper account), `orders.jsonl`, `state/<date>.json`, `run/<date>/` (agent inputs, brief, decision, reviewer output), `reports/` (day reports, `artifact.html`), `handoff/` (live handoff notes), `daemon.log`, and `ledger_demo.json` (DEMO data for the dashboard) |
| `data/raw/commodities/` | PORT | Daily futures and driver series from 2000 (CL=F, BZ=F, GC=F, SI=F, HG=F, NG=F, PL=F, URA, SMH, XLV, VIX, TIP, TNX, DX-Y.NYB, U-UN.TO) |
| `data/raw/stocks_cache.json` | PORT | Daily closes for the US names, read by `familydata.py`; goes away when the harness is ported |

## Archive (`archive/`)
US / S&P 500 era, moved 2026-11-09, nothing deleted. Start at `archive/README.md`. Sub-folders: `docs_us/` (old plan, IBKR facts, old strategy and to-do), `agent_us/`, `handbook_sp500/`, `src_us/` (about 35 scripts incl. the 90-configuration strategy search), `results_us/` (all results, runs, dashboards), `universe_us/`, `data_us/` (git-ignored: S&P prices, headlines, US OHLC, consensus, estimates, insider).

## Outside this repo
- `D:\Projects\Marketing\news-market-analysis\.env`: the user's env file (Kaggle token, Alpha Vantage, Finnhub, Massive/Polygon keys, personal email). Scripts read the project `.env` first, then this one. Never print it.
- `D:\Projects\Marketing\news-market-analysis\api_docu_vintage.txt`: saved Alpha Vantage API documentation (US-era).
- `D:\Projects\Marketing\news-market-analysis\context\` (Romanian), `README.md`, `requirements.txt`: notes from an earlier GDELT news-vs-S&P framing. Not authoritative; `STRATEGY.md` wins.
- Scheduled task `snapshot-estimates-daily` (`C:\Users\pinza\.claude\scheduled-tasks\`): DISABLED 2026-11-09 (it snapshotted US analyst estimates; its script is archived in `archive/src_us/snapshot_estimates.py`). Re-enable only after repointing it.
- **Since 2026-11-09 15:10 CET the account runs in the cloud:** Claude Code cloud tasks `eu-paper-morning` (cron `7 7 * * 1-5` UTC) and `eu-paper-evening` (`7 17 * * 1-5` UTC) in environment `eu-paper` (network allowlist Yahoo, Google News, ntfy; Opus), routine pages https://claude.ai/code/routines/trig_01Qj8UKGLJvYWAFrSCyYseVk and https://claude.ai/code/routines/trig_014a3C7vhbEKKEU82jtBjvbD; state in git branch `claude/paper-state` (`claude/paper-state-test` is a test copy). The laptop daemon, the Windows task `EuPaperDaemon` and the three local Claude tasks are DISABLED (kept for fallback). To look at the dashboard locally run `python -I src\state_sync.py pull` first.
- Cloud task `eu-paper-intraday` (cron `37 8-15 * * 1-5` UTC; routine https://claude.ai/code/routines/trig_01UJMy3cPH9qWSRVwcT54gtt): hourly check during the session, wakes the Opus trader only on triggers (`src/eu_cycle.py intraday`, `find_triggers`, 7 self-tests: `python -I src\eu_cycle.py selftest`).
- Windows task `EuPaperDaemon` (disabled) (Task Scheduler, at logon, allowed on battery, no time limit, restart on failure) runs `src/eu_daemon.py`. Claude scheduled tasks `eu-paper-researcher` (cron 09:00 local = 08:00 CET), `eu-paper-trader` (09:30 local), `eu-paper-reviewer` (19:00 local, publishes the report) in `C:\Users\pinza\.claude\scheduled-tasks\`; the machine is on Bucharest time, one hour ahead of CET. Published day report: https://claude.ai/artifact/7TxjomynSos5DdRG3zaox6 (private).
- Claude tooling set up on the way: TradingKit MCP in `C:\Users\pinza\.claude.json` (unavailable, membership check failed); click hook scripts in `C:\Users\pinza\.claude\scripts\` (`click_at.py`, `click_tray.py`) unrelated to the project.

## How to get things
- Remote: `origin` = git@github.com:pinzariugeorge/news-market-analysis.git, branch `main`; push only when the user says so.
- Live quote check: `python -I src\live_feed.py SHEL.L ASML.AS 4GLD.DE`.
- Rebuild the European probe: `python -I src\eu_probe.py` (about 2 minutes, no key).
