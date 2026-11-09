# European News-Driven Paper Trading (folder name `sp500-news-sim` is historical)

Research and simulation only. Not financial advice. No real money.

## What this project does
Tests, honestly, whether a news-driven agent (or any simple rule) can trade single European stocks and commodity exposure by theme (oil and gas, gold, chips, pharma, copper) at a profit after realistic costs. It started as an S&P 500 news study (2026-11-05), grew into US single-stock tests, and on 2026-11-09 pivoted to European markets only. Plan: our own local paper broker with live (delayed) free prices, Saxo Bank as the reference broker, forward paper trading judged against random calls and a basket.

## Where to look
- `ROADMAP.md`: where everything is (check first). `STRATEGY.md`: decisions and rules. `PLAN_EU.md`: design, paper broker, phases. `PROGRESS_LOG.md`: history and exact next step. `TODO.md`: open items. `JOURNAL.md`: notes and open questions. `CLAUDE.md`: standing instructions for Claude sessions.
- `results/US_LESSONS.md`: what the US era taught us (no edge found; rules that carry over).
- `universe/EU_UNIVERSE.md`: European candidates, liquidity, what is verified.
- `src/live_feed.py`, `src/eu_probe.py`: free live quotes and European history. `src/handoff.py`: memory between stateless agent runs.
- `archive/`: the whole US / S&P era, kept, not deleted (`archive/README.md`).
- `.env`: private API keys (never shared, never committed). See `.env.example`.

## Core rules (short)
1. Agents see only information available at their decision time; outcomes are only for scoring.
2. Pre-register tests; judge against random calls, a basket and cash, with the same costs.
3. Only forward paper results count as evidence for an LLM agent.
4. Loss control before return; no leverage, shorts or options.

## Status
See `PROGRESS_LOG.md` (newest entry at the bottom).
