"""Builds the end-of-day report as ONE self-contained, phone-friendly HTML page (no network, no scripts), for upload to Claude cloud and for reading or discussing on a phone.

Usage: python -I src/eu_report.py --snapshot      writes data/paper/reports/snapshot.html (small always-current account page for Claude cloud)
       python -I src/eu_report.py [YYYY-MM-DD]   -> data/paper/reports/<date>.html and data/paper/reports/latest.html (same content)
Inputs (all optional; a missing one becomes a short "not available" line, never an error): ledger, day report JSON from `eu_cycle.py close`, reviewer output JSON (report, questions),
trader decision JSON, researcher brief, day state and warnings. Paper money, research only, not advice.
"""
import datetime as dt
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import paper_broker as pb  # noqa: E402

PAPER = pb.PAPER


def rj(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def e(x):
    return html.escape(str(x if x is not None else ""))


def money(x, sign=False):
    return ("{:+,.2f}" if sign else "{:,.2f}").format(x)


def spark(vals, w=300, h=70):
    if len(vals) < 2:
        return '<p class="mute">The equity curve appears after the second trading day.</p>'
    mn, mx = min(vals), max(vals)
    r = (mx - mn) or 1
    pts = " ".join("{:.1f},{:.1f}".format(i / (len(vals) - 1) * w, 6 + (1 - (v - mn) / r) * (h - 12)) for i, v in enumerate(vals))
    return '<svg viewBox="0 0 {} {}" width="100%" height="{}" role="img" aria-label="Equity curve"><polyline fill="none" stroke="var(--accent)" stroke-width="2" points="{}"/></svg>'.format(w, h, h, pts)


def build(d):
    ds = d.isoformat()
    led = pb.load()
    rep = rj(PAPER / "reports" / (ds + ".json")) or {}
    rv = rj(PAPER / "run" / ds / "reviewer_output.json") or {}
    dec = rj(PAPER / "run" / ds / "trader_decision.json") or {}
    brief = (PAPER / "run" / ds / "brief.md")
    brief = brief.read_text(encoding="utf-8") if brief.exists() else ""
    st = rj(PAPER / "state" / (ds + ".json")) or {"steps": {}, "warnings": []}
    eq = rep.get("equity") or (led["equity_history"][-1]["equity"] if led["equity_history"] else led["start_cash"])
    day_pct, day_eur = rep.get("day_pnl_pct", 0.0), rep.get("day_pnl_eur", 0.0)
    tot_pct = rep.get("total_pnl_pct", (eq / led["start_cash"] - 1) * 100)
    fills = [f for f in led["fills"] if f["time"][:10] == ds]
    orders = [o for o in led["orders"] if o["time"][:10] == ds]
    cls = lambda v: "up" if v > 0 else "down" if v < 0 else ""  # noqa: E731
    P = []
    P.append('<section class="hero"><div class="l">Equity (EUR, paper)</div><div class="big">{}</div><div class="row"><span class="{}">Today {} ({:+.2f}%)</span><span class="{}">Total {:+.2f}%</span></div><div class="mute">Cash {} - started with {}</div></section>'.format(
        money(eq), cls(day_eur), money(day_eur, True), day_pct, cls(tot_pct), tot_pct, money(led["cash"]), money(led["start_cash"])))
    P.append("<section><h2>What happened today</h2><p>{}</p></section>".format(e(rv.get("report") or "The reviewer has not written today's conclusion yet. Figures below come straight from the ledger.")))
    qs = rv.get("questions") or []
    if qs:
        P.append("<section><h2>Questions to talk through</h2><ol>{}</ol></section>".format("".join("<li>{}</li>".format(e(q)) for q in qs)))
    if dec:
        P.append("<section><h2>The trader's view this morning</h2><p>{}</p><p class=\"mute\">Would change its mind if: {}</p></section>".format(e(dec.get("market_view", "")), e(dec.get("would_change_my_mind", ""))))
        rows = "".join("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(e(t), e(v.get("action")), e(v.get("symbol") or "-"), e(v.get("confidence"))) for t, v in dec.get("themes", {}).items())
        P.append('<section><h2>Theme calls</h2><div class="tw"><table><tr><th>Theme</th><th>Call</th><th>Name</th><th>Conf.</th></tr>{}</table></div></section>'.format(rows))
    if orders or fills:
        rows = "".join("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(e(o["time"][11:16]), e(o["side"]), e(o["symbol"]), o["qty"], e(o["status"] + (" - " + "; ".join(o.get("reasons", [])) if o.get("reasons") else ""))) for o in orders)
        P.append('<section><h2>Orders</h2><table><tr><th>UTC</th><th>Side</th><th>Name</th><th>Qty</th><th>Status</th></tr>{}</table></section>'.format(rows))
        rows = "".join("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(e(f["time"][11:16]), e(f["side"]), e(f["symbol"]), "{} @ {:.2f} {}".format(f["qty"], f["price"], f["currency"]), money(f["fee_eur"])) for f in fills)
        if rows:
            P.append('<section><h2>Fills</h2><table><tr><th>UTC</th><th>Side</th><th>Name</th><th>Qty @ price</th><th>Costs EUR</th></tr>{}</table></section>'.format(rows))
    else:
        P.append("<section><h2>Trades</h2><p>No orders today.</p></section>")
    if led["positions"]:
        rows = "".join("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(e(p["symbol"]), p["qty"], e(p["exit_by"]), e(str(p.get("catalyst", ""))[:90])) for p in led["positions"])
        P.append('<section><h2>Open positions</h2><table><tr><th>Name</th><th>Qty</th><th>Exit by</th><th>Catalyst quoted</th></tr>{}</table></section>'.format(rows))
    else:
        P.append("<section><h2>Open positions</h2><p>None (all cash).</p></section>")
    P.append("<section><h2>Equity</h2>{}</section>".format(spark([h["equity"] for h in led["equity_history"]])))
    if brief:
        P.append("<section><h2>Research brief (short)</h2><pre>{}</pre></section>".format(e(brief[:2600] + ("..." if len(brief) > 2600 else ""))))
    lessons = (rv.get("handoff") or {}).get("lessons") or []
    P.append("<section><h2>Lessons ledger</h2>{}</section>".format("<ul>{}</ul>".format("".join("<li>({} cases) {}</li>".format(x.get("cases"), e(x.get("rule"))) for x in lessons)) if lessons else "<p>Empty: a lesson needs at least 5 closed trades before it may change a call.</p>"))
    steps = "".join("<li>{} {} {}</li>".format(e(k), "ok" if v["ok"] else "FAILED", e(v.get("note", ""))) for k, v in st["steps"].items())
    warns = "".join("<li>{}</li>".format(e(w)) for w in st["warnings"])
    P.append("<section><h2>System health</h2><ul>{}{}</ul><p class=\"mute\">Reconcile: {}. Prices delayed about 15 minutes. Costs use unverified Saxo-style fees.</p></section>".format(steps, warns, e(rep.get("reconcile", "not run yet"))))
    css = (":root{--bg:#f6f7f9;--card:#fff;--ink:#16181d;--mute:#667085;--line:#e4e7ec;--up:#0a7f4f;--down:#c42b2b;--accent:#2457d6}"
           "@media (prefers-color-scheme:dark){:root:not([data-theme=\"light\"]){--bg:#0f1115;--card:#171a21;--ink:#e8eaee;--mute:#8b93a1;--line:#272c36;--up:#3fb97f;--down:#ef6b6b;--accent:#6c93ff;color-scheme:dark}}"
           ":root[data-theme=\"dark\"]{--bg:#0f1115;--card:#171a21;--ink:#e8eaee;--mute:#8b93a1;--line:#272c36;--up:#3fb97f;--down:#ef6b6b;--accent:#6c93ff;color-scheme:dark}"
           "*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;padding-block:8px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}"
           "main{max-width:720px;margin:0 auto}h1{font-size:20px;margin:8px 0 2px;text-wrap:balance}h2{font-size:15px;margin:0 0 8px}"
           "section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin:12px 0;min-width:0}.hero .big{font-size:34px;font-weight:700;font-variant-numeric:tabular-nums}"
           ".l,.mute{color:var(--mute);font-size:13px}.row{display:flex;gap:16px;flex-wrap:wrap;font-weight:600}.up{color:var(--up)}.down{color:var(--down)}"
           ".tw{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums}th,td{text-align:left;padding:6px 4px;border-bottom:1px solid var(--line);vertical-align:top}pre{white-space:pre-wrap;font:13px/1.45 inherit;margin:0}ul,ol{margin:0;padding-left:20px}"
           "button{font:inherit;padding:10px 14px;border-radius:10px;border:1px solid var(--accent);background:var(--card);color:var(--accent);cursor:pointer}button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}")
    summary = "Paper trading day {}. Equity {} EUR (today {} EUR, {:+.2f} percent; total {:+.2f} percent). {} Questions: {}".format(
        ds, money(eq), money(day_eur, True), day_pct, tot_pct, rv.get("report") or "No conclusion written yet.", " ".join("{}. {}".format(i + 1, q) for i, q in enumerate(qs)) or "none")
    P.insert(1, '<section><button id="cp" type="button">Copy summary for a voice chat</button> <span id="cpm" class="mute"></span><textarea id="sm" hidden>{}</textarea></section>'.format(e(summary)))
    js = ("<script>document.getElementById('cp').onclick=function(){var t=document.getElementById('sm').value,m=document.getElementById('cpm');"
          "function ok(){m.textContent='Copied. Paste it into a Claude chat, then start voice.'}function no(){m.textContent='Could not copy: select the text below instead.';var a=document.getElementById('sm');a.hidden=false;a.select()}"
          "try{navigator.clipboard.writeText(t).then(ok,no)}catch(x){no()}}</script>")
    body = "<main><h1>Paper trading day {}</h1><div class=\"mute\">European stocks, 1,000 EUR paper account, Opus with learning. Research only, not advice.</div>{}</main>{}".format(e(ds), "".join(P), js)
    return css, body


def page(d, artifact=False):
    css, body = build(d)
    if artifact:   # the Artifact tool wraps the file in its own skeleton: no doctype, html, head or body tags
        return '<title>Paper Trading Day</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<style>{}</style>\n{}'.format(css, body)
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Paper Trading Day</title><style>{}</style></head><body>{}</body></html>'.format(css, body)


SNAP_CSS = (":root{--bg:#f6f7f9;--card:#fff;--ink:#16181d;--mute:#667085;--line:#e4e7ec;--up:#0a7f4f;--down:#c42b2b}"
            "@media (prefers-color-scheme:dark){:root:not([data-theme=\"light\"]){--bg:#0f1115;--card:#171a21;--ink:#e8eaee;--mute:#8b93a1;--line:#272c36;--up:#3fb97f;--down:#ef6b6b;color-scheme:dark}}"
            ":root[data-theme=\"dark\"]{--bg:#0f1115;--card:#171a21;--ink:#e8eaee;--mute:#8b93a1;--line:#272c36;--up:#3fb97f;--down:#ef6b6b;color-scheme:dark}"
            "*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;padding-block:8px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}"
            "main{max-width:560px;margin:0 auto}.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin:10px 0;min-width:0}"
            ".big{font-size:36px;font-weight:700;font-variant-numeric:tabular-nums}.row{display:flex;gap:16px;flex-wrap:wrap;font-weight:600}.mute{color:var(--mute);font-size:13px}.up{color:var(--up)}.down{color:var(--down)}"
            "h2{font-size:14px;margin:0 0 6px;color:var(--mute);font-weight:600}.tw{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums}th,td{text-align:left;padding:5px 4px;border-bottom:1px solid var(--line)}")


def snapshot(now=None):
    """Tiny always-current account page (balance, today, positions, pending orders, today's fills), published to Claude cloud after every scheduled run. Prices are the delayed quotes of the run."""
    import eu_cycle
    now = now or pb.utc_now()
    d = now.date()
    led = pb.load()
    fx = pb.get_fx()
    eq = pb.equity_now(led, fx)
    prev = pb.equity_on(led, d)
    day_eur, day_pct = eq - prev, (eq / prev - 1) * 100
    tot_pct = (eq / led["start_cash"] - 1) * 100
    cls = lambda v: "up" if v > 0.004 else "down" if v < -0.004 else ""  # noqa: E731
    try:
        line = eu_cycle.summary(now)
    except Exception:  # noqa: BLE001
        line = ""
    rows = ""
    for p in led["positions"]:
        q = pb.get_quote(p["symbol"])
        last = pb.to_eur(q["price"], p["currency"], fx) if q else None
        cost = pb.to_eur(p["avg_price"], p["currency"], fx)
        pnl = (last - cost) * p["qty"] if last else None
        rows += "<tr><td>{}</td><td>{}</td><td>{:.2f}</td><td>{}</td><td class=\"{}\">{}</td></tr>".format(
            e(p["symbol"]), p["qty"], cost, "{:.2f}".format(last) if last else "-", cls(pnl or 0), "{:+.2f}".format(pnl) if pnl is not None else "-")
    pend = [o for o in led["orders"] if o["status"] == "ACCEPTED"]
    fills = [x for x in led["fills"] if x["time"][:10] == d.isoformat()]
    body = ('<main><div class="card"><div class="mute">Paper account, EUR - updated {} UTC</div><div class="big">{:,.2f}</div>'
            '<div class="row"><span class="{}">Today {:+.2f} ({:+.2f}%)</span><span class="{}">Total {:+.2f}%</span></div><div class="mute">Cash {:,.2f}</div></div>').format(
        now.strftime("%H:%M"), eq, cls(day_eur), day_eur, day_pct, cls(tot_pct), tot_pct, led["cash"])
    body += ('<div class="card"><h2>Positions</h2>{}</div>'.format('<div class="tw"><table><tr><th>Name</th><th>Qty</th><th>Entry EUR</th><th>Now EUR</th><th>P&amp;L EUR</th></tr>' + rows + "</table></div>") if rows else '<div class="card"><h2>Positions</h2>None, all cash.</div>')
    body += '<div class="card"><h2>Orders waiting</h2>{}</div>'.format(e(", ".join("{} {} x {}".format(o["side"], o["qty"], o["symbol"]) for o in pend)) or "None")
    body += '<div class="card"><h2>Today\'s fills</h2>{}</div>'.format(e("; ".join("{} {} x {} @ {:.2f}".format(x["side"], x["qty"], x["symbol"], x["price"]) for x in fills)) or "None")
    if line:
        body += '<div class="card mute">{}</div>'.format(e(line))
    body += '<div class="mute">Prices delayed about 15 minutes. Paper money, research only.</div></main>'
    return '<title>Account Snapshot</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<style>{}</style>\n{}'.format(SNAP_CSS, body)


def main():
    if "--snapshot" in sys.argv:
        out = PAPER / "reports"
        out.mkdir(parents=True, exist_ok=True)
        try:
            import eu_overview    # all accounts on one page (main + labs); falls back to the main-only page if the other branches cannot be read
            s = eu_overview.build()
        except Exception as ex:  # noqa: BLE001
            print("overview failed, writing the main-only snapshot:", str(ex)[:80])
            s = snapshot()
        (out / "snapshot.html").write_text(s, encoding="utf-8")
        print(out / "snapshot.html", len(s), "bytes")
        return
    d = dt.date.fromisoformat([a for a in sys.argv[1:] if not a.startswith("--")][0]) if [a for a in sys.argv[1:] if not a.startswith("--")] else pb.utc_now().date()
    out = PAPER / "reports"
    out.mkdir(parents=True, exist_ok=True)
    h = page(d)
    (out / (d.isoformat() + ".html")).write_text(h, encoding="utf-8")
    (out / "latest.html").write_text(h, encoding="utf-8")
    a = page(d, artifact=True)   # same page without the document skeleton, for publishing to Claude cloud
    (out / "artifact.html").write_text(a, encoding="utf-8")
    print(out / "artifact.html", len(a), "bytes")


if __name__ == "__main__":
    main()
