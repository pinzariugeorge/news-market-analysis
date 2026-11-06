# Strategy Document

Read this at the start of every session. Update it when a decision changes.

## Goal
Collect historical global and local news plus daily S&P 500 prices, learn which kinds of news actually move the market, and eventually run closed-loop day-trading agents that reason from events and are scored against real outcomes.

## Core rules
1. **Closed loop.** Agents see only information published before the decision date. Never future prices or outcomes.
2. **Event first, outcome hidden.** Agents get a neutral description of an event and must reason out the expected market effects themselves (e.g. oil rises, so fertilizer and transport costs rise, so airline margins fall). Real outcomes are used only for scoring.
3. **Lookahead bias control.** Models may remember real history. Run every test twice: real names and dates, and anonymized (names replaced by neutral descriptions, dates made relative). A big drop when anonymized means the agent leaned on memory.
4. **Benchmark everything** against simple baselines such as buy and hold.

## Pilot choices (decided)
- Year: 2020.
- Events: big macro news only (central bank decisions, oil moves, elections, major crises).
- News source (decided 2026-11-06): S&P headlines dataset only (`dyutidasmahaptra/s-and-p-500-with-financial-news-headlines-20082024`, 1,514 headlines after de-duplication in 2020). Reuters and ABC are dropped for now. Add GDELT, wire services or official releases later only if important events turn out to be uncovered. The `CP` column (S&P close) is dropped on load.
- Prices: daily S&P 500 history from Yahoo Finance or similar free source, stored locally.
- Models: small, cheap model for filtering and summarizing news; stronger model only for the prediction step.

## End goal and phases (decided 2026-11-06)
End goal: a live trading agent (scheduled routines, like a daily pre-market / open / midday / close cycle) that uses the handbook and what we learned from history to make profitable trades. The goal is profit, not "beat the S&P". We still measure against buy and hold and cash, because that is how we know whether the handbook adds anything (in a rising market buy and hold also profits).
1. **Historical research:** see how the market moved after different news (2008-2019), build and test the handbook.
2. **Simulation:** run the agent on 2020 (test), then 2021-2024 (holdout), news-driven, past-only information. Score after costs.
3. **Paper trading:** live schedule, paper money only, every run reviewed by the user.
4. **Live trading:** only if paper results justify it, with the user's explicit go-ahead, small size first.
Time horizon: the aim is a long-running system (years, not a 30-day challenge): as many trading days as possible and as profitable as possible. So judge results over many months and market regimes (calm, crash, recovery, election cycles), never on one short stretch; the 2008-2024 data lets us check this.
Calendar events matter: for example US midterm elections (see handbook 3.6b), Fed meetings and earnings seasons get their own handbook entries.
Not decided yet: broker, scheduler, research source for live use (the video setup used Alpaca, Claude Code routines, Perplexity; not adopted).

## Borrowed practices (from the analyzed trading-agent video, adopted selectively)
- **File memory loop:** every agent run is stateless; it reads the state files first and writes lessons and decisions back at the end. State files for the agent: strategy/rules, trade log, research/event log, open storylines, weekly review.
- **Guardrails** written into the agent's rules: max share of the portfolio per position, loss stop per position and a daily loss cap, a limit on new positions per period, no options or leverage, and "no trade" is a valid decision. Exact numbers to be chosen and tested in simulation.
- **Periodic self-review:** weekly, the agent logs what worked, what failed and which handbook entries or rules to change. Changes to the handbook are made from 2008-2019 evidence, never from the 2020 test.
- **Decision log:** every decision records inputs, reasoning, prediction and later the outcome, so scoring is auditable.
- **Test before trusting:** run each routine several times and read the full run history before relying on it. Keep secrets in environment variables, never in committed files.
- Not adopted: his strategy (generic, 30-day claim unproven) and the live tools.

## Data horizon (decided 2026-11-06)
2008 as the start was only because the headlines dataset begins in 2008. Prices now go back to 1950 (`data/raw/sp500_1950_2024_daily.csv`), so base rates and calendar-event studies (elections, Fed days, seasons, crises) use 1950-2019. Wanted: more news and an event calendar before 2008 (dot-com crash, 2001 attacks, 2002 lows, 2003 war, 2006 midterms) for the agent; source still to be chosen. 2020 stays the test year and 2021+ the holdout for everything.

## Handbook (decided 2026-11-06)
Goal: a handbook of how event types affect the market (mechanism, magnitude, horizon, amplifying and dampening conditions, affected sectors, confidence, "no meaningful effect" as a valid call). It is used by the simulation agent and for day trading. Agents act as expert financial analysts using the handbook, ongoing storylines (multi-day/multi-week events) and past-only market context (trend, volatility).
- Built from several years of data plus general finance knowledge, NOT from 2020 outcomes. 2020 is the held-out test year (circular otherwise).
- No anonymization runs (user decision): real names and dates only. Consequence: model memory of real history cannot be measured, so treat 2020 backtest results as optimistic. This relaxes core rule 3.
- Expect next-day index direction to be close to a coin flip; compare against buy and hold, and value "no edge" calls.

## Agent design v0 (decided 2026-11-06, see `agent/`)
- Daily decision before the open of day D from a past-only record (`agent/DAILY_RECORD.md`), the handbook, open storylines and recent decisions. Output is a structured JSON decision (`agent/AGENT_PROMPT.md`).
- Index only, long or flat, no leverage, no options, no shorts in v0. Provisional guardrails live in the prompt and are tuned on 2008-2019 only.
- Scored on D's close-to-close return against five baselines (buy and hold, cash, a volatility-regime rule, capped always-long, random with the same exposure) with costs and an ablation without headlines (`agent/DECISION_LOG.md`).
- Phases: develop on 2008-2019, freeze, test once on 2020, then 2021-2024, then paper, then live.

## Timing rule (decided 2026-11-06)
A headline dated D may have been published after the close, so it is used only for the decision on the next trading day after D (`decision_date` column in `data/processed/news_2020.csv`). Friday/weekend news goes to Monday. Headlines after the last 2020 trading day have no decision day.

## Pipeline steps
1. Project structure and documents.
2. Download 2020 daily S&P 500 prices.
3. Download 2020 news; cheap rule-based filtering and de-duplication; small model turns clusters into short neutral event summaries; save once and reuse.
4. Reasoning agent: event summary plus only prior events, traces cause-and-effect chains to sectors and the index, makes a prediction. Cache common causal chains.
5. Simulation loop stepping through 2020 day by day, with and without anonymization.
6. Score each reasoning step and final call against real prices and buy and hold. Track accuracy by event type.
7. Short report: what worked, what did not, what to do next.

## Continuity rules
- Keep `ROADMAP.md` (file map) and all context files current in the same change as the work (see `CLAUDE.md`).
- Every run is stateless. Start of session: read this file and `PROGRESS_LOG.md`. End of session: update the log with what was done and the exact next step.
- Record critical actions as they happen so an interrupted run can recover without repeating work.

## Housekeeping
- Project stays in its own folder with only project-relevant context.
- API keys go in `.env` only, never in chat.
- Ask before spending money on paid data or paid API usage. Decided 2026-11-06: do not use the Anthropic API; model work runs inside Claude Code on the user's Pro subscription (subagents for simulation, a routine for the live phase).
- Research and simulation only. No real money, no financial advice.
