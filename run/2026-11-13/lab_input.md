# Lab input, decision day 2026-11-13 (now 10:26 UTC)
Output file to write: /home/user/news-market-analysis/data/paper_lab/run/2026-11-13/lab_output.json

## This lab: core | focus: any idea family (momentum, trend, quality, anything not obviously fast or news driven) | allowed horizons: [1, 2, 3, 5, 10, 20]

## Registered ideas (registry)
- [testing] high-momentum-20d: Stocks trading at their recent high after a strong run keep drifting up because investors anchor on the high and under-react to the good news behind the run. | rule: Entry: below_3m_high >= -1.0% AND d20 >= +10% AND entry cost <= 1.5%. If more than 2 names qualify on a day, buy only the 2 with the largest d20. Size: max whole shares under the 25% cap. Horizon 20 trading days; exit at horizon or the -8% stop. No re-entry in a name already held. | source: George & Hwang (2004), The 52-Week High and Momentum Investing, Journal of Finance; adapted to the 3-month high available in the features | note: New. First signal day: AZN, BAYN, GSK, NOVN, SAN.PA all qualify on price; AZN fails the cost filter (2.26%); BAYN and SAN.PA have the largest d20. All signals are pharma, so the results are exposed to one sector.
- [testing] guidance-drift-10d: After a company raises its forecast or reports results above expectations, the price keeps drifting in the direction of the news for days because investors under-react to earnings information. | rule: Entry: a headline on the decision day that names the company and says it raised its forecast/guidance/outlook or beat results expectations, AND d1 >= +2% (the market confirms the news as positive), AND entry cost <= 1.5%. Horizon 10 trading days; exit at horizon or the -8% stop. Analyst rating/target changes and regulatory approvals do not count. | source: Bernard & Thomas (1989), Post-Earnings-Announcement Drift; Chan, Jegadeesh & Lakonishok (1996), Momentum Strategies | note: First signal 2026-11-11: IFX.DE headline 'Chip Maker Infineon Lifts AI Sales Goal' (WSJ, 09:53) with d1 +6.71% and entry cost 0.83%, so the rule fires; 0 closed trades.
- [testing] no-news-drop-reversal-3d: A large one-day drop without company-specific news is often liquidity or flow driven and partly reverses within days, while drops with news do not. | rule: Entry: d1 <= -3.0% AND no headline on the decision day naming the company (theme-wide commodity headlines are allowed) AND the stock's main driver (oil for oil_gas, gold for gold_miners, copper for copper_uranium, ^STOXX50E otherwise) moved less than half as much as the stock, AND entry cost <= 1.5%. Horizon 3 trading days; exit at horizon or the -8% stop. | source: Jegadeesh (1990), Evidence of Predictable Behavior of Security Returns; Lehmann (1990); Chan (2003), Stock price reaction to news and no-news | note: New. No signal today: the largest drop is REP.MC -2.83%, and it is fully explained by Brent -2.73%.

# Lab results per idea (closed trades only; excess = net trade % minus the mean move of the whole universe over the same days, i.e. the luck benchmark)
- [testing] high-momentum-20d (Stocks trading at their recent high after a strong run keep drifting up because investors ): 0 closed  => too few closed trades (20 needed) to judge
- [testing] guidance-drift-10d (After a company raises its forecast or reports results above expectations, the price keeps): 0 closed  => too few closed trades (20 needed) to judge
- [testing] no-news-drop-reversal-3d (A large one-day drop without company-specific news is often liquidity or flow driven and p): 0 closed  => too few closed trades (20 needed) to judge

Account: equity 991.71 EUR, cash 382.09 EUR, start 1000.00 EUR, total -0.83%.
Open positions:
- BAYN.DE Bayer x4 entry 56.95 EUR now 56.84 EUR, opened 2026-11-10, exit by 2026-12-08, theme pharma, catalyst quoted: lab idea high-momentum-20d: BAYN.DE is at its 3-month high (below_3m_high 0.00) with d20 +29.33%, th
- SAN.PA Sanofi x2 entry 86.17 EUR now 88.09 EUR, opened 2026-11-10, exit by 2026-12-08, theme pharma, catalyst quoted: lab idea high-momentum-20d: SAN.PA is at its 3-month high (below_3m_high 0.00) with d20 +21.85%, sec
- IFX.DE Infineon x4 entry 52.40 EUR now 51.52 EUR, opened 2026-11-11, exit by 2026-11-25, theme chips, catalyst quoted: lab idea guidance-drift-10d: Decision-day headline says Infineon lifted its AI sales goal and expect
Pending orders: none

## Per-name features (daily closes up to now; last, 1/5/20-day move %, % below the 3-month high)
- ANTO.L: last 3218.0 d1 +0.03 d5 +3.37 d20 -5.35 below_3m_high -21.15
- AZN.L: last 13978.24 d1 +0.35 d5 +0.35 d20 +12.31 below_3m_high -0.62
- BAYN.DE: last 56.84 d1 +0.50 d5 +2.27 d20 +27.85 below_3m_high -0.42
- BESI.AS: last 155.75 d1 -1.46 d5 +8.61 d20 +0.13 below_3m_high -34.50
- BOL.ST: last 508.0 d1 -0.27 d5 +0.91 d20 -4.80 below_3m_high -13.13
- BP.L: last 572.5 d1 +0.97 d5 +2.34 d20 -6.77 below_3m_high -10.34
- EDV.L: last 3753.0 d1 -0.66 d5 -8.33 d20 -10.56 below_3m_high -21.70
- ENI.MI: last 25.83 d1 +1.43 d5 +3.13 d20 -0.46 below_3m_high -6.56
- EQNR.OL: last 405.5 d1 +0.42 d5 +2.68 d20 -6.26 below_3m_high -10.64
- FRES.L: last 2452.0 d1 +0.33 d5 -2.43 d20 -9.82 below_3m_high -23.83
- GLEN.L: last 515.0 d1 -0.14 d5 +4.01 d20 -11.68 below_3m_high -18.12
- GSK.L: last 1912.0 d1 +0.58 d5 +1.16 d20 +2.66 below_3m_high -0.60
- IFX.DE: last 51.52 d1 -1.13 d5 +12.60 d20 -1.66 below_3m_high -20.35
- KGH.WA: last 283.0 d1 -0.46 d5 +1.14 d20 -12.72 below_3m_high -25.13
- NOVN.SW: last 134.58 d1 +0.27 d5 +1.13 d20 +7.92 below_3m_high +0.00
- NOVO-B.CO: last 275.55 d1 -0.07 d5 +2.26 d20 +6.14 below_3m_high -10.48
- REP.MC: last 30.35 d1 +1.51 d5 +1.51 d20 +1.85 below_3m_high -3.77
- RIO.L: last 6321.0 d1 -0.06 d5 +0.64 d20 -7.26 below_3m_high -18.31
- SAN.PA: last 88.09 d1 +0.13 d5 +5.19 d20 +22.45 below_3m_high +0.00
- SHEL.L: last 3711.5 d1 +1.27 d5 -0.30 d20 -5.75 below_3m_high -8.09
- STMPA.PA: last 42.58 d1 +0.56 d5 +13.13 d20 +3.41 below_3m_high -18.12
- TTE.PA: last 81.77 d1 +1.41 d5 +2.56 d20 +1.31 below_3m_high -4.28

## Headlines per theme (newest first)
### oil_gas
- [2026-11-13 10:18] Equinor shares trade ex-dividend for Q2 2026 wi... - Pluang (Pluang)
- [2026-11-13 10:15] India Seeks Private Investors for $910 Million Oil Reserve - Crude Oil Prices Today | OilPrice.com (Crude Oil Prices Today | OilPrice.com)
- [2026-11-13 10:09] Equinor ASA: Ex. dividend second quarter 2026 today - OSE - The Manila Times (The Manila Times)
- [2026-11-13 10:07] Iran Blockade Leaves Saudi Oil Routes Exposed, Keeping Brent Upside Open - Crux Investor (Crux Investor)
- [2026-11-13 10:01] Here's one place in Florida you are guaranteed to find a junonia shell - The News-Press (The News-Press)
- [2026-11-13 09:59] Israeli forces shell 5 southern Lebanon towns as drones fly low over Beirut - Anadolu Ajansı (Anadolu Ajansı)
### gold_miners
- [2026-11-13 10:16] Inflation persists, but markets keep defying gravity - GoldBroker (GoldBroker)
- [2026-11-13 10:06] Why Did Agnico Eagle Mines Limited (TSX:AEM) Fall 4.056% to $254.28 on November 12, 2026? - kalkine.ca (kalkine.ca)
- [2026-11-13 09:56] Aris Mining releases PFS for Toroparu Gold Project in Guyana - Mining Technology (Mining Technology)
- [2026-11-13 09:54] NRL identifies eight copper-gold porphyry discoveries in Chagai - Investify (Investify)
- [2026-11-13 09:48] Why the latest gold price pullback is not shaking producer confidence - MiningMX (MiningMX)
- [2026-11-13 09:15] Gold prices rebound from 13-month low as major investors return - Traders Union (Traders Union)
### chips
- [2026-11-13 09:38] Besi stock: Applied Materials deepens advanced-packaging tie - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-13 09:37] ASML Stock Quote Price and Forecast - CNN (CNN)
- [2026-11-13 09:27] European blue-chip earnings growth set to hit four-year high, energy sector leads - The Economic Times (The Economic Times)
- [2026-11-13 09:06] ASML Holding stock faces capacity test as AI demand reaches 2030 - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-13 08:55] ASML Korea Union Demands Direct Talks With Samsung Electronics - Seoul Economic Daily (Seoul Economic Daily)
- [2026-11-13 08:41] European shares edge lower as AI uncertainty weighs on chip and luxury stocks - Traders Union (Traders Union)
### pharma
- [2026-11-13 09:39] Polycythemia Vera Market Gains Momentum as FDA Approves - openPR.com (openPR.com)
- [2026-11-13 09:39] Sanofi extends its winning streak, Citi raises target - www.marketscreener.com (www.marketscreener.com)
- [2026-11-13 09:23] GSK wins positive CHMP opinion for Bexsero meningitis B booster - Sharecast.com (Sharecast.com)
- [2026-11-13 09:20] Kinzey Capital Management: Pharma Lifts Bayer's 2026 Outlook - ACCESS Newswire (ACCESS Newswire)
- [2026-11-13 08:37] GSK gets support from EU panel for Meningitis B booster in adolescents - London South East (London South East)
- [2026-11-13 08:24] GSK plc executive share purchases: Can GSK sustain its recent gains? - Traders Union (Traders Union)
### copper_uranium
- [2026-11-13 09:59] Amarc Resources Ltd. (TSXV:AHR): Freeport-Funded JOY Drilling and a Boliden Partnership Put Copper-Gold Assets Back in View - kalkine.ca (kalkine.ca)
- [2026-11-13 09:39] US inflation exceeding expectations pressures copper prices; SHFE copper spot premiums are expected to rebound after contract rollover [SMM Macro Weekly Review] - Shanghai Metals Market (Shanghai Metals Market)
- [2026-11-13 09:23] Will copper price hold $6.08 support amid oversold conditions? - Traders Union (Traders Union)
- [2026-11-13 09:00] Weak mag. 2.5 earthquake - South Pacific Ocean, 154 km northwest of Antofagasta, Provincia de Antofagasta, Region de Antofagasta, Chile, on Thursday, Nov 12, 2026, at 09:46 pm (GMT -5) - Volcano Discovery (Volcano Discovery)
- [2026-11-13 08:36] RIO trades flat as weak momentum keeps Rio Tinto stock in check - Traders Union (Traders Union)
- [2026-11-13 08:25] Copper, Uranium and Lithium Price Forecast: Nvidia CEO Exit Hits Copper - FXEmpire (FXEmpire)
### macro
- [2026-11-13 09:28] Stock Futures Lower as Investors Look to U.S. Inflation Data - WSJ (WSJ)
- [2026-11-13 08:29] European stock market open: Stocks ease slightly as the rally takes a breather - investingLive (investingLive)
- [2026-11-13 08:29] PERSPECTIVE: Democratic Sweep Adds New Twist to Markets’ Iran War, AI, and Debt Worries - EnergyNow.com (EnergyNow.com)
- [2026-11-13 08:25] French inflation rises to 3.7% in October, highest since December 2023 - Reuters (Reuters)
- [2026-11-13 08:09] Goldman Sachs lifts 12-month target for European stocks on energy price relief - Reuters (Reuters)
- [2026-11-13 07:29] FTSE 100 set to fall as Ukraine peace talks and US-Iran tensions unsettle markets - Share Talk (Share Talk)

## Drivers
- BZ=F: -0.34%
- CL=F: -0.76%
- GC=F: +0.48%
- HG=F: -0.48%
- NG=F: -2.07%
- EURUSD=X: -0.34%
- ^STOXX50E: +0.08%
- ^GDAXI: +0.06%
- ^FTSE: +0.20%
- ^VIX: -1.60%

## Traded names: price EUR, quote age min, entry cost % (commission, FX, tax, slippage), max whole shares under the 25% lab cap
- ANTO.L [copper_uranium] 38.49 EUR, age 15.1 min, entry cost 1.64%, max 6 shares
- AZN.L [pharma] 167.19 EUR, age 15.1 min, entry cost 2.28%, max 1 shares
- BAYN.DE [pharma] 56.86 EUR, age 15.3 min, entry cost 0.93%, max 4 shares
- BESI.AS [chips] 155.75 EUR, age 15.2 min, entry cost 0.85%, max 1 shares
- BOL.ST [copper_uranium] 45.53 EUR, age 0.3 min, entry cost 1.09%, max 5 shares
- BP.L [oil_gas] 6.85 EUR, age 15.2 min, entry cost 1.54%, max 36 shares
- EDV.L [gold_miners] 44.89 EUR, age 15.3 min, entry cost 1.63%, max 5 shares
- ENI.MI [oil_gas] 25.83 EUR, age 15.5 min, entry cost 0.96%, max 9 shares
- EQNR.OL [oil_gas] 38.39 EUR, age 15.3 min, entry cost 1.11%, max 6 shares
- FRES.L [gold_miners] 29.33 EUR, age 15.4 min, entry cost 1.61%, max 8 shares
- GLEN.L [copper_uranium] 6.16 EUR, age 15.1 min, entry cost 1.53%, max 40 shares
- GSK.L [pharma] 22.87 EUR, age 15.2 min, entry cost 1.58%, max 10 shares
- IFX.DE [chips] 51.48 EUR, age 15.2 min, entry cost 0.84%, max 4 shares
- KGH.WA [copper_uranium] 64.14 EUR, age 15.1 min, entry cost 1.08%, max 3 shares
- NOVN.SW [pharma] 145.32 EUR, age 15.2 min, entry cost 1.14%, max 1 shares
- NOVO-B.CO [pharma] 36.83 EUR, age 0.2 min, entry cost 1.05%, max 6 shares
- REP.MC [oil_gas] 30.35 EUR, age 15.8 min, entry cost 1.07%, max 8 shares
- RIO.L [copper_uranium] 75.61 EUR, age 15.1 min, entry cost 1.61%, max 3 shares
- SAN.PA [pharma] 88.1 EUR, age 15.2 min, entry cost 1.4%, max 2 shares
- SHEL.L [oil_gas] 44.39 EUR, age 15.3 min, entry cost 1.58%, max 5 shares
- STMPA.PA [chips] 42.58 EUR, age 15.1 min, entry cost 1.29%, max 5 shares
- TTE.PA [oil_gas] 81.77 EUR, age 15.2 min, entry cost 1.19%, max 3 shares

Lab limits: {"start_cash": 1000.0, "max_positions": 5, "max_pos_pct": 0.25, "min_conf": 0.0, "horizons": [1, 2, 3, 5, 10, 20], "max_new_buys_day": 5, "stop_pct": -8.0, "daily_loss_pct": -3.0, "weekly_loss_pct": -6.0, "max_fee_pct": 1.5, "cutoff_min": 30, "open_delay_min": 15}