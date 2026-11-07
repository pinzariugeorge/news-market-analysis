"""Download SEC insider-transaction bulk data (Forms 3/4/5) and keep only open-market purchases for our tickers.

The SEC blocks automated requests that do not identify the requester, so you must run this yourself with YOUR contact in an environment variable
(never put it in chat). The script also reads the variable personal_email from the project .env or the parent .env. PowerShell:
    $env:SEC_USER_AGENT = "Your Name your.email@example.com"
    python -I src/download_insider.py
Bash:
    SEC_USER_AGENT="Your Name your.email@example.com" python -I src/download_insider.py
Source (official, free): https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets
Files: https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/<YYYY>q<N>_form345.zip (quarterly, 2006 onward; we take 2014q1 to 2024q4;
2025+ is the reserved final test period and is not downloaded). Each zip is deleted after filtering. The SEC asks for at most 10 requests per second; this script sleeps 2 seconds.
Output: data/raw/insider/purchases.csv (git-ignored) with one row per open-market purchase (transaction code P, acquired):
  filing_date, trans_date, ticker, issuer, owner, relationship, title, shares, price, value, accession
Resumable: quarters already processed are listed in data/raw/insider/done.txt. Run `python -I src/download_insider.py --selftest` to test the parser offline.
"""
import csv
import io
import os
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "insider"
BASE = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{}q{}_form345.zip"
FIRST, LAST = (2014, 1), (2024, 4)


def tickers():
    out = set()
    for f in (ROOT / "data" / "raw" / "ohlc_long").glob("*.csv"):
        if not f.stem.startswith("_"):
            out.add(f.stem.upper())
    cache = ROOT / "data" / "raw" / "stocks_cache.json"
    if cache.exists():
        import json
        out |= {t.upper() for t in json.loads(cache.read_text(encoding="utf-8"))}
    return out


def read_tsv(z, name):
    raw = z.read(name).decode("utf-8", errors="replace")
    return csv.DictReader(io.StringIO(raw), delimiter="\t")


def filter_zip(z, wanted):
    """Return rows for open-market purchases by tickers in `wanted`."""
    names = {n.upper(): n for n in z.namelist()}
    sub = {}
    for r in read_tsv(z, names["SUBMISSION.TSV"]):
        sym = (r.get("ISSUERTRADINGSYMBOL") or "").strip().upper()
        if sym in wanted and (r.get("DOCUMENT_TYPE") or "").strip() in ("4", "4/A"):
            sub[r["ACCESSION_NUMBER"]] = (r.get("FILING_DATE", ""), sym, r.get("ISSUERNAME", ""))
    owners = {}
    for r in read_tsv(z, names["REPORTINGOWNER.TSV"]):
        a = r["ACCESSION_NUMBER"]
        if a in sub and a not in owners:
            owners[a] = (r.get("RPTOWNERNAME", ""), r.get("RPTOWNER_RELATIONSHIP", ""), r.get("RPTOWNER_TITLE", ""))
    rows = []
    for r in read_tsv(z, names["NONDERIV_TRANS.TSV"]):
        a = r["ACCESSION_NUMBER"]
        if a not in sub or (r.get("TRANS_CODE") or "").strip() != "P" or (r.get("TRANS_ACQUIRED_DISP_CD") or "A").strip() != "A":
            continue
        try:
            sh = float(r.get("TRANS_SHARES") or 0)
            px = float(r.get("TRANS_PRICEPERSHARE") or 0)
        except ValueError:
            continue
        o = owners.get(a, ("", "", ""))
        rows.append([sub[a][0], r.get("TRANS_DATE", ""), sub[a][1], sub[a][2], o[0], o[1], o[2], sh, px, round(sh * px, 2), a])
    return rows


def quarters():
    y, q = FIRST
    while (y, q) <= LAST:
        yield y, q
        q += 1
        if q == 5:
            y, q = y + 1, 1


def selftest():
    def tsv(header, rows):
        return "\n".join(["\t".join(header)] + ["\t".join(r) for r in rows])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("SUBMISSION.tsv", tsv(["ACCESSION_NUMBER", "FILING_DATE", "DOCUMENT_TYPE", "ISSUERCIK", "ISSUERNAME", "ISSUERTRADINGSYMBOL"],
                                         [["a1", "03-JAN-2020", "4", "1", "Exxon", "XOM"], ["a2", "03-JAN-2020", "4", "2", "Other", "ZZZZ"]]))
        z.writestr("REPORTINGOWNER.tsv", tsv(["ACCESSION_NUMBER", "RPTOWNERNAME", "RPTOWNER_RELATIONSHIP", "RPTOWNER_TITLE"], [["a1", "Doe John", "Officer", "CFO"], ["a2", "X", "Director", ""]]))
        z.writestr("NONDERIV_TRANS.tsv", tsv(["ACCESSION_NUMBER", "TRANS_DATE", "TRANS_CODE", "TRANS_SHARES", "TRANS_PRICEPERSHARE", "TRANS_ACQUIRED_DISP_CD"],
                                             [["a1", "02-JAN-2020", "P", "1000", "10.5", "A"], ["a1", "02-JAN-2020", "S", "500", "10.6", "D"], ["a2", "02-JAN-2020", "P", "5", "1", "A"]]))
    with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as z:
        rows = filter_zip(z, {"XOM"})
    assert len(rows) == 1 and rows[0][2] == "XOM" and rows[0][9] == 10500.0, rows
    print("selftest ok:", rows[0])


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    ua = os.environ.get("SEC_USER_AGENT", "").strip()
    if "@" not in ua:
        for env in (ROOT / ".env", ROOT.parent / ".env"):  # variable personal_email in the project .env or the parent .env (never printed)
            if env.exists():
                for line in env.read_text(encoding="utf-8").splitlines():
                    if line.lower().startswith("personal_email=") and "@" in line:
                        ua = "sp500-news-sim research " + line.split("=", 1)[1].strip().strip('"').strip("'")
    if "@" not in ua:
        sys.exit('Set SEC_USER_AGENT to "Your Name your.email@example.com" (or personal_email=... in .env) first (the SEC requires a contact in the request header).')
    OUT.mkdir(parents=True, exist_ok=True)
    donef = OUT / "done.txt"
    done = set(donef.read_text().split()) if donef.exists() else set()
    outf = OUT / "purchases.csv"
    new = not outf.exists()
    wanted = tickers()
    print("{} tickers; quarters {}q{} to {}q{}".format(len(wanted), *FIRST, *LAST))
    with open(outf, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["filing_date", "trans_date", "ticker", "issuer", "owner", "relationship", "title", "shares", "price", "value", "accession"])
        for y, q in quarters():
            tag = "{}q{}".format(y, q)
            if tag in done:
                continue
            req = urllib.request.Request(BASE.format(y, q), headers={"User-Agent": ua, "Accept-Encoding": "identity"})
            try:
                data = urllib.request.urlopen(req, timeout=120).read()
            except Exception as e:  # noqa: BLE001
                print(tag, "failed:", str(e)[:100])
                continue
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                rows = filter_zip(z, wanted)
            w.writerows(rows)
            fh.flush()
            with open(donef, "a") as d:
                d.write(tag + "\n")
            print(tag, "purchases kept:", len(rows), "(zip {:.1f} MB)".format(len(data) / 1e6))
            time.sleep(2)
    print("done ->", outf)


if __name__ == "__main__":
    main()
