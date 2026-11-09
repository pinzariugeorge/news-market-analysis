# A trading day, end to end (European paper trading, 1,000 EUR per account)

Status: DESIGN, nothing of the daily cycle runs yet. Times are CET (Xetra, Euronext, Zurich, Nordics, Madrid, Milan all trade about 09:00-17:30 CET; London 08:00-16:30 UK time is the same hours; Oslo closes 16:20, Copenhagen 17:00). No trading on exchange holidays (calendar file to build). Research and simulation only.

> **Update 2026-11-09: the day now runs in the cloud as two tasks** (`agent/CLOUD_TASKS.md`): morning 08:07 CET (collect, researcher, trader, orders) and evening 18:07 CET (replay stops and exits from the bars, fills, close, reviewer, report, state push). The timetable below is the design; the local daemon and local tasks are disabled.

## Who does what
| Role | Is | Job | Model |
|---|---|---|---|
| Collector | Python | news, calendars, overnight moves, quote snapshots | none |
| Researcher | agent | reads the collected material, writes the morning brief per theme and a short candidate list with named catalysts and sources | Sonnet |
| Trader | agent | reads handoff, outcomes of past trades, brief, positions and delayed quotes; returns decisions JSON and the next handoff note | Opus (account A) and Sonnet (account B) |
| Risk manager | Python | checks every order request against the limits; rejects or shrinks; the agent can never touch the ledger | none |
| Paper broker | Python | order log, fills, fees, FX, hours, ledger, reconcile | none |
| Reviewer | agent | end of day: what happened, storyline updates, lessons ledger (>= 5 closed trades before a lesson may change a call) | Sonnet |
| Baseline bots | Python | random calls with the same number of longs, equal-weight basket, cash; same costs; the yardsticks | none |

Separation of duties: agents only submit order requests; only the risk manager and broker write the ledger. Each agent run is stateless and reads only its listed files (handoff note first), as in `agent/HANDOFF.md`.

## The day
| Time (CET) | Step | Details |
|---|---|---|
| 07:30 | Collector run | Google News RSS per theme and per held or candidate name, central-bank and OPEC items, earnings dates for the next 5 days, overnight moves in Brent, gold, copper, gas, FX, US and Asia closes as context only; saves everything to `data/live/<date>/` and takes a quote snapshot. Holiday or no data: the day is skipped, positions held |
| 08:00 | Researcher | Writes `research/<date>.md`: per theme what changed overnight, scheduled events today, up to 5 candidate catalysts with quoted headline and source. May run web searches. Uses only information dated before 08:00 |
| 08:30 | Trader | Reads, in order: handoff note (warnings first), outcomes block, morning brief, positions and orders, delayed quotes (age shown). Returns per theme: long, flat, hold or close, with horizon (5, 10 or 20 days), confidence, named catalyst, order request (symbol, quantity in whole shares, market or limit). "No trade" is a valid answer. Writes the new handoff note |
| 08:40 | Risk manager | Applies the limits below to each request; writes accepted orders to the order log before anything is sent (idempotent id); logs rejections with the reason |
| 09:15-09:20 | Broker fills | An accepted market order fills at the open of the first 5-minute bar at or after 09:15 (skips the opening auction), plus spread and slippage by liquidity, plus fees. Computed once that bar is available from the delayed feed, so the agent never sees a later price than its decision time |
| 09:30-16:45 | Watchers (every 30 min, Python) | Marks to market; checks stop (-8% on a position, closed at the next bar), exit date reached, daily loss cap, data gaps; wakes an agent only on a trigger (position move beyond a threshold, breaking headline on a held name). No agent is polling |
| 12:30 | Midday check (optional) | Trader re-run only if a trigger fired in the morning; otherwise skipped to save usage |
| 16:45 | Pre-close | Positions whose horizon ends today get a sell order for the close (filled at the last bars, about 17:20-17:25) |
| 17:45 | Close job | Marks to market, writes the daily equity point, reconciles ledger vs recomputation from fills (fails loudly on mismatch), updates the dashboard data |
| 18:00 | Reviewer | Writes the day report: trades, fees, P&L against the baseline bots, storyline status, outcome of closed trades; updates the lessons ledger (cases counted from closed trades only); prepares tomorrow's `next_job` |
| Friday 18:30 | Weekly review | Performance of each account vs random calls, basket and cash; lessons audit; proposals listed, none applied without the user |
| Quarterly | Universe refresh | Re-apply the point-in-time liquidity and price filter (names at most 333 EUR, median value at least 20 million EUR a day) |

## Limits (proposed, user to confirm before day 1)
- Account 1,000 EUR, cash only: no leverage, no shorts, no options, no ETFs or ETCs.
- At most 3 open positions, each at most 35% of equity (about 333 EUR), whole shares only; a buy is skipped if the fixed fee would exceed 1% of the order.
- Holds of 5, 10 or 20 trading days, capped at 20; at most 3 new orders a day.
- Stop at -8% on a position; daily loss cap 3% of equity (no new buys for the rest of the day); weekly loss cap 6% (no new buys until the next Monday review).
- Only names from the point-in-time universe (`universe/EU_SCREEN.md` filters); long only with a named catalyst and confidence at least 0.52.
- Costs modelled: fee max(2.5 EUR, 0.08%) per order (reported Saxo, to confirm), currency conversion up to 0.25% on non-EUR names, custody accrual 0.12% a year, spread and slippage 2 to 10 basis points by liquidity, UK stamp duty 0.5% on purchases, French transaction tax 0.4% on large caps, Italian 0.1%, Spanish 0.2% on purchases (rates to verify). These taxes alone make UK and French names expensive at this size.

## Accounts and test design
- Start with two agent accounts of 1,000 EUR each: A = Opus with learning, B = Sonnet with learning; plus the three baseline bots. Add more accounts only after 60 trading days.
- Pre-registered pass bar (to freeze before day 1): at least 60 trading days and 30 trades per account; beat random calls with the same number of longs and the equal-weight basket after costs; not driven by one episode (result excluding the best single trade must stay positive); confidence must not be uninformative (outcomes should rise with confidence). If it fails, the answer is "no edge", which is a valid result.

## Failure handling
Overlap lock between runs; stale handoff warning; missing or old quotes mean no trade; a crash after an order was logged is recovered from the order log without repeating it; corrupt state file skipped with the previous valid note used; PC off or app closed means the day is skipped (positions are only marked at the next run); a quote older than 30 minutes is never used for a fill.

## Machine and scheduling
- The Python jobs (collector, fills, watchers, close, bots) run from Windows Task Scheduler. The three agent runs are Claude Code scheduled tasks that call subagents and need the PC on and the Claude app open at the time (cloud routines cannot read the local ledger). Window to keep the PC on: 07:30 to 18:15 on trading days.
- Usage estimate on the Pro plan, from the US-era runs: an Opus decision day cost about 1.2 to 1.7 points of the 5-hour limit and a Sonnet day under 0.5, so one live day (researcher, trader, reviewer for two accounts) is roughly 3 to 4 points of one 5-hour window and about 0.5% of the weekly limit. Affordable; measured values to replace the estimate after the first week.

## Build order (each step self-tested, then reported)
1. Paper broker core: ledger, order log, fills, cost model (fees, FX, taxes), exchange hours and holidays, reconcile, crash recovery (`src/paper_broker/`).
2. Risk manager and baseline bots.
3. Collector (news, calendar, quotes) and the European handbook and prompts (trader, researcher, reviewer) with the handoff and lessons plumbing.
4. Scheduler (Task Scheduler jobs and the three scheduled agent tasks), dry-run week on past days replaying 5-minute bars, then day 1 live paper.
