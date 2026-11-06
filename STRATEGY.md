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

## Handbook (decided 2026-11-06)
Goal: a handbook of how event types affect the market (mechanism, magnitude, horizon, amplifying and dampening conditions, affected sectors, confidence, "no meaningful effect" as a valid call). It is used by the simulation agent and for day trading. Agents act as expert financial analysts using the handbook, ongoing storylines (multi-day/multi-week events) and past-only market context (trend, volatility).
- Built from several years of data plus general finance knowledge, NOT from 2020 outcomes. 2020 is the held-out test year (circular otherwise).
- No anonymization runs (user decision): real names and dates only. Consequence: model memory of real history cannot be measured, so treat 2020 backtest results as optimistic. This relaxes core rule 3.
- Expect next-day index direction to be close to a coin flip; compare against buy and hold, and value "no edge" calls.

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
- Ask before spending money on paid data or paid API usage.
- Research and simulation only. No real money, no financial advice.
