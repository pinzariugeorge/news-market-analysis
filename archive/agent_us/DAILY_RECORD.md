# Daily record (what the agent sees each day)

Built by `src/build_daily_context.py <YYYY-MM-DD>`. One record per decision day D. Contains only information available before the open of D. A test confirmed the record is identical when every price on or after D is removed from the data.

## Timing rule
- The agent decides before the open of day D.
- Market information: closes dated before D (the previous trading day is the latest).
- Headlines: those with `decision_date == D`, meaning published after the previous trading day's date and before D (a headline dated Friday, Saturday or Sunday lands on Monday). A headline dated D is not shown until D+1.
- The record never contains D's own price, return or any later data.
- Scoring uses D's close-to-close return (D close vs previous close), added only after the decision is stored.

## Fields
| Field | Meaning |
|---|---|
| `decision_day`, `weekday`, `information_cutoff` | Which day, and what the information cutoff is |
| `market_state.last_trading_day`, `last_close`, `return_last_day_pct` | Latest known close and its move |
| `return_5d_pct`, `return_20d_pct`, `return_60d_pct` | Trailing returns to the last close |
| `realized_vol_20d_daily_pct` | Standard deviation of the last 20 daily moves |
| `vol_regime_1calm_to_4stormy` | Quartile of that volatility versus the previous 10 years (past only) |
| `drawdown_from_252d_high_pct`, `distance_from_200d_avg_pct` | Where the market sits in its range and trend |
| `consecutive_up_or_down_days` | Signed streak (negative = down days) |
| `big_moves_2pct_last_10_days` | Cluster warning (handbook principle 12) |
| `calendar.*` | Month, trading day of month, turn-of-month and year-end windows, US election cycle type and days to the next election (all statutory, known in advance) |
| `headlines`, `headlines_total`, `headlines_truncated` | Up to 40 headlines (published date + title), cause often missing |

## Not in the record (kept separately)
- Handbook (`handbook/HANDBOOK.md`): given to the agent as stable knowledge.
- Open storylines (`agent/state/storylines.md`): the agent's own state, updated after each day.
- Recent decisions and outcomes: the last N rows of the decision log with outcomes revealed only up to D-1.

## Known limits
- Scheduled-event calendars (FOMC, jobs report, CPI, earnings seasons) are not yet included; add them when the date lists exist (see `TODO.md`).
- Headlines are weak on causes (see `handbook/BIGDAY_REVIEW.md`).
- Because we use real names and dates, a language model may remember later events. The agent prompt tells it to reason as of the cutoff, but this cannot be verified (see `STRATEGY.md`).
