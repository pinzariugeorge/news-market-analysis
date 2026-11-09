# Archive: the US / S&P 500 era (moved 2026-11-09)

Nothing here is deleted. It was moved out of the working tree when the project switched to European markets (`STRATEGY.md`, `PLAN_EU.md`). Everything is still in git history; the raw data is git-ignored and exists only on this machine.

What was learned from this era is in `results/US_LESSONS.md` (read that, not the files below). Scripts in `src_us/` still run only if moved back to `src/` (they use `ROOT = parent of src`).

| Folder | What is in it |
|---|---|
| `docs_us/` | `PLAN.md` (Plan v2 for Interactive Brokers Ireland), `PHASE1_FACTS.md` (IBKR fees, access, Romanian tax), `STRATEGY_sp500_era.md` (the strategy file as it stood), `TODO_us_era.md` (open items as they stood) |
| `agent_us/` | Early prompts: index-only agent (`AGENT_PROMPT.md`, `DAILY_RECORD.md`) and the first family prompts (superseded by the catalyst and learning prompts in `agent/`) |
| `handbook_sp500/` | S&P index handbook v0, review of 247 big-move days, sources |
| `src_us/` | About 35 scripts: S&P news and price downloads, the 90-configuration strategy search (`strat_lab*.py`), indicator, earnings, surprise and insider tests, dashboards, pilot harness, TradingKit local replica |
| `results_us/` | All result write-ups and CSVs, the pilot and agent runs (`pilot_v0`, `fam_v0`, `fam_post*`, `fam_opus1`, `fam_opus2`), dashboards, the TradingKit loop log |
| `universe_us/` | US candidate lists, rule selections, broad screen, solar chain, earnings data sources |
| `data_us/` | Git-ignored. S&P 500 index prices 1950-2024, Kaggle headlines, processed news corpus, US daily OHLC (2003 on), Alpha Vantage consensus history, estimate snapshots, SEC insider purchases |

Still in the working tree on purpose: `src/` harness stack to be ported to Europe (`familydata.py`, `build_universe.py`, `select_universe.py`, `family_prepare.py`, `score_family_run.py`, `learn_prep.py`, `costs.py`), `src/handoff.py`, `data/raw/commodities/` and `data/raw/stocks_cache.json` (read by that stack). See `ROADMAP.md`.
