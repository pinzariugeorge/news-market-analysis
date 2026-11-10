# Lab input, decision day 2026-11-10 (now 13:53 UTC)
Output file to write: /home/user/news-market-analysis/data/paper_lab/run/2026-11-10/lab_output.json

## Registered ideas (registry)
- [testing] high-momentum-20d: Stocks trading at their recent high after a strong run keep drifting up because investors anchor on the high and under-react to the good news behind the run. | rule: Entry: below_3m_high >= -1.0% AND d20 >= +10% AND entry cost <= 1.5%. If more than 2 names qualify on a day, buy only the 2 with the largest d20. Size: max whole shares under the 25% cap. Horizon 20 trading days; exit at horizon or the -8% stop. No re-entry in a name already held. | source: George & Hwang (2004), The 52-Week High and Momentum Investing, Journal of Finance; adapted to the 3-month high available in the features | note: New. First signal day: AZN, BAYN, GSK, NOVN, SAN.PA all qualify on price; AZN fails the cost filter (2.26%); BAYN and SAN.PA have the largest d20. All signals are pharma, so the results are exposed to one sector.
- [testing] guidance-drift-10d: After a company raises its forecast or reports results above expectations, the price keeps drifting in the direction of the news for days because investors under-react to earnings information. | rule: Entry: a headline on the decision day that names the company and says it raised its forecast/guidance/outlook or beat results expectations, AND d1 >= +2% (the market confirms the news as positive), AND entry cost <= 1.5%. Horizon 10 trading days; exit at horizon or the -8% stop. Analyst rating/target changes and regulatory approvals do not count. | source: Bernard & Thomas (1989), Post-Earnings-Announcement Drift; Chan, Jegadeesh & Lakonishok (1996), Momentum Strategies | note: New. First signal: IFX.DE raised its data-centre revenue forecast to nearly 4 bn EUR, d1 +2.59%.
- [testing] no-news-drop-reversal-3d: A large one-day drop without company-specific news is often liquidity or flow driven and partly reverses within days, while drops with news do not. | rule: Entry: d1 <= -3.0% AND no headline on the decision day naming the company (theme-wide commodity headlines are allowed) AND the stock's main driver (oil for oil_gas, gold for gold_miners, copper for copper_uranium, ^STOXX50E otherwise) moved less than half as much as the stock, AND entry cost <= 1.5%. Horizon 3 trading days; exit at horizon or the -8% stop. | source: Jegadeesh (1990), Evidence of Predictable Behavior of Security Returns; Lehmann (1990); Chan (2003), Stock price reaction to news and no-news | note: New. No signal today: the largest drop is REP.MC -2.83%, and it is fully explained by Brent -2.73%.

# Lab results per idea (closed trades only; excess = net trade % minus the mean move of the whole universe over the same days, i.e. the luck benchmark)
- [testing] high-momentum-20d (Stocks trading at their recent high after a strong run keep drifting up because investors ): 0 closed  => too few closed trades (20 needed) to judge
- [testing] guidance-drift-10d (After a company raises its forecast or reports results above expectations, the price keeps): 0 closed  => too few closed trades (20 needed) to judge
- [testing] no-news-drop-reversal-3d (A large one-day drop without company-specific news is often liquidity or flow driven and p): 0 closed  => too few closed trades (20 needed) to judge

Account: equity 1000.00 EUR, cash 1000.00 EUR, start 1000.00 EUR, total +0.00%.
Open positions: none.
Pending orders: none

## Per-name features (daily closes up to now; last, 1/5/20-day move %, % below the 3-month high)
- ANTO.L: last 3262.0 d1 -1.30 d5 +3.95 d20 -9.09 below_3m_high -20.07
- AZN.L: last 14052.0 d1 -0.10 d5 +2.12 d20 +18.12 below_3m_high -0.10
- BAYN.DE: last 57.1 d1 +0.85 d5 +10.15 d20 +29.33 below_3m_high +0.00
- BESI.AS: last 150.25 d1 +2.21 d5 -3.75 d20 -12.90 below_3m_high -36.82
- BOL.ST: last 517.4 d1 -0.46 d5 +3.73 d20 -5.55 below_3m_high -11.53
- BP.L: last 543.72 d1 -2.33 d5 -7.73 d20 -10.87 below_3m_high -14.84
- EDV.L: last 4183.0 d1 -2.36 d5 +17.60 d20 +1.23 below_3m_high -12.73
- ENI.MI: last 24.54 d1 -1.78 d5 -5.74 d20 -4.40 below_3m_high -11.25
- EQNR.OL: last 376.5 d1 -2.13 d5 -10.80 d20 -11.66 below_3m_high -17.03
- FRES.L: last 2579.0 d1 -2.24 d5 +12.82 d20 -5.04 below_3m_high -19.88
- GLEN.L: last 506.6 d1 -1.71 d5 +0.46 d20 -13.09 below_3m_high -19.46
- GSK.L: last 1940.5 d1 +1.89 d5 +6.18 d20 +10.70 below_3m_high +0.00
- IFX.DE: last 49.44 d1 +1.68 d5 -5.65 d20 -11.71 below_3m_high -23.56
- KGH.WA: last 287.5 d1 -0.66 d5 +4.41 d20 -16.58 below_3m_high -23.94
- NOVN.SW: last 134.32 d1 +0.64 d5 +2.14 d20 +12.59 below_3m_high +0.00
- NOVO-B.CO: last 273.1 d1 +0.11 d5 +1.09 d20 +6.41 below_3m_high -11.27
- REP.MC: last 28.39 d1 -3.30 d5 -6.33 d20 -4.15 below_3m_high -9.99
- RIO.L: last 6357.0 d1 -0.92 d5 +4.59 d20 -9.15 below_3m_high -17.85
- SAN.PA: last 86.2 d1 +0.51 d5 +6.45 d20 +21.85 below_3m_high +0.00
- SHEL.L: last 3599.5 d1 -2.74 d5 -6.83 d20 -6.88 below_3m_high -10.86
- STMPA.PA: last 39.45 d1 -0.45 d5 -8.47 d20 -10.00 below_3m_high -24.13
- TTE.PA: last 77.47 d1 -1.63 d5 -6.34 d20 -3.03 below_3m_high -9.32

## Headlines per theme (newest first)
### oil_gas
- [2026-11-10 13:51] BP Takes Operatorship of Three Namibia’s Offshore Licenses in Eco Farm-Down - Brazil Energy Insight (Brazil Energy Insight)
- [2026-11-10 13:42] New regulation for heating oil market, but no price controls - BBC (BBC)
- [2026-11-10 13:33] Santander Downgrades Shell to Neutral, Trims PT - marketscreener.com (marketscreener.com)
- [2026-11-10 13:30] Tribunal Hearings Begin in UK-Argentina Row Over Falklands Oil Project - Crude Oil Prices Today | OilPrice.com (Crude Oil Prices Today | OilPrice.com)
- [2026-11-10 13:15] Avient : Advances Sustainability Goals with Renewable Electricity from TotalEnergies Solar Installation - www.marketscreener.com (www.marketscreener.com)
- [2026-11-10 13:07] New updates on when petrol and diesel prices will fall after drop in oil price - Wales Online (Wales Online)
### gold_miners
- [2026-11-10 13:45] Gold price, silver rate today: Why is gold rate down on Tuesday? Check latest bullion outlook - The Economic Times (The Economic Times)
- [2026-11-10 13:25] Gold Price Today: Gold Falls 1.56% on November 10, 2026 - USA Today (USA Today)
- [2026-11-10 13:04] Gold price closing session on November 10th: Continuously reversing direction, closing session in red - Laodong.vn (Laodong.vn)
- [2026-11-10 12:45] Gold Slips as Investors Eye US Inflation Data for Fed Cues - وكالة الأنباء العمانية (العمانية) (وكالة الأنباء العمانية (العمانية))
- [2026-11-10 12:33] Bengaluru Bullion Rates: Gold (22K, 24K) & Silver Prices - Rediff MoneyWiz (Rediff MoneyWiz)
- [2026-11-10 12:30] Midland, in Partnership With Fresnillo, Commences an Airborne Gravity Gradiometer Survey on the La Peltrie Project - GlobeNewswire (GlobeNewswire)
### chips
- [2026-11-10 13:41] Global Stocks Rally as Oil Falls Below $90 - STL.News (STL.News)
- [2026-11-10 13:13] Infineon is raising its data center revenue forecast to nearly €4 billion - Quartz (Quartz)
- [2026-11-10 13:08] Infineon says AI data centre boom to persist despite growing backlash - Euronews.com (Euronews.com)
- [2026-11-10 13:05] Chief executives of Europe's chip firms Infineon, STMicroelectronics and NXP speak at a conference in Munich - The Daily News | Texas' Oldest Newspaper (The Daily News | Texas' Oldest Newspaper)
- [2026-11-10 13:00] Market Wrap: European Stocks Rise, Infineon Shares Up 5% 🔼 Wall Street Weakens Ahead of U.S. CPI - XTB.com (XTB.com)
- [2026-11-10 12:34] European shares closer to record high on easing energy cost hopes - Middle East Online (Middle East Online)
### pharma
- [2026-11-10 13:32] Deutsche Bank Research Raises Bayer PT, Keeps Buy Rating - www.marketscreener.com (www.marketscreener.com)
- [2026-11-10 13:13] Novartis ranks No. 1 in 2026 Access to Medicine Index - Novartis (Novartis)
- [2026-11-10 13:01] NVAX Q3 2026 deep dive: Sanofi milestone and cost controls shape outlook - Yahoo! Finance Canada (Yahoo! Finance Canada)
- [2026-11-10 13:00] Omniose Announces Its Acquisition by AstraZeneca - Business Wire (Business Wire)
- [2026-11-10 13:00] Novartis ranks first place in 2026 Access to Medicine Index - GlobeNewswire (GlobeNewswire)
- [2026-11-10 12:55] Bayer won U.S. FDA approval for a first-in-class stroke blood thinner - Quartz (Quartz)
### copper_uranium
- [2026-11-10 13:16] Southern Copper stock: UBS lifts rating after monthly selloff - ad-hoc-news.de (ad-hoc-news.de)
- [2026-11-10 13:07] Light mag. 3.3 earthquake - Provincia de El Loa, Region de Antofagasta, Chile, on Tuesday, Nov 10, 2026, at 01:03 pm (Universal Time) - Volcano Discovery (Volcano Discovery)
- [2026-11-10 12:31] Southern Copper upgraded by UBS with a new price target - Quantisnow (Quantisnow)
- [2026-11-10 12:12] UBS Upgrades Southern Copper to Neutral From Sell, Price Target is $180 - marketscreener.com (marketscreener.com)
- [2026-11-10 11:51] SP Angel – Today’s Market View, Tuesday 10th November 2026 - Share Talk (Share Talk)
- [2026-11-10 11:27] Fund Update: 823,578 RIO TINTO PLC (RIO) shares added to Cullen Capital Management, LLC portfolio - Quiver Quantitative (Quiver Quantitative)
### macro
- [2026-11-10 13:41] Global Stocks Rally as Oil Falls Below $90 - STL.News (STL.News)
- [2026-11-10 12:34] European shares closer to record high on easing energy cost hopes - Middle East Online (Middle East Online)
- [2026-11-10 12:07] Ringgit edges up against US dollar as markets eye de-escalation in Iran conflict - Malay Mail (Malay Mail)
- [2026-11-10 11:00] US floated redrawing Ukraine's regional borders to let Russia claim Donbas victory - The Economist - Hromadske (Hromadske)
- [2026-11-10 10:52] Stocks rally as investors snap up tech shares at lower prices - Yahoo Finance Australia (Yahoo Finance Australia)
- [2026-11-10 09:57] Markets today | Oil prices slide further as hopes of US-Iran deal lift global stocks - IOL (IOL)

## Drivers
- BZ=F: -3.52%
- CL=F: -3.07%
- GC=F: -1.23%
- HG=F: -0.85%
- NG=F: -0.03%
- EURUSD=X: +0.41%
- ^STOXX50E: +1.00%
- ^GDAXI: +1.10%
- ^FTSE: +0.36%
- ^VIX: +4.47%

## Traded names: price EUR, quote age min, entry cost % (commission, FX, tax, slippage), max whole shares under the 25% lab cap
- ANTO.L [copper_uranium] 39.11 EUR, age 15.1 min, entry cost 1.63%, max 6 shares
- AZN.L [pharma] 168.2 EUR, age 15.0 min, entry cost 2.27%, max 1 shares
- BAYN.DE [pharma] 57.1 EUR, age 15.4 min, entry cost 0.93%, max 4 shares
- BESI.AS [chips] 150.15 EUR, age 15.1 min, entry cost 0.88%, max 1 shares
- BOL.ST [copper_uranium] 46.75 EUR, age 0.1 min, entry cost 1.06%, max 5 shares
- BP.L [oil_gas] 6.51 EUR, age 15.1 min, entry cost 1.53%, max 38 shares
- EDV.L [gold_miners] 50.06 EUR, age 15.1 min, entry cost 1.66%, max 4 shares
- ENI.MI [oil_gas] 24.54 EUR, age 15.1 min, entry cost 0.93%, max 10 shares
- EQNR.OL [oil_gas] 35.36 EUR, age 15.2 min, entry cost 1.09%, max 7 shares
- FRES.L [gold_miners] 30.87 EUR, age 15.5 min, entry cost 1.64%, max 8 shares
- GLEN.L [copper_uranium] 6.06 EUR, age 15.1 min, entry cost 1.54%, max 41 shares
- GSK.L [pharma] 23.22 EUR, age 15.5 min, entry cost 1.57%, max 10 shares
- IFX.DE [chips] 49.44 EUR, age 15.0 min, entry cost 0.87%, max 5 shares
- KGH.WA [copper_uranium] 65.5 EUR, age 15.5 min, entry cost 1.06%, max 3 shares
- NOVN.SW [pharma] 145.88 EUR, age 15.0 min, entry cost 1.14%, max 1 shares
- NOVO-B.CO [pharma] 36.5 EUR, age 0.2 min, entry cost 1.06%, max 6 shares
- REP.MC [oil_gas] 28.39 EUR, age 15.1 min, entry cost 1.05%, max 8 shares
- RIO.L [copper_uranium] 76.08 EUR, age 15.1 min, entry cost 1.6%, max 3 shares
- SAN.PA [pharma] 86.22 EUR, age 15.1 min, entry cost 1.41%, max 2 shares
- SHEL.L [oil_gas] 43.06 EUR, age 15.0 min, entry cost 1.61%, max 5 shares
- STMPA.PA [chips] 39.44 EUR, age 15.1 min, entry cost 1.24%, max 6 shares
- TTE.PA [oil_gas] 77.44 EUR, age 15.0 min, entry cost 1.24%, max 3 shares

Lab limits: {"start_cash": 1000.0, "max_positions": 5, "max_pos_pct": 0.25, "min_conf": 0.0, "horizons": [1, 2, 3, 5, 10, 20], "max_new_buys_day": 5, "stop_pct": -8.0, "daily_loss_pct": -3.0, "weekly_loss_pct": -6.0, "max_fee_pct": 1.5, "cutoff_min": 30, "open_delay_min": 15}