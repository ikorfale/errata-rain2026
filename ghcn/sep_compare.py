"""Post-hoc, after Fable's review (28.10): repeat the record checks with the same Jan 1 - Sep 30 window on gauges and CPC.
1) CPC whole land, 2006-2026: share of area where 2026 is the top Rx1day (within_era.py's cell rule), by region.
2) Gauges (stations_sep.jsonl), 2026 top of 2006-2026 and of 1979-2026 (P5 rule), by region, with expected counts.
3) Same sites, CPC cell vs gauge, 2006-2026. Ties count as a top on both sides here."""
import json, sys, numpy as np
from math import exp, factorial
sys.path.insert(0, "ghcn"); from analyze_ghcn import region
Y = list(range(2006, 2027))
D = {y: np.load(f"extremes/years_sep/{y}.npz") for y in Y}
print("CPC ndays", {y: int(D[y]["ndays"]) for y in (2006, 2024, 2025, 2026)})
rx = np.array([D[y]["rx1"].astype(float) for y in Y]); miss = np.array([D[y]["miss"] for y in Y])
full = np.all(miss <= 15, 0) & (np.nanmedian(rx, 0) >= 10) & np.all(np.isfinite(rx), 0)
lat = np.arange(89.75, -90, -0.5); lon = np.arange(0.25, 360, 0.5)
LA, LO = np.meshgrid(lat, lon, indexing="ij"); w = np.cos(np.deg2rad(LA)) * full
top26 = np.where(full, rx[-1] >= np.nanmax(rx, 0), False)
print("1) CPC land share with 2026 top (Jan-Sep): %.4f (expected %.4f)" % ((w * top26).sum() / w.sum(), 1 / 21))
REG = {"East Asia": (20, 50, 100, 145), "South/SE Asia": (-10, 30, 65, 125), "Europe": (35, 70, 350, 40), "N America": (15, 70, 190, 300),
       "S America": (-56, 13, 278, 326), "Africa": (-35, 37, 342, 52), "Australia": (-45, -10, 110, 155), "N Asia": (50, 75, 40, 180)}
for k, (a, b, c, d) in REG.items():
    m = (LA >= a) & (LA <= b) & (((LO >= c) & (LO <= d)) if c < d else ((LO >= c) | (LO <= d)))
    ww = w * m; print("   %-14s %.3f" % (k, (ww * top26).sum() / ww.sum()))
pois = lambda k, e: 1 - sum(exp(-e) * e**i / factorial(i) for i in range(k))
st = [json.loads(l) for l in open("ghcn/stations_sep.jsonl")]
for lo_y, lab in ((2006, "2006-2026"), (1979, "1979-2026 (P5 rule)")):
    agg = {}
    for s in st:
        y = {int(k): v["rx1"] for k, v in s["years"].items() if int(k) >= lo_y}
        if 2026 not in y or len(y) < (18 if lo_y == 2006 else 2): continue
        a = agg.setdefault(region(s["lat"], s["lon"]), [0, 0, 0.0]); a[0] += 1; a[1] += y[2026] >= max(y.values()); a[2] += 1 / len(y)
    t = np.sum(list(agg.values()), 0)
    print("2) gauges, 2026 top of", lab)
    for r, a in sorted(agg.items()) + [("all", t)]:
        print("   %-10s n=%3d top %2d expected %.1f  P(>=k) %.3f" % (r, a[0], a[1], a[2], pois(int(a[1]), a[2])))
out = {}
for s in st:
    y = {int(k): v["rx1"] for k, v in s["years"].items() if 2006 <= int(k) <= 2026}
    if 2026 not in y or len(y) < 18: continue
    i = int((89.75 - s["lat"]) / 0.5 + 0.5); j = int((s["lon"] % 360 - 0.25) / 0.5 + 0.5) % 720
    c = rx[:, i, j]
    if not np.all(np.isfinite(c)) or np.any(miss[:, i, j] > 15): continue
    g, k = y[2026] >= max(y.values()), c[-1] >= c.max()
    o = out.setdefault(region(s["lat"], s["lon"]), [0, 0, 0, 0]); o[0] += 1; o[1] += g; o[2] += k; o[3] += g and k
print("3) same sites, 2006-2026, Jan-Sep")
for r, o in sorted(out.items()) + [("all", np.sum(list(out.values()), 0))]:
    print("   %-10s n=%3d gauge top %2d  CPC cell top %2d  both %2d  expected each %.1f" % (r, o[0], o[1], o[2], o[3], o[0] / 21))
