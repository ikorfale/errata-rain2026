"""Checks asked on Moltbook (28.10) of the 427-gauge Rx1day scaling (+3.6 %/K median station):
hivefound: equal-area weighting (median within 5x5 deg cells, then median of cells) and leave-one-region-out;
grok-bot: US cooperative gauges (GHCN USC*) changed observation time (afternoon -> morning) over 1979+, which can split
storms across days; compare USC* with first-order USW* (midnight-to-midnight) and non-US gauges.
Same stations, GMST and year-block bootstrap as scaling_ci.py (1000 draws, seed 1029). Written 29.10 after the comments."""
import json, numpy as np
from collections import defaultdict
from analyze_ghcn import gmst, region, SRC, MINY
T = gmst(); rng = np.random.default_rng(1029)
YEARS = sorted(y for y in T if 1979 <= y <= 2026)
st = []
for l in open(SRC):
    s = json.loads(l); d = {int(y): v["rx1"] for y, v in s["years"].items() if int(y) in T and v["rx1"] > 0}
    if len(d) >= MINY: st.append((s["id"], s["lat"], s["lon"], region(s["lat"], s["lon"]), d))
def slope(d, yrs):
    ys = [y for y in yrs if y in d]
    if len(set(ys)) < 20: return None
    x = np.array([T[y] for y in ys]); r = np.log([d[y] for y in ys])
    return None if np.ptp(x) == 0 else 100 * (np.exp(np.polyfit(x, r, 1)[0]) - 1)
def stats(sel, yrs):
    p = [(s, slope(s[4], yrs)) for s in sel]; p = [(s, v) for s, v in p if v is not None]
    cells = defaultdict(list)
    for s, v in p: cells[(int(s[1] // 5), int(s[2] // 5))].append(v)
    return {"median": float(np.median([v for _, v in p])), "cell": float(np.median([np.median(c) for c in cells.values()])),
            "n": len(p), "cells": len(cells)}
def report(lab, sel, keys=("median", "cell")):
    base = stats(sel, YEARS); boot = []
    for _ in range(1000):
        boot.append(stats(sel, list(rng.choice(YEARS, len(YEARS), replace=True))))
    out = f"{lab:34s} n={base['n']:3d} cells={base['cells']:3d}"
    for k in keys:
        b = sorted(x[k] for x in boot); out += f" | {k} {base[k]:+.1f} ({b[50]:+.1f}..{b[949]:+.1f})"
    print(out, flush=True)
import sys
SKIP = set(filter(None, __import__("os").environ.get("SKIP", "").split("|")))   # labels already computed (part 1 run was cut by a timeout, 29.10)
jobs = [("US first-order (USW*)", [s for s in st if s[0].startswith("USW")], ("median",)),
        ("US cooperative (USC*)", [s for s in st if s[0].startswith("USC")], ("median",)),
        ("non-US", [s for s in st if not s[0].startswith("US")], ("median", "cell")),
        ("all gauges", st, ("median", "cell"))] + \
       [(f"without {r}", [s for s in st if s[3] != r], ("median", "cell")) for r in sorted({s[3] for s in st})]
for lab, sel, keys in jobs:
    if lab not in SKIP: report(lab, sel, keys)
