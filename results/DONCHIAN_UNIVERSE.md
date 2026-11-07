# Daily Donchian breakout on the whole single-stock universe (2026-11-07)

Rule (daily, long-only): buy at the close when the close is above the highest close of the previous 55 days; exit when the close falls below a ratcheting stop (highest close minus 3 x ATR since entry). Cost 0.15% per side, all-in per name. Script `src/run_donchian_universe.py` (closes only: ATR proxied by 1.4 x mean absolute daily change; breakouts on closes). 40 names, 5 families, from `data/raw/stocks_cache.json`, 2016-11 onward. Split per CLAUDE.md: build 2016-11..2022-12, validation 2023-01..2024-12; 2025+ not evaluated here. Sanity check against TradingKit (2024-01..2026-11): NVDA +69% vs +66%, AMD +72% vs +73%, AVGO +2% vs +16%, so the approximation is close.

| Window | Mean return, strategy | Mean return, buy-and-hold | Median, strategy | Names positive | Mean drawdown, strategy | Mean drawdown, B&H | Equal-weight basket, strategy (DD) | Equal-weight basket, B&H (DD) |
|---|---|---|---|---|---|---|---|---|
| Build 2016-11..2022-12 | +11.5% | +157% | +3.6% | 22 of 40 | 35.5% | 54.2% | +11.5% (10.3%) | +157% (35.9%) |
| Validation 2023..2024 | +6.4% | +49.5% | +0.2% | 20 of 40 | 18.5% | 33.9% | +6.4% (7.4%) | +49.5% (16.4%) |

By family (strategy vs buy-and-hold, validation): oil_gas -1% vs -14%, gold_miners -3% vs +36%, chips +22% vs +146%, pharma +3% vs +5%, copper -7% vs 0%.

## Reading
- The rule cuts drawdown by roughly half but also cuts almost all of the return: about +2% a year over six years across the universe, and about half of the names lose money. It is not an edge, it is a more cautious way of being long.
- The TradingKit wins (NVDA, AMD, AVGO, gold, WTI at +16% to +73% in 2024-2026) came from instruments that trended strongly. Across all 40 names the result is near zero, which is the selection effect again: the best-looking instruments in a test were chosen from a few candidates that happened to trend.
- Gold miners lost money with the rule while gold itself made money: trends in the metal did not carry into the stocks.
- Caveats: survivor bias (names that exist today), closes-only approximation, 0.15% cost without slippage, no dividends.
