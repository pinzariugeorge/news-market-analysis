# Lab input, decision day 2026-11-13 (now 12:18 UTC)
Output file to write: /home/user/news-market-analysis/data/paper_lab_short/run/2026-11-13/lab_output.json

## This lab: short | focus: fast ideas held 1 to 3 days: dip reversal, one-day news reaction, gap and fade | allowed horizons: [1, 2, 3]

## Registered ideas (registry)
- [testing] nonews-dip-reversal: Large one-day drops without company-specific news tend to be liquidity or overreaction moves that partly reverse over the next few days, while drops with news do not. | rule: BUY at the table's max shares when a name has d1 <= -4.0% and no headline in its theme today names the company; skip if entry cost > 1.3%. Horizon 3 trading days; exit at horizon or the -8% stop. | source: Lehmann 1990 (QJE) and Jegadeesh 1990 (JF) short-term reversal; Chan 2003 (JFE) 'Stock price reaction to news and no-news' | note: 0 closed. 2026-11-12: EDV.L d1 -6.03% but two gold_miners headlines name Endeavour (Mana output warning), so it is a news drop and is excluded; its 1.6% entry cost would also fail the 1.3% cap. No trigger.
- [testing] news-day-drift: Large one-day gains that come with company-specific results or guidance news are under-reacted to and keep drifting for a few days, unlike no-news moves. | rule: BUY at the table's max shares when a name has d1 >= +4.0% and at least one headline today names the company and reports its results, guidance, forecast or outlook; skip if entry cost > 1.3%. Horizon 3 trading days; exit at horizon or the -8% stop. | source: Chan 2003 (JFE) news vs no-news; Savor 2012 (JFE) 'Stock returns after major price shocks: the role of information' | note: 0 closed; one open (IFX.DE x4 from 2026-11-11, now -2.2% vs entry, exit by 2026-11-16). 2026-11-12: no name with d1 >= +4%, no trigger.
- [testing] theme-laggard-catchup: When one name in a theme jumps on its own news, peers in the same theme that have not yet moved catch up over the next one to two days because information diffuses slowly across related stocks. | rule: If a name has d1 >= +5.0% with a same-day headline naming it, BUY at max shares any other name in the same theme with d1 <= +1.0% and no headline naming it today; skip if entry cost > 1.3%. Horizon 2 trading days; exit at horizon or the -8% stop. | source: Hou 2007 (RFS) 'Industry information diffusion and the lead-lag effect in stock returns' | note: First run; chips leader IFX.DE +7.34% but peers BESI.AS +5.50% and STMPA.PA +4.75% already moved, so no laggard today.

# Lab results per idea (closed trades only; excess = net trade % minus the mean move of the whole universe over the same days, i.e. the luck benchmark)
- [testing] nonews-dip-reversal (Large one-day drops without company-specific news tend to be liquidity or overreaction mov): 0 closed  => too few closed trades (20 needed) to judge
- [testing] news-day-drift (Large one-day gains that come with company-specific results or guidance news are under-rea): 0 closed  => too few closed trades (20 needed) to judge
- [testing] theme-laggard-catchup (When one name in a theme jumps on its own news, peers in the same theme that have not yet ): 0 closed  => too few closed trades (20 needed) to judge

Account: equity 994.24 EUR, cash 786.48 EUR, start 1000.00 EUR, total -0.58%.
Open positions:
- IFX.DE Infineon x4 entry 52.76 EUR now 51.94 EUR, opened 2026-11-11, exit by 2026-11-16, theme chips, catalyst quoted: lab idea news-day-drift: IFX.DE is up 7.34% today with a company outlook headline ('Infineon expects
Pending orders: none

## Per-name features (daily closes up to now; last, 1/5/20-day move %, % below the 3-month high)
- ANTO.L: last 3212.0 d1 -0.16 d5 +3.18 d20 -5.53 below_3m_high -21.29
- AZN.L: last 13938.0 d1 +0.06 d5 +0.06 d20 +11.99 below_3m_high -0.91
- BAYN.DE: last 56.94 d1 +0.67 d5 +2.45 d20 +28.07 below_3m_high -0.25
- BESI.AS: last 157.05 d1 -0.63 d5 +9.52 d20 +0.96 below_3m_high -33.96
- BOL.ST: last 508.0 d1 -0.27 d5 +0.91 d20 -4.80 below_3m_high -13.13
- BP.L: last 573.3 d1 +1.11 d5 +2.48 d20 -6.64 below_3m_high -10.21
- EDV.L: last 3759.0 d1 -0.50 d5 -8.18 d20 -10.41 below_3m_high -21.57
- ENI.MI: last 25.88 d1 +1.59 d5 +3.29 d20 -0.31 below_3m_high -6.42
- EQNR.OL: last 406.5 d1 +0.67 d5 +2.94 d20 -6.03 below_3m_high -10.42
- FRES.L: last 2452.0 d1 +0.33 d5 -2.43 d20 -9.82 below_3m_high -23.83
- GLEN.L: last 515.5 d1 -0.04 d5 +4.11 d20 -11.59 below_3m_high -18.04
- GSK.L: last 1906.5 d1 +0.29 d5 +0.87 d20 +2.36 below_3m_high -0.88
- IFX.DE: last 51.94 d1 -0.33 d5 +13.52 d20 -0.86 below_3m_high -19.70
- KGH.WA: last 282.0 d1 -0.81 d5 +0.79 d20 -13.03 below_3m_high -25.40
- NOVN.SW: last 134.02 d1 -0.15 d5 +0.71 d20 +7.47 below_3m_high -0.34
- NOVO-B.CO: last 274.95 d1 -0.29 d5 +2.04 d20 +5.91 below_3m_high -10.67
- REP.MC: last 30.41 d1 +1.71 d5 +1.71 d20 +2.05 below_3m_high -3.58
- RIO.L: last 6323.0 d1 -0.03 d5 +0.67 d20 -7.23 below_3m_high -18.29
- SAN.PA: last 87.94 d1 -0.05 d5 +5.02 d20 +22.24 below_3m_high -0.05
- SHEL.L: last 3715.0 d1 +1.36 d5 -0.20 d20 -5.66 below_3m_high -8.00
- STMPA.PA: last 43.17 d1 +1.95 d5 +14.69 d20 +4.85 below_3m_high -16.99
- TTE.PA: last 81.75 d1 +1.39 d5 +2.53 d20 +1.29 below_3m_high -4.31

## Headlines per theme (newest first)
### oil_gas
- [2026-11-13 12:01] BP exits Indonesia’s fuel retail market, selling 49.9% stake to AKR - Indonesia Business Post (Indonesia Business Post)
- [2026-11-13 12:00] Crude oil price falls as peace hopes grow; oilseeds hit - The Western Producer (The Western Producer)
- [2026-11-13 11:59] Dan Sparkes: BP to increase number of drilling rigs at ACG field complex to 8 - Report.az (Report.az)
- [2026-11-13 11:49] Equinor and Aker BP proceed as planned after Supreme Court ruling - EnergyWatch (EnergyWatch)
- [2026-11-13 11:34] World oil market is returning to surplus as Gulf exports recover, IEA says - Yahoo! Finance Canada (Yahoo! Finance Canada)
- [2026-11-13 11:31] Schwabo Capital Corporation (TSXV:SBO.H) Sinks in Quiet Trading as the Shell Offers Few Public Clues - kalkine.ca (kalkine.ca)
### gold_miners
- [2026-11-13 12:14] Gold & Silver Prices Fall: Weak Global Cues, Fading Demand - Rediff MoneyWiz (Rediff MoneyWiz)
- [2026-11-13 11:11] Gold struggles below $3,900 ahead of US PPI data - FXStreet (FXStreet)
- [2026-11-13 11:09] Why Is Fresnillo (LSE:FRES) Moving Within [FTSE 350]? - Kalkine Media (Kalkine Media)
- [2026-11-13 10:43] Gem, jewellery exports up 34% on growing demand, rise in gold prices - BusinessLine (BusinessLine)
- [2026-11-13 10:19] Gold-silver, Nifty-gold and Sensex-gold ratios: What do they signal for investors? - Moneycontrol.com (Moneycontrol.com)
- [2026-11-13 10:16] Inflation persists, but markets keep defying gravity - GoldBroker (GoldBroker)
### chips
- [2026-11-13 12:15] OpenAI Backs Congressional Effort to Limit China's Access to AI Semiconductors Including ASML Tech (ASML) - GuruFocus (GuruFocus)
- [2026-11-13 11:21] ASML's Buyback Machine Keeps Running While Labour Talks Hit the Skids - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-13 11:02] ETFs Are Net Sellers of ASML (ASML) on Nov. 11 - Yahoo Finance (Yahoo Finance)
- [2026-11-13 11:02] Infineon stock eyes 20% FY27 growth after record quarter - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-13 10:51] STMicroelectronics stock schedules STM32 investor webcast - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-13 10:08] Is Synopsys (SNPS) A Bargain Following Its European Chip Design Platform Deal? - Yahoo Finance (Yahoo Finance)
### pharma
- [2026-11-13 12:10] Sanofi-backed Windward hits $225M IPO goal to advance respiratory drugs from China - Fierce Biotech (Fierce Biotech)
- [2026-11-13 12:04] AstraZeneca's Baxfendy recommended for EU approval in hypertension - StreetInsider (StreetInsider)
- [2026-11-13 12:03] EU Medicines Agency Panel Issues Positive Opinion on AstraZeneca's Hypertension Drug - marketscreener.com (marketscreener.com)
- [2026-11-13 11:47] The first 266 thousand Sanofi flu vaccines pass state control - Mezha.net (Mezha.net)
- [2026-11-13 11:44] Novartis eyes Rhapsido’s broader use on positive urticaria data drop - Yahoo Finance (Yahoo Finance)
- [2026-11-13 11:31] FTSE 100 GSK (LSE:GSK) Advances Its Medicines and Vaccines - Kalkine Media (Kalkine Media)
### copper_uranium
- [2026-11-13 12:00] Copper benchmark rocked by miner-smelter tug-of-war - Mining.com.au (Mining.com.au)
- [2026-11-13 11:36] Light mag. 3.0 earthquake - Antofagasta, Chile, on Friday, Nov 13, 2026, at 11:30 am (Universal Time) - Volcano Discovery (Volcano Discovery)
- [2026-11-13 11:25] Nvidia's Huang Exit Shakes Copper's AI Demand Story as Goldman Trims Price Target - BigGo Finance (BigGo Finance)
- [2026-11-13 10:29] Rio Tinto stock commits Bell Bay jobs and investment through 2031 - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-13 10:13] Goldman Sachs Projects Copper Prices at $15,600 per Tonne by December 2027 Amid Supply Constraints - Yahoo Finance UK (Yahoo Finance UK)
- [2026-11-13 10:12] Goldman Sachs Forecasts Copper Prices to Reach $15,600 per Tonne by December 2027 - Yahoo Finance (Yahoo Finance)
### macro
- [2026-11-13 11:08] Nexi stock gains strategic role in ECB digital euro network - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-13 10:31] SA citrus exports fall short of record as Iran War squeezes key markets - Daily Maverick (Daily Maverick)
- [2026-11-13 08:29] European stock market open: Stocks ease slightly as the rally takes a breather - investingLive (investingLive)
- [2026-11-13 08:29] PERSPECTIVE: Democratic Sweep Adds New Twist to Markets’ Iran War, AI, and Debt Worries - EnergyNow.com (EnergyNow.com)
- [2026-11-13 08:25] French inflation rises to 3.7% in October, highest since December 2023 - Reuters (Reuters)
- [2026-11-13 08:11] Goldman Sachs lifts 12-month target for European stocks on energy price relief - The Edge Malaysia (The Edge Malaysia)

## Drivers
- BZ=F: +0.28%
- CL=F: -0.23%
- GC=F: +0.35%
- HG=F: -0.37%
- NG=F: -1.68%
- EURUSD=X: -0.38%
- ^STOXX50E: -0.01%
- ^GDAXI: +0.02%
- ^FTSE: +0.10%
- ^VIX: -2.62%

## Traded names: price EUR, quote age min, entry cost % (commission, FX, tax, slippage), max whole shares under the 25% lab cap
- ANTO.L [copper_uranium] 38.43 EUR, age 15.5 min, entry cost 1.64%, max 6 shares
- AZN.L [pharma] 166.77 EUR, age 15.2 min, entry cost 2.28%, max 1 shares
- BAYN.DE [pharma] 56.94 EUR, age 15.5 min, entry cost 0.93%, max 4 shares
- BESI.AS [chips] 157.05 EUR, age 15.2 min, entry cost 0.85%, max 1 shares
- BOL.ST [copper_uranium] 45.49 EUR, age 0.5 min, entry cost 1.09%, max 5 shares
- BP.L [oil_gas] 6.86 EUR, age 15.0 min, entry cost 1.54%, max 36 shares
- EDV.L [gold_miners] 44.98 EUR, age 15.5 min, entry cost 1.62%, max 5 shares
- ENI.MI [oil_gas] 25.88 EUR, age 15.9 min, entry cost 0.95%, max 9 shares
- EQNR.OL [oil_gas] 38.5 EUR, age 15.2 min, entry cost 1.11%, max 6 shares
- FRES.L [gold_miners] 29.34 EUR, age 15.5 min, entry cost 1.6%, max 8 shares
- GLEN.L [copper_uranium] 6.17 EUR, age 15.0 min, entry cost 1.54%, max 40 shares
- GSK.L [pharma] 22.81 EUR, age 15.4 min, entry cost 1.58%, max 10 shares
- IFX.DE [chips] 51.94 EUR, age 15.1 min, entry cost 0.83%, max 4 shares
- KGH.WA [copper_uranium] 63.87 EUR, age 15.1 min, entry cost 1.08%, max 3 shares
- NOVN.SW [pharma] 144.65 EUR, age 15.5 min, entry cost 1.14%, max 1 shares
- NOVO-B.CO [pharma] 36.74 EUR, age 0.1 min, entry cost 1.06%, max 6 shares
- REP.MC [oil_gas] 30.41 EUR, age 16.6 min, entry cost 1.07%, max 8 shares
- RIO.L [copper_uranium] 75.65 EUR, age 15.6 min, entry cost 1.61%, max 3 shares
- SAN.PA [pharma] 87.92 EUR, age 15.6 min, entry cost 1.4%, max 2 shares
- SHEL.L [oil_gas] 44.45 EUR, age 15.3 min, entry cost 1.59%, max 5 shares
- STMPA.PA [chips] 43.17 EUR, age 15.1 min, entry cost 1.28%, max 5 shares
- TTE.PA [oil_gas] 81.75 EUR, age 15.1 min, entry cost 1.2%, max 3 shares

Lab limits: {"start_cash": 1000.0, "max_positions": 5, "max_pos_pct": 0.25, "min_conf": 0.0, "horizons": [1, 2, 3], "max_new_buys_day": 5, "stop_pct": -8.0, "daily_loss_pct": -3.0, "weekly_loss_pct": -6.0, "max_fee_pct": 1.5, "cutoff_min": 30, "open_delay_min": 15}