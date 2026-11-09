# Journal

Plain-language notes: surprises, doubts, ideas, open questions.

## 2026-11-05
- Project started. Pilot year 2020 chosen because it has both quiet stretches and big shocks (COVID crash, rebound, election).
- Answered: no single Kaggle headlines dataset covers 2020 well on its own. Best full-year finance one is small (1519 headlines); Reuters is richer but stops in July; ABC covers the whole year but is general and mostly Australian.
- Watch out: the S&P headlines dataset ships the day's S&P close next to each headline. That is future information for the agents, so it must be removed on load. Also unknown: whether a given headline was published before or after the market close on its date. This matters for the closed-loop rule and needs a decision (for example, only use a headline for the next trading day's decision).
- Open question: do we need GDELT after all? Only if the three sources above leave important 2020 events uncovered (e.g. the Nov 2020 election, vaccine news).

## 2026-11-09
- Pivot to European markets only, with our own local paper broker. Reason from the user: broker API keys are slow to get, and a local simulator fed with live prices lets agents train on a forward record.
- Surprise: Yahoo's `range=max` with a daily interval silently returns monthly bars; explicit `period1/period2` gives true daily history. The first liquidity table was wrong until this was fixed.
- Surprise: Europe has almost no liquid gold miners and no uranium producer with usable history, so the gold and oil themes may need ETCs, which breaks the old "no ETFs" rule (user to decide).
- Open: Saxo fees and which names a Romanian retail client can buy are only third-party figures; the broker's own instrument search settles it.
- Open: the Yahoo feed is unofficial; if it breaks we need a paid source (ask first).
- Open: the Sonnet-with-learning run on the US days was dropped with the US era.
- Decided: 1,000 EUR account, no ETFs. At that size the minimum fee dominates (about 1.2% to 1.8% a round trip) and six first-choice names cost more than one position can hold. The honest test is whether any agent beats random calls after that drag.
- Started paper trading with a late start at 13:33 CET. The first Opus trader chose no trade: with entry costs of about 1.6% to 2.3% per name (commission minimum, FX, stamp duty and French tax, slippage) and a round trip about twice that, only a very strong name-specific catalyst can pay. Expect many no-trade days; the test is whether trades, when they happen, beat random calls.
- Machine runs on Bucharest time (CET+1): scheduled-task cron is local time, everything inside Python is UTC.
