# EU mechanical screen test (pre-registered in PREREG_SCREEN.md)

Cost 0.3% round trip; excess = event return minus mean return of all stocks entering the same day; t clustered by entry month; survivor bias, local currency.

## Horizon 10 days (all-stock excess sd 7.5%)

| screen | period | events | dates | mean excess % (gross) | net of cost | t (net, clustered) | share net>0 |
|---|---|---|---|---|---|---|---|
| TREND | build | 5839 | 2500 | +0.15 | -0.15 | -2.20 | 46% |
| TREND | validation | 3895 | 1493 | +0.18 | -0.12 | -1.41 | 48% |
| TREND | test | 2669 | 1010 | -0.05 | -0.35 | -3.26 | 46% |
| S1 | build | 951 | 757 | +0.77 | +0.47 | 1.95 | 50% |
| S1 | validation | 464 | 367 | +0.76 | +0.46 | 1.02 | 51% |
| S1 | test | 317 | 243 | +1.00 | +0.70 | 1.46 | 51% |
| S2 | build | 1104 | 685 | +0.98 | +0.68 | 2.64 | 51% |
| S2 | validation | 792 | 460 | +0.49 | +0.19 | 0.62 | 50% |
| S2 | test | 661 | 350 | +0.09 | -0.21 | -0.54 | 47% |
| S3 | build | 273 | 244 | +0.54 | +0.24 | 0.45 | 48% |
| S3 | validation | 200 | 162 | -0.22 | -0.52 | -1.00 | 46% |
| S3 | test | 115 | 99 | +1.04 | +0.74 | 0.79 | 57% |

Pass check (build+validation pooled, screens S1-S3):
- S1: net>0 build True / val True; n>=100 & 50 dates True; t 2.14 (>=2 True); mean +0.77 vs random p95 +0.29 (True) -> **PASS**
- S2: net>0 build True / val True; n>=100 & 50 dates True; t 2.39 (>=2 True); mean +0.77 vs random p95 +0.27 (True) -> **PASS**
- S3: net>0 build True / val False; n>=100 & 50 dates True; t -0.22 (>=2 False); mean +0.22 vs random p95 +0.51 (False) -> **FAIL**

## Horizon 20 days (all-stock excess sd 10.2%)

| screen | period | events | dates | mean excess % (gross) | net of cost | t (net, clustered) | share net>0 |
|---|---|---|---|---|---|---|---|
| TREND | build | 3203 | 1890 | +0.05 | -0.25 | -1.87 | 45% |
| TREND | validation | 2153 | 1165 | +0.22 | -0.08 | -0.48 | 47% |
| TREND | test | 1472 | 756 | -0.11 | -0.41 | -1.79 | 44% |
| S1 | build | 816 | 653 | +1.20 | +0.90 | 2.68 | 50% |
| S1 | validation | 422 | 342 | +1.29 | +0.99 | 1.78 | 50% |
| S1 | test | 293 | 227 | +2.05 | +1.75 | 1.99 | 50% |
| S2 | build | 873 | 580 | +1.72 | +1.42 | 3.79 | 53% |
| S2 | validation | 621 | 398 | +0.67 | +0.37 | 0.77 | 48% |
| S2 | test | 504 | 292 | +0.25 | -0.05 | -0.11 | 45% |
| S3 | build | 260 | 234 | +2.37 | +2.07 | 2.42 | 52% |
| S3 | validation | 195 | 158 | +0.64 | +0.34 | 0.50 | 47% |
| S3 | test | 108 | 93 | +0.60 | +0.30 | 0.23 | 48% |

Pass check (build+validation pooled, screens S1-S3):
- S1: net>0 build True / val True; n>=100 & 50 dates True; t 3.20 (>=2 True); mean +1.23 vs random p95 +0.45 (True) -> **PASS**
- S2: net>0 build True / val True; n>=100 & 50 dates True; t 3.30 (>=2 True); mean +1.28 vs random p95 +0.43 (True) -> **PASS**
- S3: net>0 build True / val True; n>=100 & 50 dates True; t 2.32 (>=2 True); mean +1.63 vs random p95 +0.79 (True) -> **PASS**

## Power: independent events needed to detect a net edge at t = 2

| horizon | sd of one event (%) | edge 1% | edge 2% | edge 3% |
|---|---|---|---|---|
| 10 | 8.3 | 275 | 69 | 31 |
| 20 | 11.2 | 500 | 125 | 56 |

The main account closes a few trades a month (about 4 to 8 at most with 3 positions and 10-20 day holds), so 30 trades cover a net edge of roughly 4% a trade at best: a pass bar of 30 trades cannot show a normal edge. Scoring every name every day (hundreds of calls a month, no fees) is the route to power; events cluster in time, so the real sample is smaller than the count.
