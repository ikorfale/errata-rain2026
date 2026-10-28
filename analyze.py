"""Is 2026's rain odd? CPC global unified gauge precipitation (0.5 deg, land),
2026 vs the 1991-2020 daily climatology, and vs earlier strong El Nino years
(1997, 2015, 2023) and La Nina years (2010, 2022) over the same calendar window."""
import json, sys
import numpy as np, netCDF4 as nc

LAST = 298                      # index of 2026-10-26 (0-based day of year)
WINDOWS = {"aug1-oct26": (212, LAST), "oct1-oct26": (273, LAST), "jun1-oct26": (151, LAST)}

ltm_ds = nc.Dataset("ltm.nc")
lat = ltm_ds["lat"][:]; lon = ltm_ds["lon"][:]

def total(path, a, b):
    v = nc.Dataset(path)["precip"][a:b + 1]          # mm/day, masked
    return v.sum(axis=0) if np.ma.isMaskedArray(v) else np.ma.masked_invalid(v).sum(axis=0)

def ltm_total(a, b):
    return ltm_ds["precip"][a:b + 1].sum(axis=0)

YEARS = {"2026": "cpc2026.nc", "1997": "cpc1997.nc", "2015": "cpc2015.nc",
         "2023": "cpc2023.nc", "2010": "cpc2010.nc", "2022": "cpc2022.nc"}

# land boxes: (lat_min, lat_max, lon_min, lon_max) with lon in 0..360
BOXES = {
    "S China: Hunan-Guangxi-Guizhou-Jiangxi": (22, 30, 104, 118),
    "SE coast China (Fujian-Guangdong)": (21, 27, 110, 120),
    "Yangtze lower (Jiangsu-Anhui-Zhejiang)": (28, 33, 115, 122),
    "North China Plain": (34, 40, 112, 119),
    "NW China (Gansu-Ningxia-Shaanxi N)": (35, 40, 100, 110),
    "Sichuan-Chongqing": (28, 32, 102, 108),
    "Thailand (all)": (6, 20, 98, 105.5),
    "Southern Thailand": (5.5, 11, 98, 102.5),
    "Northern-central Thailand": (14, 20, 98, 102),
    "Vietnam-Cambodia south": (9, 14, 103, 109),
    "Indonesia (Java-Sumatra S-Borneo S)": (-9, -1, 104, 116),
    "Philippines": (6, 18.5, 120, 126),
    "India (all)": (8, 30, 70, 88),
    "Ethiopia": (4, 14, 35, 43),
    "Horn: Somalia-Kenya east": (-3, 6, 39, 48),
    "Southern Africa": (-34, -22, 18, 32),
    "Western-central Europe": (43, 52, -2 + 360, 15),   # wraps, handled below
    "Iberia": (36, 43.5, -9 + 360, 3),
    "Amazon north": (-8, 5, 290, 310),
    "Central America": (8, 17, 268, 284),
    "SE Australia": (-39, -32, 140, 151),
    "Peru-Ecuador coast": (-8, 1, 278, 282),
    "Uruguay-S Brazil-NE Argentina": (-35, -26, 300, 310),
    "US Gulf coast": (29, 33, 264, 278),
}

def box_mask(b):
    la0, la1, lo0, lo1 = b
    LA, LO = np.meshgrid(lat, lon, indexing="ij")
    m = (LA >= la0) & (LA <= la1)
    if lo0 > lo1:   # wraps through 0
        m &= (LO >= lo0) | (LO <= lo1)
    else:
        m &= (LO >= lo0) & (LO <= lo1)
    return m

w_area = np.cos(np.deg2rad(lat))[:, None] * np.ones((1, lon.size))

def box_pct(obs, clim, b):
    m = box_mask(b) & ~np.ma.getmaskarray(obs) & ~np.ma.getmaskarray(clim) & (clim > 0)
    if m.sum() < 4: return None, int(m.sum())
    w = w_area[m]
    return float(100 * (obs.filled(0)[m] * w).sum() / (clim.filled(0)[m] * w).sum()), int(m.sum())

out = {"source": "NOAA CPC Global Unified Gauge-Based Analysis of Daily Precipitation, 0.5 deg (PSL), climatology 1991-2020",
       "last_day": "2026-10-26", "windows": {}}
for wname, (a, b) in WINDOWS.items():
    clim = ltm_total(a, b)
    tots = {y: total(p, a, b) for y, p in YEARS.items()}
    res = {"boxes": {}, "pattern_corr": {}}
    for bn, bb in BOXES.items():
        res["boxes"][bn] = {y: box_pct(tots[y], clim, bb)[0] for y in YEARS}
        res["boxes"][bn]["cells"] = box_pct(tots["2026"], clim, bb)[1]
    # pattern correlation over land 35S-40N where climatology >= 0.5 mm/day mean
    ndays = b - a + 1
    LA = np.meshgrid(lat, lon, indexing="ij")[0]
    valid = (np.abs(LA) <= 40) & (clim.filled(0) >= 0.5 * ndays)
    for y in YEARS:
        valid &= ~np.ma.getmaskarray(tots[y])
    anom = {y: np.log((tots[y].filled(0)[valid] + 10) / (clim.filled(0)[valid] + 10)) for y in YEARS}
    w = w_area[valid]
    def wcorr(x, z):
        xm = x - np.average(x, weights=w); zm = z - np.average(z, weights=w)
        return float(np.sum(w * xm * zm) / np.sqrt(np.sum(w * xm**2) * np.sum(w * zm**2)))
    for y in YEARS:
        if y != "2026":
            res["pattern_corr"][y] = round(wcorr(anom["2026"], anom[y]), 3)
    comp = (anom["1997"] + anom["2015"] + anom["2023"]) / 3
    res["pattern_corr"]["elnino_composite_97_15_23"] = round(wcorr(anom["2026"], comp), 3)
    # where the composite is clearly signed, how often does 2026 share the sign
    strong = np.abs(comp) > 0.2
    agree = np.sign(anom["2026"][strong]) == np.sign(comp[strong])
    res["sign_agreement_where_composite_strong"] = {"cells": int(strong.sum()), "share_same_sign": round(float(np.average(agree, weights=w[strong])), 3)}
    # share of land (40S-40N) far from normal in 2026 vs other years: <50% or >150%
    ratio = {y: tots[y].filled(0)[valid] / clim.filled(0)[valid] for y in YEARS}
    res["extreme_share"] = {y: {"below50": round(float(np.average(r < 0.5, weights=w)), 3),
                               "above150": round(float(np.average(r > 1.5, weights=w)), 3)} for y, r in ratio.items()}
    res["valid_cells"] = int(valid.sum())
    out["windows"][wname] = res
    if wname == "aug1-oct26":
        np.savez_compressed("map_aug_oct.npz", lat=lat, lon=lon, obs=tots["2026"].filled(np.nan),
                            clim=clim.filled(np.nan), comp=np.where(valid, 0, np.nan))
        # also full composite map for drawing
        comp_full = sum(np.log((tots[y].filled(np.nan) + 10) / (clim.filled(np.nan) + 10)) for y in ("1997", "2015", "2023")) / 3
        np.save("comp_aug_oct.npy", comp_full)

json.dump(out, open("result.json", "w"), indent=1)
print(json.dumps(out, indent=1))
