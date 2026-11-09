"""Earnings surprise tests using analyst consensus history (data from src/download_consensus.py).

Usage: python -I src/run_surprise_test.py [--demo]
--demo runs on IBM only (public demo data plus Yahoo prices) to test the code. Data up to 2024-12-31 only.
Tests, per period (build up to 2022, validation 2023-2024):
 A. Reaction vs surprise: mean reaction-day move by surprise bucket (miss < -2%, in line -2..+2%, beat +2..+10%, big beat > +10%).
 B. Drift after surprise: entry at the close of reaction day + 1, hold H = 5, 10, 20 days, minus 0.3% cost, minus the stock's
    unconditional mean for the period (excess).
 C. Beat persistence: P(beat | previous quarter beat) versus P(beat | previous quarter miss).
 D. Pre-announcement: buy the close before the release reaches the market and sell the reaction-day close (hold through the
    event), by previous surprise bucket and in total, minus 0.3%.
Reaction day R = report date for pre-market reports, next trading day for post-market (unknown time treated as post-market).
Writes results/surprise_test.csv.
"""
import argparse
import csv
import json
import math
import statistics as st
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import build_universe as bu  # noqa: E402

COST = 0.3
LAST = "2024-12-31"
PER = {"build": ("0000", "2022-12-31"), "valid": ("2023-01-01", LAST)}


def per_of(d):
    for p, (a, b) in PER.items():
        if a <= d <= b:
            return p


def bucket(s):
    return "miss" if s < -2 else "inline" if s <= 2 else "beat" if s <= 10 else "bigbeat"


def tstat(v):
    return st.mean(v) / (st.pstdev(v) / math.sqrt(len(v))) if len(v) > 2 and st.pstdev(v) > 0 else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    cdir = ROOT / "data" / "raw" / "consensus"
    if a.demo:
        j = json.loads(urllib.request.urlopen(urllib.request.Request("https://www.alphavantage.co/query?function=EARNINGS&symbol=IBM&apikey=demo", headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
        files = {"IBM": j["quarterlyEarnings"]}
    else:
        files = {p.stem: json.loads(p.read_text(encoding="utf-8"))["quarterlyEarnings"] for p in sorted(cdir.glob("*.json"))}
    if not files:
        sys.exit("No consensus files: run src/download_consensus.py first (needs a free Alpha Vantage key in .env).")
    prices = {}
    for t in files:
        _, b = bu.fetch(t, "10y")
        d = sorted(x[0] for x in b if x[0] <= LAST)
        c = {x[0]: x[1] for x in b}
        prices[t] = (d, [c[x] for x in d], {x: i for i, x in enumerate(d)})
    events = []
    for t, q in files.items():
        d, c, ix = prices[t]
        qs = sorted([r for r in q if r.get("estimatedEPS") not in (None, "None", "") and r.get("surprisePercentage") not in (None, "None", "")], key=lambda r: r["reportedDate"])
        prev = None
        for r in qs:
            rd = r["reportedDate"]
            if rd < "2010-01-01" or rd > LAST:
                prev = r
                continue
            nxt = [x for x in d if x >= rd]
            if not nxt:
                continue
            post = (r.get("reportTime") or "").startswith("post") or not r.get("reportTime")
            R = [x for x in d if x > rd][0] if post else nxt[0]
            if R not in ix or ix[R] < 25 or ix[R] + 22 >= len(d):
                prev = r
                continue
            i = ix[R]
            s = float(r["surprisePercentage"])
            events.append({"t": t, "R": R, "i": i, "s": s, "b": bucket(s), "prev_b": bucket(float(prev["surprisePercentage"])) if prev and prev.get("surprisePercentage") not in (None, "None", "") else None,
                           "react": (c[i] / c[i - 1] - 1) * 100, "pre20": (c[i - 1] / c[i - 21] - 1) * 100})
            prev = r
    print("{} events from {} tickers".format(len(events), len(files)))
    rows = []
    print("\nA. reaction-day move by surprise bucket")
    for p in PER:
        for b in ("miss", "inline", "beat", "bigbeat"):
            v = [e["react"] for e in events if per_of(e["R"]) == p and e["b"] == b]
            if len(v) >= 5:
                print("  {:5s} {:8s} n={:4d} mean move {:+.2f}%  up {:.0f}%".format(p, b, len(v), st.mean(v), 100 * sum(1 for x in v if x > 0) / len(v)))
                rows.append({"test": "A", "period": p, "group": b, "H": "", "n": len(v), "mean": round(st.mean(v), 2), "excess": "", "t": round(tstat(v), 2)})
    print("\nB. drift after the reaction (excess over the stock's unconditional mean, net of cost)")
    for H in (5, 10, 20):
        um = {}
        for t, (d, c, ix) in prices.items():
            for i in range(25, len(d) - H - 2):
                p = per_of(d[i])
                if p:
                    um.setdefault((t, p), []).append((c[i + 1 + H] / c[i + 1] - 1) * 100 - COST)
        um = {k: st.mean(v) for k, v in um.items()}
        for p in PER:
            for b in ("miss", "beat", "bigbeat"):
                v = []
                for e in events:
                    if per_of(e["R"]) == p and e["b"] == b and (e["t"], p) in um:
                        d, c, ix = prices[e["t"]]
                        v.append((c[e["i"] + 1 + H] / c[e["i"] + 1] - 1) * 100 - COST - um[(e["t"], p)])
                if len(v) >= 5:
                    print("  H={:2d} {:5s} {:8s} n={:4d} excess {:+.2f}  t {:+.2f}".format(H, p, b, len(v), st.mean(v), tstat(v)))
                    rows.append({"test": "B", "period": p, "group": b, "H": H, "n": len(v), "mean": "", "excess": round(st.mean(v), 2), "t": round(tstat(v), 2)})
    print("\nC. beat persistence")
    for p in PER:
        pb = [e for e in events if per_of(e["R"]) == p and e["prev_b"] in ("beat", "bigbeat")]
        pm = [e for e in events if per_of(e["R"]) == p and e["prev_b"] in ("miss",)]
        allb = [e for e in events if per_of(e["R"]) == p and e["prev_b"]]
        f = lambda xs: 100 * sum(1 for e in xs if e["b"] in ("beat", "bigbeat")) / len(xs) if xs else float("nan")
        print("  {:5s} P(beat | prev beat) {:.0f}% (n={})  P(beat | prev miss) {:.0f}% (n={})  all {:.0f}%".format(p, f(pb), len(pb), f(pm), len(pm), f(allb)))
    print("\nD. buy before the release, sell the reaction-day close (hold through), net of cost, by previous surprise")
    for p in PER:
        for g in ("beat+bigbeat", "miss", "all"):
            v = []
            for e in events:
                if per_of(e["R"]) != p or not e["prev_b"]:
                    continue
                if g == "beat+bigbeat" and e["prev_b"] not in ("beat", "bigbeat"):
                    continue
                if g == "miss" and e["prev_b"] != "miss":
                    continue
                v.append(e["react"] - COST)
            if len(v) >= 5:
                print("  {:5s} {:13s} n={:4d} mean net {:+.2f}%  up {:.0f}%  t {:+.2f}".format(p, g, len(v), st.mean(v), 100 * sum(1 for x in v if x > 0) / len(v), tstat(v)))
                rows.append({"test": "D", "period": p, "group": g, "H": "", "n": len(v), "mean": round(st.mean(v), 2), "excess": "", "t": round(tstat(v), 2)})
    if not a.demo:
        with open(ROOT / "results" / "surprise_test.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "period", "group", "H", "n", "mean", "excess", "t"])
            w.writeheader(); w.writerows(rows)
        print("\nsaved results/surprise_test.csv")


if __name__ == "__main__":
    main()
