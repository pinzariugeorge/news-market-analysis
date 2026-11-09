# Pre-registration: European paper trading, account A (written 2026-11-09 13:40 CET, before the first decision)

Written before any live decision so the result cannot be bent afterwards. Research and simulation only.

## Setup (defaults, NOT confirmed by the user except where marked)
- One account, 1,000 EUR (user, 2026-11-09), Opus with learning (user, 2026-11-09). All three agent roles (researcher, trader, reviewer) on Opus (user: "only Opus with learning").
- Instruments: single European stocks only, no ETFs or ETCs (user). Traded universe for the first weeks: the five themes below, names priced at most 333 EUR and liquid (median traded value at least 20 million EUR a day): oil_gas SHEL.L TTE.PA BP.L ENI.MI EQNR.OL REP.MC; gold_miners FRES.L EDV.L; chips IFX.DE STMPA.PA BESI.AS; pharma AZN.L NOVN.SW NOVO-B.CO SAN.PA GSK.L BAYN.DE; copper_uranium (copper only) GLEN.L RIO.L ANTO.L BOL.ST KGH.WA. Themes and names are a default, not confirmed.
- Limits (default, not confirmed): 3 positions, at most 35% of equity each, whole shares, cash only, no shorts or leverage; holds 5, 10 or 20 trading days; stop -8% on a position; daily loss cap 3% and weekly 6% (no new buys); at most 3 new buy orders a day; a buy is rejected if the fixed fee would exceed 1% of the order; long only with a named catalyst and confidence at least 0.52; no new buys in the last 30 minutes of a session.
- Fills: first 5-minute bar starting at or after the order time (and not before 15 minutes after the open), at that bar's open, with spread and slippage by liquidity (3 to 12 basis points), commission max(2.5 EUR, 0.08%), currency conversion 0.25% on non-EUR names, purchase taxes (UK 0.5%, France 0.4%, Italy 0.1%, Spain 0.2%), custody 0.12% a year. Fee figures are third-party and unverified.
- Memory: handoff note (`agent/HANDOFF.md`) and the outcomes block from closed trades; a lesson changes a call only with at least 5 supporting closed trades.

## Baselines (computed offline from history and the same cost model, no live code)
Random calls with the same number of long entries, horizons and costs (300 draws, median and 5th to 95th percentile); equal-weight basket of the traded universe rebalanced monthly; cash.

## Pass bar (fixed now)
After at least 60 trading days and at least 30 closed trades, the account passes only if all hold: net return after costs above the median of random calls and above the equal-weight basket; still positive after removing the best single trade; mean net return per trade positive with a bootstrap 90% interval above zero; higher-confidence trades do better than lower-confidence ones (rank correlation above zero). Otherwise the answer is "no edge shown", which is a valid result. Early looks are reported but do not stop or change the test.

## Not allowed during the test
Changing the universe, limits, costs, prompts or models without writing the change and its date in `PROGRESS_LOG.md`; results before the change then count as a separate period. Looking at outcomes to choose names.

## Known caveats
The agent may recall history (all days are after its knowledge cutoff, but its knowledge of company facts is older). One account, one market regime, about three months: low power by design; a pass would call for a longer second test, not for real money.
