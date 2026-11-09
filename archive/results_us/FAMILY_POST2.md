# Lowered-bar agent run on the post-cutoff window (2026-11-07)

Change from `results/FAMILY_POST.md`: new prompt `agent/FAMILY_AGENT_PROMPT_CATALYST.md` (long needs confidence >= 0.52 and a named, checkable catalyst quoted from the headlines or record; momentum, trend flags, mood and already-large moves do not count). 22 decision days, every 3 trading days from 2026-07-01 to 2026-09-30 (after the knowledge cutoff), one Sonnet subagent per day in sequence, each with the price record, Google News headlines published before the open (`src/download_news.py`) and the previous agent's handoff note. Scored with `src/score_family_run.py --run fam_post2 --min-conf 0.52` (long = buy the family leader at the close of the decision day, hold 5/10/20 days, costs included, 1,000 USD whole-share portfolio, at most 3 longs).

## Result
- 110 calls: 19 long, 91 flat. Longs: 14 oil and gas (XOM), 4 pharma (LLY), 1 copper and uranium (FCX). Nothing in gold miners or chips.
- Long calls: mean +2.55% per hold after costs, positive on 63%. The flat calls, had they been held: +1.76%, positive on 52%. Difference +0.8 points on 19 calls, and 14 of them are the same oil episode (the Iran supply story, XOM repeated on most days), so effectively one or two independent bets. Not statistically meaningful.
- Confidence did not track outcomes (correlation -0.01).
- Whole-share portfolio (1,000 USD): 1,065 USD at the end (+6.5%), maximum drawdown -2%, fees 2.5 USD, 3 trades executed (LLY at about 1,200 USD a share was unaffordable in a 333 USD slot, so its 4 calls were not traded). Random calls with the same number of longs and horizons: median 1,096 USD, 5th to 95th percentile 959 to 1,241. The agent sits below the median of random.
- The "leaders basket" benchmark in the summary (2,508 USD) compounds overlapping 21-day holds every 3 days and is overstated here; use the counterfactual means instead.

## Reading
- Lowering the bar made the agent trade (19 longs against 0 before), almost only on one theme: oil after the Iran supply headlines. The catalyst rule worked as designed (each long quoted a headline) but there is no evidence of added value over random choice: well within noise, and the sample is 22 days in one market regime.
- A real test needs many more days and many independent catalysts, a better company-news feed than Google News search titles, and probably a calibration step (does a quoted catalyst predict returns better than the base rate?). That is a large token cost for a likely small effect.

## Bug fixed in `src/score_family_run.py`
A repeated long call on a ticker already held overwrote the position and lost the cash used to buy it (final equity showed 463 USD instead of 1,065). A repeated call now extends the hold. Earlier runs had no repeated longs, so their results are unchanged (fam_post re-scored: 1,000 USD, 0 orders).
