# Trading universe (research list, not recommendations)

Date of data: 2026-11-05/06 (Yahoo daily bars, last 1 year). Built by `src/build_universe.py`; input `universe/solar_chain.csv`, output `universe/solar_chain_metrics.csv`. Research and simulation only. Nothing here says a name will make money: volatility, size and liquidity describe the past year only.

## The idea (from the user)
Instead of the S&P 500, follow a theme through its supply chain: pick a cost component or demand driver (for solar: polysilicon, silver, modules, inverters, trackers, installers, storage), find the listed companies on each link, and watch how news on that component moves them. Companies must be currently listed and tradable now; history (including 2020) is only for building and testing the handbook.

## How a name enters the universe (criteria, measurable)
1. Listed now, tradable by a Romanian retail client (US stocks yes; US-listed ETFs no; EU stocks yes). Check the broker's list before trading.
2. Liquidity: 30-day average dollar volume large enough that a small order does not move the price (here: above about $5M a day).
3. Enough movement to cover costs: daily volatility several times the per-trade cost. High volatility also means high risk.
4. A causal link to a trackable driver (component price, policy, rates) so that news can be reasoned about with the handbook.
5. Data available for history and news (still to be sourced for single companies).

## Solar value chain, last 12 months

| Ticker | Role | Avg $ volume/day | Daily vol | Avg abs move | Days with 5%+ move | Max drawdown | 1-year change |
|---|---|---|---|---|---|---|---|
| FLNC | battery storage | 43M | 7.4% | 4.9% | 35.6% | -84% | -74% |
| SEDG | inverters | 88M | 6.0% | 4.4% | 35.2% | -67% | -33% |
| CSIQ | modules, storage | 20M | 5.5% | 4.1% | 32.4% | -74% | -61% |
| SHLS | electrical balance of system | 46M | 5.3% | 4.0% | 30.0% | -48% | -2% |
| ENPH | microinverters | 211M | 5.3% | 3.6% | 23.6% | -66% | -7% |
| ARRY | trackers | 40M | 5.0% | 3.8% | 27.6% | -74% | -37% |
| RUN | installer and financer | 83M | 5.0% | 3.7% | 26.4% | -68% | -52% |
| S92.DE (EUR) | inverters (Germany) | 6M | 4.4% | 3.5% | 22.5% | -30% | +79% |
| NXT | trackers | 239M | 4.3% | 3.4% | 22.0% | -51% | -7% |
| SI=F | silver (cell input cost) | n/a | 4.2% | 2.9% | 18.3% | -57% | +9% |
| AMAT | equipment supplier | 3.1B | 3.9% | 3.0% | 18.0% | -56% | +37% |
| JKS | modules (China) | 7M | 3.7% | 2.8% | 16.4% | -74% | -64% |
| DQ | polysilicon (China) | 6M | 3.6% | 2.6% | 13.2% | -72% | -61% |
| FSLR | modules (US) | 467M | 3.3% | 2.4% | 10.0% | -47% | -28% |
| WCH.DE (EUR) | polysilicon, chemicals | 5M | 2.8% | 2.1% | 7.1% | -26% | +17% |
| TAN (US-listed ETF) | solar basket | 66M | 2.4% | 2.0% | 2.0% | -46% | -12% |
| SPY (reference) | S&P 500 | 33.8B | 0.9% | 0.6% | 0% | -9% | +9% |

(Percent columns are rounded; exact values in the metrics CSV. The 1-year change uses the first and last close of the range.)

## What the numbers say
- Movement is not the problem: solar names move 3-7% a day, five to eight times the S&P 500, and a third of days exceed 5% for the most volatile ones.
- The cost of that movement is risk: most names fell 47-84% from a peak inside one year and eleven of the fourteen single stocks are down over the year. A strategy on these names must control losses before it chases gains.
- Liquidity is uneven: FSLR, ENPH, NXT, SEDG, RUN trade $80-470M a day; JKS, DQ, S92.DE, WCH.DE only $5-7M, so small orders are fine but spreads may be wider.
- Fees matter less at these volatilities, but a fixed fee still bites on a small account.
- Solar is currently a distressed, news-heavy sector (China oversupply and consolidation, US tariffs and policy, falling installations in China, volatile polysilicon prices), which is why it moves a lot and why prices can be driven by policy headlines the handbook has no entry for yet.

## Context found while building this list (sources are partly low-authority)
- Polysilicon prices rose in January 2026, then fell for many weeks in spring and were flat to slightly up by late October, per [pv magazine](https://www.pv-magazine.com/2026/01/09/polysilicon-prices-jump-over-9-as-china-supply-tightens/) and the [TaiyangNews price index](https://taiyangnews.info/price-index/taiyangnews-pv-price-index-cw43-2026).
- Chinese manufacturing capacity is said to be about double global demand, with consolidation and losses at major producers ([Energy Intelligence](https://www.energyintel.com/0000019c-5692-df6d-abbf-dfdae7680000)).
- US policy: a Section 232 polysilicon probe and a reported 15% tariff plan are described as the industry's main supply risk ([PV Tech](https://www.pv-tech.org/section-232-polysilicon-probe-wood-mackenzie-solarpv-donald-trump/)); details unconfirmed.
- Not verified: the status of installers (for example Sunnova) and of some European makers. Check each company before use.

## Open questions and next steps
- Which themes besides solar (for example lithium, copper, semiconductors, uranium, oil services)? Each theme gets its own CSV in this folder.
- Company-level news and earnings dates are not sourced yet (candidates: Benzinga stock-news dataset, the `fnspid_news` subset; see `TODO.md`).
- Handbook needs company-level and component-price entries (earnings reactions, guidance, tariffs, component price moves).
- Real per-trade costs by account size must be in every backtest (see `TODO.md`).
