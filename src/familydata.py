"""Shared data access for the family run (stocks, commodity and driver series, point-in-time names).

Prices: stocks and the sector ETFs from Yahoo (cached in data/raw/stocks_cache.json), commodity and driver series from
data/raw/commodities/*.csv (src/download_commodities.py). Names per family at a date come from universe/rule_selections.csv
(latest as-of snapshot on or before the date); the family leader is the first (highest liquidity rank) name.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import build_universe as bu  # noqa: E402

FAMILIES = ["oil_gas", "gold_miners", "chips", "pharma", "copper_uranium"]
FAMILY_LABEL = {"oil_gas": "Oil and gas producers", "gold_miners": "Gold miners", "chips": "Chips", "pharma": "Pharma", "copper_uranium": "Copper and uranium"}
DRIVERS = {
    "oil_gas": [("CL=F", "WTI crude oil"), ("BZ=F", "Brent crude oil"), ("NG=F", "Natural gas")],
    "gold_miners": [("GC=F", "Gold"), ("SI=F", "Silver"), ("^TNX", "US 10-year yield"), ("DX-Y.NYB", "US dollar index"), ("TIP", "TIPS ETF (real rates)")],
    "chips": [("SMH", "Semiconductor ETF")],
    "pharma": [("XLV", "Health care ETF")],
    "copper_uranium": [("HG=F", "Copper"), ("U-UN.TO", "Sprott uranium trust (CAD)"), ("URA", "Uranium ETF")]}
MACRO = [("^VIX", "VIX")]
COMM_DIR = ROOT / "data" / "raw" / "commodities"
CACHE = ROOT / "data" / "raw" / "stocks_cache.json"


def csv_name(sym):
    return sym.replace("^", "").replace("=", "_").replace(".", "_") + ".csv"


def load_series():
    out = {}
    for fam in list(DRIVERS) + ["macro"]:
        for sym, _ in (DRIVERS[fam] if fam in DRIVERS else MACRO):
            rows = list(csv.DictReader(open(COMM_DIR / csv_name(sym), encoding="utf-8")))
            out[sym] = {r["Date"]: float(r["Close"]) for r in rows}
    return out


def load_stocks(refresh=False):
    cands = [r["ticker"] for r in csv.DictReader(open(ROOT / "universe" / "candidates.csv", encoding="utf-8"))]
    if CACHE.exists() and not refresh:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    data = {}
    for t in cands:
        try:
            _, b = bu.fetch(t, "10y")
            data[t] = {x[0]: x[1] for x in b}
        except Exception:  # noqa: BLE001
            pass
    CACHE.write_text(json.dumps(data), encoding="utf-8")
    return data


def selections():
    sel = {}
    for r in csv.DictReader(open(ROOT / "universe" / "rule_selections.csv", encoding="utf-8")):
        sel.setdefault(r["asof"], {}).setdefault(r["family"], []).append((int(r["rank"]), r["ticker"]))
    return {a: {f: [t for _, t in sorted(v)] for f, v in fams.items()} for a, fams in sel.items()}


def names_at(sel, day):
    ok = [a for a in sel if a <= day]
    snap = sel[max(ok)] if ok else sel[min(sel)]
    return snap          # {family: [ticker, ...]} first is the leader
