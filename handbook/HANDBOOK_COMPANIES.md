# Handbook v1: single stocks and commodity links (five families)

Companion to `HANDBOOK.md` (index-level principles and event types still apply). Numbers come from `src/build_family_stats.py` / `handbook/family_stats.csv`: written from data up to 2022-12-31 ("build"), checked on 2023-2024 ("valid"). The final test period (2025 onward) was not used. Items marked (general knowledge) are not measured. Names are the rule-selected universe (`universe/UNIVERSE_RULE.md`); today's names, so survivor bias remains. US-listed ETFs (SMH, XLV, URA) appear only as measurement drivers. Not financial advice.

## 1. How to use this (for the agent)
1. Identify the family of the stock, then its driver (section 2) and the scheduled catalysts that fall inside the holding period.
2. Expect the stock to follow its driver the same day, not the next day: yesterday's driver move predicts today's stock move at about zero (lead correlation -0.07 to +0.01 for oil, gold, copper and uranium in build; chips and pharma were mildly negative, about -0.03 to -0.17, in build and about 0 in valid; valid range -0.06 to +0.10). No stable next-day signal. Do not trade the reaction to a driver that already moved; trade the expected scheduled event or stay out.
3. Size by volatility: pharma about 1.5% a day, oil and gas 1.5-2.7%, gold 2.2-2.5%, copper and uranium 2.4-3.0%, chips 3.0% (family section).
4. Do not hold two names of the same family: average within-family daily correlation is 0.49-0.78, against 0.14-0.32 between families (gold has the lowest between-family correlation, 0.14).
5. Prefer holds of 10-20 trading days (costs; see `results/UNIVERSE_BASELINES.md`); no selection rule (momentum, volatility, trend, oversold, candlestick patterns) has shown an edge (`results/WIDE_TEST.md`, `results/INDICATOR_TESTS.md`). "No trade" is a normal answer.

## 2. Driver links (daily returns, R-squared / beta; build -> valid)
| Family | Driver | R-squared build -> valid | Beta | Reading |
|---|---|---|---|---|
| Oil and gas (XOM, CVX, COP, OXY) | WTI crude futures | 0.23-0.30 -> 0.24-0.37 | 0.33-0.61 | Moderate and stable; stocks move about a third to a half as much as crude |
| Gold miners (NEM, AEM, WPM, AU) | Gold futures | 0.35-0.38 -> 0.34-0.46 | 1.3-2.1 | Stable; miners amplify gold by 1.3 to 2 times (AU the most) |
| Chips (NVDA, MU, AMD, INTC) | Semiconductor sector ETF | 0.48-0.66 -> 0.29-0.70 | 0.8-1.3 | Strong for NVDA, MU, AMD; Intel decoupled in valid (0.29) |
| Pharma (LLY, JNJ, ABBV, MRK) | Health care sector ETF | 0.40-0.55 -> 0.22-0.30 | 0.8-1.5 | Weak in valid: pharma moves on its own news |
| Copper miners (FCX, SCCO, TECK) | Copper futures | 0.28-0.35 -> 0.28-0.46 | 0.9-1.4 | Moderate and stable |
| Uranium (CCJ) | Uranium ETF | 0.70 -> 0.80 | 1.06 | Strong (an ETF largely made of the same stocks) |
Next-day lead correlation is near zero everywhere (see rule 2). The 2020-04 negative-price oil roll was removed from the oil driver.

## 3. Family entries
### 3.1 Oil and gas producers (XOM, CVX, COP, OXY)
- Base rates (pooled names, daily): volatility 2.7% (build, includes 2020) and 1.5% (valid); days with a 3% move: 15% and 5%; up days about 50%. Volatility is much lower outside crises.
- Drivers (general knowledge): crude and natural gas prices, OPEC+ decisions, inventories, geopolitical supply risk, demand outlook; cost inputs: drilling and services costs, steel, labor; refiners and airlines move opposite to crude for different reasons.
- Scheduled catalysts (general knowledge): weekly US crude inventories (Wednesday), natural gas storage (Thursday), OPEC+ meetings, quarterly earnings (late January, April, July, October). Measured weekday activity: Mondays are about 16% more active than other days (weekend news gap); Wednesday is only 4% more active, so the inventory report moves the stocks little on average. First Friday of the month: 10% more active.
- Event reaction: see `HANDBOOK.md` 3.5. Volume-shock days (volume at least 2.5 times normal and a 3% move; a proxy for earnings and news): 2.3 per name per year in build, mean move 10%; the 10-day drift after them is noisy (only 6 events in valid).
- Amplifiers: low spare capacity, conflict near supply routes. Dampeners: high inventories, spare capacity.
### 3.2 Gold miners (NEM, AEM, WPM, AU)
- Base rates: daily volatility 2.5% (build), 2.2% (valid); 3% moves on 17% and 14% of days; up days 50%.
- Drivers: gold price (miners move 1.3-2.1 times as much, measured), real interest rates, dollar strength, central bank buying, safe-haven demand (general knowledge); cost inputs: energy, labor, all-in sustaining cost; royalty and streaming companies (WPM) carry less cost risk (general knowledge).
- Scheduled catalysts (general knowledge): Fed meetings, inflation and jobs reports, quarterly earnings with production and cost guidance. Measured: Thursdays are 9% more active, first Fridays 5% more.
- Event reaction: volume-shock days 1.6 per name per year, mean move 6.6-7.0%; after-event drift is inconsistent between periods.
- Lowest correlation with other families (0.14): a diversifier.
### 3.3 Chips (NVDA, MU, AMD, INTC)
- Base rates: daily volatility 3.0% in both periods; 3% moves on 23-24% of days; 5% moves on 7-9%; up days about 52%. The most volatile family.
- Drivers: strong sector link (R-squared 0.5-0.7); demand from cloud and AI spending, memory prices (DRAM, HBM) for MU, chip supply and export rules, inventory cycle (general knowledge).
- Scheduled catalysts (general knowledge): earnings of the large chip and cloud companies, TSMC monthly sales (about the 10th of each month), memory price reports. Measured: Thursdays 7% more active; first Fridays about 5% less.
- Event reaction: volume-shock days 2.4-3.2 per name per year, mean move 8-10%, up 56-58% of the time.
- Intel behaves differently from the AI-driven names (decoupled from the sector in 2023-24).
### 3.4 Pharma (LLY, JNJ, ABBV, MRK)
- Base rates: daily volatility 1.5% (build) and 1.4% (valid); 3% moves on 4-5% of days; defensive family.
- Drivers: pipeline readouts and trial results, FDA decisions, drug-pricing policy, patent expiries, obesity-drug demand for LLY (general knowledge); the sector link weakened in 2023-24 (R-squared 0.22-0.30).
- Scheduled catalysts (general knowledge): earnings, FDA decision dates, major medical conferences. Measured weekday and first-Friday effects are negligible (within 4%).
- Event reaction: volume-shock days 2.0-2.1 per name per year, mean move 6.4-6.7%, only 35-41% of them up (bad news days dominate).
### 3.5 Copper and uranium (FCX, SCCO, TECK, CCJ)
- Base rates: daily volatility 3.0% (build), 2.4% (valid); 3% moves on 23% and 18% of days; up days 50%.
- Drivers: copper price (R-squared 0.28-0.46), China demand and manufacturing data, inventories, mine outages and supply disruptions, dollar strength; uranium: spot price, utility contracting, nuclear policy (general knowledge).
- Scheduled catalysts (general knowledge): monthly China data, quarterly earnings, supply news. Measured: first Fridays 5% more active.
- Event reaction: volume-shock days 2.5-2.7 per name per year, mean move 7.7%, up 58-70% of the time (a positive tilt in this sample).

## 4. Base rates table (pooled names; build -> valid)
| Family | Daily volatility % | Avg abs move % | Days >= 3% | Days >= 5% | Up days % |
|---|---|---|---|---|---|
| Oil and gas | 2.66 -> 1.49 | 1.65 -> 1.12 | 15.1 -> 5.2 | 4.8 -> 0.5 | 50.9 -> 49.5 |
| Gold miners | 2.51 -> 2.21 | 1.76 -> 1.62 | 17.4 -> 14.3 | 5.1 -> 3.4 | 50.0 -> 50.5 |
| Chips | 3.04 -> 2.97 | 2.11 -> 2.14 | 23.4 -> 24.1 | 9.0 -> 7.2 | 51.9 -> 52.3 |
| Pharma | 1.55 -> 1.41 | 1.02 -> 0.95 | 4.8 -> 4.0 | 1.3 -> 0.7 | 52.7 -> 51.9 |
| Copper and uranium | 2.97 -> 2.37 | 2.11 -> 1.78 | 23.4 -> 17.5 | 7.5 -> 3.8 | 50.0 -> 50.1 |
(For comparison the S&P 500 had daily volatility 0.96% over 1950-2019 and 3% moves on 1.2% of days.) Single-stock direction is close to a coin flip: up days are 50-53% in every family.

## 5. Limits
- Event days are a proxy (no earnings calendar yet): a volume shock plus a 3% move. Event counts in the validation period are small (6-20), so drift figures are noisy and signs differ between periods; treat the event rows as magnitude guidance, not as a drift signal.
- Today's names (survivor bias); the build period contains 2020 and the oil anomaly; driver ETFs are US-listed proxies.
- Parts marked (general knowledge) are unmeasured and should be tested before an agent relies on them.
- No timing edge has been found for any family so far; this handbook describes behavior (size, drivers, catalysts), not a trading rule.
