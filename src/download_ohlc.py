"""Download daily OHLCV for a wide list of US-listed single stocks (and a few index series for regime filters) from Yahoo's public chart endpoint.

Usage: python -I src/download_ohlc.py [--long]   (--long: history from 2003 into data/raw/ohlc_long, for crisis-period tests)
Writes data/raw/ohlc/<TICKER>.csv with columns date,open,high,low,close,volume. Prices are adjusted for splits and dividends (open/high/low are scaled by the
adjusted-close ratio). Resumable: existing files are skipped. Names that no longer trade (delisted, acquired) are simply missing, so any test on this
universe carries survivor bias. Research only; the list is hand-written large caps across sectors, commodity producers and a few foreign ADRs.
"""
import csv
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import sys
LONG = "--long" in sys.argv
OUT = ROOT / "data" / "raw" / ("ohlc_long" if LONG else "ohlc")
UA = {"User-Agent": "Mozilla/5.0 (research-script)"}
P1 = int((dt.datetime(2003 if "--long" in sys.argv else 2014, 1, 1) - dt.datetime(1970, 1, 1)).total_seconds())
P2 = int((dt.datetime(2026, 11, 7) - dt.datetime(1970, 1, 1)).total_seconds())

TICKERS = """
AAPL MSFT NVDA AVGO ORCL CRM ADBE AMD QCOM TXN INTU AMAT MU LRCX KLAC ADI NOW PANW SNPS CDNS INTC CSCO IBM ACN ANET FTNT MCHP NXPI MPWR ON KEYS GLW HPQ WDC STX TER
GOOGL META NFLX DIS CMCSA T VZ TMUS CHTR EA TTWO
AMZN TSLA HD MCD NKE LOW SBUX BKNG TJX ORLY AZO MAR HLT CMG ROST YUM DHI LEN F GM EBAY LULU
WMT COST PG KO PEP PM MO MDLZ CL KMB GIS KR STZ HSY SYY
LLY JNJ MRK ABBV PFE TMO ABT DHR AMGN BMY GILD ISRG VRTX REGN MDT SYK BSX ZTS CVS CI HUM ELV MCK IDXX EW BIIB
JPM BAC WFC C GS MS BLK SCHW AXP V MA COF USB PNC TFC MET PRU AIG CB MMC SPGI MCO ICE CME
GE CAT DE HON UNP UPS RTX LMT NOC GD BA MMM EMR ETN ITW PH CSX NSC FDX WM LUV DAL UAL
XOM CVX COP EOG SLB OXY PSX MPC VLO WMB KMI HAL BKR DVN FANG APA OKE CTRA
LIN SHW APD FCX NEM ECL DOW DD NUE CTVA MLM VMC MOS CF ADM
NEE DUK SO D AEP EXC SRE XEL PEG
PLD AMT EQIX CCI PSA O SPG WELL
AEM WPM KGC FNV AU GOLD HMY CCJ SCCO TECK
TSM ASML NVO AZN NVS SAP BP SHEL TTE RIO BHP VALE PLTR UBER
^GSPC ^VIX
""".split()


def fetch(t):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/{}?period1={}&period2={}&interval=1d&events=div,splits".format(urllib.parse.quote(t), P1, P2)
    res = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read())["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose")
    rows = []
    for i, ts in enumerate(res["timestamp"]):
        c, o, h, l, v = q["close"][i], q["open"][i], q["high"][i], q["low"][i], q["volume"][i]
        if c is None or o is None or h is None or l is None:
            continue
        r = (adj[i] / c) if adj and adj[i] else 1.0
        d = (dt.datetime(1970, 1, 1) + dt.timedelta(seconds=ts)).date().isoformat()
        rows.append([d, round(o * r, 4), round(h * r, 4), round(l * r, 4), round(c * r, 4), v or 0])
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    for t in TICKERS:
        f = OUT / (t.replace("^", "_") + ".csv")
        if f.exists():
            ok += 1
            continue
        try:
            rows = fetch(t)
            if len(rows) < 300:
                print(t, "too short", len(rows))
                fail += 1
                continue
            with open(f, "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["date", "open", "high", "low", "close", "volume"])
                w.writerows(rows)
            ok += 1
        except Exception as e:
            print(t, "failed", str(e)[:80])
            fail += 1
        time.sleep(0.25)
    print("done ok", ok, "failed", fail)


if __name__ == "__main__":
    main()
