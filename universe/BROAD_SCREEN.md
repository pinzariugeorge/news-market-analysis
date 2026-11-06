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
