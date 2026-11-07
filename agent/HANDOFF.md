# Handoff rule (live phase, also used in the chained post-cutoff test)

Why: every agent run is stateless and has no chat history. The handoff note is the only memory between runs. Research and simulation only; not financial advice.

## Procedure per run (the harness does the file work with `src/handoff.py`)
1. `python -I src/handoff.py lock`: stop if it exits with code 2 (another run started less than 30 minutes ago; a lock older than that is treated as a crashed run).
2. `python -I src/handoff.py read`: the text goes at the top of the agent's input. Warnings tell the agent what to do first:
   - FIRST RUN: no note, start from the handbook and the empty storylines template.
   - STALE (note older than 5 days): re-check positions and prices before acting.
   - PENDING ORDERS: reconcile with the broker before any new order.
   - Corrupt or invalid files are skipped and the newest valid note is used.
3. The agent decides and returns its normal JSON plus a `handoff` object (below).
4. `python -I src/handoff.py write decision.json`: validates and stores the note atomically (temp file then rename) in `agent/state/handoff/<decision_day>_<run_id>.json` and updates `LATEST.json`. An invalid note is rejected and the run counts as failed (the previous note stays current).
5. `python -I src/handoff.py unlock`.

## The `handoff` object (all fields required; at most 6,000 bytes)
```json
{
  "run_id": "short unique id",
  "written_at": "ISO timestamp",
  "decision_day": "YYYY-MM-DD",
  "data_cutoff": "YYYY-MM-DD (last information used; never after decision_day)",
  "what_changed": "what is different since the previous note, in two or three sentences",
  "families": {"oil_gas|gold_miners|chips|pharma|copper_uranium": {"position": "flat | long <name> since <date>, <horizon> days", "why": "one sentence"}},
  "open_storylines": [{"name": "...", "status": "open|escalating|fading|closed", "note": "...", "first_seen": "YYYY-MM-DD"}],
  "pending_orders": [{"symbol": "...", "side": "buy|sell", "qty": 0, "status": "sent, no fill seen | filled | cancelled"}],
  "next_job": "the exact next job, for example: decide for 2026-07-13 using the handbook and the new record; sell XOM on 2026-07-20 if still held"
}
```
Rules: drop closed storylines after 20 trading days; do not copy the whole reasoning, keep what the next run needs; `pending_orders` must list every order sent and not yet confirmed.

## Failure behaviours covered (tests: `python -I src/handoff.py selftest`)
First run with no note; corrupt note or pointer file; stale note; pending orders from a crashed run; two overlapping runs; note with future data; oversized note; missing family.
Not covered by code (belongs to the live routine): machine or app offline at the scheduled time (the next run sees a STALE or one-day-late note and must not trade on old prices), and broker-side reconciliation itself.
