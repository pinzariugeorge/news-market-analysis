# Baselines on the rule-selected universe, 500 USD account (2026-11-06)

Produced by `python -I src/run_universe_baselines.py` (data: `results/universe_baselines.csv`). Account of 500 USD, at most 2 positions from different families, each half of equity, whole shares, real order costs from `src/costs.py` (IBKR Ireland tiered, USD cash), universe chosen point-in-time by the rule in `universe/UNIVERSE_RULE.md`. Signals use only closes before the trade day; trades execute one day later. A new pair is chosen every H trading days; a name chosen again is kept (no cost). Periods: 2022 for reference, 2023-2024 validation, 2025 to now final test. Nothing was tuned. "Random" is the average of 300 random-pair runs with its 5th to 95th percentile. Tax is shown for the whole period (16% of a positive gain).

Today's liquid names, 5-10 years of survivors: all buy-and-hold numbers are biased upward, and with only two positions at a time one name can dominate a result.

## Return on 500 USD (percent), by period and holding period H
| Strategy | H | 2022 | 2023-24 | 2025-now |
|---|---|---|---|---|
| Cash | - | 0% | 0% | 0% |
| Hold two names (oil and gas + pharma, whole period) | - | +24% | -20% | +49% |
| Momentum (top 20-day return) | 5 | -28% | +31% | +141% |
| Momentum | 10 | -28% | +84% | +209% |
| Momentum | 20 | +11% | +62% | +106% |
| Low volatility (lowest 60-day vol) | 5 / 10 / 20 | -7% / -2% / +1% | -22% / -9% / +14% | +49% / +46% / +39% |
| Trend (above 200-day average, best 60-day) | 5 / 10 / 20 | -35% / -35% / -22% | +139% / +105% / +94% | +4% / +14% / +27% |
| Random pairs, average (5th to 95th) | 5 | -13% (-39 to +21) | +4% (-38 to +59) | +41% (-12 to +117) |
| Random pairs, average (5th to 95th) | 10 | -6% (-33 to +28) | +18% (-27 to +73) | +58% (-2 to +126) |
| Random pairs, average (5th to 95th) | 20 | -1% (-30 to +37) | +27% (-22 to +96) | +65% (+8 to +155) |

## Findings
1. No strategy is consistent. Trend gained +139% in 2023-24 and lost 35% in 2022 and gained 4% in 2025-now; momentum lost 28% in 2022 and gained 209% in the final test. The same rule swings between the worst and best of the random range.
2. Random pairs show how much is luck: with two positions, the 5th to 95th percentile spans about 100 to 200 points of return per period. One result from one pair means almost nothing. Comparing strategies needs many more independent decisions than a two-name account produces.
3. Short holds are expensive on 500 USD: 5-day rotation paid 13 to 84 USD in fees (3% to 17% of the account, up to 146 USD or 29% for random rotation) for 30 to 200 orders. 20-day holds paid 7 to 39 USD. Fees are the clearest result: longer holds lose less to costs.
4. Buy-and-hold of two names was +24% / -20% / +49%: dependent on which two names.
5. In the final test momentum with H=10 (+209%) and H=5 (+141%) beat the random 95th percentile, but the same rule lost 28% in 2022 and was only +84% and +31% in validation; this is not evidence of an edge.
6. Low volatility is the only rule that never lost much in a bad year (2022: -7% to +1%) and cut drawdowns (about -10% in 2023-25 against -20% to -35% for others), but it lagged in strong years.

## What this means
- The baselines are noise-dominated at this size. The plan must judge strategies on many names and many decisions (for example all 20 names in parallel as a paper portfolio, or each decision scored on its own, without the two-position limit) before concluding anything.
- Keep holding periods at 10 to 20 days: fees are 3 to 5 times lower than at 5 days.
- Any agent has to beat random with the same exposure and low-volatility on risk, across periods, not in one period.
