"""Handbook check on big-move days: label every 2008-2019 day with |S&P move| >= 2% by event type and summarize.

Usage: python -I src/review_big_days.py
Writes handbook/bigday_review.csv (date, ret_pct, event_type, same_day_headlines, headline_names_cause).
Labels are assigned by hand-written rules below, WITH HINDSIGHT (this is a handbook-building exercise on
2008-2019, not a prediction test; 2020+ is never touched). 'headline_names_cause' is a keyword proxy.
"""
import csv, re, statistics as st
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CREDIT, CB, DATA, FISCAL, GEO = "credit/banking/sovereign stress (3.3)", "central bank action (3.1)", "economic data/growth (3.2)", "fiscal/political (3.6-3.7)", "geopolitical/accident (3.4)"
FOREIGN, TRADE, MKT, OIL, SECTOR, EARN, ELEC, BREX = "foreign shock (3.14)", "trade policy (3.8)", "market structure/vol spike (3.13)", "oil/commodity (3.5)", "sector rotation (3.12)", "earnings/company (3.9)", "election (3.6b)", "Brexit/referendum (3.7)"

# default label by date range (inclusive), then single-day overrides
RANGES = [
 ("2008-01-01","2008-12-31",CREDIT), ("2009-01-01","2009-03-31",CREDIT), ("2009-04-01","2009-12-31",DATA),
 ("2010-01-01","2010-12-31",DATA), ("2011-07-20","2011-12-31",CREDIT), ("2011-01-01","2011-07-19",DATA),
 ("2012-01-01","2012-12-31",DATA), ("2013-01-01","2013-12-31",DATA), ("2014-01-01","2014-12-31",FOREIGN),
 ("2015-01-01","2015-12-31",FOREIGN), ("2016-01-01","2016-12-31",FOREIGN), ("2018-01-01","2018-12-31",CB), ("2019-01-01","2019-12-31",TRADE)]
OVER = {
 "2008-01-23":CB,"2008-03-11":CB,"2008-03-18":CB,"2008-06-06":DATA,"2008-06-26":OIL,"2008-07-29":OIL,"2008-08-05":OIL,"2008-04-16":EARN,
 "2008-10-30":CB,"2008-12-16":CB,"2008-11-04":ELEC,"2008-12-01":DATA,"2008-11-05":DATA,"2008-11-06":DATA,"2008-12-04":DATA,"2008-02-05":DATA,
 "2009-03-18":CB,"2010-01-22":SECTOR,"2010-02-04":CREDIT,"2010-04-27":CREDIT,"2010-05-04":CREDIT,"2010-05-06":MKT,"2010-05-10":CB,"2010-05-20":CREDIT,
 "2010-10-05":CB,"2010-08-11":CB,"2011-02-22":GEO,"2011-09-21":CB,"2011-11-30":CB,"2012-06-06":CREDIT,"2012-06-21":CB,"2012-06-29":CREDIT,"2012-09-06":CB,
 "2012-11-07":ELEC,"2013-01-02":FISCAL,"2013-04-15":GEO,"2013-06-20":CB,"2013-10-10":FISCAL,"2014-02-03":DATA,"2014-04-10":SECTOR,"2014-12-17":CB,"2014-12-18":CB,
 "2015-06-29":CREDIT,"2015-09-28":SECTOR,"2015-12-04":DATA,"2016-01-22":OIL,"2016-01-13":OIL,"2016-01-15":OIL,"2016-01-29":CB,"2016-03-01":OIL,"2016-06-24":BREX,
 "2016-09-09":CB,"2016-11-07":ELEC,"2018-02-02":DATA,"2018-02-05":MKT,"2018-02-08":MKT,"2018-03-22":TRADE,"2018-03-23":TRADE,"2018-03-26":TRADE,"2018-04-02":TRADE,
 "2018-04-06":TRADE,"2018-10-16":DATA,"2018-10-24":EARN,"2018-11-07":ELEC,"2018-11-28":CB,"2018-12-04":TRADE,"2018-12-07":DATA,"2018-12-26":MKT,
 "2019-01-03":EARN,"2019-01-04":CB,"2019-06-04":CB,"2019-08-14":DATA}
CAUSE_KW = re.compile(r"fed|rate|downgrad|brexit|bailout|rescue|stimulus|jobs|tariff|china|greece|euro|vote|oil|aig|citi|lehman|bank|recession|crisis|data|manufactur|shutdown|deal|fiscal|yield|inver|credit|debt|earnings|profit", re.I)

def label(d):
    if d in OVER: return OVER[d]
    for a,b,t in RANGES:
        if a<=d<=b: return t
    return "unlabeled"

news=defaultdict(list)
for r in csv.DictReader(open(ROOT/"data/processed/news_all.csv",encoding="utf-8")):
    if r["split"]=="handbook": news[r["date"]].append(r["title"])
days=[r for r in csv.DictReader(open(ROOT/"data/processed/market_days.csv")) if "2008"<=r["date"]<"2020" and r["ret_pct"] and abs(float(r["ret_pct"]))>=2]
out=[]
for r in days:
    d=r["date"]; hs=news[d]
    out.append((d,float(r["ret_pct"]),label(d),len(hs),int(any(CAUSE_KW.search(h) for h in hs))))
with open(ROOT/"handbook/bigday_review.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["date","ret_pct","event_type","same_day_headlines","headline_names_cause"]); w.writerows(out)

print(len(out),"big days; with same-day headlines:",sum(1 for o in out if o[3]),"; headlines with a cause keyword:",sum(o[4] for o in out))
by=defaultdict(list)
for o in out: by[o[2]].append(o)
print("{:42s} {:>4s} {:>6s} {:>6s} {:>6s} {:>6s} {:>6s} {:>5s}".format("type","n","down%","medAbs","minRet","maxRet","hlCause","noHL"))
for t,v in sorted(by.items(),key=lambda kv:-len(kv[1])):
    rs=[o[1] for o in v]
    print("{:42s} {:4d} {:6.0f} {:6.2f} {:6.2f} {:6.2f} {:6.0f} {:5.0f}".format(t,len(v),100*sum(r<0 for r in rs)/len(rs),st.median(abs(r) for r in rs),min(rs),max(rs),100*sum(o[4] for o in v)/len(v),100*sum(1 for o in v if o[3]==0)/len(v)))
yr=Counter(o[0][:4] for o in out); print("by year:",dict(sorted(yr.items())))
top4=sum(yr[y] for y in ("2008","2009","2011","2018")); print("share in 2008,2009,2011,2018: {:.0f}%".format(100*top4/len(out)))
dates=[o[0] for o in out]
import datetime as dt
dd=[dt.date.fromisoformat(x) for x in dates]
near=sum(1 for i,x in enumerate(dd) if (i>0 and (x-dd[i-1]).days<=7) or (i+1<len(dd) and (dd[i+1]-x).days<=7))
print("big days within 7 calendar days of another big day: {:.0f}%".format(100*near/len(dd)))
