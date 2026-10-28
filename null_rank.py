"""Rank 2026 among 1979-2026 by pattern correlation with the El Nino composite (Aug 1 - Oct 26).
Climatology = mean of the 1991-2020 window totals from years/ (same files, same window).
Anomaly = log((P+10)/(clim+10)), land 40S-40N where clim >= 0.5 mm/day, area-weighted.
Composite years are compared with the mean of the other two composite years (leave-one-out)."""
import json, urllib.request
import numpy as np

YRS = list(range(1979, 2027))
T = {y: np.load(f"years/{y}.npz") for y in YRS}
tot = {y: T[y]["tot"] for y in YRS}
ok = {y: T[y]["nmiss"] == 0 for y in YRS}
clim = np.nanmean([tot[y] for y in range(1991, 2021)], axis=0)
lat = np.arange(89.75, -90, -0.5)              # CPC 0.5 deg grid, north to south
assert lat.size == clim.shape[0]
LA = lat[:, None] * np.ones((1, clim.shape[1]))
w_all = np.cos(np.deg2rad(LA))
base = (np.abs(LA) <= 40) & np.isfinite(clim) & (clim >= 0.5 * 87)
anom = {y: np.log((tot[y] + 10) / (clim + 10)) for y in YRS}
EN = (1997, 2015, 2023)

def wcorr(x, z, w):
    xm = x - np.average(x, weights=w); zm = z - np.average(z, weights=w)
    return float(np.sum(w * xm * zm) / np.sqrt(np.sum(w * xm**2) * np.sum(w * zm**2)))

# ONI, Aug-Sep-Oct season (CPC); 2026 ASO may be missing -> JAS
oni = {}
try:
    txt = urllib.request.urlopen("https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt", timeout=30).read().decode()
    for line in txt.splitlines()[1:]:
        s, yr, total, an = line.split()
        if s in ("JAS", "ASO"): oni.setdefault(int(yr), {})[s] = float(an)
except Exception as e:
    print("ONI fetch failed", e)

rows = []
for y in YRS:
    others = [e for e in EN if e != y]
    comp = sum(anom[e] for e in others) / len(others)
    m = base & ok[y] & np.all([ok[e] for e in others], axis=0)
    r = wcorr(anom[y][m], comp[m], w_all[m])
    o = oni.get(y, {})
    rows.append({"year": y, "r": round(r, 3), "cells": int(m.sum()), "loo": y in EN,
                 "oni": o.get("ASO", o.get("JAS")), "oni_season": "ASO" if "ASO" in o else ("JAS" if o else None)})
rows.sort(key=lambda d: -d["r"])
for i, d in enumerate(rows, 1):
    d["rank"] = i
    print(f'{i:2d} {d["year"]} r={d["r"]:+.3f} oni={d["oni"]} cells={d["cells"]}{" (leave-one-out)" if d["loo"] else ""}')
r26 = next(d for d in rows if d["year"] == 2026)
non_en = [d["r"] for d in rows if not d["loo"] and d["year"] != 2026]
res = {"window": "Aug 1 - Oct 26", "years": rows, "rank_2026": r26["rank"], "n_years": len(rows),
       "r_2026": r26["r"], "n_non_composite_years_above_2026": sum(r > r26["r"] for r in non_en),
       "n_non_composite_years": len(non_en)}
oo = [(d["oni"], d["r"]) for d in rows if d["oni"] is not None and d["year"] != 2026 and not d["loo"]]
if len(oo) > 10:
    a = np.array(oo); res["corr_oni_vs_r_excl2026_and_composite"] = round(float(np.corrcoef(a[:, 0], a[:, 1])[0, 1]), 3)
json.dump(res, open("null_rank.json", "w"), indent=1)
print({k: v for k, v in res.items() if k != "years"})
