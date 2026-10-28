"""Score PREREG-era5asia.md P1-P4 from data/*.json. Window 1 Jan-30 Sep every year; ties broken against 2026."""
import json, glob, math, random
import numpy as np
from collections import defaultdict
gis = {}
for l in open("gistemp.csv").read().splitlines()[2:]:
    f = l.split(",")
    if f[13] != "***": gis[int(f[0])] = float(f[13])
rx = defaultdict(dict)   # region -> point -> {year: Rx1day}
for fn in sorted(glob.glob("data/*.json")):
    reg, name = fn[5:-5].split("_", 1); j = json.load(open(fn))
    by = defaultdict(list)
    for t, p in zip(j["daily"]["time"], j["daily"]["precipitation_sum"]):
        if p is not None and t[5:7] <= "09": by[int(t[:4])].append(p)
    rx[reg][name] = {y: max(v) for y, v in by.items() if len(v) >= 270}
def binom_tail(k, n, p): return sum(math.comb(n, i) * p**i * (1-p)**(n-i) for i in range(k, n+1))
res = {}
for reg in ("China", "Thailand"):
    pts = rx[reg]; rec = []; pct = []
    for name, s in pts.items():
        if 2026 not in s or len(s) < 48: print("incomplete", reg, name, len(s)); continue
        v26 = s[2026]; others = [s[y] for y in s if y != 2026]
        rec.append(all(v26 > o for o in others)); pct.append(sum(o < v26 for o in others) / len(others))
        if rec[-1]: print(f"  record: {reg} {name} {v26:.1f} mm (previous max {max(others):.1f})")
    n, k = len(rec), sum(rec)
    res[reg] = dict(n=n, records=k, p_tail=binom_tail(k, n, 1/48), median_pct=float(np.median(pct)))
    print(f"{reg}: 2026 record at {k} of {n} points (expected {n/48:.2f}; P(>= {k}) = {res[reg]['p_tail']:.3f}); median percentile {np.median(pct):.2f}")
# P4: China scaling, 1979-2025, point fixed effects
pts = rx["China"]; years = list(range(1979, 2026))
def slope(ys):
    X, Y = [], []
    for name, s in pts.items():
        m = np.mean([math.log(s[y]) for y in years if s.get(y, 0) > 0])
        for y in ys:
            if s.get(y, 0) > 0: X.append(gis[y]); Y.append(math.log(s[y]) - m)
    X = np.array(X); Y = np.array(Y); X = X - X.mean()
    return 100 * (math.exp((X @ Y) / (X @ X)) - 1)
b = slope(years); random.seed(1); boots = sorted(slope([random.choice(years) for _ in years]) for _ in range(2000))
res["China_scaling"] = dict(pct_per_K=b, ci95=[boots[50], boots[1949]])
print(f"China scaling 1979-2025: {b:+.1f} %/K, 95% CI over years {boots[50]:+.1f} to {boots[1949]:+.1f}")
print("P1", res["China"]["records"] <= 3, "| P2", res["Thailand"]["records"] <= 2, "| P3", 0.35 <= res["China"]["median_pct"] <= 0.80,
      "| P4", -3 <= b <= 12 and boots[50] <= 7 <= boots[1949])
json.dump(res, open("result.json", "w"), indent=1)
