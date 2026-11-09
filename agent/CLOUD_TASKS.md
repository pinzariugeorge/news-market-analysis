# Cloud scheduled tasks for the European paper account (environment `eu-paper`, repo pinzariugeorge/news-market-analysis, Opus)

Two Claude Code cloud tasks replace the laptop daemon and the three local tasks. State is read at the start and written at the end through the git branch `claude/paper-state` (`src/state_sync.py`). Times are your local time (Bucharest, one hour ahead of CET, daylight saving moves together with CET): the morning task is 08:07 CET and the evening task 18:07 CET, weekdays only. Cloud runs may start a few minutes late. Research and simulation only.

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
