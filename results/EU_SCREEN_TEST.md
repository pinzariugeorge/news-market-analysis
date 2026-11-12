# EU mechanical screen test (pre-registered in PREREG_SCREEN.md)

Cost 1.5% round trip; excess = event return minus mean return of all stocks entering the same day; t clustered by entry month; survivor bias, local currency.

## Horizon 10 days (all-stock excess sd 7.5%)

| screen | period | events | dates | mean excess % (gross) | net of cost | t (net, clustered) | share net>0 |
|---|---|---|---|---|---|---|---|
| TREND | build | 5839 | 2500 | +0.15 | -1.35 | -19.71 | 36% |
| TREND | validation | 3895 | 1493 | +0.18 | -1.32 | -15.70 | 38% |
| S1 | build | 951 | 757 | +0.77 | -0.73 | -2.99 | 42% |
| S1 | validation | 464 | 367 | +0.76 | -0.74 | -1.66 | 42% |
| S2 | build | 1104 | 685 | +0.98 | -0.52 | -2.03 | 41% |
| S2 | validation | 792 | 460 | +0.49 | -1.01 | -3.27 | 40% |
| S3 | build | 273 | 244 | +0.54 | -0.96 | -1.84 | 42% |
| S3 | validation | 200 | 162 | -0.22 | -1.72 | -3.30 | 40% |

Pass check (build+validation pooled, screens S1-S3):
- S1: net>0 build False / val False; n>=100 & 50 dates True; t -3.35 (>=2 False); mean +0.77 vs random p95 +0.29 (True) -> **FAIL**
- S2: net>0 build False / val False; n>=100 & 50 dates True; t -3.67 (>=2 False); mean +0.77 vs random p95 +0.27 (True) -> **FAIL**
- S3: net>0 build False / val False; n>=100 & 50 dates True; t -3.42 (>=2 False); mean +0.22 vs random p95 +0.51 (False) -> **FAIL**

## Horizon 20 days (all-stock excess sd 10.2%)

| screen | period | events | dates | mean excess % (gross) | net of cost | t (net, clustered) | share net>0 |
|---|---|---|---|---|---|---|---|
| TREND | build | 3203 | 1890 | +0.05 | -1.45 | -10.67 | 38% |
| TREND | validation | 2153 | 1165 | +0.22 | -1.28 | -7.82 | 41% |
| S1 | build | 816 | 653 | +1.20 | -0.30 | -0.89 | 44% |
| S1 | validation | 422 | 342 | +1.29 | -0.21 | -0.37 | 43% |
| S2 | build | 873 | 580 | +1.72 | +0.22 | 0.58 | 47% |
| S2 | validation | 621 | 398 | +0.67 | -0.83 | -1.71 | 43% |
| S3 | build | 260 | 234 | +2.37 | +0.87 | 1.02 | 44% |
| S3 | validation | 195 | 158 | +0.64 | -0.86 | -1.27 | 43% |

Pass check (build+validation pooled, screens S1-S3):
- S1: net>0 build False / val False; n>=100 & 50 dates True; t -0.92 (>=2 False); mean +1.23 vs random p95 +0.45 (True) -> **FAIL**
- S2: net>0 build True / val False; n>=100 & 50 dates True; t -0.73 (>=2 False); mean +1.28 vs random p95 +0.43 (True) -> **FAIL**
- S3: net>0 build True / val False; n>=100 & 50 dates True; t 0.23 (>=2 False); mean +1.63 vs random p95 +0.79 (True) -> **FAIL**

## Power: independent events needed to detect a net edge at t = 2

| horizon | sd of one event (%) | edge 1% | edge 2% | edge 3% |
|---|---|---|---|---|
| 10 | 8.3 | 275 | 69 | 31 |
| 20 | 11.2 | 500 | 125 | 56 |

The main account closes a few trades a month (about 4 to 8 at most with 3 positions and 10-20 day holds), so 30 trades cover a net edge of roughly 4% a trade at best: a pass bar of 30 trades cannot show a normal edge. Scoring every name every day (hundreds of calls a month, no fees) is the route to power; events cluster in time, so the real sample is smaller than the count.
