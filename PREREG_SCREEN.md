# Pre-registration: mechanical screens on European stocks (written 2026-11-12, before any result)

Purpose: test the mechanical half of "screen first, news second" on 35 years of European daily data. News is NOT tested here (no clean historical news); it is tested forward as an ablation (see `STRATEGY.md`). Research only.

## Data and rules
- Universe: the 39 European single stocks in `data/raw/eu/daily/` (ETCs 4GLD, BRNT, COPA, CRUD, NGAS, SGLD, SSLV excluded; also CEY has no data). All are current names: survivor bias, stated. Returns in local currency (no FX).
- Signals use only data up to day t's close. Entry at day t+1 open, exit at the close of day t+1+H. One entry per stock per H days (no overlap).
- Cost: 1.5% round trip per position (1,000 EUR account, from `PLAN_EU.md`); gross also reported.
- Periods: build 2003-2014, validation 2015-2021, test 2022-2026-11 (opened once, only for configs that pass build and validation).

## The 3 screens (the only ones tried; 6 configs with H = 10 and 20)
- **S1 event momentum:** close above its 200-day mean AND volume at least 2x its 20-day mean AND day return at least +2%.
- **S2 oversold in uptrend:** close above 200-day mean AND 3-day return at most -5%.
- **S3 shock reversal:** close above 200-day mean AND volume at least 2x 20-day mean AND day return at most -4%.
- Baselines on the same dates: (a) all stocks, any date (unconditional mean of the same H); (b) trend filter only (close above 200-day mean); (c) random entries: same number of events per period, drawn from stocks and dates with a 200-day history, 1,000 draws.

## Metric and pass bar
- Excess = event return minus the mean H-day return of all stocks on the same entry date (removes market moves). Net = excess minus cost.
- A config passes only if ALL hold: net excess above 0 in build AND in validation; at least 100 events on at least 50 distinct dates in each; t-statistic of mean net excess at least 2 in pooled build+validation with errors clustered by entry month; mean net excess above the 95th percentile of random entries in pooled build+validation.
- With 6 configs, a pass is still a hypothesis: it needs the untouched test period and then forward paper evidence.
- Fail on all = "no mechanical edge at this cost", a valid result.

## Power calculation (same script)
For each H: sd of event returns, and the number of independent events needed to detect a net edge of 1%, 2%, 3% at t = 2; compared with how many closed trades the main account makes per month.

## Amendment 2026-11-12 (after the 1.5% result, so post hoc): second cost level
All 6 configs failed at 1.5%. User asked to rerun at 0.3% round trip (about what a larger account pays). This adds 6 configs (12 counted in total) and was chosen after seeing the first result: treat a pass as a hypothesis. Same screens, periods and pass bar. Results: `results/EU_SCREEN_TEST_cost0.3.md`.
