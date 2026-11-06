"""Baselines on the rule-selected single-stock universe with a 500 USD account: whole shares, at most 2 positions, real order costs.

Usage: python -I src/run_universe_baselines.py [--capital 500] [--sims 300]
Universe: point-in-time top-4 names per family (universe/rule_selections.csv, rule in universe/UNIVERSE_RULE.md); at each
decision day the latest as-of snapshot dated on or before that day is used. Signals use only closes BEFORE the trade day;
trades execute at the trade-day close (one day after the signal). A new pair is chosen every H trading days; a name that is
chosen again is simply kept (no cost). Costs come from src/costs.py (IBKR Ireland tiered, whole shares, USD cash).
Positions: up to 2 names from different families, each half of current equity; names whose price exceeds half of equity are skipped.
Strategies: cash, hold_two (two names held all period), random_rotate (mean and 5th-95th percentile of many runs),
momentum (top 20-day return), lowvol (lowest 60-day volatility), trend (above 200-day average, best 60-day return, else cash).
Periods: build 2022 (reference only), validation 2023-2024, final test 2025 to now. Nothing is tuned on the test period.
Writes results/universe_baselines.csv. Tax: 16% of the positive total gain, shown separately (annual declaration approximated).
"""
import argparse
import csv
import random
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import build_universe as bu  # noqa: E402
import costs as cs           # noqa: E402

PERIODS = {"2022 (build, reference)": ("2022-01-03", "2022-12-30"),
           "2023-2024 (validation)": ("2023-01-03", "2024-12-31"),
           "2025-now (final test)": ("2025-01-02", "2026-11-05")}
TAX = 0.16


def load():
    cands = list(csv.DictReader(open(ROOT / "universe" / "candidates.csv", encoding="utf-8")))
    fam = {r["ticker"]: r["family"] for r in cands}
    close = {}
    for t in fam:
        try:
            _, b = bu.fetch(t, "10y")
            close[t] = {x[0]: x[1] for x in b}
        except Exception:  # noqa: BLE001
            pass
    sel = {}
    for r in csv.DictReader(open(ROOT / "universe" / "rule_selections.csv", encoding="utf-8")):
        sel.setdefault(r["asof"], []).append(r["ticker"])
    return fam, close, sel


def universe_at(sel, d):
    ok = [a for a in sel if a <= d]
    return sel[max(ok)] if ok else sel[min(sel)]


def run(strategy, H, cal, i0, i1, fam, close, sel, capital, rng=None, fixed=None, P=2):
    cash, pos, orders, fees = capital, {}, 0, 0.0
    peak, mdd, state = capital, 0.0, {"fixed": fixed, "P": P}
    p = cs.CostParams()

    def px(t, d):
        return close[t].get(d)

    def equity(d):
        return cash + sum(sh * (px(t, d) or ep) for t, (sh, ep) in pos.items())

    for j in range(i0, i1 + 1):
        d = cal[j]
        if (j - i0) % H == 0 and j >= 1:
            eq = equity(d)
            slot = eq / P
            prev = cal[j - 1]
            names = [t for t in universe_at(sel, prev) if t in close and prev in close[t] and px(t, d) is not None]
            names = [t for t in names if close[t][prev] <= slot]
            target = strategy(j, cal, close, fam, names, rng, state)
            for t in list(pos):                      # sell what is not in the target
                if t not in target and px(t, d) is not None:
                    sh, ep = pos.pop(t)
                    value = sh * px(t, d)
                    c = cs.one_way_cost(value * (1 + 1e-12), px(t, d), p, sell=True)
                    cash += value - c; fees += c; orders += 1
            for t in target:                         # buy what is new
                if t in pos or px(t, d) is None:
                    continue
                price = px(t, d)
                sh = int(slot / price)
                while sh >= 1:
                    value = sh * price
                    c = cs.one_way_cost(value * (1 + 1e-12), price, p)
                    if cash >= value + c:
                        cash -= value + c; pos[t] = (sh, price); fees += c; orders += 1
                        break
                    sh -= 1
        eq = equity(d)
        peak = max(peak, eq); mdd = min(mdd, eq / peak - 1)
    final = equity(cal[i1])
    gain = final - capital
    return {"final": final, "ret_pct": gain / capital * 100, "max_dd_pct": mdd * 100, "orders": orders, "fees": fees,
            "final_after_tax": capital + gain - TAX * max(0.0, gain)}


def pick_two(ranked, fam, n=2):
    out = []
    for t in ranked:
        if len(out) == n:
            break
        if all(fam[t] != fam[o] for o in out):
            out.append(t)
    return out


def s_cash(*a):
    return []


def s_hold(j, cal, close, fam, names, rng, state):
    if state["fixed"] is None:
        by = {}
        for t in names:
            by.setdefault(fam[t], t)
        order = [by[f] for f in ("oil_gas", "pharma", "gold_miners", "chips", "copper_uranium") if f in by][:state["P"]]
        state["fixed"] = order
    return state["fixed"]


def s_random(j, cal, close, fam, names, rng, state):
    pool = names[:]
    rng.shuffle(pool)
    return pick_two(pool, fam, state["P"])


def ret_n(close, t, cal, j, n):
    a, b = close[t].get(cal[j - 1]), close[t].get(cal[j - 1 - n])
    return None if a is None or b is None else a / b - 1


def s_momentum(j, cal, close, fam, names, rng, state):
    sc = [(ret_n(close, t, cal, j, 20), t) for t in names]
    sc = sorted([x for x in sc if x[0] is not None], reverse=True)
    return pick_two([t for _, t in sc], fam, state["P"])


def s_lowvol(j, cal, close, fam, names, rng, state):
    sc = []
    for t in names:
        c = [close[t].get(cal[k]) for k in range(j - 61, j)]
        if None in c:
            continue
        r = [c[k] / c[k - 1] - 1 for k in range(1, len(c))]
        sc.append((st.pstdev(r), t))
    return pick_two([t for _, t in sorted(sc)], fam, state["P"])


def s_trend(j, cal, close, fam, names, rng, state):
    sc = []
    for t in names:
        c = [close[t].get(cal[k]) for k in range(j - 200, j)]
        if None in c or c[-1] <= sum(c) / 200:
            continue
        r = ret_n(close, t, cal, j, 60)
        if r is not None:
            sc.append((r, t))
    return pick_two([t for _, t in sorted(sc, reverse=True)], fam, state["P"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capital", type=float, default=500.0)
    ap.add_argument("--sims", type=int, default=300)
    ap.add_argument("--positions", type=int, default=2, help="number of positions (names from different families)")
    a = ap.parse_args()
    P = a.positions
    fam, close, sel = load()
    cal = sorted(close["XOM"])
    rows = []
    strategies = [("cash", s_cash), ("hold_two", s_hold), ("momentum20", s_momentum), ("lowvol60", s_lowvol), ("trend200", s_trend)]
    for pname, (d0, d1) in PERIODS.items():
        i0 = next(i for i, d in enumerate(cal) if d >= d0)
        i1 = max(i for i, d in enumerate(cal) if d <= d1)
        print("\n== {} ({} to {}), start capital {}".format(pname, cal[i0], cal[i1], a.capital))
        print("{:12s} {:>3s} {:>8s} {:>8s} {:>8s} {:>7s} {:>7s} {:>10s}".format("strategy", "H", "final", "ret%", "maxDD%", "orders", "fees", "after tax"))
        for H in (5, 10, 20):
            for name, s in strategies:
                if name in ("cash", "hold_two") and H != 5:
                    continue
                r = run(s, 10**6 if name == "hold_two" else H, cal, i0, i1, fam, close, sel, a.capital, P=P)
                rows.append({"period": pname, "strategy": name, "H": H if name not in ("cash", "hold_two") else "-", **{k: round(v, 2) for k, v in r.items()}})
                print("{:12s} {:>3} {:8.1f} {:8.1f} {:8.1f} {:7d} {:7.2f} {:10.1f}".format(name, H if name not in ("cash", "hold_two") else "-", r["final"], r["ret_pct"], r["max_dd_pct"], r["orders"], r["fees"], r["final_after_tax"]))
            rnd = random.Random(7)
            res = [run(s_random, H, cal, i0, i1, fam, close, sel, a.capital, rng=rnd, P=P) for _ in range(a.sims)]
            v = sorted(x["ret_pct"] for x in res)
            rows.append({"period": pname, "strategy": "random_rotate_mean", "H": H, "final": round(st.mean(x["final"] for x in res), 2),
                         "ret_pct": round(st.mean(v), 2), "max_dd_pct": round(st.mean(x["max_dd_pct"] for x in res), 2),
                         "orders": round(st.mean(x["orders"] for x in res), 1), "fees": round(st.mean(x["fees"] for x in res), 2),
                         "final_after_tax": round(st.mean(x["final_after_tax"] for x in res), 2)})
            print("{:12s} {:>3} {:8.1f} {:8.1f} {:8.1f} {:7.0f} {:7.2f} {:10.1f}   ret% 5th-95th: {:.1f} to {:.1f}".format(
                "random(mean)", H, st.mean(x["final"] for x in res), st.mean(v), st.mean(x["max_dd_pct"] for x in res),
                st.mean(x["orders"] for x in res), st.mean(x["fees"] for x in res), st.mean(x["final_after_tax"] for x in res), v[int(.05 * (len(v) - 1))], v[int(.95 * (len(v) - 1))]))
    out = ROOT / "results" / ("universe_baselines.csv" if (int(a.capital), P) == (500, 2) else "universe_baselines_{}_{}pos.csv".format(int(a.capital), P))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["period", "strategy", "H", "final", "ret_pct", "max_dd_pct", "orders", "fees", "final_after_tax"])
        w.writeheader(); w.writerows(rows)
    print("\nsaved", out)


if __name__ == "__main__":
    main()
