# Family run fam_v0 (validation, 2023-2024) (2026-11-06)

Agent: Sonnet subagents with `agent/FAMILY_AGENT_PROMPT.md`, `handbook/HANDBOOK.md` and `handbook/HANDBOOK_COMPANIES.md`, one independent agent per decision day, each seeing only a past-only record (`results/fam_v0/records/`). 23 decision days (every 21 trading days from 2023-01-03 to 2024-11-04), 5 families each = 115 calls. A long call buys the family leader (highest-liquidity name from the point-in-time rule) at the close of the decision day and sells 5, 10 or 20 days later; a flat call is scored on the leader's counterfactual return. Portfolio: 1,000 USD, up to 3 longs with confidence at least 0.55, whole shares, real costs. Dashboard: `results/dashboard_family.html` (all prices, commodities, drivers, decisions). Data: `results/fam_v0/decisions.csv`, `summary.json`.

## Result
- All 115 calls were flat. Average confidence 0.50; no call reached the 0.55 needed for a long. The portfolio stayed in cash: 1,000 USD, 0 orders, 0 fees.
- Counterfactual (what holding the leader would have returned after about 0.3% cost): positive on 59% of calls, mean +1.48% per holding period. By family: chips +5.82%, copper and uranium +1.20%, pharma +0.36%, gold miners +0.19%, oil and gas -0.18%.
- Leaders basket (all five leaders, equal weight, 21-day holds, 0.3% cost): 1,000 -> 1,712 USD over the same period.
- Cost: about 75,000 tokens per decision day (23 days = about 1.7M tokens on the subscription).

## Reading
- The agent behaved as the prompt and our earlier tests suggested: no concrete edge, so no trades. That is consistent with every test so far (no selection rule beats the basket) but it is not evidence of skill: it missed the gains of a rising market in these names.
- Its confidence (0.50) was lower than the share of positive outcomes (59%). That gap reflects the names' drift in 2023-2024: today's liquid names in a bull run (survivor and hindsight bias), and chips in particular (+5.8% per period).
- Raising its confidence to trade more would only encode that drift; it is not a signal.
- Model memory of 2023-2024 cannot be excluded even though the prompt tells it to ignore later knowledge.

## Options
1. Accept: no edge found, so the agent stays in cash; judge the project as research.
2. Change the prompt (for example lower the long threshold) using this validation period only, then freeze it; this mostly buys exposure to drift.
3. Run the unchanged agent once on the reserved final test period (2025 onward) for completeness, about 1.7M tokens.
4. Stop spending subscription usage on agent runs and keep the tests cheap (rules and baselines).
