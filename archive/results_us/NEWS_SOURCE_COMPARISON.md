# News source comparison: Google News search vs Finnhub Company News (2026-11-07)

Same 22 post-cutoff decision days (2026-07-01 to 2026-09-30), same prompt (`agent/FAMILY_AGENT_PROMPT_CATALYST.md`: long at confidence >= 0.52 only with a quoted catalyst), same chained handoff, same scoring (`src/score_family_run.py --min-conf 0.52`). Only the headlines differ. Runs: `results/fam_post2` (Google News search, six theme queries, titles only) and `results/fam_post3` (Finnhub `/company-news` for each family's four names, headline plus source, time, related tickers and 160 characters of summary; `src/download_news_finnhub.py`). Finnhub's Market News endpoint (`/news`) has no date range, so it cannot be backtested.

| | Google News (fam_post2) | Finnhub company news (fam_post3) |
|---|---|---|
| Items per day (average) | about 29 | about 37 |
| Long calls out of 110 | 19 (oil 14, pharma 4, copper/uranium 1) | 3 (all Eli Lilly) |
| Mean net return of the longs | +2.55%, 63% positive | +0.79%, 67% positive (3 calls) |
| Same calls if held when flat | +1.76% | +1.85% |
| Portfolio, 1,000 USD whole shares | 1,065 | 1,000 (no order: LLY about 1,200 USD a share does not fit a 333 USD slot) |
| Random calls with the same structure, median (5th to 95th) | 1,097 (959 to 1,241) | 1,073 (1,008 to 1,167) |
| Correlation of confidence with outcome | -0.01 | -0.06 |

## Reading
- Finnhub's company news produced far fewer catalysts. It is dominated by aggregator and opinion pieces (Zacks, Seeking Alpha, Yahoo) and by stock-specific items; it has no commodity or geopolitical stream. The Iran supply story that drove the Google run's 14 oil longs never appears as a company headline, so the agent stayed flat on oil. The only Finnhub trades were Eli Lilly on trial and filing news.
- Neither run shows skill: the long calls are within noise of the flat counterfactual, and both sit at or below the random median. The Google run's gains came from one oil episode.
- The two sources are complements, not substitutes: company news gives firm-specific catalysts with timestamps; macro and commodity events need a separate feed (Finnhub's general news can only be collected going forward, not backtested).
- Practical consequence for paper trading: use Finnhub company news plus an SEC 8-K feed for company events, and add a forward-collected macro/commodity feed (daily snapshots of Finnhub `/news?category=general`, EIA and OPEC releases, an event calendar). Judge the agent only on a pre-registered rule and enough days.

## Third source: Massive (formerly Polygon) news, `fam_post4`

Same 22 decision days, catalyst prompt, chained handoff. `src/download_news_massive.py` (`/v2/reference/news`, `ticker.any_of`, dated, publisher and tickers included, 40 items per day, history from about 2022 on the free plan, 5 calls a minute).
Result: 0 longs in 22 days, all five families flat every day (portfolio stays at 1,000, fees 0). Typical items were Zacks and Motley Fool pieces with no event on the family leader, so the catalyst rule never fired.
Reading: the source is clean and backtestable, but it carries company commentary, not macro or commodity events (the Iran-oil stream that drove the Google run's trades is absent). Nothing to score; no evidence for or against skill.

## Model and learning test (same 22 Google News days, catalyst prompt, longs at confidence >= 0.52)

| run | agent | longs | mean net per long | portfolio (start 1,000) | random-call median (5th-95th) |
|---|---|---|---|---|---|
| fam_post2 | Sonnet | 19 | +2.55% | 1,065 | 1,097 (959-1,241) |
| fam_opus1 | Opus | 29 | +5.36% | 1,132 | 1,213 (1,027-1,408) |
| fam_opus2 | Opus + outcome feedback and lessons ledger | 27 | +2.86% | 1,065 | 1,258 (1,095-1,445) |

Reading: Opus took more trades and made more per long than Sonnet, but every run finished below the median of random calls with the same number of longs, so none shows skill. The learning arm did worse than plain Opus; its ledger never reached 5 supporting cases (the rule that lets a lesson change calls), so it could not act on lessons, and its oil trades kept losing late in the episode. The daily-schedule plumbing works (src/learn_prep.py builds the outcome block, src/handoff.py stores lessons, agent/FAMILY_AGENT_PROMPT_LEARN.md). Sonnet with learning not run (usage cap). Bug fixed after the run: the validator rejected `cases: 0` on the last day's note; zero is now allowed.
