# Earnings surprise tests with analyst consensus (2026-11-07)

Data: Alpha Vantage EARNINGS (free key; `src/download_consensus.py`, files in `data/raw/consensus/`, git-ignored): consensus estimate, actual, surprise and report time per quarter for 20 names (XOM, CVX, COP, OXY, EOG, NEM, NVDA, MU, AMD, INTC, AVGO, QCOM, AMAT, LLY, JNJ, ABBV, MRK, PFE, FCX, SCCO), history from 1996 where available. Test: `src/run_surprise_test.py` (`results/surprise_test.csv`), 639 earnings events from 2010 to 2024-12-31; build = up to 2022, validation = 2023-2024; the final test period (2025 onward) is untouched. Costs 0.3% round trip; excess = minus the stock's unconditional mean for the same period. Surprise buckets: miss below -2%, in line -2% to +2%, beat +2% to +10%, big beat above +10%.

## Results
**A. The market reacts to the surprise, immediately and consistently.** Reaction-day move: miss -2.4% (build) and -2.9% (validation); in line -0.6% and -1.6%; beat +0.4% and +1.0%; big beat +0.9% and +2.0%. Share of reactions that were up: 26-30% after a miss, 56-57% after a beat.

**B. No drift after the reaction.** Excess return over 5, 10 and 20 days after each bucket is within about +/-1.5 points and the signs flip between periods (for example beat at 20 days: -1.73, t = -2.4 in build, then -0.19 in validation; miss at 5 days: -0.04 then +1.25). One cell beyond |t| = 2 out of 18, not repeated.

**C. Beating is the norm and only weakly persistent.** Companies beat consensus 65% of the time (72% in validation). After a beat the next quarter is a beat 71% (build) and 76% (validation) of the time; after a miss 58% and 72%. The gap is small and shrank in validation.

**D. Holding through earnings does not pay.** Buying before the release and selling at the reaction-day close: -0.40% on average net of cost in build (t = -1.68) and +0.06% in validation, whatever the previous quarter's surprise. The only large cell (after a previous miss in validation: +2.52%, t = 2.41, n = 25) has the opposite sign in build (-0.82%).

## Reading
- The surprise explains the reaction, but the surprise itself is not predictable from the history of past surprises: beats are common, persistence is weak, and the market has already priced the expected beat.
- With consensus-history data alone there is still no tradable earnings edge, before or after the release. An edge would need information that predicts the surprise before the release (analyst estimate revisions, guidance, industry data), none of which we have as history.
- Same caveats: today's liquid names (survivor bias), US filers with Alpha Vantage coverage, free-tier data quality unchecked against another source.

## Next possibilities
- `EARNINGS_ESTIMATES` (Alpha Vantage, in the supplied documentation): analyst EPS and revenue estimates with analyst count and revision history. Revisions are the classic predictor of surprises, but history of past revisions is probably not available; we could start saving daily snapshots now to build our own point-in-time history for a forward test.
- `EARNINGS_CALL_TRANSCRIPT` (since 2010Q1, with sentiment signals): one request per name and quarter, so the daily request limit makes a full history slow (about 1,100 requests for 20 names over 14 years); a sample is possible.
