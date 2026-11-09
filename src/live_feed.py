"""Live (about 15 minutes delayed) prices for European stocks and ETCs from Yahoo Finance, free, no key. Research and paper trading only.

This is the price feed of the local paper broker (see `PLAN_EU.md`). Yahoo's endpoint is unofficial: it can change or throttle, so every call retries and the
caller must treat a missing quote as "no quote" (never as a price of zero). Personal research use only, within Yahoo's terms.

Functions
  bars(symbol, rng="1d", interval="5m") -> list of (utc_iso, open, high, low, close, volume), oldest first; the last bar is usually still forming
  quote(symbol) -> dict(symbol, price, currency, exchange, bar_time_utc, age_minutes, state) with price = last completed or forming 5-minute close
  snapshot(symbols, path) -> appends one JSON line per symbol to a dated file under data/live/ (forward record for later backtests; git-ignored)
Prices in pence (currency "GBp") are returned as quoted; the broker converts units, not this module.
CLI: python -I src/live_feed.py SHEL.L ASML.AS 4GLD.DE        prints a quote per symbol
     python -I src/live_feed.py --selftest                      offline parse test
"""
import datetime as dt
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIVE = ROOT / "data" / "live"
URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range={}&interval={}"


def _fetch(symbol, rng, interval):
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(URL.format(symbol, rng, interval), headers={"User-Agent": "Mozilla/5.0"}), timeout=20)
            return json.loads(r.read())["chart"]["result"][0]
        except Exception:  # noqa: BLE001
            time.sleep(1.5 * (attempt + 1))
    return None


def parse(result):
    """Turn a Yahoo chart result into (meta, bars). Bars with a missing close are dropped."""
    if not result or not result.get("timestamp"):
        return {}, []
    q = result["indicators"]["quote"][0]
    bars = [(dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i])
            for i, t in enumerate(result["timestamp"]) if q["close"][i] is not None]
    return result.get("meta", {}), bars


def bars(symbol, rng="1d", interval="5m"):
    return parse(_fetch(symbol, rng, interval))[1]


def quote(symbol, now=None):
    meta, b = parse(_fetch(symbol, "1d", "5m"))
    if not b:
        return None
    now = now or dt.datetime.now(dt.timezone.utc)
    t = dt.datetime.strptime(b[-1][0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    return {"symbol": symbol, "price": b[-1][4], "currency": meta.get("currency"), "exchange": meta.get("exchangeName"), "bar_time_utc": b[-1][0],
            "age_minutes": round((now - t).total_seconds() / 60, 1), "state": meta.get("marketState", "")}


def snapshot(symbols, path=None):
    LIVE.mkdir(parents=True, exist_ok=True)
    path = Path(path) if path else LIVE / (dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d") + ".jsonl")
    n = 0
    with open(path, "a", encoding="utf-8") as fh:
        for s in symbols:
            q = quote(s)
            if q:
                q["taken_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                fh.write(json.dumps(q) + "\n")
                n += 1
            time.sleep(0.4)
    return n


def selftest():
    fake = {"meta": {"currency": "EUR", "exchangeName": "GER"}, "timestamp": [1700000000, 1700000300], "indicators": {"quote": [{"open": [1, 2], "high": [1, 2], "low": [1, 2], "close": [1.5, None], "volume": [10, 0]}]}}
    meta, b = parse(fake)
    assert len(b) == 1 and b[0][4] == 1.5 and meta["currency"] == "EUR", b
    assert parse(None) == ({}, [])
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        for s in sys.argv[1:]:
            print(quote(s))
