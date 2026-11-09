"""Local broker-style dashboard for the paper account: account summary, watchlist with live (delayed) prices, positions, orders, trade history, equity curve, agent notes.

Run:  python -I src/dashboard_server.py            -> http://127.0.0.1:8765  (reads data/paper/ledger.json, or the DEMO ledger if there is none)
      python -I src/dashboard_server.py --cloud     -> same page, but the ledger is pulled from the cloud state branch every 2 minutes into data/paper_view/ (never touches data/paper/); prices stay live (about 15 min delayed)
      python -I src/dashboard_server.py --demo      -> writes data/paper/ledger_demo.json (clearly marked DEMO, built from real daily closes) and exits
      python -I src/dashboard_server.py --selftest  -> offline checks of the account maths
Standard library only. Prices come from `src/live_feed.py` (Yahoo, about 15 minutes delayed); the page refreshes every 30 seconds. Research and paper trading only.

Ledger v0 (JSON, written by the paper broker when it exists; the planned SQLite ledger will export the same shape):
  {"mode": "PAPER" | "DEMO", "currency": "EUR", "start_cash": 1000.0, "cash": 0.0,
   "positions": [{"symbol","name","qty","avg_price","currency","opened","exit_by","catalyst","confidence","horizon","agent"}],
   "orders": [{"id","time","symbol","side","qty","type","limit","status"}],
   "fills": [{"id","time","symbol","side","qty","price","currency","fee_eur","catalyst","agent"}],
   "equity_history": [{"date","equity"}],
   "notes": [{"time","agent","text"}]}
Prices are in the instrument currency as quoted (pence for ".L"); the dashboard converts to EUR with Yahoo FX rates (pence / 100 x GBPEUR).
"""
import csv
import datetime as dt
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import live_feed as lf  # noqa: E402

PAPER = ROOT / "data" / "paper"
LEDGER, DEMO = PAPER / "ledger.json", PAPER / "ledger_demo.json"
PAGE = ROOT / "dashboard" / "index.html"
WATCH = ("SHEL.L TTE.PA BP.L ENI.MI EQNR.OL FRES.L EDV.L IFX.DE STMPA.PA BESI.AS AZN.L NOVN.SW NOVO-B.CO SAN.PA GSK.L BAYN.DE GLEN.L RIO.L ANTO.L BOL.ST").split()
FXSYM = {"GBp": "GBPEUR=X", "CHF": "CHFEUR=X", "DKK": "DKKEUR=X", "NOK": "NOKEUR=X", "SEK": "SEKEUR=X", "PLN": "PLNEUR=X", "USD": "USDEUR=X"}
CACHE, LOCK = {}, threading.Lock()
VIEW = ROOT / "data" / "paper_view"
CLOUD = False
SYNC = {"at": None, "err": None}


def sync_loop():
    """Cloud mode: pull the ledger state from the git branch into data/paper_view/ every 2 minutes (read-only for the account; the cloud tasks are the only writers)."""
    import state_sync
    while True:
        try:
            state_sync.pull(paper=VIEW)
            SYNC["at"], SYNC["err"] = dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S"), None
        except Exception as e:  # noqa: BLE001
            SYNC["err"] = str(e)[:120]
        time.sleep(120)


def cached(key, fn, ttl=30):
    with LOCK:
        hit = CACHE.get(key)
        if hit and time.time() - hit[0] < ttl:
            return hit[1]
    val = fn()
    with LOCK:
        CACHE[key] = (time.time(), val)
    return val


def fee_eur(value_eur):
    """Reported Saxo Classic model (UNVERIFIED): 0.08% with a 2.5 EUR minimum per order."""
    return round(max(2.5, 0.0008 * value_eur), 2)


def to_eur(price, cur, fx):
    if cur == "EUR":
        return price
    r = fx.get(cur)
    return None if r is None else price * (r / 100 if cur == "GBp" else r)


def account(ledger, quotes, fx):
    """Equity, cash, per-position values and P&L in EUR from the ledger and quotes (pure function, tested)."""
    pos, mv = [], 0.0
    for p in ledger["positions"]:
        q = quotes.get(p["symbol"])
        last = q["price"] if q else None
        cur = p.get("currency", "EUR")
        val = None if last is None else to_eur(last, cur, fx)
        cost = to_eur(p["avg_price"], cur, fx)
        v_eur = None if val is None else val * p["qty"]
        c_eur = None if cost is None else cost * p["qty"]
        pnl = None if v_eur is None or c_eur is None else v_eur - c_eur
        mv += v_eur or 0.0
        pos.append(dict(p, last=last, value_eur=v_eur, cost_eur=c_eur, pnl_eur=pnl, pnl_pct=None if not c_eur or pnl is None else pnl / c_eur * 100))
    equity = ledger["cash"] + mv
    return {"positions": pos, "market_value": mv, "equity": equity, "total_pnl": equity - ledger["start_cash"], "total_pnl_pct": (equity / ledger["start_cash"] - 1) * 100}


def load_ledger():
    if CLOUD:
        f = VIEW / "ledger.json"
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    for f in (LEDGER, DEMO):
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8"))
    return None


def get_fx():
    def go():
        out = {"EUR": 1.0}
        for cur, s in FXSYM.items():
            q = lf.quote(s)
            if q:
                out[cur] = q["price"]
        return out
    return cached("fx", go, 300)


def get_quotes(symbols):
    def go():
        with ThreadPoolExecutor(6) as ex:
            res = list(ex.map(lf.quote, symbols))
        return {s: r for s, r in zip(symbols, res) if r}
    return cached("q:" + ",".join(sorted(symbols)), go, 30)


def get_bars(symbol, rng="1d"):
    return cached("b:" + symbol + rng, lambda: lf.bars(symbol, rng, "5m" if rng in ("1d", "5d") else "1d"), 60)


def spark(symbol):
    b = get_bars(symbol, "1d")
    return [round(x[4], 4) for x in b][-80:]


def state():
    ledger = load_ledger()
    if not ledger:
        return {"error": "no ledger yet: " + ("waiting for the first pull of the cloud state ({})".format(SYNC["err"] or "starting") if CLOUD else "run with --demo or start the paper broker")}
    syms = sorted(set(WATCH) | {p["symbol"] for p in ledger["positions"]})
    quotes, fx = get_quotes(syms), get_fx()
    acc = account(ledger, quotes, fx)
    with ThreadPoolExecutor(6) as ex:
        sp = dict(zip(syms, ex.map(spark, syms)))
    watch = []
    for s in syms:
        q = quotes.get(s)
        sps = sp.get(s) or []
        chg = (sps[-1] / sps[0] - 1) * 100 if len(sps) > 1 else None
        watch.append({"symbol": s, "price": q and q["price"], "currency": q and q["currency"], "age_min": q and q["age_minutes"], "change_pct": chg, "spark": sps})
    return {"mode": ledger.get("mode", "PAPER"), "now_utc": dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S"), "ledger": ledger, "account": acc, "watch": watch, "fx": fx, "synced": dict(SYNC) if CLOUD else None}


def make_demo():
    """DEMO ledger from real daily closes: two positions opened 8 trading days ago and one round trip closed 3 days ago. Illustrative only, not a result."""
    def closes(sym):
        rows = list(csv.DictReader(open(ROOT / "data" / "raw" / "eu" / "daily" / (sym + ".csv"), encoding="utf-8")))
        return [(r["date"], float(r["close"])) for r in rows if r["close"]]
    fx = get_fx()
    cur = {"SHEL.L": "GBp", "NOVN.SW": "CHF", "BOL.ST": "SEK"}
    names = {"SHEL.L": "Shell", "NOVN.SW": "Novartis", "BOL.ST": "Boliden"}
    data = {s: closes(s) for s in cur}
    cash, fills, positions, orders = 1000.0, [], [], []
    oid = 0
    for s, qty, back, cat in (("SHEL.L", 7, 8, "DEMO: oil headline example"), ("NOVN.SW", 2, 8, "DEMO: pharma headline example")):
        d, p = data[s][-back]
        v = to_eur(p, cur[s], fx) * qty
        f = fee_eur(v)
        cash -= v + f
        oid += 1
        fills.append({"id": oid, "time": d + "T08:05:00Z", "symbol": s, "side": "BUY", "qty": qty, "price": p, "currency": cur[s], "fee_eur": f, "catalyst": cat, "agent": "demo"})
        positions.append({"symbol": s, "name": names[s], "qty": qty, "avg_price": p, "currency": cur[s], "opened": d, "exit_by": data[s][-1][0], "catalyst": cat, "confidence": 0.53, "horizon": 10, "agent": "demo"})
    s, qty = "BOL.ST", 6
    (d1, p1), (d2, p2) = data[s][-9], data[s][-4]
    for side, d, p in (("BUY", d1, p1), ("SELL", d2, p2)):
        v = to_eur(p, cur[s], fx) * qty
        f = fee_eur(v)
        cash += (-v if side == "BUY" else v) - f
        oid += 1
        fills.append({"id": oid, "time": d + "T08:05:00Z", "symbol": s, "side": side, "qty": qty, "price": p, "currency": cur[s], "fee_eur": f, "catalyst": "DEMO: copper headline example", "agent": "demo"})
    orders.append({"id": oid + 1, "time": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "symbol": "IFX.DE", "side": "BUY", "qty": 5, "type": "LIMIT", "limit": 40.0, "status": "WORKING (demo)"})
    hist = [{"date": data["SHEL.L"][-i][0], "equity": round(1000 + (i % 3 - 1) * 2.0, 2)} for i in range(9, 0, -1)]
    ledger = {"mode": "DEMO", "currency": "EUR", "start_cash": 1000.0, "cash": round(cash, 2), "positions": positions, "orders": orders, "fills": sorted(fills, key=lambda x: x["time"]), "equity_history": hist,
              "notes": [{"time": data["SHEL.L"][-1][0], "agent": "demo", "text": "DEMO ledger: positions are examples built from real closes so the screen can be checked. No agent traded."}]}
    PAPER.mkdir(parents=True, exist_ok=True)
    DEMO.write_text(json.dumps(ledger, indent=1), encoding="utf-8")
    return ledger


def selftest():
    led = {"cash": 500.0, "start_cash": 1000.0, "positions": [{"symbol": "A.L", "qty": 10, "avg_price": 1000.0, "currency": "GBp"}, {"symbol": "B.DE", "qty": 2, "avg_price": 100.0, "currency": "EUR"}]}
    acc = account(led, {"A.L": {"price": 1100.0}, "B.DE": {"price": 110.0}}, {"EUR": 1.0, "GBp": 1.2})
    assert abs(acc["positions"][0]["value_eur"] - 132.0) < 1e-9 and abs(acc["positions"][0]["pnl_eur"] - 12.0) < 1e-9, acc  # 10 x 1100p = 110 GBP x 1.2
    assert abs(acc["equity"] - (500 + 132 + 220)) < 1e-9 and abs(acc["total_pnl"] - (-148.0)) < 1e-9, acc
    assert fee_eur(100) == 2.5 and fee_eur(10000) == 8.0
    print("selftest ok")


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, body, ctype="application/json", code=200):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        try:
            if u.path == "/":
                self.send(PAGE.read_bytes(), "text/html")
            elif u.path == "/api/state":
                self.send(json.dumps(state()))
            elif u.path == "/api/bars":
                q = parse_qs(u.query)
                self.send(json.dumps(get_bars(q.get("symbol", [""])[0], q.get("range", ["5d"])[0])))
            else:
                self.send("not found", "text/plain", 404)
        except Exception as e:  # noqa: BLE001
            self.send(json.dumps({"error": str(e)[:200]}), code=500)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--demo" in sys.argv:
        led = make_demo()
        print("wrote", DEMO, "cash", led["cash"])
    else:
        if "--cloud" in sys.argv:
            CLOUD = True
            threading.Thread(target=sync_loop, daemon=True).start()
            for _ in range(60):          # wait up to 60 s for the first pull
                if load_ledger() or SYNC["err"]:
                    break
                time.sleep(1)
        elif not load_ledger():
            make_demo()
        print("dashboard on http://127.0.0.1:8765  (Ctrl+C to stop)")
        ThreadingHTTPServer(("127.0.0.1", 8765), H).serve_forever()
