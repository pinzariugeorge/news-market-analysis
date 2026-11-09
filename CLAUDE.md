# Instructions for Claude sessions in this repo

- Start of session: read `ROADMAP.md`, `STRATEGY.md`, `PROGRESS_LOG.md`. Use ROADMAP.md to find files instead of searching.
- Keep the context files up to date as you work, in the same change as the work itself, not at the end: `ROADMAP.md` (any file added, moved, renamed or repurposed), `STRATEGY.md` (any changed decision), `PROGRESS_LOG.md` (what was done, exact next step), `JOURNAL.md` (surprises, open questions), `README.md` (if the overview changes).
- Open items live in `TODO.md`; tick them off or add to them as work happens.
- Project focus (user decision 2026-11-09): European markets only, no S&P 500 or other US markets. Own local paper broker with live delayed prices; Saxo is the reference broker. The US era is in `archive/` and `results/US_LESSONS.md`.
- Research and simulation only: no real money, no financial advice.
- Never print or paste secrets from `.env`. Ask before spending money on paid data or APIs.
- No outcome leaks: an agent must never see prices or outcomes after its decision time (the old `CP` column in the S&P headlines was one such leak; it is archived).
- Commit when the user asks; do not push without being told.
