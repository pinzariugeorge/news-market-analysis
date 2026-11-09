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

12. **Big days come in clusters.** 74% of 2%+ days in 2008-2019 fell in four years and 79% were within a week of another one. After the first 2%+ day, expect more large moves in both directions (a -9% day followed by a +11% day within two weeks happened). Size down or stay out; do not guess direction.

## 2. Base rates (S&P 500 daily closes; `data/processed/market_days.csv`; handbook period only, to 2019)
| Stat | 1950-2019 (17,612 days) | 1950-1989 | 1990-2019 | 2008-2019 |
|---|---|---|---|---|
| Daily standard deviation | 0.96% | 0.84% | 1.10% | 1.24% |
| Up days | 52.8% | 52.6% | 53.0% | 53.9% |
| \|move\| >= 1% | 20.2% | 16.7% | 24.9% | 25.9% |
| \|move\| >= 2% | 4.3% | 2.7% | 6.4% | 8.2% |
| \|move\| >= 3% | 1.2% | 0.6% | 2.1% | 3.2% |
| \|move\| >= 5% | 0.23% | 0.11% | 0.40% | 0.73% |

Mean daily move is about +0.035% in every period (about 9% a year). A typical day is a small move; size depends on the regime, direction barely does.

**Volatility clusters, direction does not follow.**
- After a day of 2% or more (either sign), the next day's average absolute move is 1.25% vs 0.65% overall (1950-2019).
- Direction after a big day: after a drop of 2%+ (n=380) the next day was up 55% (mean +0.15%); after a rise of 2%+ (n=372) up 56% (mean +0.16%). So there is no reliable direction signal from a big day. (The 2008-2019 only figures, 58% up after drops and 49% after rises, did not hold over the longer sample: do not use them.)
- By the previous 20-day realized volatility (quartiles low to high): next-day standard deviation 0.56%, 0.69%, 0.86%, 1.47%, while the share of up days stays 52-53% in all four. Use volatility to size the possible move, not to pick the direction.

Any single-day direction call starts from roughly 53% up. The edge, if any, must come from magnitude, sector, horizon and knowing when to stay out.

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
- Reaction: in-line ~0; large miss/beat: +/-0.5% to 1.5%. Rarely more than 2% in normal times. In a recession or stress regime the same data can move the index -3% to -9% (observed: 54 big days, -8.9% to +3.8%).
- Horizon: day; the trend of several readings matters more than one.
- Amplifiers: data is the key input the Fed watches, thin liquidity. Dampeners: one noisy reading, revisions.
- Sectors: cyclicals (industrials, banks) vs. defensives; homebuilders on housing data.
- Index effect: low to medium. Confidence: low unless several readings agree.

### 3.3 Credit or banking stress (bank failure, funding market freeze, sovereign debt crisis)
- Mechanism: threatens the payment system and lending; hits earnings of everything via funding costs and fear of contagion.
- Reaction: large and persistent. Index -3% to -9% in single days when the system itself is in doubt; relief rallies of the same size or larger on rescue plans (observed 2008-2019: -9.0% to +11.6%, median absolute 3.2% over 121 big days).
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
- Reaction: the surprise matters; resolution of uncertainty often lifts the market regardless of winner. Index move typically within +/-2% on the day (up to +/-4% in a crisis, e.g. 2008-11-04 +4.1%); sector rotations larger.
- Horizon: day to weeks; policy implementation later.
- Amplifiers: unexpected winner, pledge of a sharp policy break (trade, tax, regulation). Dampeners: divided government, expectation of gridlock.
- Sectors: depend on the platform (energy, healthcare, financials, defense, infrastructure).
- Evidence: 2016-11-09: overnight futures fell sharply on a surprise result, yet the S&P closed +1.11% that day, led by financials, as policy expectations (tax cuts, deregulation) re-rated sectors. Lesson: the first reaction can reverse within hours; predict sectors, and be wary of calling the index from overnight moves.

### 3.6b US midterm elections (calendar event, every 4 years in November)
- Mechanism: not a surprise-driven event in most cases. Uncertainty about the balance of Congress (and so about tax, spending, regulation) weighs on the market before the vote and resolves after it. Divided government (gridlock) is usually read as "less policy risk".
- Typical pattern (published research, mostly pre-2019 data; some quoted averages may include later years, so treat them as context and do not tune to them): the midterm year is the weakest year of the four-year presidential cycle, with the market often weak or choppy until the vote and then rising. The 12 months after a midterm are positive in the large majority of cases since 1950, with averages in the low-to-mid teens in percent; Q4 plus the next two quarters were positive far more often than average quarters. Sources are listed in `handbook/SOURCES.md`.
- Our own check, all 13 midterms with data 1970-2018 (S&P 500 closes from election day; `data/raw/sp500_1950_2024_daily.csv`; earlier midterms fall on days the market was closed, so they are missing):
  | Measure | Mean | Median | Share positive |
  |---|---|---|---|
  | Prior 3 months | +3.1% | +4.0% | 69% |
  | Day after the vote | +0.57% | +0.37% | 77% |
  | +1 month | +0.6% | +2.3% | 69% |
  | +6 months | +13.1% | +12.9% | 100% |
  | +1 year | +13.1% | +12.0% | 100% |
  - Day after, per year: 1970 +0.20, 1974 -0.48, 1978 +0.64, 1982 +3.91, 1986 +0.15, 1990 -1.80, 1994 -0.05, 1998 +0.70, 2002 +0.91, 2006 +0.21, 2010 +0.37, 2014 +0.57, 2018 +2.12 (%).
  - Weakest 1-year follow-ups: 1986 +1.9%, 2010 +2.1%, 2014 +4.5%. No negative 1-year result in 13 cases.
  - 2018 detail: prior 3 months -3.6%, day after +2.12%, but -4.4% over the next month (Fed-driven slide into the 2018-12-24 low) before recovering; a bounce can fail for a few weeks if a stronger driver is at work.
- Reading: it is not a coin flip between "rise or fall": the vote itself is a small positive on the day in about 3 of 4 cases (big swings are rare and have specific causes: 1982 recession-end/rate-cut rally +3.9%, 1990 recession/Gulf War -1.8%), and the 6 to 12 months after were positive in all 13. Only 13 cases and not independent of the general upward drift of stocks (base rate for any 12 months is about +9 to 10%), so the edge over a random year is modest (+13% vs ~+9%).
- Practical rules: (1) before the vote: reduced conviction, expect choppiness, do not add risk just because "midterm rally" is coming; (2) the day after: modest positive bias (+), strongest if the market was down into the vote and the outcome is divided government; (3) next months: bullish bias unless a stronger driver (Fed tightening, credit stress) contradicts it; (4) if an unexpected outcome changes tax/regulation expectations, reason by sector (see 3.6).
- Index effect: low to medium. Confidence: medium for a positive drift over 6-12 months, low for any single day.

### 3.6c US presidential election (every 4 years)
- Our check (S&P closes from election day, 9 elections 1972-2016 with data; earlier ones fall on market holidays): day after mean -0.84% (median -0.67%, positive in 3 of 9); +1 month mean -1.1% (median +0.5%); +6 months mean +5.0%; +1 year mean +12.6% (positive 8 of 9). Prior 3 months mean -0.4%.
- Reading: more uncertainty around the vote than at midterms (the executive changes), with a weak day or month around it in many cases and a positive 6 to 12 months afterward. Surprise outcomes matter more (see 3.6, 2016-11-09: overnight futures fell, the S&P closed +1.1%).
- Confidence: low for the day, medium for a positive drift over 6 to 12 months.

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

### 3.15 Calendar and seasonal patterns (S&P 500, 1950-2019)
Use as small tilts only. Effects are small, partly arbitraged away, and were found by testing many slices (risk of data-mining), so they never override a stronger driver such as a crisis, a Fed surprise or a regime change.
- **Month of the year** (mean / up share): January +1.1% / 61%, February +0.1% / 56%, March +1.2% / 64%, April +1.5% / 71%, May +0.2% / 59%, June +0.1% / 53%, July +1.1% / 57%, August -0.1% / 54%, September -0.4% / 46%, October +0.8% / 60% (largest volatility, sd 5.5%), November +1.6% / 69%, December +1.5% / 74%. September is the only clearly negative month; November to April is the strong stretch; August to October is the fragile stretch.
- **Year-end ("Santa") window** (last 5 trading days of December plus the first 2 of January): average +1.35%, positive in 78% of 69 years.
- **Turn of the month** (last trading day plus the first 3 of the next month): average +0.113% a day vs +0.016% on other days, about seven times the normal daily drift.
- **Day of week:** 1950-2019 Monday averaged -0.06% (up 48%), Wednesday +0.08% and Friday +0.07% (up 55-56%). Since 1990 the weekday differences are tiny (all +0.015% to +0.06%, up 52-54%): treat the old "weak Monday" as gone.
- **Midterm and presidential election cycle:** see 3.6b and 3.6c.
- Not yet studied: FOMC meeting days, earnings seasons (mid-January, April, July, October), quarter-end rebalancing, options expiration, holidays. See `TODO.md`.

### 3.16 Volatility regime (a modifier, not an event)
- Mechanism: when recent volatility is high, every shock moves prices more and news is amplified; when it is low, moves are small and bad news is often shrugged off.
- Use: the 20-day realized volatility sets how big a move to expect (next-day sd 0.56% in the calmest quartile vs 1.47% in the most volatile). It does not predict direction. Size positions and stops by it, and require more evidence before acting in a high-volatility regime.

## 4. How an agent should use this
1. Classify each new item as an event type; ignore headlines that only report the market's own move or contain no new cause.
2. Check scale, surprise vs. expectation and whether the story is new or a continuation of an open storyline.
3. Read the market regime from past-only data (recent trend and realized volatility).
4. Apply the entry: pick the horizon, the affected sectors and the index effect. Compare with base rates.
5. Output: direction, horizon, confidence, and an explicit "no edge" when channel, scale or surprise is missing.

## 5. Review of big-move days
See `handbook/BIGDAY_REVIEW.md` (247 days labeled by event type, observed ranges per type, findings). Main result: most big days are inside stress clusters, and the news dataset names a cause on fewer than 1 in 4 of them.

## 6. Known limits of this draft
- Written mostly from general knowledge; not yet fitted to data. Magnitudes are rough.
- Headline data is thin in 2008-2010 and lists few causes; the news source holds many market-recap headlines.
- Next-day index direction is close to a coin flip; the edge, if any, is likely in sector calls, volatility and knowing when not to act.
