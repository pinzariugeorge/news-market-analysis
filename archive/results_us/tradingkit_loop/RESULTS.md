# TradingKit 1-hour loop: results (2026-11-07)

Stocks: NVDA, AMD, AVGO, 2021-05-03 to 2026-11-06 (9,672 hourly bars, the 10,000-bar free-plan cap). Gold spot: 2025-09-15 to 2026-11-06 (about 14 months, same cap). Cost 0.15% per side for stocks, 0.03% for gold (assumption). Long-only, 100% equity sizing, $1,000 start. Full table in `LOG.md`. 8 variants, 8 runs.

## Update: daily bars (wider window)
Same Donchian 20-bar breakout, 3 ATR trail, daily bars, whole history (2020-11 to 2026-11), parameters fixed in advance. Profit factor above 1.1 on all five instruments (gold 3.21, AMD 2.61, NVDA 2.07, AVGO 1.45, WTI 1.16), trades only 24-31 per instrument (so the 100-trade bar is out of reach on daily), drawdown 15% on gold but 34-40% on the stocks and 62% on WTI, and below buy-and-hold everywhere (gold +75% vs +114%). Daily is far more consistent and cheaper than 1h. Details in `LOG.md`.

## Verdict (1-hour runs)
**No strategy qualified.** The bars: net profit > 0, 100+ trades, profit factor > 1.10, max drawdown <= 20%, beats buy-and-hold, no look-ahead. None met all of them on any instrument; the closest (I3 on NVDA) failed on trade count (87) and buy-and-hold.

## Ranking (best first, by robustness then PF and drawdown)
| Rank | Strategy | Instrument | Trades | PF | Max DD % | Net % | Buy and hold % | Fails |
|---|---|---|---|---|---|---|---|---|
| 1 | I8 Donchian 70 / 3 ATR trail | Gold spot | 80 | 1.19 | 13.7 | +7.7 | +8.9 | trades < 100, slightly below B&H |
| 2 | I3 Donchian 70 / 3 ATR trail | NVDA | 87 | 1.72 | 19.9 | +174.9 | +1,205 | trades < 100, far below B&H |
| 3 | I7 Donchian 70 + SMA600 regime / 3 ATR | NVDA | 78 | 1.52 | 20.5 | +88.7 | +1,205 | trades, DD, B&H |
| 4 | I2 Donchian 140 / 4 ATR | NVDA | 56 | 1.62 | 31.4 | +95.2 | +1,205 | trades, DD, B&H |
| 5 | I4 Donchian 50 / 3 ATR | NVDA | 102 | 1.43 | 31.8 | +121.9 | +1,205 | DD, B&H |
| 6 | I5 Donchian 70 / 3 ATR | AMD | 83 | 1.23 | 36.0 | +50.8 | +480 | trades, DD, B&H |
| 7 | I6 Donchian 70 / 3 ATR | AVGO | 87 | 1.08 | 27.7 | +12.2 | +577 | PF, trades, DD, B&H |
| 8 | I1 RSI(2) pullback, SMA200 filter | NVDA | 267 | 0.63 | 51.2 | -48.1 | +1,205 | everything |

## What the loop showed
1. **Costs kill 1-hour mean reversion.** I1 made about +$16 before commission over 267 trades and lost $481 net (commission $497). At 0.3% round trip, a strategy needs a large average gain per trade, so fast systems fail.
2. **Breakouts with a trailing stop are the only thing with a positive profit factor,** because they make few trades with large winners (win rate 41-46%). But the NVDA result (PF 1.72) did not transfer with the same settings: AMD PF 1.23, AVGO PF 1.08, both with 28-36% drawdown. The NVDA result is in-sample luck: three settings were tried on NVDA before picking 70/3.
3. **Trade count and drawdown pull in opposite directions** (50-bar entry: 102 trades but 32% drawdown; 70-bar: 87 trades, 20%). A regime filter (I7) cut trades and return without fixing it.
4. **Buy-and-hold is the wall on these stocks.** NVDA +1,205%, AMD +480%, AVGO +577% in the window; no timing rule that sits in cash part of the time gets near that. The requirement "beat buy-and-hold" is only reachable on assets that did not trend as hard (gold was roughly flat versus its holding return).

## Reproduce I3 / I8 (best two)
Pine v6, long-only. Inputs: Breakout bars = 70, ATR trail mult = 3.0. `strategy(..., pyramiding=1, process_orders_on_close=true, commission 0.15 (stocks) or 0.03 (gold) percent, default_qty 100% of equity)`. Entry: `close > ta.highest(high, 70)[1]` while flat. Exit: `strategy.exit("LX", from_entry="L", stop=trail)` where `trail` starts at `close - 3*ATR(14)` at entry and ratchets up as `max(trail, close - 3*ATR(14))` each bar. Source is in the loop run history (I2 source with those inputs).

## Limits
- Only 8 variants and 1 instrument per idea except the Donchian 70/3 (3 stocks plus gold); no out-of-sample split beyond comparing instruments.
- Free plan: 10,000 bars per run, so gold covers only 14 months. Commodity spot data is sparse and observed-only.
- WTI and Brent were not tested.
- Sizing is whole shares from a $1,000 start; no slippage, no dividends.

## Update 2: build/validation matrix (daily) and universe check
See `daily_matrix.csv` and `../DONCHIAN_UNIVERSE.md`. Donchian 55 / 3 ATR trail was the best of five configs on the build window (2020-11..2023-12) and held out of sample (2024..2026-11): NVDA +66% (PF 3.1, DD 25%), AMD +73% (2.1, 30%), AVGO +16% (1.5, 25%), gold +53% (9.5, 9%), WTI +43% (5.4, 17%); on gold and WTI it beat buy-and-hold with about a third of the drawdown, on the stocks it trailed buy-and-hold. EMA cross and momentum without a stop: 50%+ drawdown. RSI(2) pullback: +10% on NVDA over the build window. Tested on all 40 names over 10 years the same rule returned about +2% a year with half the drawdown, so the five-instrument result is a best case.
