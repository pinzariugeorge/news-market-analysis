# TradingKit loop log (started 2026-11-07 13:52 UTC; 5-hour usage 26% at start; stop at 60% or 2 hours)

Windows (1h bars; the free plan caps a run at 10,000 bars including 300 warmup):
- Stocks (NVDA, AMD, AVGO): from 2021-05-03 to 2026-11-06 (`from=1620000000000`, `to=1793975400000`), about 9,700 bars. Buy-and-hold over this window is very large (NVDA about +1,200%), so beating it long-only with drawdown <= 20% is a very hard bar.
- Commodities (WTI, Brent, gold): spot series, observed bars only, 24/7 UTC bins, no volume; window set per run.
- Cost: 0.15% per side, no slippage modeled (engine default 0).

| # | Idea | Instrument | Window | Trades | PF | Max DD % | Net profit % | Buy and hold % | Qualifies |
|---|---|---|---|---|---|---|---|---|---|
| 1 | RSI(2)<10 pullback, SMA200 trend filter, exit close>SMA5, 3 ATR stop | NVDA | 2021-05-03..2026-11-06 | 267 | 0.63 | 51.2 | -48.1 | about +1,200 | no |

Note I1: before costs the result was about +16 USD on 1,000 over 267 trades (no edge); commission was 497 USD. At 0.3% round trip, any 1h strategy with hundreds of short trades loses to costs. Need fewer trades with larger average gain per trade (trend or breakout).
| 2 | Donchian 140-bar breakout, ratcheting 4 ATR trail | NVDA | 2021-05-03..2026-11-06 | 56 | 1.62 | 31.4 | +95.2 | about +1,200 | no (trades<100, DD>20, below B&H) |
| 3 | Donchian 70-bar breakout, 3 ATR trail | NVDA | 2021-05-03..2026-11-06 | 87 | 1.72 | 19.9 | +174.9 | about +1,200 | no (trades<100, below B&H) |
| 4 | Donchian 50-bar breakout, 3 ATR trail | NVDA | 2021-05-03..2026-11-06 | 102 | 1.43 | 31.8 | +121.9 | about +1,200 | no (DD>20, below B&H) |
| 5 | Donchian 70-bar breakout, 3 ATR trail (same params as I3, no tuning) | AMD | 2021-05-03..2026-11-06 | 83 | 1.23 | 36.0 | +50.8 | +480 | no (trades<100, DD>20, below B&H). NVDA result did not transfer. |

Buy-and-hold over the same window (from data/raw/stocks_cache.json): NVDA +1,205%, AMD +480%, AVGO +577%.
Variants tried so far: 5 (I1 to I5). I3's NVDA result (PF 1.72, DD 19.9) was picked after trying 140/4, 70/3, 50/3 on NVDA only; treat it as in-sample.
| 6 | Donchian 70-bar breakout, 3 ATR trail (same params as I3) | AVGO | 2021-05-03..2026-11-06 | 87 | 1.08 | 27.7 | +12.2 | +577 | no (trades<100, DD>20, below B&H) |
| 7 | Donchian 70 + regime filter (close>SMA600) + 3 ATR trail | NVDA | 2021-05-03..2026-11-06 | 78 | 1.52 | 20.5 | +88.7 | +1,205 | no (trades<100, DD>20.0, below B&H). Filter cut trades and return; not run on AMD/AVGO. |
| 8 | Donchian 70-bar breakout, 3 ATR trail, cost 0.03% per side (assumption) | Gold spot XAUUSD | 2025-09-15..2026-11-06 (about 14 months) | 80 | 1.19 | 13.7 | +7.7 | about +8.9 (GC=F proxy) | no (trades<100, below B&H) |

Stopped after 8 variants (usage 29%, about 5 minutes of wall time): nothing qualified and the pattern was clear. More variants would mostly add false discoveries.

## Daily bars (user asked for a wider window: holds of days, not hours)
Window: 2020-11-02 to 2026-11-06 (whole available history, about 1,500 daily bars, no 10,000-bar limit issue). Same strategy (Donchian 20-bar breakout, ratcheting 3 ATR trail), parameters fixed in advance, not tuned. Cost 0.15% per side stocks, 0.03% commodities. Buy-and-hold from stocks_cache.json and the GC=F / CL_F futures files (proxy for spot).

| # | Idea | Instrument | Trades | PF | Max DD % | Net profit % | Buy and hold % | Qualifies |
|---|---|---|---|---|---|---|---|---|
| D1 | Donchian 20 / 3 ATR trail, daily | NVDA | 24 | 2.07 | 34.1 | +382 | +1,439 | no (trades<100, DD>20, below B&H) |
| D1 | same | AMD | 24 | 2.61 | 39.6 | +268 | +510 | no (trades<100, DD>20, below B&H) |
| D1 | same | AVGO | 27 | 1.45 | 34.7 | +69 | +768 | no (trades<100, DD>20, below B&H) |
| D1 | same | Gold spot | 31 | 3.21 | 15.4 | +75.5 | +114 | no (trades<100, below B&H) |
| D1 | same | WTI spot | 27 | 1.16 | 61.9 | +32 | +146 | no (trades<100, DD>20, below B&H) |

Brent not run. Daily results are much more consistent across instruments than the 1-hour ones (profit factor above 1.1 on all five), with far lower cost drag (commission about 5-24% of start capital instead of 50%+).
