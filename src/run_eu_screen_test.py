"""Mechanical screens on European stocks, as pre-registered in PREREG_SCREEN.md. Standard library only.
Run: python -I src\run_eu_screen_test.py [--test]   (--test also evaluates the untouched 2022+ period for configs that passed build+validation)
Writes results/EU_SCREEN_TEST.md. Research only."""
import csv
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data" / "raw" / "eu" / "daily"
ETC = {"4GLD.DE", "BRNT.L", "COPA.L", "CRUD.L", "NGAS.L", "SGLD.L", "SSLV.L"}
COST = float(sys.argv[sys.argv.index("--cost") + 1]) if "--cost" in sys.argv else 1.5  # percent round trip
HS = (10, 20)
PERIODS = {"build": (2003, 2014), "validation": (2015, 2021), "test": (2022, 2026)}


def load(path):
    rows = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        try:
            o, c, v = float(r["open"]), float(r["close"]), float(r["volume"] or 0)
        except (ValueError, KeyError):
            continue
        if o > 0 and c > 0:
            rows.append((r["date"], o, c, v))
    return rows


def period_of(date):
    y = int(date[:4])
    for k, (a, b) in PERIODS.items():
        if a <= y <= b:
            return k
    return None


def main():
    do_test = "--test" in sys.argv
    stocks = {}
    for p in sorted(D.glob("*.csv")):
        t = p.stem
        if t in ETC:
            continue
        rows = load(p)
        if len(rows) > 400:
            stocks[t] = rows
    # per stock candidate list: (entry_date, H) -> forward return; features at signal day
    recs = {H: [] for H in HS}  # (ticker, idx, entry_date, ret_pct, flags dict)
    day_sum = {H: defaultdict(float) for H in HS}
    day_cnt = {H: defaultdict(int) for H in HS}
    for t, rows in stocks.items():
        n = len(rows)
        cl = [r[2] for r in rows]
        vo = [r[3] for r in rows]
        # rolling sums
        pre = [0.0]
        for x in cl:
            pre.append(pre[-1] + x)
        vpre = [0.0]
        for x in vo:
            vpre.append(vpre[-1] + x)
        for H in HS:
            for i in range(200, n - H - 1):
                entry = rows[i + 1][1]
                ex = rows[i + 1 + H][2]
                r = (ex / entry - 1) * 100
                if abs(r) > 100:
                    continue
                ed = rows[i + 1][0]
                day_sum[H][ed] += r
                day_cnt[H][ed] += 1
                ma = (pre[i + 1] - pre[i - 199]) / 200
                v20 = (vpre[i] - vpre[i - 20]) / 20
                up = cl[i] > ma
                vshock = v20 > 0 and vo[i] >= 2 * v20
                r1 = (cl[i] / cl[i - 1] - 1) * 100
                r3 = (cl[i] / cl[i - 3] - 1) * 100
                recs[H].append((t, i, ed, r, {"TREND": up, "S1": up and vshock and r1 >= 2, "S2": up and r3 <= -5, "S3": up and vshock and r1 <= -4}))
    out = ["# EU mechanical screen test (pre-registered in PREREG_SCREEN.md)", "", "Cost {}% round trip; excess = event return minus mean return of all stocks entering the same day; t clustered by entry month; survivor bias, local currency.".format(COST), ""]
    results = {}
    random.seed(7)
    for H in HS:
        # excess for every record
        ex_all = []
        for (t, i, ed, r, fl) in recs[H]:
            m = (day_sum[H][ed] - r) / (day_cnt[H][ed] - 1) if day_cnt[H][ed] > 1 else r
            ex_all.append(r - m)
        pools = defaultdict(list)  # period -> excess of trend-eligible records (for random draws)
        for rec, e in zip(recs[H], ex_all):
            p = period_of(rec[2])
            if p:
                pools[p].append(e)
        for name in ("TREND", "S1", "S2", "S3"):
            for per in ("build", "validation", "test"):
                if per == "test" and not do_test:
                    continue
                last = {}
                ev = []  # (month, excess)
                dates = set()
                for rec, e in zip(recs[H], ex_all):
                    t, i, ed, r, fl = rec
                    if period_of(ed) != per or not fl[name]:
                        continue
                    if t in last and i < last[t]:
                        continue
                    last[t] = i + 1 + H
                    ev.append((ed[:7], e))
                    dates.add(ed)
                results[(name, H, per)] = (ev, dates)
    # report
    def stats(ev):
        if not ev:
            return None
        xs = [e for _, e in ev]
        n = len(xs)
        mean = sum(xs) / n
        g = defaultdict(float)
        for m, e in ev:
            g[m] += e - mean
        G = len(g)
        se = math.sqrt(sum(v * v for v in g.values()) * (G / max(G - 1, 1))) / n if n else float("nan")
        return n, mean, (mean - COST) / se if se > 0 else float("nan"), sum(1 for x in xs if x - COST > 0) / n

    # random baseline per period pooled build+validation
    def rand95(H, n):
        pool = pools_cache[H]["build"] + pools_cache[H]["validation"]
        means = sorted(sum(random.choice(pool) for _ in range(n)) / n for _ in range(1000))
        return means[949]

    pools_cache = {}
    for H in HS:
        pc = defaultdict(list)
        for rec in recs[H]:
            pass
        pools_cache[H] = pc
    for H in HS:
        ex_all = []
        for (t, i, ed, r, fl) in recs[H]:
            m = (day_sum[H][ed] - r) / (day_cnt[H][ed] - 1) if day_cnt[H][ed] > 1 else r
            ex_all.append(r - m)
        for rec, e in zip(recs[H], ex_all):
            p = period_of(rec[2])
            if p:
                pools_cache[H][p].append(e)
        sd_all = math.sqrt(sum(x * x for x in ex_all) / len(ex_all))
        out.append("## Horizon {} days (all-stock excess sd {:.1f}%)".format(H, sd_all))
        out.append("")
        out.append("| screen | period | events | dates | mean excess % (gross) | net of cost | t (net, clustered) | share net>0 |")
        out.append("|---|---|---|---|---|---|---|---|")
        for name in ("TREND", "S1", "S2", "S3"):
            for per in ("build", "validation") + (("test",) if do_test else ()):
                ev, dates = results[(name, H, per)]
                s = stats(ev)
                if not s:
                    out.append("| {} | {} | 0 | 0 | | | | |".format(name, per))
                    continue
                out.append("| {} | {} | {} | {} | {:+.2f} | {:+.2f} | {:.2f} | {:.0%} |".format(name, per, s[0], len(dates), s[1], s[1] - COST, s[2], s[3]))
        out.append("")
        out.append("Pass check (build+validation pooled, screens S1-S3):")
        for name in ("S1", "S2", "S3"):
            b, v = results[(name, H, "build")], results[(name, H, "validation")]
            sb, sv = stats(b[0]), stats(v[0])
            pooled = b[0] + v[0]
            sp = stats(pooled)
            if not (sb and sv and sp):
                out.append("- {}: not enough events -> FAIL".format(name))
                continue
            r95 = rand95(H, sp[0])
            checks = [sb[1] - COST > 0, sv[1] - COST > 0, sb[0] >= 100 and len(b[1]) >= 50 and sv[0] >= 100 and len(v[1]) >= 50, sp[2] >= 2, sp[1] > r95]
            out.append("- {}: net>0 build {} / val {}; n>=100 & 50 dates {}; t {:.2f} (>=2 {}); mean {:+.2f} vs random p95 {:+.2f} ({}) -> **{}**".format(
                name, checks[0], checks[1], checks[2], sp[2], checks[3], sp[1], r95, checks[4], "PASS" if all(checks) else "FAIL"))
        out.append("")
    # power
    out.append("## Power: independent events needed to detect a net edge at t = 2")
    out.append("")
    out.append("| horizon | sd of one event (%) | edge 1% | edge 2% | edge 3% |")
    out.append("|---|---|---|---|---|")
    for H in HS:
        xs = []
        for name in ("S1", "S2", "S3"):
            for per in ("build", "validation"):
                xs += [e for _, e in results[(name, H, per)][0]]
        sd = math.sqrt(sum((x - sum(xs) / len(xs)) ** 2 for x in xs) / len(xs)) if xs else float("nan")
        out.append("| {} | {:.1f} | {:.0f} | {:.0f} | {:.0f} |".format(H, sd, (2 * sd / 1) ** 2, (2 * sd / 2) ** 2, (2 * sd / 3) ** 2))
    out.append("")
    out.append("The main account closes a few trades a month (about 4 to 8 at most with 3 positions and 10-20 day holds), so 30 trades cover a net edge of roughly 4% a trade at best: a pass bar of 30 trades cannot show a normal edge. Scoring every name every day (hundreds of calls a month, no fees) is the route to power; events cluster in time, so the real sample is smaller than the count.")
    text = "\n".join(out)
    (ROOT / "results" / ("EU_SCREEN_TEST.md" if COST == 1.5 else "EU_SCREEN_TEST_cost{}.md".format(COST))).write_text(text + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
