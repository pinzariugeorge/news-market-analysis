# Free consensus and guidance data (checked 2026-11-07)

Goal: know, for each earnings release, what analysts expected and what the company said about the future, so an agent could forecast surprises instead of guessing. Not financial advice.

## Consensus estimates and surprises
| Source | What it gives | Free? | Status |
|---|---|---|---|
| **Alpha Vantage `EARNINGS`** | Per quarter: report date, report time (pre-market or post-market), reported EPS, estimated EPS (consensus), surprise and surprise percent. Tested with the public demo key on IBM: 123 quarters from 1996 to 2026 | Free key (instant, by email); free tier about 25 requests a day (to confirm on their page) | Best option: deep history. Needs you to create the key. `src/download_consensus.py` is ready; 20 names fit in one day |
| Nasdaq public earnings-surprise endpoint | Last 4 quarters with consensus and surprise | Keyless, unofficial | Works (tested for Nvidia); too shallow for backtests, useful for a live check |
| Finnhub free tier | Earnings calendar about 1 month ahead, last 4 quarters of EPS surprises, company news for 1 year; 60 calls a minute per its pricing page | Free key | Shallow history; good for live |
| Financial Modeling Prep, API Ninjas | Earnings and surprise history | Free keys, limits unconfirmed; API Ninjas puts consensus and surprise in premium tiers | Not used |
| Yahoo `quoteSummary` earnings history | Last 4 quarters | Needs a session crumb (401 without it); unofficial | Not used |

## Guidance (what the company says about the future)
- No free structured source found. Financial Datasets lists forward guidance extracted from earnings releases for 600+ US tickers with 3+ years of history, Benzinga lists EPS and revenue guidance back to 2011, and LSEG has guidance back to 1994: all appear to be paid; prices unconfirmed.
- Free route: guidance sits in the earnings press release (8-K Exhibit 99.1, free on SEC EDGAR, which we already use for dates). Extracting it needs reading each release (model time and tokens); it could be tried on a sample, for example the last 8 quarters of 15 names, to see if guidance raises and cuts carry information.

## What to do
1. You create a free Alpha Vantage key and add `ALPHAVANTAGE_API_KEY=...` to `.env` (never in chat). Then `python -I src/download_consensus.py` fetches 20 names (rerun the next day if the limit hits) and `python -I src/run_surprise_test.py` runs the tests.
2. The tests (code already checked on the IBM demo data, which only has 32 usable events): reaction by surprise size, drift after surprises, whether beats persist quarter to quarter, and whether holding through earnings pays after a beat or miss in the previous quarter.
3. Guidance is optional and costs tokens; decide after step 2.
