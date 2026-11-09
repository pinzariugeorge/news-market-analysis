# Plan EU (2026-11-09): European markets, local paper broker, live delayed prices

Research and simulation only. No real money, no financial advice. Replaces `archive/docs_us/PLAN.md` (US stocks through Interactive Brokers Ireland).

## Decisions (user, 2026-11-09)
1. Europe only. No S&P 500, no US stocks. The S&P work was the learning phase.
2. Same themes (oil and gas, gold, chips, pharma, copper), now on European listings, as single stocks. Commodity prices are drivers and news inputs. No crypto, no ETFs or ETCs.
3. We build our own paper broker on this machine instead of waiting for broker API keys. Agents see live (delayed) prices when they analyse, which also gives a forward record to train and test on.
4. Saxo Bank is the reference broker for tradability and costs (the real broker later, if paper results justify it).
5. A free price source is acceptable; spending money on data needs the user's approval.

6. **Account size 1,000 EUR (user, 2026-11-09).** Base currency EUR.
7. **No ETFs (user, 2026-11-09).** Read as: no ETFs, ETCs or other exchange-traded products; single stocks only. Commodity prices (Brent, WTI, gold, copper, gas) are used as data and news drivers, not traded. Consequence: the gold family has only two liquid European miners and uranium has none.

## What 1,000 EUR means
- Three positions means about 333 EUR each, whole shares only. Names priced above about 333 EUR cannot be bought: ASML (about 1,310), ASM International (660), Genmab (490), argenx (855), Lonza (733), Roche (443). The sizing check lives in `universe/EU_UNIVERSE.md`.
- Fees: Saxo reportedly charges 0.08% with a minimum of about 2 to 3 EUR per order, so a round trip on 333 EUR costs about 1.2% to 1.8% before spread and FX. Holds shorter than about 20 trading days barely cover that; the paper broker must model the minimum exactly.
- FX: only EUR names avoid conversion cost (reported up to 0.25% to 0.5% each way); GBp, CHF, DKK, NOK, SEK and PLN names pay it unless a foreign-currency balance is held. Custody of 0.12% to 0.25% a year is about 1 to 2.5 EUR a year at this size.

## Free price feed (tested 2026-11-09)
Yahoo Finance chart endpoint, no key: `src/live_feed.py` (5-minute bars, last quote 0 to about 20 minutes old on SHEL.L, 4GLD.DE, NOVO-B.CO, ASML.AS, SAP.DE, TTE.PA, EQNR.OL) and daily history back to 1988-2000 for the large names (`src/eu_probe.py`). It is unofficial: it can change or throttle, and its use is for personal research only. Alternatives checked: Twelve Data free plan (US, forex and crypto real time; European markets only on the Pro plan; 8 calls a minute), EODHD free (20 calls a day, US end-of-day), Financial Modeling Prep (European delayed data not on the free tier), Eulerpool (claims 90 exchanges free, quota figures conflict, untested). Stooq no longer serves the old CSV links. If Yahoo proves unreliable we pick a paid source and ask first. Saxo itself has no free European real-time data (a data subscription is needed; its free streaming covers forex and bonds).

## Saxo facts (checked 2026-11-09; most are third-party and must be confirmed on Saxo's page for the account country)
- Exchanges listed in Saxo's data pages: Euronext (Paris, Amsterdam, Brussels, Lisbon, Dublin), Deutsche Boerse Xetra, London, plus others. Instrument availability per client is shown only inside the account.
- Stock commission (Classic): reported 0.08% with a minimum of about 2 EUR on Euronext and 3 EUR on Xetra; London reported both as "no minimum since November 2025" and "3 GBP". Platinum and VIP are cheaper but need large balances. OPEN.
- Currency conversion: official Swiss page says at most 0.25%; third parties say up to 0.5% on Classic. OPEN.
- Custody fee on stocks and ETFs: 0.12% to 0.25% a year depending on page. OPEN.
- EU retail clients: orders in products without a PRIIPs KID are rejected (US ETFs always). ETCs may or may not have a KID. OPEN.
- Saxo has a free simulation environment in its OpenAPI (token valid one day, simulated cash); whether European stocks appear there is untested. We do not need it: our own broker simulates the fills.

## Paper broker design (`src/paper_broker/`, to build)
Purpose: a faithful, auditable simulation of trading through Saxo, runnable unattended on the schedule.
- **Ledger:** SQLite file (`data/paper/ledger.db`, git-ignored): cash by currency, positions, orders, fills, fees, daily equity. Every order is written before it is "sent" (idempotent order id), so a crash can be recovered without repeating a trade. A reconcile command recomputes cash and positions from the fills and fails loudly on a mismatch.
- **Fills:** market and limit orders. A market order sent at time T fills at the open of the first 5-minute bar after T, plus a spread and slippage allowance per instrument (from liquidity), at the quantity the agent asked for (whole shares). The fill is computed only after that bar has become available (the feed is delayed), so an agent never sees a price later than its decision time.
- **Costs:** Saxo commission model (`src/costs.py` to be rewritten from the verified schedule), currency conversion for non-EUR names, custody accrual, pence-to-pound conversion, stamp duty where it applies (UK 0.5% on purchases, French and Italian financial transaction taxes) as parameters.
- **Calendar:** exchange hours and holidays per venue (Xetra and Euronext 09:00-17:30 CET, London 08:00-16:30 UK time, Oslo, Copenhagen, Stockholm, Zurich near 09:00-17:30; orders outside hours wait for the next open).
- **Risk limits** (numbers to set before the first paper day): maximum share of equity per position, maximum open positions (3), daily loss cap, no leverage, no shorts, no options, "no trade" always allowed.
- **Trade log:** every order records the agent's catalyst quote, confidence, horizon and the headline it relied on, so results can be audited and learned from (`src/learn_prep.py` already reads closed trades).
- **Corporate actions:** use adjusted history for backtests; in paper mode apply dividends and splits from the feed's events field (to verify).

## Daily cycle (CET; times to be tuned)
08:15 collect news and snapshot quotes (`live_feed.snapshot`) -> 08:30 agent run (reads handoff and outcome block, news, delayed quotes) -> 09:15 broker fills at the next bars -> 12:30 and 17:00 optional re-check runs -> 17:45 mark to market and write the daily report. Overlap lock and stale-note rules come from `src/handoff.py`.

## Phases and gates
0. Cleanup and re-plan (2026-11-09, done): US era archived, European universe probed, plan written.
1. European data and universe: daily files for all candidates (done in `data/raw/eu/daily/`), point-in-time liquidity rule ported, Saxo tradability check, a European news source (Google News RSS per company and per commodity first; Finnhub and Massive do not cover European names; a European forward feed to collect).
2. Build the paper broker with self-tests (fills, fees, FX, hours, reconcile, crash recovery); replay a past week of Yahoo bars through it to check the numbers by hand.
3. Rule baselines on the European universe with the Saxo cost model (cash, equal-weight basket, trend-filtered basket, random calls), pre-registered, data cut so that the most recent months stay unseen.
4. Forward paper trading: at least 60 trading days and at least 30 trades, the news agent against random calls with the same number of longs, the equal-weight basket and cash; bar written down before day 1. Both the Sonnet and Opus agents, with and without the lessons ledger, as separate accounts.
5. Live trading only if paper results justify it, with the user's explicit go-ahead and a small size.

## Lessons that apply (see `results/US_LESSONS.md`)
No rule or agent setup showed an edge in the US backtests; the only fallback is a trend-filtered diversified basket. So the paper test must be pre-registered and judged against random calls, not only against buy and hold, and profits from a single episode do not count.

## Near-live prices: options and advice (researched 2026-11-09; prices are list prices to confirm)
For an agent that decides once or twice a day and holds 5 to 20 days, a 15-minute delay changes nothing; true real time only matters for intraday trading, which the fee drag at 1,000 EUR rules out anyway. So start free and pay only if the free feed breaks.
| Option | Delay | Cost | Verdict |
|---|---|---|---|
| Yahoo chart endpoint (`src/live_feed.py`) | 0 to about 20 min | free | Use now. Unofficial, can throttle or change; personal use only. Keep a daily snapshot so gaps are visible |
| Saxo market data (after account opening) | real time (level 1) | about 7 EUR a month per exchange on the fee tables found (Euronext, London 7 GBP, Xetra products 1 to 7 EUR); fee refunded when you trade at least 4 times in that exchange in a month; Saxo's free streaming covers forex and bonds only | Best later, because it is the same venue and prices as the real account; confirm the current table for your account |
| EODHD | 15 to 20 min delayed live API; real-time websocket on higher plans | about 20 to 100 USD a month on the plans listed (European real-time add-on price not published) | Cheap fallback with a documented API and one key |
| Twelve Data | European real time only on Pro; sourced from Cboe Europe (Cboe UK and NL), not directly from Xetra or Euronext | about 229 USD a month Pro (list, monthly billing) | Too expensive for this size |
| Finnhub, Alpha Vantage, Polygon/Massive (keys already in `.env`) | US data only on the free tiers | free | Not useful for European prices |
| Exchange sites (Euronext, Xetra, LSE delayed pages) | 15 min | free | Scraping is fragile and against terms; skip |
Recommendation: keep Yahoo as the feed, log a snapshot every run (`live_feed.snapshot`), cross-check against Saxo's platform prices by eye once the account exists, and buy Saxo level 1 for only the exchanges actually traded if real time is ever needed. Spending needs your approval.

## Dashboard
`python -I src\dashboard_server.py` serves http://127.0.0.1:8765 : account summary (equity, cash, market value, total P&L), watchlist with delayed prices and trends, price chart with your paper fills marked, and tabs for positions, orders, trades with the catalyst the agent quoted, equity curve and agent notes. It reads `data/paper/ledger.json` (the paper broker's output, JSON v0 described in the script's docstring) and falls back to a clearly marked DEMO ledger (`data/paper/ledger_demo.json`, built from real closes, not a result). It refreshes every 30 seconds and converts pence and other currencies to EUR.
