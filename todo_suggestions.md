# Suggestions (not planned, not in TODO.md)

Ideas that came up and were NOT adopted. Move one to `TODO.md` only when you decide to do it.

## From the second trading video (pasted 2026-11-06)
- Order journal: write every order down the moment it is sent, so an interrupted run can be recovered without repeating a trade (idempotent order log).
- Failure-behavior checklist for the agent routine: no previous handoff on the first run; the next run has no chat history; the previous run crashed after sending an order; two runs overlap; corrupt or missing state file; machine or app offline.
- One handoff note at the end of every run: what changed, outcomes, remaining risks, the exact next job.
- Two update notifications a day (midday and after the close) sent to a chat tool.
- Not suggested: his same-day-flat day-trading schedule (fees make it lose on a small account) and the paid real-time data plan.

## Other ideas mentioned
- Oversold-buying test (RSI below 30) out of sample with a market-wide-selloff filter (from `results/INDICATOR_TESTS.md`).
- Crypto as a separate paper-trading study, Bitcoin and Ethereum only (judged not a shortcut).
- Dynamic-workflow tournament of many agents for non-market decisions (design reviews), not for trades.
- TradingView connector (paid plan): judged unnecessary for now; indicators and candlestick patterns can be computed and tested from price data.
