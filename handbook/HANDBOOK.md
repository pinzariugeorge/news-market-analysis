# Market Impact Handbook (v0 draft)

Status: draft written from general finance knowledge and checked against 2008-2019 only (base rates and example days below). 2020 (test) and 2021+ (holdout) were NOT used. Numbers marked "~" are rough general-knowledge estimates, not fitted. Refine from 2008-2019 data, never from 2020.

Used by: simulation agents (as part of their expert-analyst context) and live day trading. Not financial advice.

## 1. Principles (apply to every event)
1. **Surprise, not news, moves prices.** The effect depends on outcome vs. what was already expected. An expected rate hike moves little; a surprise moves a lot. If the headline says "as expected", default to no effect.
2. **Priced in.** Slow-building stories (long negotiations, gradual deterioration) are partly in prices before the headline. Sudden, unscheduled events carry the most price impact.
3. **Scale matters.** Compare the event to the size of the relevant system (a 0.1% supply loss is noise; a 5% loss is a shock). Ask: how many dollars, how many people, how many companies, how long?
4. **Persistence decides horizon.** One-off incident: hours to days. Structural change or escalation (war, sanctions, policy regime shift, credit crunch): weeks to months, with repeated waves of news. Track storylines, not just single headlines.
5. **Regime matters.** The same news hits harder when volatility is high, valuations are stretched, leverage is high or the market is already falling. In calm, trending markets bad news is often bought.
6. **Transmission chain.** Event -> who gains or loses money directly -> input costs / demand / funding conditions -> sectors -> index. Effects weaken at each link; most events never reach the index.
7. **Index vs. sectors.** The S&P 500 is diluted. Many events move one sector or a few stocks by 1-5% while the index barely moves. Prefer sector-level calls when the channel is narrow.
8. **Fed and rates are the master variable.** Discount rates and liquidity affect all stocks; growth stocks and long-duration assets most.
9. **Volatility clusters.** After a big move, big moves are more likely in either direction (see base rates). Direction is far less predictable than size.
10. **"No meaningful effect" is a first-class prediction** and usually the most likely one. Only call a move when the channel, scale and surprise all line up.
11. **Headlines describe the market too.** Many headlines report the market's own move ("Dow plunges 700 points"). That is past information for the next decision, not a new cause. Look for the cause (policy, data, credit, geopolitics) and for how much of it is already in the price.

## 2. Base rates (S&P 500 daily, 2008-2019, 3,020 days; from `data/processed/market_days.csv`)
| Stat | Value |
|---|---|
| Daily standard deviation | 1.23% (mean +0.03%) |
| Up days | 53.9% |
| \|move\| >= 1% | 25.8% of days |
| \|move\| >= 2% | 8.2% |
| \|move\| >= 3% | 3.2% |
| \|move\| >= 5% | 0.7% |
| Day after a drop of 2% or more (n=141) | next day up 58%, mean +0.21% |
| Day after a rise of 2% or more (n=106) | next day up 49%, mean -0.19% |
| Mean \|move\| the day after a 2%+ day | 1.49% vs 0.78% overall (volatility clusters) |

Caveat: 2008-2009 dominates the large-move counts. Direction after big days is only weakly predictable; the size of the next move is much more predictable than the sign. Any single-day direction call starts from roughly 54% up.

## 3. Event-type entries
Fields: mechanism | typical reaction | horizon | amplifiers | dampeners | sectors | index effect | confidence | evidence (2008-2019).

### 3.1 Central bank surprise (rate decision, guidance, balance-sheet change)
- Mechanism: changes discount rates and liquidity; surprise vs. market pricing is what counts.
- Reaction: expected decision ~0 to +/-0.5%. Hawkish surprise: index -1% to -3%, growth/tech and rate-sensitive sectors worst. Dovish or new stimulus surprise: +1% to +4%, larger in a crisis.
- Horizon: day of decision, then weeks if it changes the rate path or starts/ends a program.
- Amplifiers: high valuations, high leverage, market already uncertain, surprise at the first or last meeting of a cycle. Dampeners: well-telegraphed move, clear forward guidance.
- Sectors: banks gain from a steeper curve; utilities, REITs, tech suffer from higher rates; gold and bonds react opposite to the dollar.
- Index effect: medium to high. Confidence in direction given a clear surprise: medium.
- Evidence: Dec 2018 hawkish Fed/balance-sheet talk preceded the 2018-12-24 low (-2.71% that day). Market-wide relief rallies followed easing signals in 2019.

### 3.2 Economic data surprise (jobs, inflation, GDP, PMI)
- Mechanism: changes growth and rate expectations; in weak-economy regimes good data can lift stocks, in inflation regimes strong data can hurt (rate fears).
- Reaction: in-line ~0; large miss/beat: +/-0.5% to 1.5%. Rarely more than 2%.
- Horizon: day; the trend of several readings matters more than one.
- Amplifiers: data is the key input the Fed watches, thin liquidity. Dampeners: one noisy reading, revisions.
- Sectors: cyclicals (industrials, banks) vs. defensives; homebuilders on housing data.
- Index effect: low to medium. Confidence: low unless several readings agree.

### 3.3 Credit or banking stress (bank failure, funding market freeze, sovereign debt crisis)
- Mechanism: threatens the payment system and lending; hits earnings of everything via funding costs and fear of contagion.
- Reaction: large and persistent. Index -3% to -9% in single days when the system itself is in doubt; relief rallies of the same size on rescue plans.
- Horizon: weeks to months, in waves, until authorities backstop.
- Amplifiers: hidden leverage, interbank freeze, failure of a rescue plan or surprise legislative rejection. Dampeners: credible backstop already announced.
- Sectors: financials first (-), then everything cyclical; defensives, gold, treasuries gain.
- Index effect: high. Confidence in direction: high for the first shock, low for timing of the bottom.
- Evidence: 2008-09-29 House rejects bailout plan, S&P -8.81%; Oct-Nov 2008 days of +/-6% to 12% moves; 2011-08-08 US credit downgrade, -6.66% (sovereign-credit fear on top of euro-area debt stress).

### 3.4 Geopolitical shock (war, attack, sanctions, military escalation)
- Mechanism: uncertainty plus possible supply disruptions (energy, grain, chips) and sanctions-driven costs.
- Reaction: usually a sharp but short drop (-1% to -3%) that often reverses in days to weeks unless the conflict hits oil/trade flows or escalates; defense, gold, oil gain.
- Horizon: day one dominates; persistence only if the economy is hit through commodities or trade.
- Amplifiers: involvement of major economies, energy infrastructure, an already fragile market. Dampeners: contained, regional, no commodity link.
- Sectors: energy and defense (+); airlines, travel, importers (-).
- Index effect: low to medium. Confidence: medium for sector direction, low for the index after day one.

### 3.5 Oil and commodity supply events (OPEC decision, outage, pipeline, tanker incident)
- Mechanism: supply change -> crude price -> energy company revenue vs. consumer/transport costs.
- Reaction: a single small incident (<1% of global supply): ~0 to +2% in crude, fading within days; the stock effect on energy names is smaller. A large or sustained supply change or an OPEC policy shift: crude +/-5% to 15%, energy stocks +/-2% to 6%.
- Horizon: days for incidents; months for policy shifts and demand-supply imbalances.
- Amplifiers: low spare capacity, low inventories, existing conflict. Dampeners: high inventories, spare capacity, quick restoration.
- Sectors: energy producers (same sign as crude); airlines, cruise, transport, chemicals (opposite); inflation expectations.
- Index effect: low, except in large moves (energy is ~10% of the index; a collapse in crude can also signal weak demand or credit stress in energy debt).
- Confidence: medium for sign, low for size.

### 3.6 Elections and political outcomes
- Mechanism: expected policy changes (tax, regulation, trade, spending) re-rated by sector; the uncertainty premium resolves.
- Reaction: the surprise matters; resolution of uncertainty often lifts the market regardless of winner. Index move typically within +/-2% on the day; sector rotations larger.
- Horizon: day to weeks; policy implementation later.
- Amplifiers: unexpected winner, pledge of a sharp policy break (trade, tax, regulation). Dampeners: divided government, expectation of gridlock.
- Sectors: depend on the platform (energy, healthcare, financials, defense, infrastructure).
- Evidence: 2016-11-09: overnight futures fell sharply on a surprise result, yet the S&P closed +1.11% that day, led by financials, as policy expectations (tax cuts, deregulation) re-rated sectors. Lesson: the first reaction can reverse within hours; predict sectors, and be wary of calling the index from overnight moves.

### 3.6b US midterm elections (calendar event, every 4 years in November)
- Mechanism: not a surprise-driven event in most cases. Uncertainty about the balance of Congress (and so about tax, spending, regulation) weighs on the market before the vote and resolves after it. Divided government (gridlock) is usually read as "less policy risk".
- Typical pattern (published research, mostly pre-2019 data; some quoted averages may include later years, so treat them as context and do not tune to them): the midterm year is the weakest year of the four-year presidential cycle, with the market often weak or choppy until the vote and then rising. The 12 months after a midterm are positive in the large majority of cases since 1950, with averages in the low-to-mid teens in percent; Q4 plus the next two quarters were positive far more often than average quarters. Sources are listed in `handbook/SOURCES.md`.
- Our own check on the handbook period (S&P 500 closes, election day to later; from `data/processed/market_days.csv`):
  | Election day | Prior 3 months | Day after | +1 week | +1 month | +3 months | +6 months | +1 year |
  |---|---|---|---|---|---|---|---|
  | 2010-11-02 | +5.9% | +0.37% | +1.7% | +2.3% | +9.3% | +12.9% | +2.1% |
  | 2014-11-04 | +4.8% | +0.57% | +1.4% | +3.0% | +2.5% | +3.8% | +4.5% |
  | 2018-11-06 | -3.6% | +2.12% | -1.2% | -4.4% | -1.7% | +4.6% | +12.0% |
- Reading: the day after the vote was positive all three times (+0.4%, +0.6%, +2.1%): uncertainty resolving, not a big fall. The pattern is "rise" far more than "fall". The 2018 day-after rally (best post-midterm day in decades) was followed by a Fed-driven slide into the 2018-12-24 low, so the post-election bounce is not a trend by itself; rates and other drivers can override it. Only 3 cases in our data, so low statistical weight.
- Practical rules: (1) before the vote: reduced conviction, expect choppiness, do not add risk just because "midterm rally" is coming; (2) the day after: modest positive bias (+), strongest if the market was down into the vote and the outcome is divided government; (3) next months: bullish bias unless a stronger driver (Fed tightening, credit stress) contradicts it; (4) if an unexpected outcome changes tax/regulation expectations, reason by sector (see 3.6).
- Index effect: low to medium. Confidence: medium for a positive drift over 6-12 months, low for any single day.

### 3.7 Referendums and political shocks with unclear mechanics (e.g., Brexit)
- Mechanism: uncertainty about trade, currency, the banking system and policy; flight to safety.
- Reaction: sharp drop on the surprise, then recovery in days to weeks if there is no contagion; the local currency and local banks suffer most.
- Evidence: 2016-06-24 Brexit vote: S&P -3.59%, mostly recovered within about two to three weeks.
- Index effect: medium for 1-2 days. Confidence: medium on direction when the outcome was not the consensus.

### 3.8 Trade policy and tariffs
- Mechanism: raises costs, cuts margins and demand for exposed firms, adds uncertainty about supply chains.
- Reaction: a headline escalation: -1% to -3%; a deal or truce: +1% to +3%. Repeated headlines fade in impact as markets adapt (headline fatigue).
- Horizon: episodic over months; each step re-prices.
- Amplifiers: escalation across a broad set of goods, currency moves, a deadline. Dampeners: rumors, partial or delayed measures.
- Sectors: industrials, semiconductors, materials, agriculture, large exporters (-); domestic-focused firms less exposed.
- Evidence: 2019-08-05 S&P -2.98% as the yuan weakened past a key level and tariff escalation fears rose.

### 3.9 Company-specific shocks (earnings surprise, guidance, scandal, product failure, M&A)
- Mechanism: changes expected earnings of that firm (and read-through to peers).
- Reaction: stock +/-3% to 20% on a big surprise; peers +/-1% to 3%; the index barely moves unless the firm is a mega-cap (a handful of stocks are 20%+ of the index).
- Horizon: day, with post-earnings drift for days to weeks in the same direction.
- Sectors: the firm's industry and its suppliers/customers.
- Confidence: medium on direction given a clear beat/miss versus consensus; none without consensus.

### 3.10 Sector regulatory or legal events (drug pricing, antitrust, bank rules, emissions)
- Mechanism: changes the profit pool of a sector.
- Reaction: sector +/-2% to 8% on credible, scheduled or enacted measures; headlines about proposals fade if they are unlikely to pass.
- Horizon: weeks, with a drift as details emerge.
- Index effect: low. Confidence: medium on sector sign, low on the index.

### 3.11 Natural disasters and accidents
- Mechanism: local destruction of capacity and insured loss; supply chain and commodity effects.
- Reaction: local or sector effects (insurers, rebuilders, specific supply chains); the index is usually ~0 unless a major economic hub is hit.
- Horizon: days to months for supply chains.
- Confidence: low on the index.

### 3.12 Technology and structural shifts (new product waves, AI, disruptive entrants)
- Mechanism: re-rating of winners and losers within sectors.
- Reaction: sector rotation, mostly within days to months; valuation-driven moves can overshoot.
- Index effect: low to medium via mega-caps.

### 3.13 Market-structure events (flash crash, circuit breaker, volatility spike, forced deleveraging)
- Mechanism: mechanical selling from leveraged or volatility-linked products and stop-outs; unrelated to fundamentals.
- Reaction: very sharp intraday moves, often partly reversed; volatility stays high for days to weeks.
- Evidence: 2010-05-06 flash crash (S&P -3.24% on the day, intraday swing larger); 2018-02-05 volatility spike, S&P -4.10% with short-volatility products unwinding.
- Horizon: the first day is the shock; follow-ups are typically volatile in both directions. Confidence on direction after the shock: low; confidence that volatility remains elevated: high.

### 3.14 Foreign shocks (China, Europe, emerging markets)
- Mechanism: global growth fears, commodity demand, currency and funding stress.
- Reaction: spillover to the S&P depends on exposure; Chinese-growth scares hit materials, industrials and multinationals; euro-area funding stress hits banks.
- Evidence: 2015-08-24 China devaluation/rout worldwide, S&P -3.94%.
- Horizon: days to weeks; fades if the home market stabilizes.

## 4. How an agent should use this
1. Classify each new item as an event type; ignore headlines that only report the market's own move or contain no new cause.
2. Check scale, surprise vs. expectation and whether the story is new or a continuation of an open storyline.
3. Read the market regime from past-only data (recent trend and realized volatility).
4. Apply the entry: pick the horizon, the affected sectors and the index effect. Compare with base rates.
5. Output: direction, horizon, confidence, and an explicit "no edge" when channel, scale or surprise is missing.

## 5. Known limits of this draft
- Written mostly from general knowledge; not yet fitted to data. Magnitudes are rough.
- Headline data is thin in 2008-2010 and lists few causes; the news source holds many market-recap headlines.
- Next-day index direction is close to a coin flip; the edge, if any, is likely in sector calls, volatility and knowing when not to act.
