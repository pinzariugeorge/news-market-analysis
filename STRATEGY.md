# Strategy

Read this at the start of every session. Update it when a decision changes. The S&P 500 / US-era version is preserved in `archive/docs_us/STRATEGY_sp500_era.md`.

## Goal
Find out, honestly, whether a news-driven agent (or any simple rule) can make money trading single European stocks and commodity exposure by theme, with realistic costs, on paper first. The end goal is profit from a long-running system, judged over many months, not a short lucky stretch. Research and simulation only: no real money, no financial advice.

## Decisions
- **2026-11-09, European pivot (user):** drop the S&P 500 and the US markets completely. Trade only European markets. The S&P work was the learning phase; its lessons are in `results/US_LESSONS.md`.
- **Same themes, European listings:** oil and gas, gold, chips, pharma, copper (uranium has no usable European name; see `universe/EU_UNIVERSE.md`). Single stocks only; commodity prices are drivers and news inputs; no crypto, no alt coins.
- **No ETFs (user, 2026-11-09):** read as no ETFs, ETCs or other exchange-traded products. Gold has only two liquid European miners; uranium is dropped.
- **Account size 1,000 EUR (user, 2026-11-09):** three positions of about 333 EUR, whole shares, so names above about 333 EUR a share are excluded; Saxo minimum fees (about 2 to 3 EUR an order, reported) make short holds uneconomic.
- **Own paper broker (user):** build a local simulated broker instead of waiting for broker API keys: ledger, fills at the next available bar with spread and slippage, Saxo-style costs, exchange hours, risk limits, an auditable trade log. Design in `PLAN_EU.md`.
- **Live prices for the agents (user):** agents analyse with live (delayed about 15 minutes) prices; free Yahoo feed in `src/live_feed.py`. Spending on data needs the user's approval.
- **Reference broker:** Saxo Bank, for tradability and costs (fees, FX and custody figures are still unverified).
- **Agent setup carried over:** long or flat per theme family; long only with a named catalyst and confidence >= 0.52; up to 3 positions; holds of 5, 10 or 20 trading days (cap 20); whole shares; stateless runs with a handoff note (`agent/HANDOFF.md`); a lessons ledger where a lesson needs >= 5 supporting closed trades before it may change a call.
- **Models:** Sonnet and Opus subagents inside Claude Code on the Pro subscription; no Anthropic API. The 5-hour usage limit is tracked; the user sets the cap per task. 2026-11-12: no switch of the hourly check to Haiku for now (user: leave the topic).
- **Labs (2026-11-12, user):** stocks only also for gold and oil (ETCs asked again, declined). One "wild" lab at 2,000 EUR with looser limits, not several at 10k: too few trades per idea, more ideas means more lucky winners, and at 10k the fixed commission (~0.1%) is far below the real 1-2k account (~0.8%) and would flatter results. A lab winner is a hypothesis only; re-test on fresh days at a realistic size before it gets near real money. Real money plan: 1-2k EUR eventually.

## Core rules
1. **Closed loop:** an agent sees only information available at its decision time; outcomes are used only for scoring.
2. **Pre-register** every test and its pass bar before running it; count the configurations tried.
3. **Benchmarks:** cash, equal-weight basket, trend-filtered basket and random calls with the same number of longs, all with the same costs. Beating buy and hold in a rising market is not evidence.
4. **Costs inside every test:** fixed minimum fees are large on small orders; holds under about 20 days barely cover them.
5. **Forward evidence only:** an LLM agent's backtest is optimistic (model memory of history). Only paper trading on days after the model's knowledge cutoff counts. Pass bar for paper: at least 60 trading days and 30 trades, beating random calls and the basket, not driven by one episode.
6. **Loss control before return:** position cap, daily loss cap, no leverage, no shorts, no options, "no trade" is a valid decision.
7. **Secrets:** keys live in `.env` only, never printed or pasted in chat.

## What the US era showed (short)
About 90 rule configurations and several agent setups found no edge over a diversified basket or random calls; the one fallback is a trend-filtered diversified basket (about 7-11% a year, 20%+ drawdowns, before tax). Details: `results/US_LESSONS.md`.

## Phases (see `PLAN_EU.md` for gates)
0. Cleanup and re-plan (done 2026-11-09). 1. European data, universe and news source. 2. Paper broker with self-tests. 3. Baselines on Europe with the Saxo cost model. 4. Forward paper trading (agents and baselines side by side). 5. Live only if justified and with the user's explicit go-ahead.

## Continuity rules
- Keep `ROADMAP.md` and the other context files current in the same change as the work (`CLAUDE.md`).
- Every run is stateless. Start of session: read `ROADMAP.md`, this file, `PROGRESS_LOG.md`. End of session: log what was done and the exact next step.
- Record critical actions as they happen so an interrupted run can recover without repeating work.
- Ask before spending money on paid data or APIs.
