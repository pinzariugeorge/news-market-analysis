# European market screen (2026-11-09)

Research list, not a recommendation. Output of `src/eu_screen.py`: about 355 European large and mid caps across all sectors (DE, FR, NL/BE, UK, IT/ES/PT, Nordics, Switzerland, Austria, Poland), full table in `universe/eu_screen.csv`. The ticker list was written from general knowledge, so some large names are missing.

## Filters (fixed before looking at results)
Price at most 333 EUR (3 positions on 1,000 EUR, whole shares); median traded value over 250 days at least 20 million EUR (Yahoo volume can under-report, so this is a lower bound); at least about 4 years of daily history. 340 of 355 symbols returned data (15 stale or wrong symbols: 1COV, URW, TKWY, FLTR, AHT, BDEV, CRH, PHNX, SDR, SMDS, CNHI, NZYM-B, TRYG-B, ROG.SW, VAT). 21 names are above 333 EUR (for example Rheinmetall 818, Adyen 903, Safran 302 is just under) and 75 more fail liquidity. **244 names pass**: DE 40, FR 36, NL/BE 17, UK 53, IT/ES/PT 33, Nordics/CH/AT 65.

## What the market looks like today
- It has done well: median 12-month return of the 244 names is +11.9%, 158 of 244 (65%) trade above their 200-day average, median volatility 29%.
- The last three months were weak for many (defence, banks, chips, industrials below their 200-day line), so a recent-trend view and a 12-month view disagree.

## Where the 12-month moves are (hindsight, not a signal)
- **Energy and materials:** Repsol +74%, Equinor +58%, Eni +51%, Neste +57%, Saipem +84%, ArcelorMittal +64%. This fits the oil story that drove the US-era agent trades.
- **Pharma:** Bayer +91% (above its 200-day line), Novartis +32%; AstraZeneca +5%.
- **Chips:** STMicroelectronics +89% but -20% in 3 months, Soitec +156% then -40% in a month (volatility 107%), Aixtron +59% but -41% in 6 months: big and violent.
- **Banks:** UniCredit +20% (above 200-day), HSBC +21%, BNP +36% but -16% in 3 months.
- **Wind and power equipment:** Vestas +38%, Nordex +53%, Orsted +31%.
- **Losers:** Stellantis -56%, Alstom -54%, Kering -41%, EssilorLuxottica -39%, Vonovia -34%, Adyen -36%, Rheinmetall -53% (also unaffordable).

## Most liquid names that fit the account
SAP 382 million EUR a day, AstraZeneca 363, Novartis 356, Rolls-Royce 348, UniCredit 343, Shell 342, HSBC 321, Siemens Energy 311, Intesa 279, Nestle 277. These are the safest to trade with small orders (tight spreads); volatility is 21% to 52% a year.

## How to use this
1. It widens the candidate pool beyond the five theme families (banks, power equipment, defence, materials are all liquid and affordable). Whether to open extra themes is a user decision; the news agent's themes stay oil and gas, gold, chips, pharma, copper until then.
2. Do not pick names by their past return: the US era showed that choosing winners in the same data used to judge them is overfit. Feed the 244 names into the point-in-time liquidity rule (`universe/UNIVERSE_RULE.md`, to port) and re-run the screen quarterly.
3. Verify each chosen name in the Saxo instrument search before trusting it (not yet possible).
