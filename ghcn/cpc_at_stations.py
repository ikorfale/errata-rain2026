"""Same stations, two datasets: at each GHCN station used in era_records.py, is 2026 the top Rx1day of 2006-2026
in the CPC 0.5-deg cell that contains it? If CPC says 'top' far more often than the gauge itself, the CPC 2026
excess is partly a gridded-data artefact; if both agree, the station sample is just a different place."""
import json, numpy as np, sys
sys.path.insert(0, "ghcn"); from analyze_ghcn import region
Y = list(range(2006, 2027))
D = {y: np.load(f"extremes/years/{y}.npz") for y in Y}
print("ndays", {y: int(D[y]["ndays"]) for y in (2006, 2020, 2025, 2026)})
rx = np.array([D[y]["rx1"].astype(float) for y in Y]); miss = np.array([D[y]["miss"] for y in Y])
out = {}
for l in open("ghcn/stations.jsonl"):
    s = json.loads(l)
    y = {int(k): v["rx1"] for k, v in s["years"].items() if 2006 <= int(k) <= 2026}
    if 2026 not in y or len(y) < 18: continue
    i = int((89.75 - s["lat"]) / 0.5 + 0.5); j = int((s["lon"] % 360 - 0.25) / 0.5 + 0.5) % 720
    c = rx[:, i, j]
    if not np.all(np.isfinite(c)) or np.any(miss[:, i, j] > 15): continue
    r = region(s["lat"], s["lon"])
    st_top = y[2026] >= max(y.values()); cpc_top = c[-1] >= c.max()
    o = out.setdefault(r, [0, 0, 0, 0]); o[0] += 1; o[1] += st_top; o[2] += cpc_top; o[3] += st_top and cpc_top
tot = np.sum(list(out.values()), 0)
for r, o in sorted(out.items()) + [("all", tot)]:
    print("%-10s n=%3d  gauge 2026-top %2d  CPC cell 2026-top %2d  both %2d  (expected each %.1f)" % (r, o[0], o[1], o[2], o[3], o[0] / 21))
