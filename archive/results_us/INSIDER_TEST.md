# Insider buying test (SEC Forms 4), 2014-2024 (2026-11-07)

Data: SEC insider-transactions bulk files 2014q1-2024q4 (`src/download_insider.py`, contact email read from `.env` variable `personal_email`, never printed), filtered to open-market purchases (code P) for our tickers; 168 tickers had officer or director purchases (3,540 rows after dropping ten-percent-owner-only buys). Prices: `data/raw/ohlc_long`. Script `src/run_insider_test.py`; rules fixed in advance (see its docstring): event A = first officer/director purchase of at least 50,000 USD after 90 days without one (891 events); event B = cluster of at least 2 distinct insiders within 21 days totalling at least 100,000 USD (219 events). Entry at the close of the second trading day on or after the filing date, exit 20 or 60 trading days later, 0.15% per side; abnormal = stock return minus the equal-weight average of all universe names over the same dates; t-statistics use months as units (events overlap). Build 2014-2020, validation 2021-2024; 2025+ untouched.

| Event | Hold | Period | Events | Mean abnormal return | t | Hit rate | Mean raw return |
|---|---|---|---|---|---|---|---|
| A | 20d | build | 617 | -0.70% | -2.55 | 44% | +0.80% |
| A | 20d | valid | 264 | -0.14% | 0.08 | 46% | +1.36% |
| B | 20d | build | 155 | +0.06% | 0.07 | 45% | +3.07% |
| B | 20d | valid | 63 | +0.60% | 0.97 | 54% | +3.10% |
| A | 60d | build | 617 | -0.83% | -1.36 | 44% | +4.27% |
| A | 60d | valid | 258 | +0.29% | 0.77 | 51% | +3.99% |
| B | 60d | build | 155 | -0.50% | -0.55 | 46% | +7.52% |
| B | 60d | valid | 62 | +0.60% | 0.71 | 53% | +4.09% |

Pre-registered pass rule (mean abnormal 20-day return >= +1.0% with t >= 2.5 in build, same sign and half the size in validation): **fails**. Raw returns after insider buys are positive only because these large caps rose; against the equal-weight basket the effect is zero or slightly negative.

Reading: the documented insider-buying anomaly is concentrated in small and mid caps and in clusters of opportunistic buying; among liquid large caps, after realistic lag and costs, we see nothing. Caveats: survivor-biased large-cap universe, no filter for 10b5-1 or routine buyers, no purchase-size scaling by market value.
