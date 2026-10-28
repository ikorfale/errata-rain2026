"""#546: how far is the 1979-2026 station median from Westra 2013 (5.9-7.7 %/K) and Sun 2021 (6.6, 5.1-8.2)?
Same stations and GMST as analyze_ghcn.py. CIs: year-block bootstrap (years resampled jointly across stations,
keeps shared interannual noise), 1000 draws, seed 546. Also Rx5day, a pooled normalised regression (Westra-style),
and an equal-weight-by-region median."""
import json, numpy as np
from analyze_ghcn import gmst, region, SRC, MINY
T = gmst(); rng = np.random.default_rng(546)
st = [json.loads(l) for l in open(SRC)]
def series(key):
    out = []
    for s in st:
        ys = sorted(int(y) for y, v in s["years"].items() if int(y) in T and v[key] > 0)
        if len(ys) < MINY: continue
        out.append((region(s["lat"], s["lon"]), {y: s["years"][str(y)][key] for y in ys}))
    return out
YEARS = sorted(y for y in T if 1979 <= y <= 2026)
def slopes(data, yrs):
    p = []
    for reg, d in data:
        ys = [y for y in yrs if y in d]
        if len(set(ys)) < 20: continue
        x = np.array([T[y] for y in ys]); r = np.log([d[y] for y in ys])
        if np.ptp(x) == 0: continue
        p.append((reg, 100 * (np.exp(np.polyfit(x, r, 1)[0]) - 1)))
    return p
def pooled(data, yrs):
    X, Y = [], []
    for reg, d in data:
        ys = [y for y in yrs if y in d]; m = np.mean([d[y] for y in ys])
        X += [T[y] for y in ys]; Y += [d[y] / m for y in ys]
    b = np.polyfit(X, Y, 1)[0]; return 100 * b / np.mean(Y)
def regmed(p):
    regs = {}
    for g, v in p: regs.setdefault(g, []).append(v)
    return np.mean([np.median(v) for g, v in regs.items() if len(v) >= 20])
for key in ("rx1", "rx5"):
    data = series(key); p = slopes(data, YEARS)
    est = (np.median([v for _, v in p]), pooled(data, YEARS), regmed(p))
    bs = []
    for _ in range(1000):
        yrs = list(rng.choice(YEARS, len(YEARS)))
        q = slopes(data, yrs); bs.append((np.median([v for _, v in q]), pooled(data, yrs), regmed(q)))
    bs = np.array(bs)
    for i, name in enumerate(("median station", "pooled normalised", "region-equal median")):
        lo, hi = np.percentile(bs[:, i], [5, 95])
        print("%s %-20s %+.1f %%/K  (5-95%% %+.1f..%+.1f)  n=%d" % (key, name, est[i], lo, hi, len(p)))
