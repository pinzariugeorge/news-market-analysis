# Baselines on 2008-2019 (development period)

Produced by `python -I src/run_baselines.py` (3,021 trading days, cost 0.02% per 100% change in position). Index price only: no dividends, cash earns 0%. Every position for day t uses information up to the close of day t-1. Data: `results/baselines_2008_2019.csv`.

| Baseline | Total return | Annualized | Annual vol | Sharpe | Max drawdown | Exposure |
|---|---|---|---|---|---|---|
| buy and hold | +119.6% | 6.8% | 19.6% | 0.43 | -53.9% | 100% |
| cash | 0% | 0% | 0% | 0 | 0% | 0% |
| vol rule (long only in volatility regimes 1-3) | +131.9% | 7.3% | 11.7% | 0.66 | -27.3% | 79% |
| capped long (100% in regimes 1-3, 50% in regime 4) | +134.2% | 7.4% | 14.1% | 0.57 | -39.0% | 100% (avg size 90%) |
| trend rule (long above the 200-day average) | +96.0% | 5.8% | 10.9% | 0.57 | -16.6% | 76% |
| random long/flat, same exposure as capped long (1,000 sims) | +82.2% mean | 5.0% (5th-95th: 2.2% to 8.0%) | 18.6% | 0.35 (0.21-0.51) | -50.9% | 90% |

## Reading
- The bar to beat is a no-model rule: the volatility rule matches buy and hold in return, with 40% less volatility, half the drawdown and a Sharpe of 0.66 against 0.43. Most of its advantage is avoiding stormy periods (2008: -22.6% against -38.5%).
- Rules based on past volatility and trend reduce risk more than they add return; both lag in strong rallies (2019: +28.9% buy and hold against +14% for both).
- Random timing with the same exposure averages well below the rules (4.97% annualized), so timing carries information; luck alone gives a wide spread (2.2% to 8.0% annualized), so one backtest result means little without comparison to this spread.
- An agent is only worth deploying if it beats these after costs, in the dev period first, then once on 2020 and 2021-2024. Judge by Sharpe and drawdown as well as return.
- Caveat: the volatility rule and the 200-day rule were chosen as generic, well-known rules, not tuned on this data; still, 2008-2019 is the only period examined so far.
