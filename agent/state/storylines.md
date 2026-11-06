# Open storylines (agent state file; template)

The agent reads this file at the start of each decision and updates it at the end. Keep it short (drop closed storylines after 20 trading days). During a simulation run a separate copy is kept per run in `results/<run_name>/storylines.md`; this file is the empty template.

Format, one block per storyline:

```
## S001 <short title>
- first seen: YYYY-MM-DD
- handbook type: 3.x
- status: open | escalating | fading | closed
- scale: small | medium | large
- last update: YYYY-MM-DD
- what is known (from headlines before the cutoff only):
- market reaction so far (from prices before the cutoff only):
- what to watch next:
```

(No storylines yet.)
