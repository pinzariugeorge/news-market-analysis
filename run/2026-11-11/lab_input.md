# Lab input, decision day 2026-11-11 (now 10:17 UTC)
Output file to write: /home/user/news-market-analysis/data/paper_lab/run/2026-11-11/lab_output.json

## This lab: core | focus: any idea family (momentum, trend, quality, anything not obviously fast or news driven) | allowed horizons: [1, 2, 3, 5, 10, 20]

## Registered ideas (registry)
- [testing] high-momentum-20d: Stocks trading at their recent high after a strong run keep drifting up because investors anchor on the high and under-react to the good news behind the run. | rule: Entry: below_3m_high >= -1.0% AND d20 >= +10% AND entry cost <= 1.5%. If more than 2 names qualify on a day, buy only the 2 with the largest d20. Size: max whole shares under the 25% cap. Horizon 20 trading days; exit at horizon or the -8% stop. No re-entry in a name already held. | source: George & Hwang (2004), The 52-Week High and Momentum Investing, Journal of Finance; adapted to the 3-month high available in the features | note: New. First signal day: AZN, BAYN, GSK, NOVN, SAN.PA all qualify on price; AZN fails the cost filter (2.26%); BAYN and SAN.PA have the largest d20. All signals are pharma, so the results are exposed to one sector.
- [testing] guidance-drift-10d: After a company raises its forecast or reports results above expectations, the price keeps drifting in the direction of the news for days because investors under-react to earnings information. | rule: Entry: a headline on the decision day that names the company and says it raised its forecast/guidance/outlook or beat results expectations, AND d1 >= +2% (the market confirms the news as positive), AND entry cost <= 1.5%. Horizon 10 trading days; exit at horizon or the -8% stop. Analyst rating/target changes and regulatory approvals do not count. | source: Bernard & Thomas (1989), Post-Earnings-Announcement Drift; Chan, Jegadeesh & Lakonishok (1996), Momentum Strategies | note: IFX.DE forecast-raise headline is present, but d1 in the features at 13:53 UTC is +1.68% (below the +2% confirmation), so no entry by rule; 0 closed trades.
- [testing] no-news-drop-reversal-3d: A large one-day drop without company-specific news is often liquidity or flow driven and partly reverses within days, while drops with news do not. | rule: Entry: d1 <= -3.0% AND no headline on the decision day naming the company (theme-wide commodity headlines are allowed) AND the stock's main driver (oil for oil_gas, gold for gold_miners, copper for copper_uranium, ^STOXX50E otherwise) moved less than half as much as the stock, AND entry cost <= 1.5%. Horizon 3 trading days; exit at horizon or the -8% stop. | source: Jegadeesh (1990), Evidence of Predictable Behavior of Security Returns; Lehmann (1990); Chan (2003), Stock price reaction to news and no-news | note: New. No signal today: the largest drop is REP.MC -2.83%, and it is fully explained by Brent -2.73%.

# Lab results per idea (closed trades only; excess = net trade % minus the mean move of the whole universe over the same days, i.e. the luck benchmark)
- [testing] high-momentum-20d (Stocks trading at their recent high after a strong run keep drifting up because investors ): 0 closed  => too few closed trades (20 needed) to judge
- [testing] guidance-drift-10d (After a company raises its forecast or reports results above expectations, the price keeps): 0 closed  => too few closed trades (20 needed) to judge
- [testing] no-news-drop-reversal-3d (A large one-day drop without company-specific news is often liquidity or flow driven and p): 0 closed  => too few closed trades (20 needed) to judge

Account: equity 993.79 EUR, cash 594.17 EUR, start 1000.00 EUR, total -0.62%.
Open positions:
- BAYN.DE Bayer x4 entry 56.95 EUR now 56.94 EUR, opened 2026-11-10, exit by 2026-12-08, theme pharma, catalyst quoted: lab idea high-momentum-20d: BAYN.DE is at its 3-month high (below_3m_high 0.00) with d20 +29.33%, th
- SAN.PA Sanofi x2 entry 86.17 EUR now 85.93 EUR, opened 2026-11-10, exit by 2026-12-08, theme pharma, catalyst quoted: lab idea high-momentum-20d: SAN.PA is at its 3-month high (below_3m_high 0.00) with d20 +21.85%, sec
Pending orders: none

## Per-name features (daily closes up to now; last, 1/5/20-day move %, % below the 3-month high)
- ANTO.L: last 3334.0 d1 +3.09 d5 +2.65 d20 -6.66 below_3m_high -18.30
- AZN.L: last 13860.0 d1 -0.17 d5 -1.17 d20 +12.68 below_3m_high -1.46
- BAYN.DE: last 56.94 d1 -0.25 d5 +4.98 d20 +26.34 below_3m_high -0.25
- BESI.AS: last 157.85 d1 +4.68 d5 +3.85 d20 -9.57 below_3m_high -33.62
- BOL.ST: last 524.6 d1 +1.82 d5 +2.58 d20 -1.58 below_3m_high -10.29
- BP.L: last 567.0 d1 +2.68 d5 -0.80 d20 -7.68 below_3m_high -11.20
- EDV.L: last 4180.0 d1 +1.98 d5 +10.64 d20 +4.74 below_3m_high -12.79
- ENI.MI: last 25.16 d1 +1.66 d5 -1.49 d20 -2.23 below_3m_high -9.01
- EQNR.OL: last 394.1 d1 +3.11 d5 -3.07 d20 -8.77 below_3m_high -13.16
- FRES.L: last 2551.0 d1 +1.51 d5 +4.21 d20 -1.51 below_3m_high -20.75
- GLEN.L: last 516.8 d1 +2.42 d5 +3.17 d20 -10.48 below_3m_high -17.84
- GSK.L: last 1909.0 d1 -0.42 d5 +1.01 d20 +5.12 below_3m_high -0.75
- IFX.DE: last 52.34 d1 +6.71 d5 +4.18 d20 -5.44 below_3m_high -19.08
- KGH.WA: last 288.0 d1 -0.48 d5 +4.59 d20 -16.44 below_3m_high -23.81
- NOVN.SW: last 133.46 d1 -0.76 d5 -0.60 d20 +8.80 below_3m_high -0.76
- NOVO-B.CO: last 273.15 d1 +0.61 d5 -4.23 d20 +6.72 below_3m_high -11.26
- REP.MC: last 29.51 d1 +2.86 d5 -0.81 d20 -1.89 below_3m_high -6.44
- RIO.L: last 6419.0 d1 +1.52 d5 +3.52 d20 -7.28 below_3m_high -17.05
- SAN.PA: last 85.93 d1 -0.02 d5 +2.18 d20 +19.65 below_3m_high -0.02
- SHEL.L: last 3676.0 d1 +1.42 d5 -3.15 d20 -6.02 below_3m_high -8.96
- STMPA.PA: last 41.78 d1 +4.18 d5 +2.19 d20 -2.90 below_3m_high -19.65
- TTE.PA: last 79.57 d1 +1.75 d5 -2.45 d20 -0.75 below_3m_high -6.86

## Headlines per theme (newest first)
### oil_gas
- [2026-11-11 10:11] Shell (SHEL) Shares Rise Amid Oil Price Recovery and Positive Eu - GuruFocus (GuruFocus)
- [2026-11-11 10:00] Siemens Energy More Than Triples Dividend After Record Year - Crude Oil Prices Today | OilPrice.com (Crude Oil Prices Today | OilPrice.com)
- [2026-11-11 09:59] Oil Prices Rebound, Brent Tops $92 Amid Tanker Attacks - MarketForces Africa (MarketForces Africa)
- [2026-11-11 09:24] Crude oil price surge after Iran attack ships in Strait of Hormuz | Tap to know more | Inshorts - Inshorts (Inshorts)
- [2026-11-11 09:21] Consortia involving TotalEnergies, AG&P vie for $1.5 bln southern Vietnam LNG power plant - Theinvestor (Theinvestor)
- [2026-11-11 09:15] Occidental shares rise as debt milestone sharpens focus on oil-price risk - finchannel (finchannel)
### gold_miners
- [2026-11-11 09:39] Interim Ruling Sets TriStar Gold’s Consultation Path to Advance US$603M NPV Gold Project in Brazil - Crux Investor (Crux Investor)
- [2026-11-11 09:13] Falco’s Horne 5: A C$3.35 billion gold project trading at a fraction of its underlying value - The Armchair Trader (The Armchair Trader)
- [2026-11-11 08:54] Gold Price Forecast: XAU/USD Holds $4,030 After Hot CPI Puts a 50bp Fed Hike on the Table - FXLeaders (FXLeaders)
- [2026-11-11 08:45] Why is the glittering gold losing its sparkle? - The Economic Times (The Economic Times)
- [2026-11-11 08:30] Gold Fields urged to sweeten bid for Northern Star - The Australian (The Australian)
- [2026-11-11 08:24] Gold prices recover after a sell-off session, interest rate hike pressure remains heavy - Laodong.vn (Laodong.vn)
### chips
- [2026-11-11 10:05] Infineon expects more than 20% growth as data centre power nears €4 billion - Evertiq (Evertiq)
- [2026-11-11 10:05] Infineon expects an AI infrastructure boom to drive data center revenue higher (IFNNY:OTCMKTS) - Seeking Alpha (Seeking Alpha)
- [2026-11-11 09:53] Chip Maker Infineon Lifts AI Sales Goal on Strong Data-Center Demand - WSJ (WSJ)
- [2026-11-11 09:48] Besi stock: AI orders surge as hybrid-bonding adoption widens - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-11 09:45] STMicroelectronics Unveils Advanced MCUs for AI Datacenters and Robotics - Bisinfotech (Bisinfotech)
- [2026-11-11 09:20] European Chip Stocks Climb After CoreWeave Results Fuel AI Optimism -- Market Talk - Moomoo (Moomoo)
### pharma
- [2026-11-11 10:10] Merck's rare tumour drug Pimjetmi claims FDA approval - pharmaphorum (pharmaphorum)
- [2026-11-11 10:09] Lilly to seek FDA approval for Foundayo in sleep apnea after strong Phase 3 data - medwatch.com (medwatch.com)
- [2026-11-11 10:02] Novo Nordisk Commits $200 Million to Diabetes Care - grafa.com (grafa.com)
- [2026-11-11 09:25] AstraZeneca snaps up vaccine technology company - lifesciencesweden.se (lifesciencesweden.se)
- [2026-11-11 09:22] FDA approves Merck KGaA’s Pimjetmi for TGCT - The Pharma Letter (The Pharma Letter)
- [2026-11-11 09:12] UAE becomes first country to conditionally approve AstraZeneca drug for Berger’s disease - Fast Company Middle East (Fast Company Middle East)
### copper_uranium
- [2026-11-11 10:07] Yancoal renews $1.07 billion Glencore sales cap - Mining.com.au (Mining.com.au)
- [2026-11-11 09:23] Copper price prediction: Flat trend expected as sideways trading persists near key support - Traders Union (Traders Union)
- [2026-11-11 08:44] Light mag. 3.1 earthquake - Provincia de El Loa, Region de Antofagasta, Chile, on Wednesday, Nov 11, 2026, at 05:29 am (GMT -3) - Volcano Discovery (Volcano Discovery)
- [2026-11-11 08:35] Rio Tinto stock price prediction: Weak momentum and oversold conditions limit further downside - Traders Union (Traders Union)
- [2026-11-11 08:29] Light mag. 3.1 earthquake - 46 km south of San Pedro de Atacama, Provincia de El Loa, Region de Antofagasta, Chile, on Wednesday, Nov 11, 2026, at 05:18 am (GMT -3) - Volcano Discovery (Volcano Discovery)
- [2026-11-11 08:21] Is Rio Tinto (NYSE:RIO) Broadening Beyond Iron Ore? - Kalkine Media (Kalkine Media)
### macro
- [2026-11-11 09:23] European stocks advance as investors read inflation, oil and AI developments (EUR:USD:) - Seeking Alpha (Seeking Alpha)
- [2026-11-11 09:07] European shares rise as Siemens Energy forecast lifts AI optimism; inflation concerns persist - The Economic Times (The Economic Times)
- [2026-11-11 08:00] Oil Prices Rebound as Iran War Risks Keep Markets on Edge | Dawn News English - Dawn (Dawn)
- [2026-11-11 05:44] Global markets brace for inflation, Iran trade and Nvidia turmoil - WION (WION)
- [2026-11-11 04:35] Oil rises from two-month low as Hormuz shipping attacks offset Iran truce hopes - Aaj English TV (Aaj English TV)
- [2026-11-11 02:21] Trump says Iran war ‘effectively over’: How's it likely to impact Sensex, Nifty, gold and silver prices? Experts' views - Livemint (Livemint)

## Drivers
- BZ=F: +1.74%
- CL=F: +1.02%
- GC=F: +0.82%
- HG=F: +1.44%
- NG=F: +0.49%
- EURUSD=X: -0.73%
- ^STOXX50E: +0.68%
- ^GDAXI: +0.74%
- ^FTSE: +0.30%
- ^VIX: -4.32%

## Traded names: price EUR, quote age min, entry cost % (commission, FX, tax, slippage), max whole shares under the 25% lab cap
- ANTO.L [copper_uranium] 39.85 EUR, age 15.1 min, entry cost 1.61%, max 6 shares
- AZN.L [pharma] 165.71 EUR, age 15.1 min, entry cost 1.54%, max 1 shares
- BAYN.DE [pharma] 56.94 EUR, age 15.3 min, entry cost 0.93%, max 4 shares
- BESI.AS [chips] 157.85 EUR, age 15.1 min, entry cost 0.84%, max 1 shares
- BOL.ST [copper_uranium] 47.16 EUR, age 0.6 min, entry cost 1.06%, max 5 shares
- BP.L [oil_gas] 6.78 EUR, age 15.1 min, entry cost 1.53%, max 36 shares
- EDV.L [gold_miners] 49.98 EUR, age 15.8 min, entry cost 1.66%, max 5 shares
- ENI.MI [oil_gas] 25.16 EUR, age 15.4 min, entry cost 0.92%, max 9 shares
- EQNR.OL [oil_gas] 37.11 EUR, age 15.1 min, entry cost 1.14%, max 6 shares
- FRES.L [gold_miners] 30.5 EUR, age 15.6 min, entry cost 1.65%, max 8 shares
- GLEN.L [copper_uranium] 6.18 EUR, age 15.1 min, entry cost 1.54%, max 40 shares
- GSK.L [pharma] 22.83 EUR, age 15.2 min, entry cost 1.58%, max 10 shares
- IFX.DE [chips] 52.34 EUR, age 15.0 min, entry cost 0.83%, max 4 shares
- KGH.WA [copper_uranium] 65.33 EUR, age 1097.6 min, entry cost 1.07%, max 3 shares
- NOVN.SW [pharma] 144.56 EUR, age 15.6 min, entry cost 1.14%, max 1 shares
- NOVO-B.CO [pharma] 36.51 EUR, age 0.2 min, entry cost 1.06%, max 6 shares
- REP.MC [oil_gas] 29.51 EUR, age 15.2 min, entry cost 1.02%, max 8 shares
- RIO.L [copper_uranium] 76.75 EUR, age 15.1 min, entry cost 1.6%, max 3 shares
- SAN.PA [pharma] 85.93 EUR, age 15.4 min, entry cost 1.42%, max 2 shares
- SHEL.L [oil_gas] 43.95 EUR, age 15.3 min, entry cost 1.59%, max 5 shares
- STMPA.PA [chips] 41.78 EUR, age 15.1 min, entry cost 1.31%, max 5 shares
- TTE.PA [oil_gas] 79.55 EUR, age 15.2 min, entry cost 1.21%, max 3 shares

Lab limits: {"start_cash": 1000.0, "max_positions": 5, "max_pos_pct": 0.25, "min_conf": 0.0, "horizons": [1, 2, 3, 5, 10, 20], "max_new_buys_day": 5, "stop_pct": -8.0, "daily_loss_pct": -3.0, "weekly_loss_pct": -6.0, "max_fee_pct": 1.5, "cutoff_min": 30, "open_delay_min": 15}