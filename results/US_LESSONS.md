# Lessons from the US era (2026-11-05 to 2026-11-08)

Condensed from the archived results in `archive/results_us/`. These are the facts that still shape the European project. Method lessons carry over; US-specific numbers do not.

## What we tested and what came out
- **Rule-based strategies:** about 90 configurations on roughly 200 US stocks and 7 commodity futures (momentum, residual momentum, seasonality, industry momentum, trend, dip buying, commodity trend, indicators and candlesticks, earnings drift and surprise, insider buying). None beat a diversified basket once hindsight in the universe was reduced. Trend filters halve drawdowns but cut return. Commodity trend worked 2001-2010 and then faded. (`archive/results_us/WIDE_SEARCH.md` and the per-test files.)
- **Fallback that survived:** a trend-filtered diversified basket, about 7-11% a year with 20%+ drawdowns, before tax.
- **News agent (the one untested source of edge):** Sonnet and Opus subagents, 22 post-cutoff decision days (Jul-Sep 2026), long or flat per theme family, longs only at confidence >= 0.52 with a named catalyst. Google News gave 19 to 29 longs (mostly oil on one Iran episode), Finnhub company news 3, Massive news 0. Portfolio $1,065 (Sonnet), $1,132 (Opus), $1,065 (Opus with learning) against random-call medians of $1,097, $1,213 and $1,258. No run beat random calls. Confidence never predicted outcomes (correlation about -0.01). Outcome feedback and a lessons ledger did not help. (`archive/results_us/NEWS_SOURCE_COMPARISON.md`.)
- **Costs decide frequency:** a fixed 3 EUR fee is 0.6% of a 500 EUR order; holds of 5 days barely cover costs, 20 days pay for themselves. Cap holds at 20 trading days.
- **Inputs are priced the same day:** yesterday's oil, gold or copper move has about zero correlation with today's move in the related stock; an edge has to come from events, not from reacting to a driver that already moved.
- **Volatility is not an edge:** high-volatility names fell 47-84% from peaks within a year; loss control comes first.

## Rules that carry over
1. Agents see only information published before the decision time; outcomes are used only for scoring.
2. Pre-register the test and the pass bar before running it; count every configuration tried (multiple-testing discount).
3. Judge on many decisions and compare with random calls that have the same number of longs, with the same costs, not only with buy and hold.
4. A backtest of an LLM agent is optimistic because the model may remember history; only forward (paper) results count as evidence.
5. Every run is stateless; the handoff note (`agent/HANDOFF.md`, `src/handoff.py`) is the only memory; lessons need at least 5 supporting closed trades before they may change a call.
6. News sources: Google News RSS (date-filtered, macro and commodity rich, noisy), Finnhub and Massive (company news, North American names; Finnhub `/news` general has no date range so it must be collected forward). None of them covers European small and mid caps well; a European source is an open item.

## Where the agent got its trades
Mostly one long-running oil story and a rising market, not skill. Treat any future profit with the same suspicion until paper trading confirms it.
