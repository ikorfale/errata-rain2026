"""Apples-to-apples with the CPC within-era test (2006-2026, expected 1/21): at GHCN stations with 2026 data and
>=18 valid years in 2006-2026, is 2026 Rx1day the top (ties count as top)? Region split as analyze_ghcn.region.
Added after PREREG-ghcn.md P5 came out at 1.0x on 1979-2026: P5 compares a different era than the CPC number did."""
import json, numpy as np
from analyze_ghcn import region
st = [json.loads(l) for l in open("stations.jsonl")]
rows = []
for s in st:
    y = {int(k): v["rx1"] for k, v in s["years"].items() if 2006 <= int(k) <= 2026}
    if 2026 not in y or len(y) < 18: continue
    rows.append((region(s["lat"], s["lon"]), y[2026] >= max(y.values()), 1 / len(y)))
def show(rs, lab):
    k = sum(r[1] for r in rs); e = sum(r[2] for r in rs)
    print("%-10s stations %3d  2026 top %3d  expected %.1f  ratio %.2f" % (lab, len(rs), k, e, k / e if e else 0))
show(rows, "all")
for reg in sorted(set(r[0] for r in rows)): show([r for r in rows if r[0] == reg], reg)
# binomial-ish check: Poisson p of >=k given e
from math import exp, factorial
k = sum(r[1] for r in rows); e = sum(r[2] for r in rows)
print("P(>=%d | Poisson %.1f) = %.3f" % (k, e, 1 - sum(exp(-e) * e**i / factorial(i) for i in range(k))))
