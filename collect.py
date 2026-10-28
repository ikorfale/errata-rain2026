"""Rain extremes vs warming, step 1: for every year 1979-2026, Jan 1 - Oct 26 (same window
as 2026's latest data), per 0.5-deg land cell of NOAA CPC unified gauge daily precip:
total, Rx1day, Rx5day, days >=20 mm, wet days >=1 mm, missing days. One year at a time,
10 days per read (700 MB job limit), the raw file is deleted after use."""
import os, subprocess, sys, time
import numpy as np, netCDF4 as nc

URL = "https://downloads.psl.noaa.gov/Datasets/cpc_global_precip/precip.{}.nc"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.environ.get("OUTDIR", "years")); os.makedirs(OUT, exist_ok=True)
END = os.environ.get("END", "10-26")   # window end, MM-DD inclusive (Sep 30 run: END=09-30 OUTDIR=years_sep)
TMP = os.environ.get("TMPDIR", "/tmp")

def one(y):
    f = f"{OUT}/{y}.npz"
    if os.path.exists(f): return
    tmp = f"{TMP}/cpcx{y}{END}.nc"
    subprocess.run(["curl", "-sSf", "--retry", "5", "--retry-delay", "20", "-o", tmp, URL.format(y)], check=True)
    import datetime as dt
    b = (dt.date(y, int(END[:2]), int(END[3:])) - dt.date(y, 1, 1)).days   # last day index, inclusive
    ds = nc.Dataset(tmp); p = ds["precip"]
    shp = p.shape[1:]
    tot = np.zeros(shp); rx1 = np.full(shp, -1.0); rx5 = np.full(shp, -1.0)
    r20 = np.zeros(shp, np.int16); wet = np.zeros(shp, np.int16); miss = np.zeros(shp, np.int16)
    last4 = np.zeros((0,) + shp, np.float32); n = 0
    for s in range(0, b + 1, 10):
        v = p[s:min(s + 10, b + 1)]
        if not np.ma.isMaskedArray(v): v = np.ma.masked_invalid(v)
        m = np.ma.getmaskarray(v); x = v.filled(0).astype(np.float32)
        miss += m.sum(0).astype(np.int16)
        tot += x.sum(0); rx1 = np.maximum(rx1, x.max(0))
        r20 += (x >= 20).sum(0).astype(np.int16); wet += (x >= 1).sum(0).astype(np.int16)
        seq = np.concatenate([last4, x]); c = np.cumsum(seq, 0, dtype=np.float64)
        if seq.shape[0] >= 5:
            c = np.concatenate([np.zeros((1,) + shp), c])
            rx5 = np.maximum(rx5, (c[5:] - c[:-5]).max(0))
        last4 = seq[-4:]; n += x.shape[0]; del v, x, seq, c
    ds.close(); os.remove(tmp)
    allmiss = miss == n
    nanify = lambda a: np.where(allmiss, np.nan, a).astype(np.float32)
    np.savez_compressed(f, tot=nanify(tot), rx1=nanify(rx1), rx5=nanify(rx5), r20=r20, wet=wet,
                        miss=miss, ndays=n)
    print(y, "days", n, "land cells", int((~allmiss).sum()), time.strftime("%H:%M:%S"), flush=True)

if __name__ == "__main__":
    years = [int(a) for a in sys.argv[1:]] or list(range(2026, 1978, -1))
    for y in years:
        for k in range(2):
            try: one(y); break
            except Exception as e: print(y, "FAILED", k, e, flush=True); time.sleep(30)
