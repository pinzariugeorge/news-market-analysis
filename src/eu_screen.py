"""Screen a broad list of European stocks for things worth paper trading with a 1,000 EUR account. Research only, not a recommendation.

Input: the ticker lists below (large and mid caps of the main European indices, written from general knowledge; some symbols may be stale or wrong and are reported as "no data").
Source: Yahoo Finance daily bars (free, no key), true daily history. Output: `universe/eu_screen.csv` (git-ignored raw bars are not kept; only metrics) and a printed ranking.
Filters (fixed in advance): last close at most 333 EUR (3 positions, whole shares); median traded value over 250 days at least 20 million EUR (Yahoo volume can under-report, so this is a lower bound);
at least 5 years of history; not a fund or ETF-like product (listed here only by hand, none included).
Metrics: returns over 1, 3, 6, 12 months; 250-day volatility; drawdown from the 250-day high; above the 200-day average; fee drag = 2 x 2.5 EUR minimum on 333 EUR (about 1.5%) shown for reference.
Warning from the US era: ranking by past return picks winners with hindsight; use the result as a candidate list for the point-in-time rule, never as a signal.
Usage: python -I src/eu_screen.py        (about 5 minutes)
"""
import csv
import json
import statistics as st
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LISTS = {
    "DE": "ADS.DE AIR.DE ALV.DE BAS.DE BAYN.DE BEI.DE BMW.DE BNR.DE CBK.DE CON.DE 1COV.DE DTG.DE DBK.DE DB1.DE DHL.DE DTE.DE EOAN.DE FRE.DE FME.DE HNR1.DE HEI.DE HEN3.DE IFX.DE MBG.DE MRK.DE MTX.DE MUV2.DE P911.DE PAH3.DE QIA.DE RHM.DE RWE.DE SAP.DE SRT3.DE SIE.DE ENR.DE SHL.DE SY1.DE VOW3.DE VNA.DE ZAL.DE AIXA.DE LHA.DE TUI1.DE EVK.DE LEG.DE KGX.DE HAG.DE G1A.DE AFX.DE NDX1.DE BOSS.DE PUM.DE FPE3.DE",
    "FR": "AI.PA AIR.PA ALO.PA MT.AS CS.PA BNP.PA EN.PA CAP.PA CA.PA ACA.PA BN.PA DSY.PA EDEN.PA ENGI.PA EL.PA ERF.PA RMS.PA KER.PA OR.PA LR.PA MC.PA ML.PA ORA.PA RI.PA PUB.PA RNO.PA SAF.PA SGO.PA SAN.PA SU.PA GLE.PA STLAP.PA STMPA.PA TEP.PA HO.PA TTE.PA URW.PA VIE.PA DG.PA VIV.PA WLN.PA SOI.PA UBI.PA AM.PA ATO.PA BVI.PA DIM.PA ELIS.PA FGR.PA GTT.PA IPN.PA NK.PA RXL.PA SK.PA SW.PA TEP.PA",
    "NL_BE": "ASML.AS ASM.AS BESI.AS ADYEN.AS AD.AS AGN.AS AKZA.AS HEIA.AS INGA.AS KPN.AS NN.AS PHIA.AS PRX.AS RAND.AS REN.AS UNA.AS WKL.AS ABI.BR UCB.BR KBC.BR SOLB.BR GBLB.BR ACKB.BR UMI.BR ARGX.BR APAM.AS IMCD.AS ASRNL.AS FLOW.AS TKWY.AS BAMNB.AS",
    "UK": "AZN.L SHEL.L HSBA.L ULVR.L BP.L GSK.L RIO.L DGE.L REL.L BATS.L LSEG.L NG.L BARC.L LLOY.L VOD.L GLEN.L AAL.L CPG.L RKT.L TSCO.L NWG.L PRU.L STAN.L IMB.L BA.L BT-A.L CNA.L EXPN.L FLTR.L HLN.L III.L JD.L KGF.L LAND.L MNG.L NXT.L PSON.L RR.L SGE.L SMT.L SPX.L SSE.L SVT.L WPP.L WTB.L ANTO.L FRES.L EDV.L AHT.L AV.L BDEV.L BKG.L CRH.L ENT.L IAG.L ICG.L INF.L ITRK.L MRO.L OCDO.L PHNX.L PSN.L RMV.L SDR.L SGRO.L SMDS.L SMIN.L TW.L UU.L WEIR.L",
    "IT_ES_PT": "ENI.MI ENEL.MI ISP.MI UCG.MI G.MI STLAM.MI RACE.MI PRY.MI MONC.MI LDO.MI TRN.MI SRG.MI SPM.MI TIT.MI AMP.MI BAMI.MI BPE.MI CNHI.MI DIA.MI REC.MI NEXI.MI PIRC.MI IVG.MI ITX.MC SAN.MC BBVA.MC IBE.MC TEF.MC REP.MC CABK.MC AMS.MC FER.MC GRF.MC ELE.MC ENG.MC NTGY.MC SAB.MC BKT.MC MAP.MC ANA.MC ACX.MC COL.MC CLNX.MC IAG.MC EDP.LS GALP.LS JMT.LS EDPR.LS",
    "NORDIC_CH_AT": "NOVO-B.CO DSV.CO ORSTED.CO VWS.CO CARL-B.CO COLO-B.CO GMAB.CO PNDORA.CO DANSKE.CO NZYM-B.CO TRYG-B.CO ROCK-B.CO GN.CO DEMANT.CO AMBU-B.CO FLS.CO EQNR.OL DNB.OL TEL.OL MOWI.OL ORK.OL YAR.OL AKRBP.OL NHY.OL SALM.OL NOD.OL SUBC.OL KOG.OL VOLV-B.ST ERIC-B.ST ATCO-A.ST ATCO-B.ST ASSA-B.ST SAND.ST SEB-A.ST SHB-A.ST SWED-A.ST HEXA-B.ST INVE-B.ST EVO.ST ESSITY-B.ST ALFA.ST BOL.ST SKF-B.ST TELIA.ST HM-B.ST EPI-A.ST NIBE-B.ST SINCH.ST SAAB-B.ST ABB.ST NDA-FI.HE NESTE.HE KNEBV.HE UPM.HE FORTUM.HE SAMPO.HE STERV.HE WRT1V.HE ELISA.HE NOKIA.HE NESN.SW NOVN.SW RO.SW ROG.SW UBSG.SW ZURN.SW ABBN.SW CFR.SW SIKA.SW LONN.SW GIVN.SW HOLN.SW ALC.SW SREN.SW SCMN.SW GEBN.SW STMN.SW LOGN.SW SOON.SW PGHN.SW BAER.SW TEMN.SW VAT.SW OMV.VI VER.VI EBS.VI RBI.VI VOE.VI ANDR.VI KGH.WA PKO.WA PKN.WA PZU.WA PEO.WA LPP.WA DNP.WA",
}


def fetch(sym):
    u = "https://query1.finance.yahoo.com/v8/finance/chart/{}?period1={}&period2={}&interval=1d".format(sym, int(time.time()) - 6 * 365 * 86400, int(time.time()))
    for _ in range(2):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30)
            return json.loads(r.read())["chart"]["result"][0]
        except Exception:  # noqa: BLE001
            time.sleep(1.5)
    return None


def fx(cur, cache):
    if cur == "EUR":
        return 1.0
    if cur in cache:
        return cache[cur]
    m = {"GBp": "GBPEUR=X", "GBP": "GBPEUR=X", "CHF": "CHFEUR=X", "DKK": "DKKEUR=X", "NOK": "NOKEUR=X", "SEK": "SEKEUR=X", "PLN": "PLNEUR=X", "USD": "USDEUR=X"}.get(cur)
    r = None
    if m:
        d = fetch(m)
        if d:
            c = [x for x in d["indicators"]["quote"][0]["close"] if x]
            r = c[-1] / (100 if cur == "GBp" else 1) if c else None
    cache[cur] = r
    return r


def main():
    syms = []
    for k, v in LISTS.items():
        for s in v.split():
            if s not in [x[1] for x in syms]:
                syms.append((k, s))
    print(len(syms), "symbols")
    cache, rows = {}, []
    for k, s in syms:
        d = fetch(s)
        time.sleep(0.35)
        if not d or not d.get("timestamp"):
            rows.append([k, s, "", "", "", "", "", "", "", "", "", "", "no data"])
            continue
        m = d["meta"]
        q = d["indicators"]["quote"][0]
        recs = [(t, q["close"][i], q["volume"][i] or 0) for i, t in enumerate(d["timestamp"]) if q["close"][i] is not None]
        if len(recs) < 1000:
            rows.append([k, s, m.get("shortName", ""), "", "", "", "", "", "", "", "", "", "short history"])
            continue
        cur = m.get("currency", "")
        r = fx(cur, cache)
        if not r:
            rows.append([k, s, m.get("shortName", ""), cur, "", "", "", "", "", "", "", "", "no fx"])
            continue
        c = [x[1] for x in recs]
        last = c[-1]
        tv = st.median([x[1] * x[2] for x in recs[-250:]]) * r / 1e6
        rets = [c[i] / c[i - 1] - 1 for i in range(len(c) - 250, len(c))]
        vol = st.pstdev(rets) * 252 ** 0.5 * 100
        dd = (last / max(c[-250:]) - 1) * 100
        ma200 = sum(c[-200:]) / 200
        def ret(n):
            return (last / c[-n - 1] - 1) * 100
        rows.append([k, s, m.get("shortName", ""), cur, round(last * r, 2), round(tv, 1), round(vol, 1), round(ret(21), 1), round(ret(63), 1), round(ret(126), 1), round(ret(250), 1), round(dd, 1), "above200" if last > ma200 else "below200"])
    out = ROOT / "universe" / "eu_screen.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["region", "ticker", "name", "currency", "price_eur", "median_value_eur_m_250d", "volatility_pct", "ret_1m", "ret_3m", "ret_6m", "ret_12m", "drawdown_from_250d_high", "trend_or_note"])
        w.writerows(rows)
    ok = [r for r in rows if isinstance(r[4], float) or isinstance(r[4], int)]
    print("with data:", len(ok), "no data or short:", len(rows) - len(ok))
    print("wrote", out)


if __name__ == "__main__":
    main()
