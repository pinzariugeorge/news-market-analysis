# Indicator and candlestick tests (2026-11-06)

Produced by `python -I src/run_indicator_tests.py` (data `results/indicator_tests.csv`). 45 candidate stocks from `universe/candidates.csv` (oil and gas, gold miners, chips, pharma, copper and uranium), 10 years of daily open/high/low/close from Yahoo. Long-only signals computed at the close of day t, entry at the close of day t+1, exit after H = 5, 10, 20 trading days, 0.25% cost per round trip. A name's signals within H days of its previous signal are skipped. "Excess" = the signal's mean net return minus the unconditional mean net return of the same stocks and period, which removes the stocks' own uptrend. Periods by entry date: build up to 2022, validation 2023-2024, final test 2025 on. Nothing was tuned. Survivor bias: only today's listed names (Pioneer, Marathon Oil, Hess missing).

Signals tested: RSI(14) below 30 and above 70; MACD (12, 26, 9) bullish cross; golden cross (50-day over 200-day average); close crossing above the 20-day average; close below the lower Bollinger band (20, 2); close above the previous 20-day high (breakout); bullish engulfing candle; hammer after a downtrend; three white soldiers.

## Results (excess return in percent, positive periods out of three)
| Signal | H=5 | H=10 | H=20 | In which periods positive |
|---|---|---|---|---|
| RSI below 30 | +0.48 | +0.51 | +1.33 | 3 of 3 at every H |
| Bollinger lower band touch | +0.34 | +0.15 | +0.83 | 3, 2, 3 |
| RSI above 70 | -0.12 | -0.36 | -0.50 | 1 |
| MACD bullish cross | -0.17 | -0.05 | -0.29 | 1 |
| Golden cross | +0.01 | +0.21 | -0.89 | 1, 2, 0 |
| Close above 20-day average | -0.06 | +0.02 | -0.07 | 1-2 |
| 20-day breakout | -0.16 | -0.23 | -0.19 | 0-1 |
| Bullish engulfing | +0.05 | +0.01 | -0.01 | 2 |
| Hammer in a downtrend | -0.44 | -0.16 | -0.18 | 1 |
| Three white soldiers | -0.28 | -0.30 | -0.10 | 0-1 |

Unconditional mean net return of these stocks: +0.23% (5 days), +0.72% (10), +1.71% (20).

## Findings
1. Candlestick patterns did not help: engulfing is flat, hammer and three white soldiers are negative.
2. Trend and breakout signals (golden cross, MACD cross, 20-day breakout, crossing above the average) added nothing and breakouts slightly lost to the unconditional average.
3. The only signals positive in all three periods were buying oversold stocks (RSI below 30, Bollinger lower band), with t-statistics of about 2 to 2.8 on the pooled trades. This is not robust: (a) oversold signals fire on the same days for many stocks in market-wide selloffs, so trades are not independent; averaging per date, the t-statistics fall to 1.0-1.7 for RSI below 30 and about -0.3 to 1.3 for Bollinger, none significant; (b) 30 combinations were tested, so a t of 2.7 is expected by chance; (c) the test period is dominated by the sharp 2025 rebound; (d) buying dips of stocks that survived to today favors winners that recovered.
4. Conclusion: standard indicators and candlestick patterns gave no reliable edge on this universe. Oversold buying is the one idea worth keeping for a further test (it fits the handbook's volatility-cluster and rebound observations), but only with out-of-sample data and a market-wide-selloff filter.

## Not tested
Short signals, combinations of indicators, intraday data, volume signals, indicators on index or commodity data, and any parameter tuning (by design).
