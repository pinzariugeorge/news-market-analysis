"""Score stored agent decisions against outcomes and baselines.

Usage: python -I src/score_decisions.py --run pilot_v0 [--cost 0.02]
Reads  results/<run>/days.json, results/<run>/decisions_raw/<day>.json (agent output, see agent/AGENT_PROMPT.md)
       data/processed/market_days.csv (outcomes: day D close-to-close return)
Writes results/<run>/decisions.csv and results/<run>/summary.json

Outcomes are joined here, after the decisions exist. Because pilot days are sparse, each decision is treated as
independent: the agent starts flat each day and pays the cost on the position it takes (cost % x size).
Baselines on the same days: buy_hold (size 1), cash (0), vol_rule (1 in regimes 1-3 else 0), capped_long (1 or 0.5).
"""
import argparse
import csv
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="pilot_v0")
    ap.add_argument("--cost", type=float, default=0.02)
    a = ap.parse_args()
    run = ROOT / "results" / a.run
    days = json.loads((run / "days.json").read_text(encoding="utf-8"))
    rets = {}
    with open(ROOT / "data/processed/market_days.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["ret_pct"]:
                rets[r["date"]] = float(r["ret_pct"])
    rows, missing = [], []
    for d in days:
        p = run / "decisions_raw" / (d["day"] + ".json")
        if not p.exists():
            missing.append(d["day"])
            continue
        try:
            x = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            missing.append(d["day"] + " (bad json: %s)" % e)
            continue
        act, view = x.get("action", {}), x.get("view", {})
        size = float(act.get("size_pct", 0) or 0) if act.get("position") == "long" else 0.0
        out = rets[d["day"]]
        direction = view.get("direction", "no_edge")
        lo, hi = view.get("expected_move_pct_low"), view.get("expected_move_pct_high")
        correct = "" if direction == "no_edge" else int((out > 0) == (direction == "up"))
        in_range = "" if lo is None or hi is None else int(lo <= out <= hi)
        reg = d["vol_regime"]
        rows.append({
            "day": d["day"], "category": d["category"], "vol_regime": reg, "n_headlines": d["n_headlines"],
            "regime_label": x.get("regime", ""), "direction": direction, "exp_low": lo, "exp_high": hi,
            "horizon": view.get("horizon", ""), "confidence": view.get("confidence", ""),
            "position": act.get("position", ""), "size_pct": size,
            "events_used": ";".join(x.get("handbook_entries_used", [])),
            "n_events": len(x.get("events", [])), "n_relevant": sum(1 for e in x.get("events", []) if e.get("relevant")),
            "outcome_ret_pct": out, "strategy_ret_pct": round(size / 100 * out - a.cost * size / 100, 4),
            "buy_hold_ret_pct": out, "vol_rule_ret_pct": round(out * (1 if reg <= 3 else 0) - a.cost * (1 if reg <= 3 else 0), 4),
            "capped_long_ret_pct": round(out * (1 if reg <= 3 else 0.5) - a.cost * (1 if reg <= 3 else 0.5), 4),
            "correct": correct, "in_range": in_range,
            "reasoning": x.get("reasoning", ""), "would_change_my_mind": x.get("would_change_my_mind", ""),
            "events": x.get("events", []), "storyline_updates": x.get("storyline_updates", []),
        })
    rows.sort(key=lambda r: r["day"])
    cols = [c for c in rows[0] if c not in ("events", "storyline_updates")] if rows else []
    with open(run / "decisions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([r[c] for c in cols])
    committed = [r for r in rows if r["correct"] != ""]
    s = {
        "run": a.run, "n_days": len(days), "n_scored": len(rows), "missing": missing,
        "n_committed": len(committed),
        "hit_rate_committed": (sum(r["correct"] for r in committed) / len(committed)) if committed else None,
        "up_calls": sum(1 for r in rows if r["direction"] == "up"), "down_calls": sum(1 for r in rows if r["direction"] == "down"),
        "no_edge": sum(1 for r in rows if r["direction"] == "no_edge"),
        "long_days": sum(1 for r in rows if r["size_pct"] > 0),
        "avg_daily_ret_pct": {k: (st.mean(r[k] for r in rows) if rows else None) for k in
                              ("strategy_ret_pct", "buy_hold_ret_pct", "vol_rule_ret_pct", "capped_long_ret_pct")},
        "sum_ret_pct": {k: (sum(r[k] for r in rows) if rows else None) for k in
                        ("strategy_ret_pct", "buy_hold_ret_pct", "vol_rule_ret_pct", "capped_long_ret_pct")},
        "in_range_share": (sum(r["in_range"] for r in rows if r["in_range"] != "") / max(1, sum(1 for r in rows if r["in_range"] != ""))) if rows else None,
        "avg_confidence": (st.mean(float(r["confidence"]) for r in rows if r["confidence"] != "") if rows else None),
        "base_rate_up_pct_all_days": 52.8,
        "cost_pct_per_100pct_position": a.cost,
        "note": "Pilot days are sparse and independent; sums of daily returns, not compounded. Tiny sample: indicative only.",
    }
    (run / "summary.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    full = {"summary": s, "rows": rows}
    (run / "dashboard_data.json").write_text(json.dumps(full, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
