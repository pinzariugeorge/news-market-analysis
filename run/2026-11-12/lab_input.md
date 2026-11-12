# Lab input, decision day 2026-11-12 (now 10:18 UTC)
Output file to write: /home/user/news-market-analysis/data/paper_lab/run/2026-11-12/lab_output.json

## This lab: core | focus: any idea family (momentum, trend, quality, anything not obviously fast or news driven) | allowed horizons: [1, 2, 3, 5, 10, 20]

## Registered ideas (registry)
- [testing] high-momentum-20d: Stocks trading at their recent high after a strong run keep drifting up because investors anchor on the high and under-react to the good news behind the run. | rule: Entry: below_3m_high >= -1.0% AND d20 >= +10% AND entry cost <= 1.5%. If more than 2 names qualify on a day, buy only the 2 with the largest d20. Size: max whole shares under the 25% cap. Horizon 20 trading days; exit at horizon or the -8% stop. No re-entry in a name already held. | source: George & Hwang (2004), The 52-Week High and Momentum Investing, Journal of Finance; adapted to the 3-month high available in the features | note: New. First signal day: AZN, BAYN, GSK, NOVN, SAN.PA all qualify on price; AZN fails the cost filter (2.26%); BAYN and SAN.PA have the largest d20. All signals are pharma, so the results are exposed to one sector.
- [testing] guidance-drift-10d: After a company raises its forecast or reports results above expectations, the price keeps drifting in the direction of the news for days because investors under-react to earnings information. | rule: Entry: a headline on the decision day that names the company and says it raised its forecast/guidance/outlook or beat results expectations, AND d1 >= +2% (the market confirms the news as positive), AND entry cost <= 1.5%. Horizon 10 trading days; exit at horizon or the -8% stop. Analyst rating/target changes and regulatory approvals do not count. | source: Bernard & Thomas (1989), Post-Earnings-Announcement Drift; Chan, Jegadeesh & Lakonishok (1996), Momentum Strategies | note: First signal 2026-11-11: IFX.DE headline 'Chip Maker Infineon Lifts AI Sales Goal' (WSJ, 09:53) with d1 +6.71% and entry cost 0.83%, so the rule fires; 0 closed trades.
- [testing] no-news-drop-reversal-3d: A large one-day drop without company-specific news is often liquidity or flow driven and partly reverses within days, while drops with news do not. | rule: Entry: d1 <= -3.0% AND no headline on the decision day naming the company (theme-wide commodity headlines are allowed) AND the stock's main driver (oil for oil_gas, gold for gold_miners, copper for copper_uranium, ^STOXX50E otherwise) moved less than half as much as the stock, AND entry cost <= 1.5%. Horizon 3 trading days; exit at horizon or the -8% stop. | source: Jegadeesh (1990), Evidence of Predictable Behavior of Security Returns; Lehmann (1990); Chan (2003), Stock price reaction to news and no-news | note: New. No signal today: the largest drop is REP.MC -2.83%, and it is fully explained by Brent -2.73%.

# Lab results per idea (closed trades only; excess = net trade % minus the mean move of the whole universe over the same days, i.e. the luck benchmark)
- [testing] high-momentum-20d (Stocks trading at their recent high after a strong run keep drifting up because investors ): 0 closed  => too few closed trades (20 needed) to judge
- [testing] guidance-drift-10d (After a company raises its forecast or reports results above expectations, the price keeps): 0 closed  => too few closed trades (20 needed) to judge
- [testing] no-news-drop-reversal-3d (A large one-day drop without company-specific news is often liquidity or flow driven and p): 0 closed  => too few closed trades (20 needed) to judge

Account: equity 994.85 EUR, cash 382.09 EUR, start 1000.00 EUR, total -0.52%.
Open positions:
- BAYN.DE Bayer x4 entry 56.95 EUR now 57.58 EUR, opened 2026-11-10, exit by 2026-12-08, theme pharma, catalyst quoted: lab idea high-momentum-20d: BAYN.DE is at its 3-month high (below_3m_high 0.00) with d20 +29.33%, th
- SAN.PA Sanofi x2 entry 86.17 EUR now 88.00 EUR, opened 2026-11-10, exit by 2026-12-08, theme pharma, catalyst quoted: lab idea high-momentum-20d: SAN.PA is at its 3-month high (below_3m_high 0.00) with d20 +21.85%, sec
- IFX.DE Infineon x4 entry 52.40 EUR now 51.61 EUR, opened 2026-11-11, exit by 2026-11-25, theme chips, catalyst quoted: lab idea guidance-drift-10d: Decision-day headline says Infineon lifted its AI sales goal and expect
Pending orders: none

## Per-name features (daily closes up to now; last, 1/5/20-day move %, % below the 3-month high)
- ANTO.L: last 3253.0 d1 -1.69 d5 +4.10 d20 -5.05 below_3m_high -20.29
- AZN.L: last 14008.0 d1 +0.81 d5 -0.24 d20 +10.32 below_3m_high -0.41
- BAYN.DE: last 57.58 d1 +1.44 d5 +2.42 d20 +29.66 below_3m_high +0.00
- BESI.AS: last 159.45 d1 -0.19 d5 +13.17 d20 -2.42 below_3m_high -32.95
- BOL.ST: last 516.8 d1 -0.96 d5 +1.81 d20 -2.16 below_3m_high -11.63
- BP.L: last 564.9 d1 -0.37 d5 -0.44 d20 -7.47 below_3m_high -11.53
- EDV.L: last 3844.0 d1 -6.86 d5 -4.21 d20 -6.70 below_3m_high -19.80
- ENI.MI: last 25.49 d1 +1.13 d5 +0.51 d20 -1.13 below_3m_high -7.83
- EQNR.OL: last 397.1 d1 +0.48 d5 -2.05 d20 -7.50 below_3m_high -12.49
- FRES.L: last 2453.0 d1 -2.62 d5 -1.68 d20 -8.09 below_3m_high -23.80
- GLEN.L: last 515.7 d1 +0.00 d5 +3.78 d20 -10.17 below_3m_high -18.01
- GSK.L: last 1908.0 d1 +1.11 d5 +0.95 d20 +2.11 below_3m_high -0.81
- IFX.DE: last 51.61 d1 -0.98 d5 +12.32 d20 -1.64 below_3m_high -20.21
- KGH.WA: last 288.35 d1 +0.12 d5 +0.51 d20 -12.91 below_3m_high -23.72
- NOVN.SW: last 134.58 d1 +1.39 d5 +0.34 d20 +6.89 below_3m_high +0.00
- NOVO-B.CO: last 279.3 d1 +2.42 d5 +2.97 d20 +6.02 below_3m_high -9.26
- REP.MC: last 29.62 d1 +0.20 d5 -1.95 d20 -0.07 below_3m_high -6.09
- RIO.L: last 6356.0 d1 -0.45 d5 +1.37 d20 -6.20 below_3m_high -17.86
- SAN.PA: last 88.02 d1 +1.63 d5 +4.13 d20 +21.98 below_3m_high +0.00
- SHEL.L: last 3655.0 d1 -0.42 d5 -3.41 d20 -6.47 below_3m_high -9.48
- STMPA.PA: last 42.06 d1 -0.26 d5 +13.49 d20 +1.58 below_3m_high -19.11
- TTE.PA: last 79.31 d1 -0.08 d5 -1.72 d20 -1.12 below_3m_high -7.16

## Headlines per theme (newest first)
### oil_gas
- [2026-11-12 10:16] Brent gains as Iran hardens stance against US - https://www.engine.online/ (https://www.engine.online/)
- [2026-11-12 10:08] Treated Coconut Shell Concrete Slabs Withstand Heavy Loads in Structural Testing - Bioengineer.org (Bioengineer.org)
- [2026-11-12 10:07] Bloomberg: BP Said to Weigh Sale of Brazil Oil Block Stake to Petrobras - marketscreener.com (marketscreener.com)
- [2026-11-12 10:05] BP forces down VLCC rates from Gulf of Oman on Onassis tanker - TradeWinds News (TradeWinds News)
- [2026-11-12 10:00] China Targets Global Gas Turbine Market as AI Power Demand Explodes - Crude Oil Prices Today | OilPrice.com (Crude Oil Prices Today | OilPrice.com)
- [2026-11-12 09:57] BP in Talks to Sell Stake in Brazil Oil Discovery to Petrobras - Bloomberg.com (Bloomberg.com)
### gold_miners
- [2026-11-12 10:08] Titan counts on stabilising gold prices to drive jewellery growth; margin guidance at 11 pc - ET Retail (ET Retail)
- [2026-11-12 10:03] Gold price in Qatari market falls by 2.05 percent this week - The Peninsula Qatar (The Peninsula Qatar)
- [2026-11-12 10:02] Infographic: Domestic gold prices fall by 1 million VND/tael on November 12 - Nhan Dan Online (Nhan Dan Online)
- [2026-11-12 09:53] Gold Price Forecast: US CPI Fuels 50bps Fed Hike Fears - Equiti Global (Equiti Global)
- [2026-11-12 09:48] Why is Endeavour Mining stock sliding today? - Investing.com (Investing.com)
- [2026-11-12 09:40] As gold falls from Rs 1.8 lakh peak to Rs 1.42 lakh per 10 grams, Indians buy 30% more, spending Rs 72,00 - The Times of India (The Times of India)
### chips
- [2026-11-12 09:47] U.S., Europe chip stocks dip as Nvidia board reportedly weighs ousting Huang By Investing.com - Investing.com India (Investing.com India)
- [2026-11-12 09:38] Infineon Technologies AG : Gets a Buy rating from Deutsche Bank - marketscreener.com (marketscreener.com)
- [2026-11-12 09:10] European tech shares fall as Nvidia board weighs ousting Jensen Huang - Euronews.com (Euronews.com)
- [2026-11-12 09:10] Maison Sungai Besi — where intelligent living meets everyday convenience - EdgeProp (EdgeProp)
- [2026-11-12 08:31] Infineon Lifts Guidance Toward €20 Billion as Design Wins Pile Up - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-12 08:29] STMicroelectronics to Host Investor Webcast on STM32 - TipRanks (TipRanks)
### pharma
- [2026-11-12 10:09] Weight-loss drug boom threatens insulin supply, experts warn - bdnews24.com (bdnews24.com)
- [2026-11-12 10:07] GSK plc unveils $2.5B global restructuring: Can GSK continue its upward momentum? - Traders Union (Traders Union)
- [2026-11-12 09:27] CRISPR Therapeutics AG $CRSP Shares Sold by GSK plc - MarketBeat (MarketBeat)
- [2026-11-12 09:26] Sanofi (ENXTPA:SAN) Could Be 20% Above Fair Value As Phase 3 Vaccine Trial Begins - Simply Wall St (Simply Wall St)
- [2026-11-12 09:23] €56 Bln Bayer Eyes Pharmaceutical Manufacturing in Ethiopia - Birr Metrics (Birr Metrics)
- [2026-11-12 08:30] Ageing population puts chronic disease prevention in focus across Asia-Pacific - Vietnam Investment Review - VIR (Vietnam Investment Review - VIR)
### copper_uranium
- [2026-11-12 09:30] Light mag. 3.2 earthquake - 52 km northeast of Calama, Provincia de El Loa, Region de Antofagasta, Chile, on Thursday, Nov 12, 2026, at 06:11 am (GMT -3) - Volcano Discovery (Volcano Discovery)
- [2026-11-12 08:58] DAX 40 hits all-time high as AUD/USD drops to 10-month low and copper price slips - IG (IG)
- [2026-11-12 08:28] Rio Tinto (ASX:RIO): How Project Execution Shapes the Near-Term View - Kalkine Media (Kalkine Media)
- [2026-11-12 07:36] Southern Copper (SCCO) Wins A UBS Upgrade, Is The Stock Still Pricey? - Simply Wall St (Simply Wall St)
- [2026-11-12 07:01] Why Hindustan Copper Share Price is Rising - Equitymaster (Equitymaster)
- [2026-11-12 07:01] What do Yancoal Australia's (ASX:YAL) renewed Glencore trading caps say about its coal sales to 2029? - Kalkine (Kalkine)
### macro
- [2026-11-12 10:03] Middle East situation and Ukraine-Russia talks shift oil prices - The New Voice of Ukraine (The New Voice of Ukraine)
- [2026-11-12 09:45] European Stocks Reach Record High as Corporate Earnings Offset Technology Sector Declines: DAX, CAC, FTSE100 - Yahoo Finance UK (Yahoo Finance UK)
- [2026-11-12 07:57] European business sentiment improves, but inflation and debt risks mount: Survey - The Economic Times (The Economic Times)
- [2026-11-12 06:03] Oil falls over $1 on easing geopolitical fears and oversupply worries - WHTC (WHTC)
- [2026-11-12 03:49] Stock Market Today (November 12): Sensex, Nifty Open Flat; Oil Prices Fall Over 1% On US-Iran, Russia-Ukraine - Times Now (Times Now)
- [2026-11-12 03:07] Oil prices drop more than $1 as hopes for Iran, Ukraine peace talks pressure markets - Investify (Investify)

## Drivers
- BZ=F: -0.88%
- CL=F: -0.89%
- GC=F: -1.30%
- HG=F: -1.00%
- NG=F: +3.05%
- EURUSD=X: -0.64%
- ^STOXX50E: +0.43%
- ^GDAXI: +1.04%
- ^FTSE: +0.35%
- ^VIX: +4.29%

## Traded names: price EUR, quote age min, entry cost % (commission, FX, tax, slippage), max whole shares under the 25% lab cap
- ANTO.L [copper_uranium] 38.9 EUR, age 15.1 min, entry cost 1.64%, max 6 shares
- AZN.L [pharma] 167.55 EUR, age 15.5 min, entry cost 2.27%, max 1 shares
- BAYN.DE [pharma] 57.58 EUR, age 15.3 min, entry cost 0.92%, max 4 shares
- BESI.AS [chips] 159.45 EUR, age 15.7 min, entry cost 0.83%, max 1 shares
- BOL.ST [copper_uranium] 46.5 EUR, age 0.2 min, entry cost 1.07%, max 5 shares
- BP.L [oil_gas] 6.76 EUR, age 15.1 min, entry cost 1.54%, max 36 shares
- EDV.L [gold_miners] 45.99 EUR, age 15.5 min, entry cost 1.61%, max 5 shares
- ENI.MI [oil_gas] 25.49 EUR, age 15.1 min, entry cost 0.9%, max 9 shares
- EQNR.OL [oil_gas] 37.44 EUR, age 15.5 min, entry cost 1.13%, max 6 shares
- FRES.L [gold_miners] 29.36 EUR, age 16.4 min, entry cost 1.6%, max 8 shares
- GLEN.L [copper_uranium] 6.17 EUR, age 15.0 min, entry cost 1.53%, max 40 shares
- GSK.L [pharma] 22.83 EUR, age 15.8 min, entry cost 1.58%, max 10 shares
- IFX.DE [chips] 51.61 EUR, age 15.0 min, entry cost 0.84%, max 4 shares
- KGH.WA [copper_uranium] 65.36 EUR, age 15.2 min, entry cost 1.07%, max 3 shares
- NOVN.SW [pharma] 145.73 EUR, age 15.3 min, entry cost 1.14%, max 1 shares
- NOVO-B.CO [pharma] 37.34 EUR, age 0.2 min, entry cost 1.14%, max 6 shares
- REP.MC [oil_gas] 29.63 EUR, age 16.2 min, entry cost 1.02%, max 8 shares
- RIO.L [copper_uranium] 76.01 EUR, age 15.0 min, entry cost 1.6%, max 3 shares
- SAN.PA [pharma] 88.0 EUR, age 15.2 min, entry cost 1.4%, max 2 shares
- SHEL.L [oil_gas] 43.72 EUR, age 15.1 min, entry cost 1.6%, max 5 shares
- STMPA.PA [chips] 42.06 EUR, age 15.1 min, entry cost 1.3%, max 5 shares
- TTE.PA [oil_gas] 79.33 EUR, age 15.1 min, entry cost 1.22%, max 3 shares

Lab limits: {"start_cash": 1000.0, "max_positions": 5, "max_pos_pct": 0.25, "min_conf": 0.0, "horizons": [1, 2, 3, 5, 10, 20], "max_new_buys_day": 5, "stop_pct": -8.0, "daily_loss_pct": -3.0, "weekly_loss_pct": -6.0, "max_fee_pct": 1.5, "cutoff_min": 30, "open_delay_min": 15}