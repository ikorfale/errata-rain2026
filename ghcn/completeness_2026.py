"""Fable review 28.10 blocking #2: is the 2026 record deficit at Europe/N America gauges just missing 2026 days?
Jan-Sep window (stations_sep.jsonl). 'complete' = 2026 valid days >= the station's 2006-2025 median."""
import json, numpy as np
from collections import defaultdict
from analyze_ghcn import region
st = [json.loads(l) for l in open("stations_sep.jsonl")]
recs = defaultdict(lambda: [0, 0, 0.0])
for s in st:
    Y = s["years"]
    if "2026" not in Y: continue
    prev = [Y[str(y)]["n"] for y in range(2006, 2026) if str(y) in Y]
    if len(prev) < 15: continue
    yrs = [y for y in range(2006, 2027) if str(y) in Y]
    k = (region(s["lat"], s["lon"]), Y["2026"]["n"] >= np.median(prev))
    recs[k][0] += Y["2026"]["rx1"] >= max(Y[str(y)]["rx1"] for y in yrs); recs[k][1] += 1; recs[k][2] += 1 / len(yrs)
for (g, full), (t, n, e) in sorted(recs.items()):
    print("%-10s %-10s 2026 top of 2006-2026: %d of %d (chance %.1f)" % (g, "complete" if full else "short", t, n, e))
