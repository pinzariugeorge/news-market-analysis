# Universe rule v2 (2026-11-06): five families, four single stocks each, chosen by a point-in-time rule

Research list, not a recommendation. No indexes and no ETFs. Solar removed on 2026-11-06 (user decision; it also lost at every holding period in our test). Earlier fixed list v1 is replaced by this rule.

## What the research said
- Index providers pick theme members in three steps: a liquidity and size screen, a relevance (revenue exposure) screen, then a ranking by market value. Examples: Morningstar thematic indexes drop names below minimum 3-month average trading volume and free-float market value, and keep existing members unless they fall below lower buffer levels ([Morningstar rulebook](https://indexes.morningstar.com/api/docs/68b03893c34d5aa87630dc53)); MSCI's thematic indexes take the top 30 by free-float market value ([MSCI](https://www.msci.com/eqb/methodology/meth_docs/4_MSCI_Global_Select_Top_30_Thematic_Indexes_Methodology_20211109.pdf)); BlueStar and Indxx require at least 50% of revenue from the theme for pure plays ([MarketVector](https://www.marketvector.com/rulebooks/download/BLOGR_Index_Guide.pdf)). The buffer idea matters: members change only when they clearly fall below a lower threshold, which limits turnover.
- Backtesting sources agree that a list chosen today and tested on past years is biased (survivorship and look-ahead). The fix is a point-in-time universe: rebuild membership at each date from information available then, and keep each snapshot ([overview of point-in-time universes](https://www.coinapi.io/learn/glossary/point-in-time-universe), [backtesting pitfalls](https://www.abctradinggroup.com/backtesting-pitfalls/)). Bias estimates in these sources range from about 1% to 4% a year and come from vendor blogs, so treat them as rough.

## Conclusion
A frozen list of names is the wrong thing to freeze. We freeze the rule and apply it at every date with data before that date. In live use the rule is rerun on a schedule, not by hand.

## The rule
1. Candidates per family: large listed companies in the industry, kept in `universe/candidates.csv` (family and ticker; written from industry membership, not returns). Families: oil and gas producers, gold miners, chips, pharma, copper and uranium.
2. At each date D use only bars before D. Eligible: at least 250 trading days of history.
3. Rank eligible names by the median daily dollar volume (close times volume) over the last 250 days. The median is used because a single event day can inflate a 30-day average.
4. Take the top four per family. In live use: recompute quarterly and replace a member only if it falls out of the top six (the buffer), to avoid churn.
5. Performance is never used. Selected names must still pass a tradability check at the broker.
Script: `src/select_universe.py`; output: `universe/rule_selections.csv`.

## Result of the rule, by date
Names selected as of each date (turnover in brackets):

| As of | Oil and gas | Gold miners | Chips | Pharma | Copper and uranium |
|---|---|---|---|---|---|
| 2021-12-31 | XOM, CVX, COP, OXY | NEM, WPM, KGC, AEM | NVDA, AMD, MU, INTC | PFE, JNJ, MRK, ABBV | FCX, TECK, CCJ, SCCO |
| 2022-12-31 | same set | NEM, AEM, WPM, FNV (2 changes) | NVDA, AMD, INTC, AVGO (2) | JNJ, PFE, MRK, ABBV (none) | same set |
| 2023-12-31 | same set | same set | same set | LLY, JNJ, PFE, MRK (2) | same set |
| 2024-12-31 | same set | NEM, AEM, KGC, WPM (2) | NVDA, AMD, AVGO, TSM (2) | same set | same set |
| 2025-12-31 | same set | same set | NVDA, AVGO, AMD, TSM | LLY, JNJ, ABBV, MRK (2) | same set |
| **2026-11-06 (current)** | **XOM, CVX, COP, OXY** | **NEM, AEM, WPM, AU** | **NVDA, MU, AMD, INTC** | **LLY, JNJ, ABBV, MRK** | **FCX, CCJ, SCCO, TECK** |

- The rule is stable in oil and gas, copper and uranium, and mostly in pharma and gold; chips change most (AVGO, TSM, INTC, MU rotate in and out).
- The current set equals the earlier fixed list v1 for every family, so no name changes now except removing solar.
- Why not market value as the main rank: it needs free-float data we do not have yet from a free source. Dollar volume is a measurable stand-in for size and liquidity. Add a market value screen when a reliable source is chosen.
- Intel stays in chips because it is liquid and in the industry; an AI-only or revenue-purity filter would drop it. A purity screen is not applied yet (it needs revenue data).

## Limits
- Candidates are today's list: companies that were acquired or delisted (for example Pioneer, Marathon Oil, Hess) are missing from Yahoo and cannot show up in past selections, so past universes lean toward survivors.
- Tradability for a Romanian retail client at Interactive Brokers Ireland is not verified. Several are ADRs or foreign-listed shares (AU, WPM, TECK, AEM).
- Volatility is very different across names (1.1% daily for J&J up to about 3.7% for AMD and Micron), so position sizes must depend on volatility.

## Test design that goes with it
- Holding period: 5, 10 and 20 trading days (maximum 20, user decision), plus holds around scheduled events.
- Time split: choose and tune on data up to 2022, validate 2023-2024, final test 2025 to now, with the universe recomputed at each rebalance date using the rule above.
- Costs: 0.24% per round trip for a small US order, with higher scenarios for other fee structures.
- Baselines: buy and hold each name, equal-weight family basket, trend rule, volatility rule, random with equal exposure.

## Change log
- 2026-11-06: rule v2 replaces the frozen list v1; solar removed (user decision); candidates file created.
