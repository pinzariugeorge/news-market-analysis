> **2026-11-13: intraday and all four labs (core, short, news, wild) are PAUSED (routines disabled, not deleted). Only morning and evening run.**

# Cloud scheduled tasks for the European paper account (environment `eu-paper`, repo pinzariugeorge/news-market-analysis, Opus)

Two Claude Code cloud tasks replace the laptop daemon and the three local tasks. State is read at the start and written at the end through the git branch `claude/paper-state` (`src/state_sync.py`). Times are your local time (Bucharest, one hour ahead of CET, daylight saving moves together with CET): the morning task is 08:07 CET and the evening task 18:07 CET, weekdays only. Cloud runs may start a few minutes late. Research and simulation only.

> Third task (added 2026-11-10): `eu-paper-intraday`, cron `37 8-15 * * 1-5` UTC, model Sonnet for the checking session, Opus subagent only when `eu_cycle.py intraday` prints wake true (prompt: `agent/EU_INTRADAY_PROMPT.md`). Routine https://claude.ai/code/routines/trig_01UJMy3cPH9qWSRVwcT54gtt . Its text is stored in the routine; steps: pull, intraday, (Opus decision, apply intraday), push.

> Fourth task (added 2026-11-10): `eu-paper-lab`, cron `17 10 * * 1-5` UTC, Sonnet session plus an Opus subagent (WebSearch allowed, 4 searches), routine https://claude.ai/code/routines/trig_01BnbZvJn7RDvvnNATR4pe8t . Separate paper account: every command runs with `LAB=1 PAPER_DIR=$PWD/data/paper_lab PAPER_STATE_BRANCH=claude/lab-state`; steps: pull, due lab, prep lab, Opus (prompt `agent/EU_LAB_PROMPT.md`), apply lab, push. It never touches the main account; the broker refuses mixed use. The morning trader now also writes `shadow` calls (scored in the evening run). DST: shift this cron with the others on 2027-03-28.

> Evening task moved (2026-11-10): cron `50 16 * * 1-5` UTC (was `7 17`), 20 minutes after the 16:30 UTC close, because quotes are delayed up to 20 minutes and the last bars must exist. Shift to `50 15` on 2027-03-28 with the other crons.

> Lab family (2026-11-11): three isolated lab accounts, each one cloud task, each ends with a phone notification tagged `🧪 LAB <name>`. `eu-paper-lab` (core, any idea family; data/paper_lab; branch claude/lab-state; 12:17 Bucharest = 10:17 UTC), `eu-paper-lab-short` (data/paper_lab_short; claude/lab-short-state; LAB_HORIZONS=1,2,3; 14:17 Bucharest; routine trig_01KTMcuzV8VQnEJ6ADCN8JKd), `eu-paper-lab-news` (data/paper_lab_news; claude/lab-news-state; 16:17 Bucharest; routine trig_01AQTV2DJj7oqJGF6bZDYYFu). Lab and evening crons use `CRON_TZ=Europe/Bucharest`, so they follow daylight saving by themselves (evening 18:50 Bucharest = 16:50 UTC in winter). The morning (`7 7` UTC) and intraday (`37 8-15` UTC) crons are still plain UTC: shift them on 2027-03-28 (or convert them to CRON_TZ=Europe/Bucharest the same way: 09:07 and 10:37-17:37).

## Task 1: eu-paper-morning (weekdays 09:07 local)
```
Project: this repository (European stock paper trading, paper money, research and simulation only, not financial advice). This is a cloud run: do exactly the steps below with python3 from the repository root, change no tracked file, push only through state_sync, never print secrets. If any python command fails, stop, say which and why, and still run the final push step.
Set PAPER_STATE_BRANCH=claude/paper-state for every command (export it first).
1. python3 -I src/state_sync.py pull
2. python3 -I src/eu_cycle.py due researcher . If it prints "run": false, jump to step 9 and reply "skipped: <reason>".
3. python3 -I src/eu_cycle.py prep researcher  (prints the input path)
4. Use the Agent tool, subagent_type general-purpose, model opus, with this prompt (put the real path in): "You are one run of a research simulation agent (not financial advice). Use only the Read tool and one Write. Do not read anything else and do not run commands. 1. Read agent/EU_RESEARCHER_PROMPT.md and follow it exactly. 2. Read the input file at <path from step 3> (it names the output file; write the brief exactly there). Reply with one line: done, plus the number of candidate catalysts."
5. python3 -I src/eu_cycle.py apply researcher ""
6. python3 -I src/eu_cycle.py due trader . If "run": false, jump to step 9.
7. python3 -I src/eu_cycle.py prep trader  (prints the input path). Then use the Agent tool, subagent_type general-purpose, model opus, with this prompt: "You are one run of a research simulation agent (not financial advice). Use only the Read tool and one Write. Do not read anything else and do not run commands. 1. Read agent/EU_TRADER_PROMPT.md and follow it exactly, including the lessons rules and the exact handoff shape. 2. Read the input file at <path from step 7>; read its warnings and handoff first; it names the output file, write the JSON exactly there. Reply with one line: done, plus the orders or 'no orders'."
8. python3 -I src/eu_cycle.py apply trader <the output path named in the trader input file>
9. python3 -I src/state_sync.py push
10. Reply with one line: done plus the order results, or the error.
```

## Task 2: eu-paper-evening (weekdays 19:07 local)
```
Project: this repository (European stock paper trading, paper money, research and simulation only, not financial advice). This is a cloud run: do exactly the steps below with python3 from the repository root, change no tracked file, push only through state_sync, never print secrets. If any python command fails, stop, say which and why, and still run the final push step.
Set PAPER_STATE_BRANCH=claude/paper-state for every command (export it first).
1. python3 -I src/state_sync.py pull
2. python3 -I src/eu_cycle.py evening   (replays stops and horizon exits from the day's bars, fills pending orders, runs the close: mark to market, custody, reconcile, day report)
3. python3 -I src/eu_cycle.py due reviewer . If "run": false, jump to step 8 and reply "skipped: <reason>".
4. python3 -I src/eu_cycle.py prep reviewer  (prints the input path). Then use the Agent tool, subagent_type general-purpose, model opus, with this prompt: "You are one run of a research simulation agent (not financial advice). Use only the Read tool and one Write. Do not read anything else and do not run commands. 1. Read agent/EU_REVIEWER_PROMPT.md and follow it exactly. 2. Read the input file at <path from step 4>; it names the output file, write the JSON exactly there. Reply with one line: done."
5. python3 -I src/eu_cycle.py apply reviewer <the output path named in the reviewer input file>
6. python3 -I src/eu_report.py  (writes data/paper/reports/artifact.html)
7. Publish the page to Claude cloud: Artifact tool, action publish, file_path the absolute path of data/paper/reports/artifact.html in this repository, url https://claude.ai/artifact/7TxjomynSos5DdRG3zaox6 (updates the existing private page; no icon, do not rewrite the file). If the tool asks you to read the artifact first, read that url once and publish again. If publishing fails, say so; the report is saved in the state branch.
8. python3 -I src/state_sync.py push
9. Reply with one line: done plus the day result, or the error.
```

> Wild lab (2026-11-12): `eu-paper-lab-wild`, routine trig_016md7fQdB65sxRA2fKWemCH, `CRON_TZ=Europe/Bucharest 17 13 * * 1-5` (13:17 Bucharest). 2,000 EUR, 6 positions, 25% cap, 6 buys/day, stop -10%, halts -5% day / -10% week, any horizon; data/paper_lab_wild, branch claude/wild-state. Env LAB_START_CASH etc. are read by paper_broker (needs main to contain commit e2fd914 or later).

> Screen log (2026-11-12): no routine change. `eu_cycle.py evening` (step 2 of the evening task) now also runs `src/screen_log.py` (needs main to contain it): logs S1-S3 triggers for the traded names and scores older ones; files in `data/paper/` travel with the state branch. Read it with `python3 -I src/screen_log.py report` after `state_sync.py pull`.
