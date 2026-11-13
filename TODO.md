# To-do (open items)

Last updated: 2026-11-09. The US-era list is kept in `archive/docs_us/TODO_us_era.md`.

## Decisions needed from the user
- [x] 2026-11-13: account 2,000 EUR, ETFs/ETCs allowed, no 333 EUR cap, open universe of European cash instruments; intraday run and labs paused.
- [ ] Price a ~600 EUR order for one Xetra stock and one Xetra ETF (e.g. EXW1) in the Saxo platform trade ticket and report the commission; confirm the 10 watchlist funds are searchable (a new-instrument request costs USD 200). Decide on securities lending (custody 0% vs 0.19%).
- [ ] Position count and per-position cap at 2,000 EUR (kept at 3 x 35% for now).
- [x] Account size: 1,000 EUR (2026-11-09).
- [x] ETFs: no; read as no ETCs either, commodities are drivers only (2026-11-09). Tell me if ETCs should be allowed after all.
- [x] Scheduled task `snapshot-estimates-daily` disabled (2026-11-09); its US data in `data/raw/estimates/` is no longer updated.
- [ ] Open a Saxo account (or get access to its instrument search) to verify which European names and ETCs are tradable for a Romanian retail client, and the real commission, FX and custody figures. Never paste credentials in chat.
- [ ] Approve or refuse any paid data source if the free Yahoo feed proves unreliable.

## 0. Next (2026-11-13 review)
- [ ] All-name daily direction calls in shadow scoring (primary pass bar, `PREREG_EU.md` period 3).
- [ ] News ablation on S1 candidates (with vs without news).
- [ ] Baselines: random calls on the watchlist, equal-weight basket, trend-filtered basket, EUNL.DE buy-and-hold (incl. ETF trend baseline).
- [ ] Rebuild the screen backtest on a point-in-time universe (survivor bias).

## 1. European data and universe
- [x] Free daily history and live delayed quotes tested; 47 candidates probed (`universe/EU_UNIVERSE.md`, `src/eu_probe.py`, `src/live_feed.py`).
- [ ] Port `src/select_universe.py`, `src/familydata.py`, `src/build_universe.py` to the European daily files (`data/raw/eu/daily/`), currencies (EUR, GBp, CHF, DKK, NOK, SEK, PLN) and exchange calendars; apply the point-in-time liquidity rule.
- [ ] Commodity and driver series stay in `data/raw/commodities/`; add European energy and metal references (Brent, TTF gas, EUA carbon) if a free source exists.
- [ ] Verify Yahoo volume on Swiss and Nordic venues (Roche looks under-reported).
- [ ] Decide what replaces uranium (nothing, or an ETC if found).

## 1a-intraday. Hourly intraday check (added 2026-11-10; PAUSED 2026-11-13)
- [ ] Read the first intraday runs (list_runs / get_run_log on routine trig_01UJMy3cPH9qWSRVwcT54gtt): how often it wakes the trader, token cost per run, any wrong trigger.
- [ ] Tune the triggers after a week (event words, 3% / 2% moves) using the day's `state/<date>_intraday.json` logs.
- [ ] DST: the intraday cron is UTC too (`37 7-14` in summer time).

## 1a-cloud. In the cloud since 2026-11-09 15:10 CET
- [x] Cloud environment `eu-paper`, probe passed (Yahoo, Google News, ntfy all 200), dry run on a test state branch passed, tasks created, local daemon and tasks disabled, real state pushed to `claude/paper-state`.
- [ ] First real cloud runs: evening 2026-11-09 17:07 UTC, morning 2026-11-10 07:07 UTC. Check each with `RemoteTrigger list_runs` / `get_run_log` (or the routine pages), and `git ls-remote --heads origin`.
- [ ] Cron is UTC: on 2027-03-28 (summer time) move both crons one hour earlier (`7 6` and `7 16`) so they stay at 08:07 and 18:07 CET; move back on 2027-10-31.
- [ ] Measure the token overhead per cloud run (docs do not state it) and the weekly usage after the first week.
- [ ] Optional: add `NTFY_TOPIC` as an environment variable of `eu-paper` for phone alerts from the cloud (iOS push did not work earlier).
- [ ] Fallback if the cloud fails: `Enable-ScheduledTask EuPaperDaemon`, re-enable the three local tasks, `python -I src\state_sync.py pull`, and disable the cloud routines (never run both).

## 1a. LIVE since 2026-11-09 (account A, Opus with learning)
- [x] Paper broker, risk manager, cycle runner, daemon, prompts, logon task, scheduled agent tasks, report page; first cycle ran 13:35 CET (no trade).
- [ ] First unattended morning (2026-11-10 09:10 local): check `data/paper/state/<date>.json`, `daemon.log`, and the scheduled task runs; approve any permission prompts so they are stored on the tasks.
- [ ] Baselines offline (random calls, basket, cash) as pre-registered.
- [ ] Set lid-close action to "do nothing" (user, Windows power settings) if the laptop must keep running with the lid shut.

## 1b. Agents and daily cycle (design in `DAILY_PLAN_EU.md`)
- [ ] User confirms: roster (A = Opus with learning, B = Sonnet with learning, plus baseline bots), risk limits, themes (five, or add banks, power equipment, defence).
- [ ] Build in order: paper broker core, risk manager and baseline bots, collector and European prompts and handbook, scheduler and a dry-run week.
- [ ] Freeze the pre-registered pass bar before day 1.

## 2. Paper broker (`src/paper_broker/`)
- [x] Broker-style dashboard (`src/dashboard_server.py`, `dashboard/index.html`) with a DEMO ledger; it reads the ledger JSON v0 that the broker must write to `data/paper/ledger.json`.
- [ ] Near-live prices: stay on Yahoo; if it fails, choose between Saxo level 1 (about 7 EUR a month per exchange) and EODHD (user approval needed).
- [ ] Ledger (SQLite), order and fill model (next-bar fill, spread and slippage by liquidity), Saxo cost model replacing `src/costs.py`, FX and pence handling, exchange hours and holidays, risk limits, idempotent order log, reconcile command, self-tests.
- [ ] Replay a past week of 5-minute bars through it and check every fill and fee by hand.
- [ ] Trade log field for the quoted catalyst, confidence, horizon and headline; wire `src/learn_prep.py` to the trade log instead of `decisions_raw`.

## 3. News and event sources for Europe
- [ ] Google News RSS per company and per commodity for European names (`src/download_news.py` ported); test coverage.
- [ ] Forward collection of macro and commodity headlines from now on (daily snapshot job), since history cannot be backtested cleanly.
- [ ] European company filings and calendars (earnings dates, central bank dates, OPEC, EU regulatory decisions); Finnhub and Massive do not cover European names.

## 4. Agent and handbook
- [ ] Rewrite `handbook/AGENT_HANDBOOK.md` and `handbook/HANDBOOK_COMPANIES.md` for the European universe (drivers, exchanges, earnings seasons, local holidays).
- [ ] Port the prompts (`agent/FAMILY_AGENT_PROMPT_CATALYST.md`, `..._LEARN.md`) to European names, CET timing and live-quote inputs.
- [ ] Sonnet with learning on the same 22 US days was never run; low priority now that the US era is archived.

## 5. Paper trading
- [ ] Pre-register: rules, risk numbers, at least 60 trading days and 30 trades, benchmarks (random calls, basket, cash), stop rules, one account per agent setup.
- [ ] Daily schedule: collect, run agent, fill, mark to market, report; overlap lock and handoff from `src/handoff.py`.

## 6. Other
- [ ] Push local commits to `origin/main` when the user says so (nothing committed since the Finnhub work).
- [ ] Decide whether to rename the folder `sp500-news-sim` (it would change session paths; not done).

- [ ] User: put `NTFY_TOPIC=<your long random topic>` in `D:\Projects\Marketing
ews-market-analysis\.env`, subscribe to the same topic in the ntfy app, then test with `python -I src
otify.py "test"`.

## 6. Screen first, news second (added 2026-11-12, user)
- [x] Pre-register and backtest 3 mechanical screens on European daily data (`PREREG_SCREEN.md`, `results/EU_SCREEN_TEST.md`): all fail at 1.5% cost; gross edge is positive but smaller than cost.
- [x] Forward log of screen triggers S1-S3 built (`src/screen_log.py`, runs inside the evening cloud step). [ ] Needs commit + push to main to go live; then read `report` after ~20 trading days.
- [ ] Decide: daily direction call for every candidate name in shadow scoring (today `shadow.py` scores only calls the trader chooses, max 14 a day).
- [ ] News ablation on screen candidates: same candidates with and without the news step; judged on the shadow score (no fees).
- [ ] Decide: fewer intraday runs and drop labs without a worthwhile idea (cost and noise).
- [ ] Stock-only trend-filtered basket baseline on Europe, with costs.
- [x] Re-run at 0.3% cost done: S1 survives build, validation and test; S2, S3 do not (`results/EU_SCREEN_TEST_cost0.3.md`).
