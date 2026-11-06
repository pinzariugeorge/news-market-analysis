# Free commodity and driver prices (checked 2026-11-06)

Downloaded by `python -I src/download_commodities.py` into `data/raw/commodities/` (git-ignored; rerun to rebuild). All free, daily, from Yahoo Finance's public chart endpoint (unofficial, no key; terms can change; prices are delayed about 15-20 minutes during the day, fine for daily decisions). Research only.

## What we have (daily, from 2000 unless noted)
| Family | Series | Symbol | From | Notes |
|---|---|---|---|---|
| Oil and gas | WTI crude futures | CL=F | 2000-08 | Front-month continuous; contains the 2020-04 negative-price day (removed in `build_family_stats.py`) |
| Oil and gas | Brent crude futures | BZ=F | 2007-07 | |
| Oil and gas | Natural gas futures (Henry Hub) | NG=F | 2000-08 | Very volatile |
| Gold miners | Gold futures | GC=F | 2000-08 | |
| Gold miners | Silver, platinum futures | SI=F, PL=F | 2000 | Related metals |
| Gold miners | US 10-year yield, dollar index, TIPS ETF | ^TNX, DX-Y.NYB, TIP | 2000 / 2003 | Rate and dollar drivers; TIP is a real-rate proxy |
| Copper and uranium | Copper futures | HG=F | 2000-08 | |
| Copper and uranium | Uranium proxy | U-UN.TO (Sprott Physical Uranium Trust, CAD), URA (ETF) | 2006 / 2010 | No free daily uranium spot or usable futures: the UX=F symbol has a single bar. The trust holds physical uranium and can trade at a premium or discount to its value |
| Chips | Semiconductor sector ETF | SMH | 2000-06 | Driver proxy; no free daily memory (DRAM) price series |
| Pharma | Health care sector ETF | XLV | 2000 | Driver proxy |
| Market regime | VIX | ^VIX | 2000 | Volatility regime |

## What did not work from this machine
- FRED (St. Louis Fed) CSV downloads: every request timed out or was cut off today; they would give daily WTI, Brent, Henry Hub spot, monthly copper and uranium (IMF), real yields and the dollar index for free, so retry later or through a browser.
- Stooq: blocks scripted downloads (bot check page).
- EIA open data (weekly inventories, spot prices): free but needs a registered API key (403 without it). Useful later for the scheduled oil and gas storage reports.
- Not tested: LBMA gold fixing, Nasdaq Data Link, exchange sites (CME and LME data are paid or delayed).

## Caveats
- Continuous futures are stitched front-month contracts: roll days can show jumps that are not real price moves; use returns with care and clean obvious outliers.
- Daily spot prices for uranium (UxC, Cameco) are weekly or monthly and paid or manual; the trust or ETF is the practical free proxy.
- Yahoo is not an official data feed; for live trading, quotes would come from the broker's API.
