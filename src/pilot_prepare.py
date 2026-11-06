"""Pick pilot decision days (2008-2019 only) and write their past-only daily records.

Usage: python -I src/pilot_prepare.py [--run pilot_v0] [--seed 7]
Writes results/<run>/days.json (the chosen days with category, NO outcomes) and results/<run>/records/<day>.json.
The outcomes stay in data/processed/market_days.csv and are joined only by src/score_decisions.py after decisions exist.
Categories: big (|move| >= 2%), calm (vol regime 1-2, |move| < 1%), stormy (regime 4, |move| < 1%), normal (regime 2-3), event (midterm day after 2010).
"""
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import build_daily_context as bdc   # noqa: E402
import run_baselines as rb          # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="pilot_v0")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rows = rb.load()
    regime, trend = rb.signals(rows)
    rnd = random.Random(a.seed)
    dev = [i for i, (d, _, r) in enumerate(rows) if "2008-01-02" <= d <= "2019-12-31" and r is not None and regime[i]]
    big = [i for i in dev if abs(rows[i][2]) >= 2]
    calm = [i for i in dev if regime[i] <= 2 and abs(rows[i][2]) < 1]
    stormy = [i for i in dev if regime[i] == 4 and abs(rows[i][2]) < 1]
    normal = [i for i in dev if regime[i] in (2, 3) and abs(rows[i][2]) < 2]
    pick = []
    def take(pool, k, cat, spread_years=True):
        pool = pool[:]
        rnd.shuffle(pool)
        used_years = {rows[j][0][:4] for j, _ in pick}
        got = 0
        for i in pool:
            y = rows[i][0][:4]
            if spread_years and y in used_years and got < k - 1:
                continue
            pick.append((i, cat))
            used_years.add(y)
            got += 1
            if got == k:
                break
    take(big, 4, "big")
    take(calm, 3, "calm")
    take(stormy, 3, "stormy")
    take(normal, 1, "normal")
    ev = [i for i, (d, _, _) in enumerate(rows) if d == "2010-11-03"]
    pick.append((ev[0], "event"))
    pick.sort(key=lambda x: rows[x[0]][0])
    out = ROOT / "results" / a.run
    (out / "records").mkdir(parents=True, exist_ok=True)
    days = []
    for i, cat in pick:
        d = rows[i][0]
        rec = bdc.build(d)
        (out / "records" / f"{d}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
        days.append({"day": d, "category": cat, "vol_regime": regime[i], "n_headlines": rec["headlines_total"]})
    (out / "days.json").write_text(json.dumps(days, indent=2), encoding="utf-8")
    for x in days:
        print(x["day"], x["category"], "regime", x["vol_regime"], "headlines", x["n_headlines"])


if __name__ == "__main__":
    main()
