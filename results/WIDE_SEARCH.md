# Wide strategy search on ~200 single stocks and 7 commodity futures (2026-11-07)

Data: Yahoo daily OHLCV (adjusted for splits and dividends) for 201 liquid US-listed names (plus a few ADRs) from 2003, and 7 commodity futures from 2000 (`src/download_ohlc.py`, `data/raw/` is git-ignored). Universe is today's large caps, so it has survivor and winner hindsight; the tests reduce it with a point-in-time liquidity filter (top K by trailing dollar volume). Data cut at 2024-12-31; 2025+ untouched (reserved final test). Costs 0.15% per side (stocks), 0.05% (futures); signal at the close, trade one day later; cash earns 0. About 90 configurations were run in total, so any single good-looking line should be discounted for multiple testing. Scripts: `src/strat_lab.py` (portfolio lab), `strat_lab2.py` to `strat_lab6.py`, `strat_lab_cmd.py`, `strat_lab_pername.py`.

## Results
| Idea | Verdict |
|---|---|
| Cross-sectional momentum (6-1, 12-1; top 10/20/40), monthly | Beat the equal-weight basket in the hindsight universe (top 10, 6-1: +37% a year in 2016-22 vs 18% for the basket). With the point-in-time top-100 filter over 2004-2024 the monthly excess return is statistically zero (t = 0.2 to 0.9; top 200 only: t = 2.5 for 6-1 top 10, which includes weaker-liquidity survivors). Drawdown 60%+ in 2008. No edge worth trading. |
| Residual momentum, same-calendar-month seasonality, industry momentum | All fail the pre-registered rule (excess t >= 2.5, positive in 3 of 4 periods). Residual momentum t about -1, seasonality t = -2.8 (negative), industry momentum t = 0.7. |
| 52-week-high proximity, low-volatility among winners, dip buying, turn of month, sell-in-May | No consistent edge (CAGR 3% to 14%, below the equal-weight basket; turn-of-month negative in validation). |
| Per-stock Donchian 55 / 3 ATR (and 100 / 3) on all 201 names | Positive in 54% to 65% of names per period, median return +2% to +13%, beats buy-and-hold in only 6% to 23% of names; drawdown about half of buy-and-hold. A cautious way to be long, not an edge. |
| Portfolio of Donchian trend followers (K = 20 or 40) | CAGR 9% to 12%, drawdown 12% to 31%, below the equal-weight basket (13% to 17%). |
| Commodity trend following (7 futures, 2000-2024) | Worked in 2001-2010 (+12% a year, supercycle), about +1% a year in 2011-2022, negative in 2023-2024 (-4% to -8%). Gold alone held up (+17% in 2023-24, equal to buy-and-hold). |
| Trend filter on a diversified basket (hold when S&P above its 200-day or 10-month average, else cash) | Halves the drawdown (about 23% vs 53% over 2004-2024) at the cost of return (8% to 11% a year vs 13% to 16%); Sharpe about equal or slightly better (0.8 to 0.9 vs 0.7 to 0.8). Risk management, not extra return. |

## What this says
- No free-data rule tested here adds return over holding a diversified basket once the universe hindsight is reduced. The profitable-looking runs came from instruments that happened to trend (NVDA, AMD, gold).
- What reliably worked was owning stocks through a rising market, with a trend filter to cut the deep drawdowns: expect roughly 7% to 11% a year with 20%+ drawdowns before tax in the survivor-biased history; on $1,000 that is about $70 to $110 a year before 16% tax. That is market return, not a trading edge.
- TradingKit stopped verifying the account partway through ("membership could not be verified"), so the extra catalogue names (AAPL, MSFT, GOOGL, AMZN, META, NFLX, TSLA, PLTR, JPM, BAC, SAP, AZN, silver, platinum, palladium, Brent) were covered by the local engine, which matched TradingKit on NVDA, AMD and AVGO (+69/+72/+2 vs +66/+73/+16 in 2024-2026).

## Catalogue names, local replica of the TradingKit test (window 2020-11-02..2024-12-31, Donchian 55 / 3 ATR, `src/run_catalogue_local.py`)
TradingKit refused every call on 2026-11-07 ("membership could not be verified"), so the 20 catalogue names were run locally: 15 stocks (AAPL, MSFT, GOOGL, AMZN, META, NFLX, TSLA, PLTR, JPM, BAC, SAP, AZN, NVDA, AMD, AVGO) and 5 commodities (gold, silver, platinum, WTI, Brent; futures proxies). Strategy positive in 16 of 20, beats buy-and-hold in 0 of 20, lower drawdown in 20 of 20 (for example AAPL +40% vs +136%, DD 19% vs 31%; NVDA +187% vs +974%; gold +8% vs +40%; silver -20% vs +23%). Same conclusion: it cuts drawdown, it does not add return. Palladium and MC (LVMH) were not available locally.
