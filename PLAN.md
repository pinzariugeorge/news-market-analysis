# Plan v2 (2026-11-06): trade current companies and commodities through Interactive Brokers Ireland

Research and simulation only until the gates below are passed. Not financial advice. Replaces the index-only pipeline in `STRATEGY.md` as the working plan; the older pipeline and rules stay valid where not contradicted.

## What we learned that shapes the plan
1. **Costs decide frequency.** A fixed 3 EUR order is 0.6% of a 500 EUR trade, so daily trading of EU-listed products cannot pay. US-listed single stocks on IBKR tiered pricing cost far less for small orders (about 0.0035 USD per share, minimum 0.35 USD, cap 1% of trade value, plus small exchange and regulatory fees; for example 10 shares of a 50 USD stock is the 0.35 minimum, about 0.07% of a 500 USD order). Currency conversion (reported 0.002% with a 2 USD minimum, but sources conflict up to 0.2%) argues for converting once and holding USD cash. Futures (about 0.15-0.65 USD per contract) need a larger account and margin; micro-contract rates are unconfirmed.
2. **Inputs are priced on the same day.** Over two years the previous day's move in oil, gold, copper or an industry ETF has about zero correlation with today's move in the related stock (`universe/BROAD_SCREEN.md`). An edge must come from anticipating scheduled events or from relative moves, not from reacting to a driver that already moved.
3. **Producers follow their commodity, users do not.** Gold -> miners R-squared 0.53-0.61, oil -> energy 0.31-0.40; jet fuel -> airlines 0.07, silver -> solar 0.06. For the cost-input idea, start with producers (oil, gold, copper, uranium, memory chips) rather than the buyers of an input.
4. **The regime is stressed.** Last month: Nasdaq 100 -14.6%, semiconductors -28%. Handbook principle 12 says big moves cluster: expect large moves both ways, size small.
5. **Volatility is not an edge and most movers are down.** Solar names moved 3-7% a day and most fell 47-84% from a peak within a year. Loss control comes first.
6. **News coverage is thin.** The index headline set named a cause on fewer than one in four big-move days; we have no company-level news or earnings dates yet.
7. **Longer holds pay for themselves.** On single stocks, 5-day holds barely cover costs while 20-60 day holds earned about 0.09-0.10% per day held net of cost, in both halves of five years of data; a momentum rule never beat holding. The test is biased by hindsight selection (`universe/BROAD_SCREEN.md`). Decision 2026-11-06: holding period capped at 20 trading days, so we test 5, 10 and 20 days plus event windows.
8. **Screening many names and keeping the winners fools you.** Anything chosen because it did well in the same data used to judge it is overfit. Selection and testing must use different periods.

## Candidate theme families (research list, not recommendations)
Single stocks and commodity drivers only: no indexes and no ETFs in the traded universe (user decision 2026-11-06; index and ETF numbers in the screens are measurement references).

| Family | Why it is testable | Scheduled catalysts | Names to measure first |
|---|---|---|---|
| Oil and gas producers | Same-day link to crude (R-squared 0.3-0.4) and liquid | Weekly US inventories, OPEC meetings, gas storage, earnings | Exxon, Chevron, Occidental; crude and natural gas as drivers |
| Gold miners | Strong link to gold (R-squared 0.5-0.6) | Fed meetings, inflation and jobs data, earnings | Newmont, Barrick, Agnico Eagle |
| Memory and chip makers | Very liquid, very volatile, strong link to a sector ETF | Earnings, memory price reports, export rules | Micron, Nvidia, AMD, TSMC |
| Pharma and biotech | Leader over 6 months; event-driven | Earnings, trial results, regulatory decisions | Eli Lilly, Novo Nordisk |
| Copper and uranium producers | Commodity-linked, but both down hard in a month | Inventory data, policy, earnings | Freeport-McMoRan, Cameco |

Start with all five families (solar removed 2026-11-06), four names each chosen by the point-in-time rule in `universe/UNIVERSE_RULE.md` (rerun quarterly); narrow later by validation results.

## Phases and gates
**Phase 1: costs and access (before any more modelling).**
- Write a cost model `src/costs.py` (commission, regulatory fees, spread allowance, currency conversion) by instrument and account size (500 EUR, 5,000 EUR).
- Check the official IBKR Ireland fee schedule (stocks, US and EU, futures, currency), the account opening time for Romania, the paper trading account, the API (TWS or web API), whether US single stocks are available to Romanian retail clients, and Romanian tax and dividend withholding treatment.
- Gate: a written cost table that every backtest imports.

**Phase 2: data.**
- Daily history for the chosen names and drivers (Yahoo to start): 2000 onward where it exists.
- Scheduled calendars: earnings dates, EIA inventories, OPEC meetings, FOMC, jobs and inflation releases.
- News: a company-level source with dates (Benzinga stock-news dataset or `fnspid_news`; see `TODO.md`).
- Gate: every backtest day has past-only prices, calendar facts and headlines.

**Phase 3: handbook v1 for single names and commodities.**
- Entries for earnings reactions, guidance, commodity inventory reports, policy and tariff headlines, and driver-to-stock links.
- Built from older history only.
- Time split for single names (new, replaces the index split): build up to 2022, validate 2023-2024, final test 2025 to now. The 2020 test year stays reserved for the index work.

**Phase 4: baselines then agent, both with real costs.**
- Holding horizons tested: 5, 10 and 20 trading days (maximum 20, user decision) plus event windows.
- Baselines per name: buy and hold, trend rule, volatility rule, event-window rules (hold only around scheduled catalysts), random with equal exposure.
- Agent runs only on event days (earnings, reports) and in regime changes, not every day. This lowers both fees and model usage.
- Gate: net-of-cost return and drawdown better than the best baseline, on validation and then the final test, with enough trades for the result to mean something (at least about 100 independent decisions) and a maximum loss limit respected.

**Phase 5: paper trading on the IBKR paper account via the API.**
- One routine per day; every run reviewed; kill switch; log every order.
- Gate: at least three months, results within the range of the simulation, no operational errors.

**Phase 6: live, small.** Only with the user's explicit go-ahead. Position cap, daily loss cap, no leverage, no options, no shorting at first.

## Rules carried over
- Decisions use only information before the decision time. 2020 is not used to write the handbook. Costs are inside every result. The old-news source stays parked in `TODO.md`.
- Keep the model on the Pro subscription (subagents, chronological multi-day sessions); the API remains optional and needs approval (estimates in `TODO.md`).

## Open decisions for the user
1. Which two or three theme families to start with.
2. Account size to design for (500 EUR, 5,000 EUR, other).
3. Instruments allowed: US single stocks, EU-listed ETFs and ETCs, futures. CFDs are excluded by default.
4. Whether to allow API spend later (about 15 USD per 300 decisions with Sonnet), or stay on the subscription.
