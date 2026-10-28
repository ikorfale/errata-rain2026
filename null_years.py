"""Null for 'is 2026 El Nino-like?': the same Aug 1 - Oct 26 total for every year 1979-2026,
then each year's pattern correlation with the El Nino composite (1997, 2015, 2023; a composite
year is compared with the mean of the other two). Where does 2026 rank among 48 years?
Downloads one year at a time, keeps only the window total (window.npz), deletes the file."""
import os, sys, subprocess, json
import numpy as np, netCDF4 as nc

URL = "https://downloads.psl.noaa.gov/Datasets/cpc_global_precip/precip.{}.nc"
OUT = "years"; os.makedirs(OUT, exist_ok=True)

def window_total(y):
    f = f"{OUT}/{y}.npz"
    if os.path.exists(f): return
    tmp = f"/tmp/cpc{y}.nc"
    subprocess.run(["curl", "-sSf", "--retry", "4", "-o", tmp, URL.format(y)], check=True)
    leap = (y % 4 == 0 and y % 100 != 0) or y % 400 == 0
    a, b = 212 + leap, 298 + leap               # Aug 1 .. Oct 26
    ds = nc.Dataset(tmp); p = ds["precip"]
    tot = np.zeros(p.shape[1:], np.float64); nmiss = np.zeros(p.shape[1:], np.int16); n = 0
    for s in range(a, b + 1, 10):                   # 10 days at a time keeps memory small
        v = p[s:min(s + 10, b + 1)]
        if not np.ma.isMaskedArray(v): v = np.ma.masked_invalid(v)
        tot += v.filled(0).sum(axis=0); nmiss += np.ma.getmaskarray(v).sum(axis=0).astype(np.int16); n += v.shape[0]
        del v
    ds.close()
    np.savez_compressed(f, tot=np.where(nmiss == n, np.nan, tot).astype(np.float32), nmiss=nmiss, ndays=n)
    os.remove(tmp)
    print(y, "days", n, flush=True)

if __name__ == "__main__":
    for y in range(1979, 2027):
        try: window_total(y)
        except Exception as e: print(y, "FAILED", e, flush=True)
