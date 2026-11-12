# Lab input, decision day 2026-11-12 (now 14:18 UTC)
Output file to write: /home/user/news-market-analysis/data/paper_lab_news/run/2026-11-12/lab_output.json

## This lab: news | focus: event and news ideas: post-results or guidance drift, commodity or driver lag, sector catch-up after one name moves | allowed horizons: [1, 2, 3, 5, 10, 20]

## Registered ideas (registry)
- [testing] news-drift: Prices underreact to firm-specific news about results, guidance or analyst rating/target changes, so a name that moves up clearly more than its theme on such news keeps drifting for days to weeks. | rule: Entry: a headline in the input names the stock (or its company) and is about results, guidance/outlook, or an analyst rating or target-price change, AND the stock's d1 >= +2.0% AND d1 is at least 1.0 point above the average d1 of its theme (theme from the traded-names table). Buy max shares, horizon 10 trading days; exit at horizon or the -8% stop. One entry per name per 10 days. | source: Bernard & Thomas 1989 (post-earnings-announcement drift); Womack 1996 and Brav & Lehavy 2003 (drift after analyst recommendation / target price revisions) | note: New today; first trigger EQNR.OL (Jefferies target raise, d1 +3.30% vs oil_gas theme average +2.22%).
- [testing] theme-catchup: Information diffuses slowly across firms in the same industry, so a theme member that has not followed a strong theme move catches up over the next days. | rule: Entry: within one theme, the top name has d1 >= +3.0% and the theme average d1 >= +1.5%; buy the theme name with the lowest d1 if its d1 is at least 2.0 points below the theme average and it has no own headline in the input. Buy max shares, horizon 5 trading days; exit at horizon or the -8% stop. | source: Hou 2007 (industry information diffusion and lead-lag); Moskowitz & Grinblatt 1999 (industry momentum) | note: New today; no trigger (chips moved together +4.3 to +6.1%, oil_gas laggard TTE only 0.75 pt below theme average).
- [testing] driver-lag: Commodity producers' shares underreact to same-day moves in their main commodity and catch up over the following days. | rule: Entry: driver d1 >= +1.5% (BZ=F for oil_gas, GC=F for gold_miners, HG=F for copper_uranium) AND the stock's d1 is at least 2.0 points below the driver move AND d5 of the stock is not below -8%. Buy max shares, horizon 3 trading days; exit at horizon or the -8% stop. At most 2 names per driver per day (largest lag first). | source: Hong, Torous & Valkanov 2007 (industries lead stock markets / gradual information diffusion); own hypothesis for the commodity-stock lag form | note: New today; no trigger (BZ=F +1.33%, GC=F +0.20%, HG=F +1.00%, all below the 1.5% threshold).

# Lab results per idea (closed trades only; excess = net trade % minus the mean move of the whole universe over the same days, i.e. the luck benchmark)
- [testing] news-drift (Prices underreact to firm-specific news about results, guidance or analyst rating/target c): 0 closed  => too few closed trades (20 needed) to judge
- [testing] theme-catchup (Information diffuses slowly across firms in the same industry, so a theme member that has ): 0 closed  => too few closed trades (20 needed) to judge
- [testing] driver-lag (Commodity producers' shares underreact to same-day moves in their main commodity and catch): 0 closed  => too few closed trades (20 needed) to judge

Account: equity 1001.70 EUR, cash 773.74 EUR, start 1000.00 EUR, total +0.17%.
Open positions:
- EQNR.OL Equinor x6 entry 37.20 EUR now 37.99 EUR, opened 2026-11-11, exit by 2026-11-25, theme oil_gas, catalyst quoted: lab idea news-drift: Headline 'Jefferies raises target price for Equinor' with EQNR d1 +3.30%, 1.08 
Pending orders: none

## Per-name features (daily closes up to now; last, 1/5/20-day move %, % below the 3-month high)
- ANTO.L: last 3198.0 d1 -3.35 d5 +2.34 d20 -6.65 below_3m_high -21.64
- AZN.L: last 13986.0 d1 +0.65 d5 -0.40 d20 +10.14 below_3m_high -0.57
- BAYN.DE: last 56.78 d1 +0.04 d5 +1.00 d20 +27.85 below_3m_high -0.53
- BESI.AS: last 156.75 d1 -1.88 d5 +11.25 d20 -4.07 below_3m_high -34.08
- BOL.ST: last 510.6 d1 -2.15 d5 +0.59 d20 -3.33 below_3m_high -12.69
- BP.L: last 565.8 d1 -0.21 d5 -0.28 d20 -7.32 below_3m_high -11.39
- EDV.L: last 3805.0 d1 -7.80 d5 -5.18 d20 -7.65 below_3m_high -20.61
- ENI.MI: last 25.59 d1 +1.55 d5 +0.93 d20 -0.72 below_3m_high -7.45
- EQNR.OL: last 402.5 d1 +1.85 d5 -0.72 d20 -6.24 below_3m_high -11.30
- FRES.L: last 2438.0 d1 -3.22 d5 -2.28 d20 -8.65 below_3m_high -24.26
- GLEN.L: last 511.9 d1 -0.74 d5 +3.02 d20 -10.83 below_3m_high -18.62
- GSK.L: last 1901.5 d1 +0.77 d5 +0.61 d20 +1.77 below_3m_high -1.14
- IFX.DE: last 51.06 d1 -2.03 d5 +11.12 d20 -2.69 below_3m_high -21.06
- KGH.WA: last 283.05 d1 -1.72 d5 -1.34 d20 -14.51 below_3m_high -25.12
- NOVN.SW: last 134.12 d1 +1.04 d5 +0.00 d20 +6.53 below_3m_high -0.27
- NOVO-B.CO: last 277.05 d1 +1.60 d5 +2.14 d20 +5.16 below_3m_high -9.99
- REP.MC: last 29.67 d1 +0.37 d5 -1.79 d20 +0.10 below_3m_high -5.93
- RIO.L: last 6306.0 d1 -1.24 d5 +0.57 d20 -6.94 below_3m_high -18.51
- SAN.PA: last 88.22 d1 +1.86 d5 +4.37 d20 +22.26 below_3m_high +0.00
- SHEL.L: last 3669.0 d1 -0.04 d5 -3.04 d20 -6.12 below_3m_high -9.14
- STMPA.PA: last 41.26 d1 -2.18 d5 +11.30 d20 -0.37 below_3m_high -20.66
- TTE.PA: last 80.23 d1 +1.08 d5 -0.58 d20 +0.02 below_3m_high -6.09

## Headlines per theme (newest first)
### oil_gas
- [2026-11-12 14:05] BP, Shell, and TotalEnergies: Where Next for Oil Stocks as Crude Prices Fall? - Morningstar (Morningstar)
- [2026-11-12 14:03] Petrobras in Talks to Aquire Stake in BP’s Giant Bumerangue Oil Discovery – Sources - Brazil Energy Insight (Brazil Energy Insight)
- [2026-11-12 13:52] Why falling oil price, rupee recovery mark a breather, not breakthrough, for India - India Today (India Today)
- [2026-11-12 13:49] Oil Prices Face Mixed Signals as U.S. Distillate Stocks Fall - FXEmpire (FXEmpire)
- [2026-11-12 13:30] Brent Crude, WTI Oil Price Forecasts: Goldman Puts Oil At $108 For Q4 2026 - Exchange Rates UK (Exchange Rates UK)
- [2026-11-12 13:30] Turkey Agrees to Record $1.6 Billion Climate Policy Funding Deal - Crude Oil Prices Today | OilPrice.com (Crude Oil Prices Today | OilPrice.com)
### gold_miners
- [2026-11-12 14:11] Endeavour Mining’s gold streak ends - Investors' Chronicle (Investors' Chronicle)
- [2026-11-12 14:09] Gold price today slides 1.6% below $4,000 as dollar hits 19-month high - Cryptonews.net (Cryptonews.net)
- [2026-11-12 13:56] Gold drops over 2% as Trump plays down the need for an Iran deal - FXStreet (FXStreet)
- [2026-11-12 13:51] Endeavour Mining Greenlights $1.2B Assafou Gold Project, Targets First Gold in H1 2029 - News and Statistics - IndexBox (IndexBox)
- [2026-11-12 13:45] Gold Price Forecast: UBS's $4,000 Support Call Tested As Bullion Falls To $3,942 - Exchange Rates UK (Exchange Rates UK)
- [2026-11-12 13:45] Silver Price Outlook: Positioning In Gold, Silver Turned Light Says JP Morgan - Exchange Rates UK (Exchange Rates UK)
### chips
- [2026-11-12 14:11] ASML's Buyback Firepower Meets a Fragile Chip Recovery - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-12 14:00] STMicroelectronics’ 600V three-phase gate drivers combine flexibility, precision, and protection - EIN News (EIN News)
- [2026-11-12 14:00] Wall Street's Next Blockbuster Stock Split Could Come From This Chip Equipment Giant - The Globe and Mail (The Globe and Mail)
- [2026-11-12 13:39] Overseas Stock Markets Today: Europe Hits Records - www.stl.news (www.stl.news)
- [2026-11-12 13:16] Infineon AI Power Deals Top €10B, 5.9x Its AI Power Sales - FourWeekMBA (FourWeekMBA)
- [2026-11-12 13:15] STMicroelectronics shares, second-worst performer in the CAC 40 behind Stellantis, fall 1.5% - Idéal Investisseur (Idéal Investisseur)
### pharma
- [2026-11-12 13:39] Eli Lilly beats Novo Nordisk to win China approval for first GLP-1 weight-loss pill - Telegraph India (Telegraph India)
- [2026-11-12 13:38] Rezera (RZRA): IPO Postponed Despite Substantial GSK Anchor Order - Smartkarma (Smartkarma)
- [2026-11-12 12:14] AstraZeneca And 2 Other British Undervalued Stocks To Own - Yahoo Finance (Yahoo Finance)
- [2026-11-12 12:00] Astrosalva Therapeutics Adds Michael MacLean, Former CFO of Novartis-Acquired Avidity Biosciences, to Strategic Advisory Board - Morningstar (Morningstar)
- [2026-11-12 11:54] Symbiotec Pharmalab Limited expects FDA approval by late 2027 - Multibagg AI (Multibagg AI)
- [2026-11-12 11:35] How FDA Vision Warning Will Impact Novo Nordisk Stock Investors - Simply Wall St (Simply Wall St)
### copper_uranium
- [2026-11-12 14:00] Weak mag. 2.9 earthquake - 48 km northeast of Calama, Provincia de El Loa, Region de Antofagasta, Chile, on Thursday, Nov 12, 2026, at 10:49 am (GMT -3) - Volcano Discovery (Volcano Discovery)
- [2026-11-12 12:24] Copper hits 3-month lows, focus on demand and US rates - Business Recorder (Business Recorder)
- [2026-11-12 12:17] Glencore stock trades at 6.18 euros on Lang & Schwarz Thursday - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-12 12:01] Dedicated players, referees, and coaches celebrated at annual eMalahleni LFA awards - The Citizen (The Citizen)
- [2026-11-12 11:55] The smarter E Summit Chile launches in Antofagasta: Connecting energy, mining and industry to accelerate Chile?s energy transition - www.renewableenergymagazine.com (www.renewableenergymagazine.com)
- [2026-11-12 11:20] Weak mag. 2.9 earthquake - 98 km north of Calama, Provincia de El Loa, Region de Antofagasta, Chile, on Thursday, Nov 12, 2026, at 08:12 am (GMT -3) - Volcano Discovery (Volcano Discovery)
### macro
- [2026-11-12 11:15] AM Markets Need to Know: Nvidia CEO faces pressure, EU delays EV tariffs, and more (SP500:) - Seeking Alpha (Seeking Alpha)
- [2026-11-12 10:03] Middle East situation and Ukraine-Russia talks shift oil prices - The New Voice of Ukraine (The New Voice of Ukraine)
- [2026-11-12 09:45] European Stocks Reach Record High as Corporate Earnings Offset Technology Sector Declines: DAX, CAC, FTSE100 - Yahoo Finance UK (Yahoo Finance UK)
- [2026-11-12 08:36] Why Ukraine has already lost the welded pipe market - GMK Center (GMK Center)
- [2026-11-12 07:57] European business sentiment improves, but inflation and debt risks mount: Survey - The Economic Times (The Economic Times)
- [2026-11-12 06:11] European business sentiment picks up, inflation worries grow, su - Global Banking & Finance Review (Global Banking & Finance Review)

## Drivers
- BZ=F: +0.50%
- CL=F: -0.01%
- GC=F: -2.65%
- HG=F: -1.43%
- NG=F: +4.07%
- EURUSD=X: -0.65%
- ^STOXX50E: -0.02%
- ^GDAXI: +0.35%
- ^FTSE: +0.10%
- ^VIX: +6.98%

## Traded names: price EUR, quote age min, entry cost % (commission, FX, tax, slippage), max whole shares under the 25% lab cap
- ANTO.L [copper_uranium] 38.23 EUR, age 15.3 min, entry cost 1.65%, max 6 shares
- AZN.L [pharma] 167.15 EUR, age 15.5 min, entry cost 2.28%, max 1 shares
- BAYN.DE [pharma] 56.78 EUR, age 15.2 min, entry cost 0.93%, max 4 shares
- BESI.AS [chips] 156.8 EUR, age 15.3 min, entry cost 0.85%, max 1 shares
- BOL.ST [copper_uranium] 45.87 EUR, age 0.2 min, entry cost 1.08%, max 5 shares
- BP.L [oil_gas] 6.76 EUR, age 15.1 min, entry cost 1.54%, max 36 shares
- EDV.L [gold_miners] 45.45 EUR, age 15.8 min, entry cost 1.62%, max 5 shares
- ENI.MI [oil_gas] 25.59 EUR, age 15.3 min, entry cost 0.9%, max 9 shares
- EQNR.OL [oil_gas] 37.99 EUR, age 15.1 min, entry cost 1.12%, max 6 shares
- FRES.L [gold_miners] 29.15 EUR, age 16.2 min, entry cost 1.61%, max 8 shares
- GLEN.L [copper_uranium] 6.12 EUR, age 15.1 min, entry cost 1.54%, max 40 shares
- GSK.L [pharma] 22.73 EUR, age 15.2 min, entry cost 1.59%, max 10 shares
- IFX.DE [chips] 51.09 EUR, age 15.0 min, entry cost 0.85%, max 4 shares
- KGH.WA [copper_uranium] 64.16 EUR, age 15.2 min, entry cost 1.08%, max 3 shares
- NOVN.SW [pharma] 145.1 EUR, age 15.2 min, entry cost 1.14%, max 1 shares
- NOVO-B.CO [pharma] 37.03 EUR, age 0.1 min, entry cost 1.14%, max 6 shares
- REP.MC [oil_gas] 29.67 EUR, age 15.1 min, entry cost 1.02%, max 8 shares
- RIO.L [copper_uranium] 75.39 EUR, age 15.6 min, entry cost 1.61%, max 3 shares
- SAN.PA [pharma] 88.2 EUR, age 15.0 min, entry cost 1.4%, max 2 shares
- SHEL.L [oil_gas] 43.87 EUR, age 15.2 min, entry cost 1.6%, max 5 shares
- STMPA.PA [chips] 41.29 EUR, age 15.0 min, entry cost 1.21%, max 6 shares
- TTE.PA [oil_gas] 80.25 EUR, age 15.2 min, entry cost 1.21%, max 3 shares

Lab limits: {"start_cash": 1000.0, "max_positions": 5, "max_pos_pct": 0.25, "min_conf": 0.0, "horizons": [1, 2, 3, 5, 10, 20], "max_new_buys_day": 5, "stop_pct": -8.0, "daily_loss_pct": -3.0, "weekly_loss_pct": -6.0, "max_fee_pct": 1.5, "cutoff_min": 30, "open_delay_min": 15}