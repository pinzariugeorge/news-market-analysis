# Agent handbook (lean v1): single stocks tied to commodities and sectors

Short version of `HANDBOOK.md` (index-level principles) and `HANDBOOK_COMPANIES.md` (families) for agent runs; every number comes from those two files (checked by `src/verify_handbook.py`). Statistics were built from data up to 2022 and checked on 2023-2024. Not financial advice.

## 1. Rules of thumb
1. Surprise, not news, moves prices; a move that already happened (the stock, or its driver) is priced in. Yesterday's driver move does not predict today's stock move (lead correlations about zero, never stable).
2. Single-stock direction is close to a coin flip: up days are 50-53% in every family. "No trade" is a normal answer; take a long only with a concrete reason (a clear scheduled catalyst, a known mispricing) that you can name.
3. No selection rule has shown an edge on this universe: momentum, low volatility, trend, oversold, indicators and candlestick patterns all failed to beat holding the basket across periods. Do not use one as the reason.
4. Scale and persistence decide horizon: one-off incidents fade in days; policy or regime shifts last weeks. Prefer 10-20 trading day holds; a round trip costs about 0.3% on a small order and 5-day holds barely cover it.
5. Regime: volatility predicts the size of moves, not their direction. Big days cluster (for the S&P 500, 74% of 2% days fell in four years and 79% were within a week of another); after a 2% day the next day's average absolute move is about 1.25% versus 0.65% normally. In a stress regime (VIX spike) expect large moves both ways: size down or stay out; do not guess a rebound.
6. Index context: the S&P 500 has about 0.96% daily volatility and up days on 52.8% of days; single stocks move 1.5-3 times as much.
7. Transmission: event, then who gains or loses money directly, then costs and demand, then the stock. Effects weaken at each link; most events do not reach a stock.
8. Rates and the dollar are the master variables for gold miners and long-duration stocks; scheduled data (jobs, inflation, Fed) add variance, not direction.
9. Headlines or moves that only restate the market are not causes. If no cause is visible, say so.

## 2. Families (driver link = share of the stock's daily moves explained by the driver, build then validation)
### Oil and gas (XOM, CVX, COP, OXY)
- Driver: WTI crude, R-squared 0.23-0.30 then 0.24-0.37; stocks move 0.33-0.61 times as much as crude. Natural gas and Brent also matter.
- Volatility: 2.7% daily in the build period (includes 2020), 1.5% afterwards; days with a 3% move 15% then 5%.
- Catalysts: weekly crude inventories (Wednesday) and gas storage (Thursday) move the stocks little (Wednesday only 4% more active); Mondays about 16% more active (weekend news); OPEC+ meetings, earnings in late January, April, July, October.
- Event days (volume at least 2.5 times normal and a 3% move): 2.3 per name per year, mean move 10%.
### Gold miners (NEM, AEM, WPM, AU)
- Driver: gold, R-squared 0.35-0.38 then 0.34-0.46; miners amplify gold 1.3-2.1 times (AU the most). Rates, the dollar and safe-haven demand drive gold; streamers (WPM) carry less cost risk.
- Volatility: 2.5% then 2.2%; 3% moves on 17% then 14% of days. Lowest correlation with other families (0.14): a diversifier.
- Catalysts: Fed meetings, inflation and jobs reports (first Friday 5% more active), earnings with production and cost guidance; Thursdays 9% more active.
- Event days: 1.6 per name per year, mean move 6.6-7.0%; drift afterwards is inconsistent.
### Chips (NVDA, MU, AMD, INTC)
- Driver: the semiconductor sector, R-squared 0.48-0.66 then 0.29-0.70, beta 0.8-1.3; Intel decoupled in 2023-24 (0.29). Cloud and AI spending, memory prices, export rules, inventory cycles.
- Volatility: 3.0% in both periods; 3% moves on 23-24% of days, 5% moves on 7-9%. The most volatile family.
- Catalysts: earnings of chip and cloud companies, TSMC monthly sales (about the 10th); Thursdays 7% more active.
- Event days: 2.4-3.2 per name per year, mean move 8-10%, up 56-58%.
### Pharma (LLY, JNJ, ABBV, MRK)
- Driver: weak; sector link R-squared 0.40-0.55 then only 0.22-0.30. These stocks move on their own news: trial results, regulator decisions, drug-pricing policy, patent expiries.
- Volatility: 1.5% then 1.4%; 3% moves on 4-5% of days; the defensive family.
- Event days: 2.0-2.1 per name per year, mean move 6.4-6.7%, only 35-41% of them up (bad-news days dominate).
### Copper and uranium (FCX, SCCO, TECK, CCJ)
- Driver: copper, R-squared 0.28-0.35 then 0.28-0.46 (beta 0.9-1.4); Cameco follows the uranium ETF at 0.70 then 0.80. China demand data, inventories, supply outages, the dollar.
- Volatility: 3.0% then 2.4%; 3% moves on 23% then 18% of days.
- Event days: 2.5-2.7 per name per year, mean move 7.7%, up 58-70% (a positive tilt in this sample).

## 3. Portfolio sense
- Names in the same family are highly correlated (0.49-0.78) against 0.14-0.32 across families: hold at most one name per family.
- Earnings seasons (January-February, April-May, July-August, October-November) raise variance for every name; they are not a reason to be long.
- Drift in these names over 2023-2024 was positive on average (survivors in a rising market), so staying flat has an opportunity cost; do not treat that drift as a forecast.

## 4. Limits
- No earnings calendar; event days are a proxy. Event counts in the validation period are small (6-20 per family), so drift after events is noisy.
- Today's liquid names (survivor bias); driver ETFs are proxies. Parts about catalysts are general knowledge, not measured.
