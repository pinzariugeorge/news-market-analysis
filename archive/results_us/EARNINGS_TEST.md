# Earnings dates and post-earnings drift test (2026-11-07)

Data: `src/download_earnings.py` reads SEC EDGAR (free, no key) 8-K filings with Item 2.02 for 29 US domestic filers in the candidate list: 2,631 events with filing time (`data/processed/earnings_events.csv`). Session: 1,475 after the close, 850 before the open, 306 during trading hours. Foreign filers (AEM, WPM, AU, TECK, CCJ, TSM, ASML, NVO) have no 8-K and are not covered. Test: `src/run_earnings_test.py` (`results/earnings_test.csv`), data up to 2024-12-31 only (build = up to 2022, validation = 2023-2024; the final test period is untouched). A decision is made after the reaction day R (close of R versus the previous close), buying at the close of R+1 and selling H days later, after 0.3% round-trip cost; excess = the group's mean net return minus the same stock's unconditional mean for the same period and H.

## Findings
1. Earnings are big, undirected events: the reaction-day move averages 3.8% (build) and 4.2% (validation) in absolute terms, and 47% of events move 3% or more, yet the stock rose on only 48-50% of them.
2. No post-earnings drift to trade: after strong up (+3% or more) or strong down (-3% or less) reactions the excess return over 5, 10 and 20 days is within about +/-1 point, t-statistics are mostly below 1.7 in absolute value, and the signs flip between the build and validation periods (for example strong up at 10 days: -0.36 then +0.59; strong down at 5 days: +0.63 then -0.03). The one t-statistic beyond 2 (small reactions at 20 days in validation, -1.54 points, t = -2.6) is one of 18 cells and not a pattern.
3. Group sizes: strong up/down have 160-170 events each in the build period and about 60 in validation.

| H | Bucket | Build: n, excess, t | Validation: n, excess, t |
|---|---|---|---|
| 5 | strong up | 164, -0.44, -0.86 | 61, 0.00, -0.01 |
| 5 | strong down | 172, +0.63, +1.65 | 59, -0.03, -0.06 |
| 10 | strong up | 164, -0.36, -0.54 | 61, +0.59, +0.78 |
| 10 | strong down | 172, +0.45, +0.82 | 58, +0.43, +0.51 |
| 20 | strong up | 164, -0.51, -0.50 | 60, +0.46, +0.46 |
| 20 | strong down | 172, -0.81, -1.00 | 58, -0.27, -0.22 |

## What this means
- Trading the reaction after earnings (the classic drift idea) has no edge here: large-cap drift has largely disappeared.
- An agent can only get an earnings edge by forecasting the surprise or the guidance before the release; that needs consensus estimates and guidance, which we do not have free. Without them an event-day run would repeat the same blind guess.
- Useful as context: earnings days are the biggest single-day moves in these stocks (about 4% on average), so holding through earnings is a coin flip with large variance; the handbook should say so.
