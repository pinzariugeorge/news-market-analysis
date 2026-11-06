# Wide test: selection rules judged on many decisions (2026-11-06)

Produced by `python -I src/run_wide_test.py` (data `results/wide_test.csv`). Instead of one account with 2-3 positions, every decision date scores a whole basket: the 20 point-in-time rule-selected names (5 families x 4, `universe/UNIVERSE_RULE.md`). At each decision date (every H = 5, 10, 20 trading days) each rule picks a subset of names using closes up to that day; the subset is held equal-weight from the next close for H days. Every position is charged a full 0.25% round trip per decision (conservative; no netting of repeats). "Excess" is the rule's basket return minus the benchmark basket (all 20 names, equal weight) on the same dates; statistics are across decision dates, which do not overlap. Periods: 2022 (reference), 2023-2024 (validation), 2025 to now (final test). Nothing tuned. Survivor bias remains (today's listed names).

Rules: momentum (top half by 20-day return), reversal (bottom half), low volatility (lowest half by 60-day volatility), trend (above the 200-day average), oversold (RSI below 30), random half (mean of 200 draws; it must be about zero).

## Benchmark basket: mean net return per decision (all 20 names, equal weight)
| H | 2022 | 2023-24 | 2025-now |
|---|---|---|---|
| 5 days | -0.16% | +0.08% | +0.52% |
| 10 days | -0.14% | +0.47% | +1.28% |
| 20 days | 0.00% | +1.32% | +2.77% |

## Excess over the benchmark (percentage points per decision; n = number of decision dates)
| Rule | H | 2022 | 2023-24 | 2025-now |
|---|---|---|---|---|
| Momentum | 5 / 10 / 20 | +0.05 / +0.05 / +0.34 | -0.10 / -0.49 / -0.50 | -0.10 / -0.04 / +0.51 |
| Reversal | 5 / 10 / 20 | -0.05 / -0.05 / -0.34 | +0.10 / +0.49 / +0.50 | +0.10 / +0.04 / -0.51 |
| Low volatility | 5 / 10 / 20 | +0.11 / +0.07 / +0.46 | -0.26 / -0.54 / -1.30 | -0.17 / -0.28 / -0.84 |
| Trend (above 200-day) | 5 / 10 / 20 | +0.14 / +0.39 / +0.60 | +0.16 / +0.25 / 0.00 | +0.08 / -0.07 / +0.21 |
| Oversold (RSI below 30) | 5 / 10 / 20 | -1.06 (n=17) / -2.40 (n=7) / -3.18 (n=3) | -0.15 (n=44) / -1.86 (n=20) / -3.31 (n=11) | +2.45 (n=10) / +9.95 (n=4) / none |
| Random half | all | -0.01 to +0.03 | -0.02 to 0.00 | -0.01 to +0.02 |

## Findings
1. No rule consistently beats the equal-weight basket. Almost all t-statistics are below 2, and the signs flip between periods (momentum and reversal are mirror images by construction and swap roles).
2. Trend is the only rule with positive excess in most cells (6 of 9 positive, one zero), but the gain is small (0.1 to 0.6 points) and the t-statistics are below 1.4: a hint to re-check out of sample, nothing more.
3. Low volatility lagged the basket in 2023-2025 (-0.3 to -1.3 points); it only helped in 2022.
4. The earlier oversold result does not survive: oversold names underperformed in 2022 and 2023-24 and only gained in the 2025 rebound on 4 to 10 decision dates. It also rarely fires (1 to 2 names per date).
5. The random-half rule is about zero everywhere, so the test itself is unbiased.
6. The best "strategy" in this test is the diversified basket itself (about 0.0%, +1.3%, +2.8% per 20 days net of full costs in the three periods), which only reflects that these are today's liquid names in a recent bull run.
7. Combined with the earlier indicator and 2-3 position results: simple selection rules (momentum, volatility, trend, oversold, candlestick patterns) show no reliable edge on this universe; holding a diversified basket and keeping costs low matters more than the selection rule.

## What this means for the plan
- An agent must beat the equal-weight basket and the random baseline after costs across periods; so far no rule does.
- With 500-1,000 USD the whole basket cannot be held (20 names); the realistic account holds 2-3 names, where luck dominates (see `results/UNIVERSE_BASELINES.md`).
