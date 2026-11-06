# Review of big-move days, 2008-2019

What this is: every S&P 500 day with a move of 2% or more in 2008-2019 (247 days) was labeled by event type (`src/review_big_days.py`, results in `handbook/bigday_review.csv`) and compared with handbook entries. Labels were assigned by me WITH HINDSIGHT as a handbook-building check, not a prediction test. 2020 and later were not touched. Labels are approximate (one cause per day, judged from history and the headlines).

## Findings
1. **Big days cluster in a few episodes.** 74% fall in four years (2008: 72, 2009: 55, 2011: 35, 2018: 20); 2017 had none; 79% are within 7 calendar days of another big day. So most of the risk sits in rare stress regimes (financial crisis, the sovereign-debt / US-downgrade summer, the 2018 Q4 rates-and-trade slide). Regime detection (recent volatility, trend, stress headlines) matters more than any single headline.
2. **The news layer rarely names the cause.** 85 of 247 big days (34%) have no headline at all that day; of the 162 with headlines only 60 (24% of all big days) contain a cause keyword (Fed, downgrade, tariff, bank, ...). Many headlines are noise (gadget reviews, local news). Agents cannot rely on this dataset to explain a move; better causal sources are needed (see `TODO.md`).
3. **Event-type mix of big days:** credit/banking/sovereign stress 121 (49%), economic data/growth 54 (22%), central bank 26 (11%), foreign shocks 11, trade 9, oil/commodity 7, elections 4, market-structure spikes 4, earnings 3, sector rotation 3, geopolitical 2, fiscal 2, Brexit 1.
4. **Observed ranges vs handbook:**

| Type | Days | Down share | Median abs move | Range | Handbook before | Change |
|---|---|---|---|---|---|---|
| Credit/banking/sovereign stress | 121 | 60% | 3.2% | -9.0% to +11.6% | -3% to -9% down, same-size relief | Widened: relief rallies reached +11.6% |
| Economic data/growth | 54 | 50% | 2.6% | -8.9% to +3.8% | +/-0.5% to 1.5%, rarely >2% | Too low in recessions: data inside a downturn gave -3% to -9% days |
| Central bank action | 26 | 38% | 2.5% | -3.3% to +5.1% | hawkish -1 to -3, dovish +1 to +4 | Fits; easing in a crisis up to +5% |
| Foreign shock | 11 | 73% | 2.4% | -3.9% to +3.9% | n/a | Fits (-2% to -4%) |
| Trade policy | 9 | 89% | 2.5% | -3.2% to +2.7% | -1 to -3 / +1 to +3 | Fits |
| Oil/commodity | 7 | 43% | 2.4% | -2.9% to +2.9% | index low except large moves | Fits |
| Elections | 4 | 25% | 2.3% | -2.4% to +4.1% | within +/-2% | Up to +/-4% in a crisis (Nov 2008) |
| Market structure / vol spike | 4 | 75% | 3.9% | -4.1% to +5.0% | very sharp, partly reversed | Fits; the rebound day can be +5% |

5. **Direction:** across all 247 big days a bit more than half were down; direction within an episode alternates, so a fall is often followed within days by a large rise (-9.0% on 2008-10-15 and +10.8% on 2008-10-28; -2.7% on 2018-12-24 and +4.96% on 2018-12-26).
6. **Biggest gaps for agents:** (a) detecting the stress regime early, (b) separating scheduled events (Fed, jobs, elections: can be anticipated) from unscheduled shocks (cannot), (c) no cause in the news for three out of four big days.

## What the handbook says as a result (applied in `HANDBOOK.md`)
- Credit stress ranges widened to include +11% relief days; the data entry gets a recession-regime clause; the election entry range is widened for crisis conditions.
- New principle: most large moves occur inside clusters; after the first 2%+ day in a cluster, expect more large moves in both directions, so size down or stay out rather than guess direction.
