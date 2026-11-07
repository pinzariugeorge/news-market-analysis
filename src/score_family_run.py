"""Score the family run: every family call against what the leader stock did, plus a 1,000 USD whole-share portfolio.

Usage: python -I src/score_family_run.py [--run fam_v0] [--capital 1000]
Reads results/<run>/days.json, results/<run>/decisions_raw/<day>.json, prices via src/familydata.py.
Convention: the agent decides before the open of day D from closes dated before D; a long call buys the family leader at the
close of D and sells at the close H trading days later (H = 5, 10 or 20) after a round-trip cost from src/costs.py. A flat call is
scored on what the leader would have done (counterfactual) so we can see missed gains. Portfolio: up to 3 long calls with
confidence >= 0.55 (highest first), equal slots of equity/3, whole shares, real order costs, USD cash.
Benchmarks: leaders basket (all 5 leaders equal weight each period, 21-day holds, 0.3% cost), cash, and random calls with the same
number of long calls and horizons (300 draws, fractional shares, same cost; approximation).
Writes results/<run>/decisions.csv, summary.json, dashboard_data.json.
"""
import argparse
import csv
import json
import random
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import familydata as fd  # noqa: E402
import costs as cs       # noqa: E402

MIN_CONF = 0.55
DRIVER_OF = {"oil_gas": "CL=F", "gold_miners": "GC=F", "chips": "SMH", "pharma": "XLV", "copper_uranium": "HG=F"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="fam_v0")
    ap.add_argument("--capital", type=float, default=1000.0)
    ap.add_argument("--min-conf", type=float, default=0.55, help="confidence needed for a long (the catalyst prompt uses 0.52)")
    a = ap.parse_args()
    global MIN_CONF
    MIN_CONF = a.min_conf
    run = ROOT / "results" / a.run
    days = json.loads((run / "days.json").read_text(encoding="utf-8"))
    series, stocks, sel = fd.load_series(), fd.load_stocks(), fd.selections()
    p = cs.CostParams()
    slot0 = a.capital / 3
    rows, missing = [], []
    for D in days:
        f = run / "decisions_raw" / (D + ".json")
        if not f.exists():
            missing.append(D)
            continue
        try:
            dec = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            missing.append(D + " bad json " + str(e)[:40])
            continue
        names = fd.names_at(sel, D)
        for fam in fd.FAMILIES:
            c = dec["families"].get(fam)
            if not c:
                continue
            leader = names[fam][0]
            cal = sorted(stocks[leader])
            i = next(k for k, d in enumerate(cal) if d >= D)           # entry at the close of D
            H = int(c.get("horizon_days", 10))
            if i + H >= len(cal):
                continue
            entry_d, exit_d = cal[i], cal[i + H]
            e, x = stocks[leader][entry_d], stocks[leader][exit_d]
            gross = (x / e - 1) * 100
            try:
                cost = cs.round_trip_pct(slot0, e, p)
                affordable = True
            except ValueError:
                cost, affordable = 0.3, False
            dser = series[DRIVER_OF[fam]]
            dd = sorted(d for d in dser if entry_d <= d <= exit_d)
            drv = (dser[dd[-1]] / dser[dd[0]] - 1) * 100 if len(dd) > 1 else None
            basket = []
            for t in names[fam]:
                if t in stocks and entry_d in stocks[t] and exit_d in stocks[t]:
                    basket.append((stocks[t][exit_d] / stocks[t][entry_d] - 1) * 100)
            long_call = c["call"] == "long"
            rows.append({"day": D, "family": fam, "leader": leader, "call": c["call"], "horizon": H, "confidence": float(c.get("confidence", 0)),
                         "entry_date": entry_d, "exit_date": exit_d, "entry_px": round(e, 3), "exit_px": round(x, 3), "gross_pct": round(gross, 3),
                         "cost_pct": round(cost, 3), "net_pct": round(gross - cost, 3), "affordable": int(affordable),
                         "positive_after_cost": int(gross - cost > 0), "correct": int((gross - cost > 0) == long_call),
                         "driver_ret_pct": None if drv is None else round(drv, 3), "basket_ret_pct": round(st.mean(basket), 3) if basket else None,
                         "reasoning": c.get("reasoning", ""), "market_view": dec.get("market_view", ""), "would_change_my_mind": dec.get("would_change_my_mind", "")})
    rows.sort(key=lambda r: (r["day"], fd.FAMILIES.index(r["family"])))

    # portfolio simulation
    cash, pos, fees, orders = a.capital, {}, 0.0, 0
    allcal = sorted(stocks["XOM"])
    by_day = {}
    for r in rows:
        by_day.setdefault(r["day"], []).append(r)
    start_i = next(k for k, d in enumerate(allcal) if d >= days[0])
    equity, trades = [], []
    peak, mdd = a.capital, 0.0
    exits = {}
    for k in range(start_i, len(allcal)):
        d = allcal[k]
        for t, (sh, ep, xd, fam) in list(pos.items()):
            if xd == d:
                v = sh * stocks[t][d]
                c_ = cs.one_way_cost(v * (1 + 1e-12), stocks[t][d], p, sell=True)
                cash += v - c_; fees += c_; orders += 1
                trades.append({"ticker": t, "family": fam, "entry": ep[0], "exit": d, "shares": sh, "entry_px": round(ep[1], 3), "exit_px": round(stocks[t][d], 3), "pnl": round(sh * (stocks[t][d] - ep[1]) - c_, 2)})
                del pos[t]
        if d in by_day:
            eq_now = cash + sum(sh * stocks[t][d] for t, (sh, ep, xd, fam) in pos.items())
            longs = sorted([r for r in by_day[d] if r["call"] == "long" and r["confidence"] >= MIN_CONF], key=lambda r: -r["confidence"])[:3]
            for r in longs:
                t, price = r["leader"], stocks[r["leader"]][d]
                if t in pos:  # already holding this name: a repeated long call extends the hold instead of buying again (the old code overwrote the position and lost the cash)
                    sh0, ep0, xd0, fam0 = pos[t]
                    pos[t] = (sh0, ep0, max(xd0, allcal[min(k + r["horizon"], len(allcal) - 1)]), fam0)
                    continue
                sh = int((eq_now / 3) / price)
                while sh >= 1:
                    v = sh * price
                    c_ = cs.one_way_cost(v * (1 + 1e-12), price, p)
                    if cash >= v + c_:
                        cash -= v + c_; fees += c_; orders += 1
                        xd = allcal[min(k + r["horizon"], len(allcal) - 1)]
                        pos[t] = (sh, (d, price), xd, r["family"])
                        break
                    sh -= 1
        eq = cash + sum(sh * stocks[t][d] for t, (sh, ep, xd, fam) in pos.items())
        equity.append((d, round(eq, 2)))
        peak = max(peak, eq); mdd = min(mdd, eq / peak - 1)
        if not pos and d > rows[-1]["exit_date"]:
            break
    # leaders basket benchmark (fractional), 21-day holds from each decision day
    bench, bv = [], a.capital
    for D in days:
        names = fd.names_at(sel, D)
        rs = []
        for fam in fd.FAMILIES:
            t = names[fam][0]
            cal = sorted(stocks[t])
            i = next(k for k, d in enumerate(cal) if d >= D)
            if i + 21 < len(cal):
                rs.append(stocks[t][cal[i + 21]] / stocks[t][cal[i]] - 1)
        if rs:
            bv *= 1 + st.mean(rs) - 0.003
            bench.append((D, round(bv, 2)))
    # random calls: same number of long calls and horizons each decision day, random families
    rnd = random.Random(5)
    finals = []
    for _ in range(300):
        v = a.capital
        for D in days:
            rr = by_day.get(D, [])
            longs = sorted([r for r in rr if r["call"] == "long" and r["confidence"] >= MIN_CONF], key=lambda r: -r["confidence"])[:3]
            if not longs:
                continue
            names = fd.names_at(sel, D)
            picks = rnd.sample(fd.FAMILIES, len(longs))
            res = []
            for fam, r in zip(picks, longs):
                t = names[fam][0]
                cal = sorted(stocks[t])
                i = next(k for k, d in enumerate(cal) if d >= D)
                if i + r["horizon"] < len(cal):
                    res.append(stocks[t][cal[i + r["horizon"]]] / stocks[t][cal[i]] - 1 - 0.003)
            if res:
                v *= 1 + sum(res) / 3          # equal slots of 1/3, unused slots stay in cash
        finals.append(v)
    finals.sort()

    def mean_of(xs):
        return round(st.mean(xs), 3) if xs else None
    longs_ = [r for r in rows if r["call"] == "long"]
    flats_ = [r for r in rows if r["call"] == "flat"]
    per_family = {}
    for fam in fd.FAMILIES:
        L = [r for r in longs_ if r["family"] == fam]
        F = [r for r in flats_ if r["family"] == fam]
        per_family[fam] = {"n_long": len(L), "n_flat": len(F), "mean_net_when_long": mean_of([r["net_pct"] for r in L]),
                           "mean_net_if_long_when_flat": mean_of([r["net_pct"] for r in F]), "mean_net_all_days": mean_of([r["net_pct"] for r in rows if r["family"] == fam]),
                           "hit_rate": round(sum(r["correct"] for r in rows if r["family"] == fam) / max(1, len([r for r in rows if r["family"] == fam])), 3)}
    summary = {"run": a.run, "decision_days": len(days), "missing": missing, "calls": len(rows), "long_calls": len(longs_), "flat_calls": len(flats_),
               "hit_rate_all": round(sum(r["correct"] for r in rows) / len(rows), 3) if rows else None,
               "mean_net_when_long": mean_of([r["net_pct"] for r in longs_]), "mean_net_if_long_when_flat": mean_of([r["net_pct"] for r in flats_]),
               "mean_net_always_long_all_calls": mean_of([r["net_pct"] for r in rows]),
               "avg_confidence_long": mean_of([r["confidence"] for r in longs_]), "avg_confidence_flat": mean_of([r["confidence"] for r in flats_]),
               "per_family": per_family,
               "portfolio": {"capital": a.capital, "final": equity[-1][1] if equity else None, "max_drawdown_pct": round(mdd * 100, 1), "fees": round(fees, 2), "orders": orders},
               "benchmarks": {"leaders_basket_final": bench[-1][1] if bench else None, "cash_final": a.capital,
                              "random_calls_final_median": round(finals[len(finals) // 2], 1), "random_calls_final_5th": round(finals[int(.05 * (len(finals) - 1))], 1),
                              "random_calls_final_95th": round(finals[int(.95 * (len(finals) - 1))], 1)},
               "note": "Validation run on 2023-2024 decision days; model memory of these years cannot be excluded; survivor bias in names."}
    cols = [k for k in rows[0] if k not in ("reasoning", "market_view", "would_change_my_mind")] + ["reasoning"]
    with open(run / "decisions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    (run / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (run / "dashboard_data.json").write_text(json.dumps({"summary": summary, "rows": rows, "equity": equity, "bench": bench, "trades": trades}, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
