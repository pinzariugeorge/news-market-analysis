# Fixed universe v1 (frozen 2026-11-06)

Six families, four single stocks each, chosen by a rule fixed before any out-of-sample test. No indexes and no ETFs. Research list, not a recommendation. Data and ranks: `universe/fixed_universe.csv` (built with the Yahoo daily bars).

## Selection rule
1. Candidates per family: I listed the large listed companies in that industry (8-10 each). The candidate lists were written from industry membership and general knowledge, not by looking at returns, but they reflect what I know about these companies today.
2. Eligible: at least five years of daily history (1,200 bars) and 30-day average dollar volume of at least 50 million USD.
3. Selected: the top four eligible names by 30-day average dollar volume. Past performance is never used.
4. Frozen: names change only by a logged decision with the date and reason, never after seeing test results.

## The names

| Family | Selected (by liquidity) | Not selected |
|---|---|---|
| Oil and gas producers | Exxon Mobil (XOM), Chevron (CVX), ConocoPhillips (COP), Occidental (OXY) | Devon, EOG, Diamondback, APA |
| Gold miners | Newmont (NEM), Agnico Eagle (AEM), Wheaton Precious Metals (WPM), AngloGold Ashanti (AU) | Kinross, Franco-Nevada, Harmony, Barrick (too thin: 21M a day under this data) |
| Chips | Micron (MU), Nvidia (NVDA), AMD (AMD), Intel (INTC) | Broadcom, TSMC, Applied Materials, ASML, Qualcomm; Arm excluded (under five years of data) |
| Pharma | Eli Lilly (LLY), Johnson & Johnson (JNJ), AbbVie (ABBV), Merck (MRK) | Amgen, Pfizer, Bristol Myers, AstraZeneca, Novo Nordisk, Novartis |
| Copper and uranium | Freeport-McMoRan (FCX), Cameco (CCJ), Southern Copper (SCCO), Teck (TECK) | Uranium Energy, NexGen (under 50M a day and under five years) |
| Solar | First Solar (FSLR), Enphase (ENPH), SolarEdge (SEDG), Sunrun (RUN) | Nextracker (under five years), Shoals, Array, Canadian Solar (all under 50M a day) |

Average dollar volume of the selected names (30 days): XOM 2.2B, CVX 1.7B, COP 0.9B, OXY 0.5B; NEM 0.7B, AEM 0.35B, WPM 0.25B, AU 0.21B; MU 26.6B, NVDA 24.4B, AMD 12.9B, INTC 11.0B; LLY 3.4B, JNJ 2.0B, ABBV 1.5B, MRK 1.4B; FCX 0.8B, CCJ 0.3B, SCCO 0.23B, TECK 0.18B; FSLR 0.47B, ENPH 0.21B, SEDG 0.09B, RUN 0.08B.

## Things to know
- The rule puts Intel in the chips family (liquid, but not an AI leader) and leaves out TSMC and Broadcom, which rank 5th and 6th by volume. If you prefer a different rule, for example market value or a thematic filter, say so now; changing it later, after seeing results, would defeat the point.
- Tradability for a Romanian retail client at Interactive Brokers Ireland is not verified for any of these (several are ADRs or foreign-listed shares: AU, WPM, TECK, AEM).
- Solar is in because you asked to keep the families, but it lost at every holding period in the earlier test.
- Volatility per name (daily, 1 year) ranges from 1.1% (J&J) to 5.7% (Sunrun), so position sizes should depend on the name's volatility.

## Test design that goes with it
- Holding period: 5, 10 and 20 trading days (maximum 20, user decision 2026-11-06), plus holds around scheduled events.
- Time split: choose and tune on data up to 2022, validate 2023-2024, final test 2025 to now.
- Costs: 0.24% per round trip for a small US order, plus higher scenarios for other fee structures.
- Baselines: buy and hold each name, equal-weight family basket, trend rule, volatility rule, random with equal exposure.
