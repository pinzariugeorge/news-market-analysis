# European universe v0 (probed 2026-11-09)

Research list, not a recommendation. The five theme families of the old plan, moved to European listings, plus European-listed commodity ETCs. Numbers come from `src/eu_probe.py` (Yahoo daily bars, true daily history; liquidity = median traded value over the last 250 days in millions of EUR at today's FX; volatility = annualised 250-day standard deviation). Full table: `universe/eu_candidates.csv`.

## What is verified and what is not
- **Verified (2026-11-09):** a free daily and 5-minute history exists on Yahoo for the symbols below, with history from 1988-2018 depending on the name (`first_date` in the CSV); live quotes are 0 to about 20 minutes delayed (`src/live_feed.py`).
- **Not verified:** that each name or ETC can be bought by a Romanian retail client at Saxo. Saxo's market-data pages list Euronext, Xetra, London, Euronext Dublin and others, and a Saxo partner page maps exchange codes for Paris, Brussels, Lisbon and Xetra ETFs; a third-party review says ETFs are listed on 30 exchanges. Which names, and which ETCs, show up for this account can only be checked in the Saxo instrument search after account opening (or through the OpenAPI reference-data endpoint of a simulation account). Saxo checks that a PRIIPs KID exists before an EU retail order goes through, which can block some ETCs.
- Yahoo volume can under-report on some venues (Roche shows only 9 million EUR a day, far below its real turnover); treat the liquidity column as a lower bound.

## Candidates per family (liquidity in million EUR a day, 250-day volatility in %)
| Family | Liquid names (first choice) | Thin or problematic |
|---|---|---|
| oil_gas | Shell SHEL.L (342, 24), TotalEnergies TTE.PA (271, 24), BP BP.L (237, 32), Eni ENI.MI (193, 29), Equinor EQNR.OL (95, 39), Repsol REP.MC (77, 35) | Galp (34), Aker BP (33), OMV (18) |
| gold_miners | Fresnillo FRES.L (33, 55), Endeavour Mining EDV.L (35, 49) | Hochschild (11), Pan African (9); Centamin has no data (taken over). Europe has almost no liquid gold miners: use a gold ETC for gold |
| chips | ASML ASML.AS (815, 44), Infineon IFX.DE (211, 55), ASM International ASM.AS (119, 51), STMicroelectronics STMPA.PA (99, 56), BE Semiconductor BESI.AS (89, 57) | Aixtron (25), Soitec (30, vol 107), Nordic Semiconductor (12), Siltronic (6) |
| pharma | AstraZeneca AZN.L (363, 27), Novartis NOVN.SW (356, 23), Novo Nordisk NOVO-B.CO (193, 46), Sanofi SAN.PA (161, 24), GSK GSK.L (160, 25), Bayer BAYN.DE (104, 43), Roche RO.SW (volume under-reported) | Genmab (31), argenx (60), Lonza (82) |
| copper_uranium | Glencore GLEN.L (218, 32), Rio Tinto RIO.L (205, 29), Antofagasta ANTO.L (46, 53), Boliden BOL.ST (53, 46), KGHM KGH.WA (55, 55) | No uranium producer with usable history: Kazatomprom's London listing starts 2026-07 on Yahoo and trades 3.5 million a day. Uranium is dropped unless an ETC is found |
| commodity ETCs | NOT TRADED (user: no ETFs, read as no ETCs either). Probed for reference only: Xetra-Gold 4GLD.DE (21), Gold ETC SGLD.L (15), Brent ETC BRNT.L (9), WTI ETC CRUD.L (7.5) | Their price series can still serve as European-listed commodity drivers |

Notes: `.L` prices are in pence (GBp), so convert before computing value.

## Fit for a 1,000 EUR account (3 positions of about 333 EUR, whole shares; prices of 2026-11-09 in EUR)
Cannot be bought (price above about 333 EUR): ASML 1,310, ASM International 660, Genmab 489, argenx 855, Lonza 733, Roche 443. Everything else in the first-choice columns fits, for example Shell 44, TotalEnergies 79, BP 6.7, Eni 25, Equinor 37, Fresnillo 31, Endeavour 51, Infineon 47, STMicro 38, BESI 145, AstraZeneca 170, Novartis 147, Novo 37, Sanofi 86, GSK 23, Bayer 56, Glencore 6, Rio Tinto 77, Antofagasta 39, Boliden 47. With the chips leader ASML out, chips falls to Infineon, STMicro, BESI. Gold has only Fresnillo and Endeavour; copper_uranium is copper and diversified miners only.

## Differences from the US universe
- Fewer pure-play names: gold miners are down to two and uranium is missing; ETCs are not allowed (user decision 2026-11-09), so those themes stay thin.
- Five currencies (EUR, GBp, CHF, DKK, NOK, SEK, PLN): the paper broker holds EUR cash and converts at the FX rate with the Saxo conversion cost.
- Exchange hours differ (see `PLAN_EU.md`), so one decision time cannot be "before the US open".

## Next
Apply the point-in-time rule of `universe/UNIVERSE_RULE.md` to these candidates (needs `src/select_universe.py` ported to the European daily files in `data/raw/eu/daily/`), then verify the chosen names in the Saxo instrument search.
