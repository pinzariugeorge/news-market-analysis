# Broad screen: what has been trading well (data to 2026-11-05/06)

Built by `src/build_universe.py universe/broad_screen.csv` (Yahoo daily bars, last year). Full numbers in `universe/broad_screen_metrics.csv`. Research only. Past returns do not predict future returns; "trading well" here means strong recent trend with enough volatility and liquidity to be worth testing. Many of these are US-listed ETFs, used only as measurement proxies: EU retail clients generally cannot buy US-listed ETFs, so a UCITS equivalent or the individual stocks would be used.

## Market regime now
- The last month was a sharp pullback: S&P 500 ETF -5.7%, Nasdaq 100 -14.6%, semiconductors ETF -28.4%, copper miners -16%, uranium -22%. Most tech and semiconductor names fell 20-40% in a month. By our handbook this is a stress cluster: expect large moves in both directions, size down.
- Leadership over 3-6 months: health care (XLV +27.8% over 6 months; Eli Lilly +15% over 3 months), oil and energy (WTI +10.7% and Brent +12.2% over 3 months; Chevron +14%, Exxon +8%), and defensives (consumer staples +11.7% over 1 month).
- Weakness: semiconductors, copper, uranium, lithium, solar, silver (silver -20% over 3 months, -12% over 1 month).

## Sector ETFs (return over 3 months, volatility daily)
Health care +11.6%, energy +7.2%, staples +7.2%, financials -0.2%, utilities -0.7%, materials -1.0%, discretionary -1.9%, industrials -12.3%, technology -13.6%.

## Commodities (futures, 3 months)
Brent +12.2%, WTI +10.7%, natural gas +7.6% (but -31% over one year and -60% from its high; daily volatility 5.6%), corn +0.6%, copper -5.2%, wheat -7.5%, gold -7.8% (3 months) and -2.0% (1 month), cocoa -10.7%, platinum -12.8%, coffee -18.9%, silver -20.3%.

## Single stocks (3 months; above-200-day-average flag in the CSV)
Up: Eli Lilly +15.1%, Chevron +14.1%, Apple +9.8%, Exxon +8.0%, Microsoft +7.2%, Newmont +6.0%, Tesla +4.6%. Down: AMD -16%, Nvidia -19%, Alphabet -20%, Micron -25% (but +175% over one year), Cameco -30%, Broadcom -32%, Caterpillar -34%.

## Input-to-asset links (2 years of daily data)
How much of an asset's daily moves is explained by its cost or price driver on the same day (R-squared), and whether yesterday's driver move predicts today's asset move (lead correlation):

| Asset | Driver | Same-day correlation | R-squared | Beta | Lead (driver yesterday -> asset today) |
|---|---|---|---|---|---|
| Gold miners ETF (GDX) | Gold futures | 0.78 | 0.61 | 1.41 | -0.06 |
| Newmont | Gold futures | 0.73 | 0.53 | 1.30 | -0.04 |
| Occidental | WTI crude | 0.63 | 0.40 | 0.49 | 0.03 |
| Exxon | WTI crude | 0.60 | 0.36 | 0.33 | 0.03 |
| Energy sector ETF | WTI crude | 0.58 | 0.34 | 0.30 | 0.06 |
| Chevron | WTI crude | 0.56 | 0.31 | 0.30 | 0.05 |
| Copper miners ETF | Copper futures | 0.59 | 0.35 | 0.77 | -0.01 |
| Freeport-McMoRan | Copper futures | 0.48 | 0.23 | 0.71 | -0.01 |
| Delta Air Lines | WTI crude (fuel cost) | -0.26 | 0.07 | -0.25 | -0.01 |
| Cameco | Uranium ETF | 0.89 | 0.79 | 0.97 | -0.01 |
| Micron | Semiconductors ETF | 0.81 | 0.65 | 1.48 | -0.04 |
| Nvidia | Semiconductors ETF | 0.78 | 0.61 | 0.86 | -0.05 |
| RTX | Defense ETF | 0.76 | 0.58 | 0.88 | 0.05 |
| Lockheed Martin | Defense ETF | 0.47 | 0.22 | 0.60 | 0.05 |
| Eli Lilly | Health care ETF | 0.68 | 0.46 | 1.53 | 0.03 |
| Caterpillar | Copper futures | 0.24 | 0.06 | 0.27 | 0.04 |
| Solar ETF | Silver futures | 0.25 | 0.06 | 0.18 | 0.01 |

## What the data says
- Commodity-linked equities follow their driver strongly on the same day (gold -> miners R-squared 0.53-0.61, oil -> energy 0.31-0.40), weaker for cost-side links (jet fuel -> airlines R-squared 0.07; silver -> solar 0.06). The cost-input idea works best for producers of the commodity, not for its users.
- Yesterday's driver move does not predict today's stock move (lead correlations between -0.06 and +0.06, about zero). The market prices the input on the same day. So an edge cannot come from reacting to a driver after the fact; it would have to come from anticipating the driver (scheduled reports, positioning, forecasts) or from the pair itself (hedging, spread).

## Holding horizon test (5 years of daily data, 20 names in 6 families plus SPY; 2026-11-06)
Rule: long if the previous 20 days were up, else flat; one entry every h days. Costs: 0.24% per round trip for a small US stock order (commission plus spread allowance) and 1.2% for a 3 EUR fixed fee on a 500 EUR order. Pooled over all names.

| Hold h days | Entries | Average abs move | Always-long return | Momentum-rule return | Win rate | Net of US cost | Net of EU cost |
|---|---|---|---|---|---|---|---|
| 1 | 11,965 | 2.17% | 0.09% | 0.10% | 50.8% | -0.14% | -1.10% |
| 3 | 3,956 | 3.96% | 0.27% | 0.23% | 52.4% | -0.01% | -0.97% |
| 5 | 2,376 | 5.09% | 0.45% | 0.26% | 52.2% | +0.02% | -0.94% |
| 10 | 1,203 | 7.20% | 0.88% | 0.81% | 53.4% | +0.57% | -0.39% |
| 20 | 596 | 10.56% | 1.82% | 1.66% | 54.5% | +1.42% | +0.46% |

Average absolute move over a 5-day window by family: solar 7.8%, chips 5.5%, copper and uranium 5.2%, gold 4.5%, pharma 3.8%, oil and gas 3.2%, index 1.7%. Average always-long return over 20 days: chips +4.0%, copper and uranium +2.3%, gold +2.1%, oil and gas +1.7%, pharma +1.6%, index +0.9%, solar -0.2%.

Reading:
- A bigger move does not mean more money: solar moves most and earned nothing, chips earned most.
- The momentum rule did no better than always holding at any horizon (it trails it at 3, 5, 10 and 20 days). The positive net figures at 10 and 20 days come from the names' own uptrend, not from timing.
- Costs: at 1 day the fee eats the whole average gain; at 20 days it is small. The EU fixed fee is only covered at 20 days.
- Strong caveat: the 20 names were chosen because they have done well recently (hindsight selection), so the always-long returns are biased upward. Nothing here is a forecast or a recommendation.

## AI as a theme (11 names: chips NVDA, AMD, AVGO, MU, TSM, ASML; platforms MSFT, GOOGL, META, AMZN, PLTR; 2026-11-06)
- Last month: almost every AI chip name fell 22-40% (Micron -40%, AMD -37%, TSMC -25%, ASML -25%, Nvidia -24%, Broadcom -23%); semiconductor ETF -28%. Platforms were mixed: Microsoft +1%, Amazon flat, Meta -16%, Alphabet -19%, Palantir -20%. Over one year Micron is +175% and AMD +70%, while Nvidia is -3% and Broadcom -18%.
- Equal-weight basket of the 11 names over 5 years: +261% in total with a maximum drawdown of -50%.
- Correlation: average pairwise daily correlation over the last year is 0.61 among AI chips, 0.32 among platforms, 0.34 across all 11, against 0.79 among oil majors. Chips move together, so holding several of them is less diversification than it looks.
- Horizon test (5 years, pooled): chips average absolute move 2.3% (1 day), 5.2% (5 days), 7.2% (10 days), 10.9% (20 days); always-long return per entry 0.16%, 0.83%, 1.66%, 3.53%; the trailing-20-day momentum rule did not beat always holding for chips (3.18% vs 3.53% at 20 days) but did for platforms at 10 and 20 days (1.72% vs 1.10%, 2.94% vs 2.38%), win rate 52% at 5 days rising to 59-60% at 20 days. Same hindsight caveat: these names were chosen because they did well.
- Cost inputs and catalysts for AI: electricity and data-center power, memory prices (DRAM and HBM), advanced chip supply (TSMC capacity), export rules, and customers' capital spending guidance. Scheduled: earnings of Nvidia and the large cloud companies, TSMC monthly sales, memory price reports.

## Holding period test, single stocks only (decision 2026-11-06: no indexes or ETFs in the traded universe)
20 single stocks in the six families (oil and gas, gold miners, chips, pharma, copper and uranium, solar), 5 years of daily data, pooled; one entry every h days; cost 0.24% per round trip for a small US order.

| Hold h days | Entries | Avg abs move | Always-long return | Net of cost | Net per day held | Momentum-rule return | Win rate |
|---|---|---|---|---|---|---|---|
| 5 | 4,920 | 5.2% | 0.48% | 0.24% | 0.049% | 0.27% | 52.1% |
| 10 | 2,460 | 7.4% | 0.95% | 0.71% | 0.071% | 0.83% | 53.0% |
| 20 | 1,220 | 10.8% | 1.96% | 1.72% | 0.086% | 1.69% | 53.9% |
| 40 | 600 | 16.4% | 4.42% | 4.18% | 0.104% | 2.26% | 52.3% |
| 60 | 400 | 18.7% | 6.18% | 5.94% | 0.099% | 5.10% | 57.2% |

- Net return per day held rises with the holding period and flattens at 40-60 days (about 0.10% a day); 5-day holds barely cover costs.
- The ranking holds in both halves of the sample (first half to 2024-05-08, second half after): longer is better in each, so the result is not from one lucky period; but both halves are inside a rising market for these names.
- The momentum rule never beat simply holding. Win rates stay at 52-57%: the gain comes from the average size of winners, not from calling direction.
- By family, average 20-day return: chips +3.5%, copper and uranium +2.3%, gold +2.0%, oil and gas +1.7%, pharma +1.6%, solar -0.2% (solar lost at every horizon, win rate 40-47%).
- Caveat: the names were chosen because they did well lately (hindsight selection), so these numbers overstate what to expect. They show cost behavior and horizon shape, not forecasts. The test goes only to 60 days.
