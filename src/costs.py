"""Trading cost model for Interactive Brokers Ireland, US single stocks (Phase 1). Import it in every backtest.

Usage as a script: python -I src/costs.py        # prints round-trip cost tables for small orders
Usage as a module: from costs import round_trip_pct, one_way_cost

VERIFIED on the official IBKR Ireland commissions page (read 2026-11-06, interactivebrokers.ie/en/pricing/commissions-stocks.php):
  US stocks, Tiered, up to 300,000 shares a month: USD 0.0035 per share, minimum USD 0.35 per order, maximum 1% of trade value.
  US stocks, Fixed: USD 0.005 per share, minimum USD 1.00 per order, maximum 1% of trade value.
  Fractional shares: same rates, minimum USD 0.01. Directed API orders cannot use Tiered; SmartRouted API orders can use Tiered or Fixed.
  Tiered excludes third-party fees (exchange, clearing, regulatory pass-through). No account minimum, ticket charge or platform fee.
  FINRA Trading Activity Fee holiday for trades from 2026-10-01 to 2026-12-31.
ASSUMPTIONS (not verified, kept as parameters): third-party fees per share, SEC/regulatory fee on sells, half-spread per side,
  currency conversion cost, EUR/USD rate, tax rate. Change them here, never inside a backtest.
"""
from dataclasses import dataclass


@dataclass
class CostParams:
    plan: str = "tiered"                  # "tiered" or "fixed" (SmartRouted API orders can use either)
    tiered_per_share: float = 0.0035      # USD, verified
    tiered_min: float = 0.35              # USD per order, verified
    fixed_per_share: float = 0.005        # USD, verified
    fixed_min: float = 1.00               # USD per order, verified
    max_pct_of_value: float = 0.01        # 1% of trade value, verified (a footnote on the page says 0.5% for some cases)
    third_party_per_share: float = 0.0010  # USD per share exchange + clearing pass-through: ASSUMPTION (tiered only)
    sell_regulatory_pct: float = 0.00003  # fraction of sale value (SEC fee and similar): ASSUMPTION
    half_spread_pct: float = 0.0002       # per side, 2 basis points for large caps: ASSUMPTION; use 0.0005 for thin names
    fx_fee_pct: float = 0.00002           # 0.002% of the converted amount: from an IBKR page, sources conflict up to 0.2%
    fx_fee_min_usd: float = 2.00          # per conversion: same caveat
    fx_conversions_per_round_trip: float = 0.0   # 0 if USD cash is already held; 2 if converting EUR to USD and back
    allow_fractional: bool = False        # False for API trading: whole shares only
    gains_tax_rate: float = 0.16         # Romania, foreign broker, annual net gain, self-declared: from Romanian press, verify


def commission(shares, price, p: CostParams, fractional=False):
    value = shares * price
    if p.plan == "tiered":
        c = max(shares * p.tiered_per_share, p.tiered_min if not fractional else 0.01)
    else:
        c = max(shares * p.fixed_per_share, p.fixed_min if not fractional else 0.01)
    return min(c, p.max_pct_of_value * value)


def one_way_cost(trade_value, price, p: CostParams = None, sell=False):
    """USD cost of one order (buy or sell) for trade_value dollars at share price `price`. Fractional shares allowed."""
    p = p or CostParams()
    shares = trade_value / price
    if not p.allow_fractional:
        shares = int(shares)                   # API orders: whole shares only (users report fractional orders are rejected)
        if shares < 1:
            raise ValueError("order value below one share price")
        trade_value = shares * price
    fractional = abs(shares - round(shares)) > 1e-9
    c = commission(shares, price, p, fractional)
    if p.plan == "tiered":
        c += shares * p.third_party_per_share
    if sell:
        c += trade_value * p.sell_regulatory_pct
    c += trade_value * p.half_spread_pct
    return c


def round_trip_pct(trade_value, price, p: CostParams = None):
    """Total cost of buying and selling, as a percent of trade_value (USD), including FX conversions if any."""
    p = p or CostParams()
    usd = one_way_cost(trade_value, price, p, sell=False) + one_way_cost(trade_value, price, p, sell=True)
    usd += p.fx_conversions_per_round_trip * max(p.fx_fee_min_usd, p.fx_fee_pct * trade_value)
    return usd / trade_value * 100


if __name__ == "__main__":
    print("round-trip cost as % of order value, IBKR Ireland US stocks (assumptions as in the module docstring)")
    print("{:>9s} {:>8s} | {:>10s} {:>10s} | {:>14s}".format("order $", "price $", "tiered %", "fixed %", "tiered+2 FX %"))
    for value in (125, 250, 500, 1250, 2500, 5000):
        for price in (25, 100, 500):
            if value < price:
                continue                       # cannot buy one whole share
            t = round_trip_pct(value, price, CostParams(plan="tiered"))
            f = round_trip_pct(value, price, CostParams(plan="fixed"))
            fx = round_trip_pct(value, price, CostParams(plan="tiered", fx_conversions_per_round_trip=2))
            print("{:9d} {:8d} | {:10.2f} {:10.2f} | {:14.2f}".format(value, price, t, f, fx))
    print("\nThin-name scenario (5 bp half spread), 500 USD order at 100 USD:",
          round(round_trip_pct(500, 100, CostParams(half_spread_pct=0.0005)), 2), "%")
    print("Net of 16% tax on gains: a 5% gross gain on 500 USD keeps {:.1f}% after tax, before costs".format(5 * (1 - CostParams().gains_tax_rate)))
