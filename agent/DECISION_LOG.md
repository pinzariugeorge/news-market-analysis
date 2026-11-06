# Decision log and scoring (format, v0)

Every agent decision is stored before its outcome is known, then scored. Results go to `results/` (git-tracked summaries; large raw logs ignored if needed).

## One row per decision day (CSV: `results/<run_name>/decisions.csv`)
| Column | Meaning |
|---|---|
| `run_name`, `decision_day` | Run identifier and day D |
| `prompt_version` | e.g. `v0`, so changes can be compared |
| `vol_regime`, `regime_label` | From the record, and the agent's own label |
| `n_headlines`, `n_relevant` | Headlines shown, and how many the agent kept |
| `event_types` | Handbook entries used, semicolon-separated |
| `direction`, `exp_low`, `exp_high`, `horizon`, `confidence` | The agent's view |
| `position`, `size_pct` | Action |
| `reasoning` | Agent's reasoning text (max 120 words) |
| `outcome_ret_pct` | D close-to-close return (added after the decision is stored) |
| `strategy_ret_pct` | `size_pct/100 * outcome_ret_pct` minus costs |
| `cost_pct` | Cost for position change (provisional: 0.02% per 100% of position changed) |
| `correct` | 1 if direction was up/down and matched the sign of the outcome, blank for no_edge |
| `in_range` | 1 if the outcome fell within the expected range |

## Scoring convention for sparse pilot days
When days are sampled (not consecutive), each decision is independent: the agent starts flat each day, pays cost x size on the position taken, and results are sums of daily returns (not compounded). Full consecutive runs use the position-change cost and compounded equity curves (see `src/run_baselines.py`).

## Baselines to beat (same days, same costs)
1. Buy and hold the index.
2. Always flat (cash).
3. Long only when the volatility regime is 1-3 (a simple rule, no news).
4. Long every day with the volatility-regime cap (size 100% regime 1-3, 50% regime 4).
5. Random long/flat with the agent's average exposure (repeated many times).

## Metrics
- Total and annualized return, volatility, Sharpe ratio, maximum drawdown, exposure (share of days long), turnover.
- Direction hit rate when the agent committed (up/down), against the base rate.
- Calibration: hit rate by confidence bucket; share of outcomes inside the expected range.
- Breakdown by volatility regime, by handbook event type, by year, and on big-move days (|move| of 2% or more) versus normal days.
- Value of the news: the same agent without headlines (market state only) as an ablation.

## Run phases
1. Develop on 2008-2019 (handbook period): tune prompt and guardrails here only.
2. Freeze everything.
3. Test once on 2020; report honestly, including losses.
4. Second test on 2021-2024 (holdout).
5. Paper trading, then live, only with the user's go-ahead.

## Weekly review (in simulation and live)
Every Friday the agent writes: what worked, what failed, which handbook entries or rules to change. Changes are proposed, then applied to the handbook only from 2008-2019 evidence.
