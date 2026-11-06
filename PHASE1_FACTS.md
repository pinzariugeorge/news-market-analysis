# Phase 1 facts: Interactive Brokers Ireland, costs, access, tax (checked 2026-11-06)

Status of each fact: VERIFIED = read on the official page or document; REPORTED = from a secondary source; OPEN = not found. Not legal, tax or investment advice: confirm tax with an accountant and fees with IBKR before trading.

## Fees, US stocks (VERIFIED on the official IBKR Ireland commissions page)
- Tiered (up to 300,000 shares a month): USD 0.0035 per share, minimum USD 0.35 per order, maximum 1% of trade value (a footnote elsewhere on the page says 0.5% for some cases).
- Fixed: USD 0.005 per share, minimum USD 1.00 per order, maximum 1% of trade value.
- Tiered excludes third-party fees (exchange, clearing, regulatory pass-through); the amounts are on collapsed sections of the page that I could not read: OPEN. Fixed includes most of them.
- No account minimum, ticket charge or platform fee. Fractional shares carry the same rates (minimum USD 0.01). A FINRA activity-fee holiday runs 2026-10-01 to 2026-12-31.
- Directed API orders cannot use the Tiered structure; SmartRouted API orders can use either. Modified orders count as cancel-and-replace and can pay the minimum again.
- One user report (secondary): the API rejects fractional stock orders, so assume whole shares for automated trading.

## Other fees (REPORTED or OPEN)
- EU-listed stocks: official snippet says 3 EUR per trade for typical sizes on Western European stocks, 0.05% above about 6,000 EUR (VERIFIED earlier from IBKR's Ireland page); tiered and fixed minimums and caps per exchange from third-party reviews only.
- Currency conversion: IBKR's page says 0.002% with a 2 USD minimum; other sources say 0.03% to 0.20% (conflict, OPEN). The 2 USD minimum alone is 0.4% of a 500 USD conversion, so hold USD cash and convert rarely.
- Withdrawals: first per month free then about 1 USD (SEPA) per a third-party review (REPORTED); deposits by SEPA free (REPORTED).
- Lite plan is not available to EU residents per a third-party review (REPORTED, conflicting).
- FX and cash interest ("up to 3.38% on cash" banner) not verified for Romania.

## Access and onboarding
- European residents are routed to IBKR Ireland during signup; approval is typically 1 to 3 business days after documents (REPORTED). Documents: photo ID and proof of address (REPORTED). Funding deadline: 45 days after approval on the institutional pages (retail unverified).
- Paper trading account, API (TWS, IB Gateway, web API), and permission for US stocks for Romanian retail clients: OPEN. Ask IBKR or check Settings, Trading Permissions after approval. The API docs and a paper account need to be checked in the application flow.
- Official pages block automated fetching (HTTP 403); the commissions page was readable in the built-in browser, but its collapsible fee detail was not.

## Romanian tax (REPORTED from Romanian press and Big Four notes; confirm with an accountant)
- Gains from securities held at a foreign broker: 16% on the net annual gain (raised from 10% in 2025/2026), self-reported in the Declaratia Unica by 25 May of the following year; losses offset gains the same year and a net loss can be carried forward up to 5 years against up to 70% of gains.
- A Romanian broker would withhold 3% (held over a year) or 6% (under a year) instead; this does not apply to IBKR Ireland.
- Dividends: 16% from 2026 (REPORTED). US dividend withholding for Romanian residents and the W-8BEN form: OPEN.
- CASS health contribution on investment income: thresholds conflict between sources (OPEN).

## What this means for the model (`src/costs.py`)
- Round-trip cost on US stocks (tiered, whole shares, assumed 2 bp half spread, 0.001 USD per share third-party fee): about 0.6% on a 125 USD order, 0.3% on 250 USD, 0.18% on 500 USD, 0.10% on 1,250 USD, 0.07% on 2,500 USD, 0.06% on 5,000 USD. The 0.35 USD minimum per order dominates small orders.
- Converting EUR to USD and back adds about 0.8% on a 500 USD trade (2 USD minimum each time): hold USD cash.
- 16% tax on net gains is applied after costs: 5% gross keeps about 4.2% before costs.
- Consequence for account size: with 500 EUR spread over several names, each order is about 100 USD and costs about 0.6% round trip, so concentrate in one or two positions; with 5,000 EUR and four to five names (about 1,000 USD each) costs are about 0.1% round trip.

## Outcome ranges for a 500 USD account (historical simulation, not a forecast; 2026-11-06)
Two names from different families of the rule-selected universe, equal weight, held 21 or 42 trading days, net of 0.30% round-trip costs, before tax, 10 years of data (2016-11 to 2026-11), all pairs and start dates pooled. Today's names, so survivor and bull-market bias; no timing rule, no stop loss.

| Holding | Mean | Median | 25th to 75th percentile | 5th percentile | 95th percentile | Chance of a loss | Chance of losing over 10% |
|---|---|---|---|---|---|---|---|
| 1 month | +2.0% | +1.5% | -3.3% to +6.8% | -11.3% | +16.9% | 42% | 6.6% |
| 2 months | +4.1% | +3.1% | -4.1% to +10.9% | -14.5% | +26.5% | 39% | 10.8% |

In dollars on 500 USD: 1 month median +8, typical range -16 to +34, bad month (5th percentile) -56, good month (95th) +85; 2 months median +15, typical -21 to +55, bad -72, good +132. Since 2024 the numbers are higher (1 month median +2.2%, 2 months +4.7%), which reflects the recent bull run. After 16% tax on gains the mean falls to about +1.3% (1 month) and +3.0% (2 months). The agent has shown no edge yet, so these are buy-and-hold ranges, not a promised result.
