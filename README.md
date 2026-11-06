# S&P 500 News-Driven Agent Simulation (Pilot: 2020)

Research and simulation only. Not financial advice. No real money.

## What this project does
Goes back in time, collects news plus daily S&P 500 prices, learns which kinds of news move the market, and eventually runs closed-loop day-trading agents that reason from events and are scored against what really happened.

## Folder layout
- `STRATEGY.md`: the rules and design. Read at the start of every session.
- `PROGRESS_LOG.md`: what was done and the exact next step. Read at the start of every session, update at the end.
- `JOURNAL.md`: plain-language notes, surprises, open questions.
- `data/raw/`: downloaded source data, never edited by hand.
- `data/processed/`: cleaned data and event summaries (saved once, reused).
- `src/`: scripts (price download, news filtering, agent, simulation, scoring).
- `results/`: scores, reports.
- `cache/`: cached causal chains and model outputs.
- `.env`: private API keys (never shared, never committed). See `.env.example`.

## Core rules (short version)
1. Closed loop: agents only see information published before the decision date.
2. Event first, outcome hidden: agents reason from neutral event descriptions.
3. Lookahead control: run each test with real names/dates and anonymized.
4. Always compare against simple baselines such as buy and hold.

## Status
See `PROGRESS_LOG.md`.
