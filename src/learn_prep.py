"""Build the input block for a LEARNING agent run: handoff note + facts about how its past calls turned out. Research and simulation only.

Usage (simulation): python -I src/learn_prep.py --run fam_opus2 --day 2026-08-05 [--min-conf 0.52]   (HANDOFF_DIR / HANDOFF_STALE_DAYS as in handoff.py)
Writes results/<run>/handoff_in/<day>.txt = the usual handoff text + an "Outcomes of your past calls" section.
Point-in-time rule: a long call is reported only once its exit date is BEFORE the decision day (exit close known), so a run never sees its own future.
Outcome = leader stock net return over the held horizon (entry at the close of the call day, round-trip cost from src/costs.py) next to the family basket, plus a per-family
running tally. The agent must turn these facts into lessons itself (see agent/FAMILY_AGENT_PROMPT_LEARN.md); nothing here is a rule.
Live use: the same function takes the broker trade log instead of decisions_raw (to be wired when paper trading starts).
"""
import argparse
import json
import statistics as st
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import familydata as fd  # noqa: E402
import costs as cs       # noqa: E402


def closed_longs(run, day, min_conf):
    stocks, sel = fd.load_stocks(), fd.selections()
    p, out = cs.CostParams(), []
    days = json.loads((run / "days.json").read_text(encoding="utf-8"))
    for D in days:
        if D >= day:
            break
        f = run / "decisions_raw" / (D + ".json")
        if not f.exists():
            continue
        dec = json.loads(f.read_text(encoding="utf-8"))
        names = fd.names_at(sel, D)
        for fam in fd.FAMILIES:
            c = dec["families"].get(fam)
            if not c or c.get("call") != "long" or float(c.get("confidence", 0)) < min_conf:
                continue
            leader = names[fam][0]
            cal = sorted(stocks[leader])
            i = next((k for k, d in enumerate(cal) if d >= D), None)
            H = int(c.get("horizon_days", 10))
            if i is None or i + H >= len(cal) or cal[i + H] >= day:
                continue  # not closed before the decision day
            e, x = stocks[leader][cal[i]], stocks[leader][cal[i + H]]
            try:
                cost = cs.round_trip_pct(1000 / 3, e, p)
            except ValueError:
                cost = 0.3
            basket = [(stocks[t][cal[i + H]] / stocks[t][cal[i]] - 1) * 100 for t in names[fam] if t in stocks and cal[i] in stocks[t] and cal[i + H] in stocks[t]]
            out.append({"called": D, "family": fam, "leader": leader, "horizon": H, "entry": cal[i], "exit": cal[i + H], "net_pct": round((x / e - 1) * 100 - cost, 2),
                        "basket_pct": round(st.mean(basket), 2) if basket else None, "catalyst": str(c.get("catalyst", ""))[:140], "confidence": c.get("confidence")})
    return out


def block(trades):
    if not trades:
        return "# Outcomes of your past calls\nNo long call has closed yet. There is nothing to learn from yet; do not invent lessons."
    L = ["# Outcomes of your past calls (facts computed by the harness; closed trades only)"]
    for t in trades:
        L.append("- {} {} ({}), called {}, held {}d to {}: net {:+.2f}% (family basket {:+.2f}%). Catalyst you quoted: {}".format(
            t["family"], t["leader"], t["confidence"], t["called"], t["horizon"], t["exit"], t["net_pct"], t["basket_pct"] or 0, t["catalyst"] or "(none)"))
    L.append("Per-family tally (closed trades):")
    for fam in fd.FAMILIES:
        x = [t["net_pct"] for t in trades if t["family"] == fam]
        if x:
            L.append("- {}: {} trades, {} won, mean net {:+.2f}%".format(fam, len(x), sum(v > 0 for v in x), st.mean(x)))
    L.append("All: {} trades, {} won, mean net {:+.2f}%".format(len(trades), sum(t["net_pct"] > 0 for t in trades), st.mean(t["net_pct"] for t in trades)))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--day", required=True)
    ap.add_argument("--min-conf", type=float, default=0.52)
    a = ap.parse_args()
    run = ROOT / "results" / a.run
    ho = subprocess.run([sys.executable, "-I", str(ROOT / "src" / "handoff.py"), "read", "--asof", a.day], capture_output=True, text=True, cwd=ROOT).stdout
    text = ho.rstrip() + "\n\n" + block(closed_longs(run, a.day, a.min_conf)) + "\n"
    (run / "handoff_in").mkdir(parents=True, exist_ok=True)
    (run / "handoff_in" / (a.day + ".txt")).write_text(text, encoding="utf-8")
    print(text.splitlines()[-1][:120])


if __name__ == "__main__":
    main()
