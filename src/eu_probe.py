"""Probe the European candidate universe: does a free daily history exist, how long, how liquid, how volatile. Research only.

Source: Yahoo Finance chart endpoint (free, unofficial, about 15 minutes delayed live, daily history for years). No key. Terms of use are Yahoo's: personal research only.
Candidates are our own list of European-listed names per theme family (the five families of the old plan, moved to Europe) plus European-listed commodity ETCs.
Whether each is tradable at Saxo is NOT checked here (needs a Saxo account search); see `universe/EU_UNIVERSE.md`.
Usage: python -I src/eu_probe.py            -> writes data/raw/eu/daily/<TICKER>.csv (git-ignored) and universe/eu_candidates.csv
Liquidity = median daily traded value over the last 250 days, converted to EUR with Yahoo FX rates (approximate, today's rate).
"""
import csv
import datetime as dt
import json
import statistics as st
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "eu" / "daily"

# family, ticker (Yahoo symbol), name, kind
CANDS = [
    ("oil_gas", "SHEL.L", "Shell", "stock"), ("oil_gas", "TTE.PA", "TotalEnergies", "stock"), ("oil_gas", "BP.L", "BP", "stock"),
    ("oil_gas", "ENI.MI", "Eni", "stock"), ("oil_gas", "EQNR.OL", "Equinor", "stock"), ("oil_gas", "REP.MC", "Repsol", "stock"),
    ("oil_gas", "GALP.LS", "Galp", "stock"), ("oil_gas", "OMV.VI", "OMV", "stock"), ("oil_gas", "AKRBP.OL", "Aker BP", "stock"),
    ("gold_miners", "FRES.L", "Fresnillo", "stock"), ("gold_miners", "EDV.L", "Endeavour Mining", "stock"), ("gold_miners", "HOC.L", "Hochschild", "stock"),
    ("gold_miners", "CEY.L", "Centamin", "stock"), ("gold_miners", "PAF.L", "Pan African", "stock"),
    ("chips", "ASML.AS", "ASML", "stock"), ("chips", "ASM.AS", "ASM International", "stock"), ("chips", "BESI.AS", "BE Semiconductor", "stock"),
    ("chips", "IFX.DE", "Infineon", "stock"), ("chips", "STMPA.PA", "STMicroelectronics", "stock"), ("chips", "AIXA.DE", "Aixtron", "stock"),
    ("chips", "SOI.PA", "Soitec", "stock"), ("chips", "NOD.OL", "Nordic Semiconductor", "stock"), ("chips", "WAF.DE", "Siltronic", "stock"),
    ("pharma", "NOVO-B.CO", "Novo Nordisk", "stock"), ("pharma", "RO.SW", "Roche", "stock"), ("pharma", "NOVN.SW", "Novartis", "stock"),
    ("pharma", "AZN.L", "AstraZeneca", "stock"), ("pharma", "SAN.PA", "Sanofi", "stock"), ("pharma", "GSK.L", "GSK", "stock"),
    ("pharma", "BAYN.DE", "Bayer", "stock"), ("pharma", "GMAB.CO", "Genmab", "stock"), ("pharma", "ARGX.BR", "argenx", "stock"), ("pharma", "LONN.SW", "Lonza", "stock"),
    ("copper_uranium", "ANTO.L", "Antofagasta", "stock"), ("copper_uranium", "GLEN.L", "Glencore", "stock"), ("copper_uranium", "RIO.L", "Rio Tinto", "stock"),
    ("copper_uranium", "BOL.ST", "Boliden", "stock"), ("copper_uranium", "KGH.WA", "KGHM", "stock"), ("copper_uranium", "KAP.L", "Kazatomprom", "stock"),
    ("copper_uranium", "LUN.TO", "Lundin Mining (Toronto, not European: check only)", "stock"),
    ("commodity", "BRNT.L", "Brent oil ETC (LSE, USD)", "etc"), ("commodity", "CRUD.L", "WTI oil ETC (LSE, USD)", "etc"), ("commodity", "SGLD.L", "Gold ETC (LSE, USD)", "etc"),
    ("commodity", "4GLD.DE", "Xetra-Gold (Xetra, EUR)", "etc"), ("commodity", "SSLV.L", "Silver ETC (LSE, USD)", "etc"), ("commodity", "COPA.L", "Copper ETC (LSE, USD)", "etc"),
    ("commodity", "NGAS.L", "Natural gas ETC (LSE, USD)", "etc"),
]
FX = {"EUR": None, "GBp": "GBPEUR=X", "GBP": "GBPEUR=X", "USD": "USDEUR=X", "NOK": "NOKEUR=X", "SEK": "SEKEUR=X", "DKK": "DKKEUR=X", "CHF": "CHFEUR=X", "PLN": "PLNEUR=X"}


def get(sym, rng="max", itv="1d"):
    # range=max silently returns monthly bars; explicit period1/period2 with interval=1d returns true daily bars
    if rng == "max":
        u = "https://query1.finance.yahoo.com/v8/finance/chart/{}?period1=0&period2={}&interval={}".format(sym, int(time.time()), itv)
    else:
        u = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range={}&interval={}".format(sym, rng, itv)
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30)
            return json.loads(r.read())["chart"]["result"][0]
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None


def fx_rate(cur):
    if cur == "EUR":
        return 1.0
    s = FX.get(cur)
    if not s:
        return None
    d = get(s, "5d", "1d")
    if not d:
        return None
    c = [x for x in d["indicators"]["quote"][0]["close"] if x]
    r = c[-1] if c else None
    return r / 100 if cur == "GBp" and r else r


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rates, rows = {}, []
    for fam, t, name, kind in CANDS:
        d = get(t)
        time.sleep(0.5)
        if not d or not d.get("timestamp"):
            rows.append([fam, t, name, kind, "", "", "", "", "", "", "no data"])
            print(t, "no data")
            continue
        m = d["meta"]
        cur = m.get("currency", "")
        if cur not in rates:
            rates[cur] = fx_rate(cur)
        q = d["indicators"]["quote"][0]
        recs = [(dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%d"), q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i])
                for i, ts in enumerate(d["timestamp"]) if q["close"][i] is not None]
        with open(OUT / (t.replace("/", "_") + ".csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["date", "open", "high", "low", "close", "volume"])
            w.writerows(recs)
        last = recs[-250:]
        tv = [c * (v or 0) for _, _, _, _, c, v in last]
        fxr = rates.get(cur)
        med_eur = st.median(tv) * fxr if fxr and tv else None
        rets = [recs[i][4] / recs[i - 1][4] - 1 for i in range(max(1, len(recs) - 250), len(recs))]
        vol = st.pstdev(rets) * (252 ** 0.5) * 100 if len(rets) > 20 else None
        peak = max(r[4] for r in last)
        dd = (recs[-1][4] / peak - 1) * 100
        rows.append([fam, t, name, kind, m.get("exchangeName", ""), cur, recs[0][0], len(recs), round(med_eur / 1e6, 2) if med_eur else "", round(vol, 1) if vol else "", round(dd, 1), ""])
        print(t, m.get("exchangeName"), cur, recs[0][0], len(recs), "median EUR m/day", round(med_eur / 1e6, 2) if med_eur else None, "vol", round(vol, 1) if vol else None)
    with open(ROOT / "universe" / "eu_candidates.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["family", "ticker", "name", "kind", "exchange", "currency", "first_date", "days", "median_value_eur_m_per_day_250d", "volatility_pct_250d", "drawdown_from_250d_high_pct", "note"])
        w.writerows(rows)
    print("wrote universe/eu_candidates.csv", len(rows))


if __name__ == "__main__":
    main()
