# Journal

Plain-language notes: surprises, doubts, ideas, open questions.

## 2026-11-05
- Project started. Pilot year 2020 chosen because it has both quiet stretches and big shocks (COVID crash, rebound, election).
- Answered: no single Kaggle headlines dataset covers 2020 well on its own. Best full-year finance one is small (1519 headlines); Reuters is richer but stops in July; ABC covers the whole year but is general and mostly Australian.
- Watch out: the S&P headlines dataset ships the day's S&P close next to each headline. That is future information for the agents, so it must be removed on load. Also unknown: whether a given headline was published before or after the market close on its date. This matters for the closed-loop rule and needs a decision (for example, only use a headline for the next trading day's decision).
- Open question: do we need GDELT after all? Only if the three sources above leave important 2020 events uncovered (e.g. the Nov 2020 election, vaccine news).
