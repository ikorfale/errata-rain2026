"""Rx1day scaling with global temperature on long GHCN-Daily stations (stations.jsonl from fetch.py).
Comparable to Westra, Alexander & Zwiers 2013 (J. Climate 26:3904): per-station ln(Rx1day) regressed on the
GMST anomaly; they found ~2/3 of 8,326 stations positive, 10.0% significant positive, 2.2% significant negative,
median 5.9-7.7 %/K over 1900-2009. Sun et al. 2021 (J. Climate 34:243), data to 2018: median 6.6 %/K (5.1-8.2).
Here: window Jan 1 - Oct 26, years 1979-2026, GMST = GISTEMP v4 Jan-Sep mean (same months every year).
Field significance by permuting GMST across years, one permutation for all stations (keeps spatial correlation).
Caveat: any monotone drift at a station (instrument, siting) also correlates with GMST; the null does not remove it.
Also: share of stations whose 2026 Rx1day is their 1979-2026 record, against the 1/n expected by chance."""
import json, os, sys, csv
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "stations.jsonl")
MINY = int(os.environ.get("MINY", 35))

def gmst():
    T = {}
    rows = list(csv.reader(open(os.path.join(HERE, "gistemp.csv"))))[2:]
    for r in rows:
        y = int(r[0]); v = r[1:10]
        if 1979 <= y <= 2026 and "***" not in v: T[y] = sum(map(float, v)) / 9
    return T

def kendall_z(x, y):
    n = len(x); s = 0
    for i in range(n - 1):
        s += np.sum(np.sign(x[i + 1:] - x[i]) * np.sign(y[i + 1:] - y[i]))
    return s / np.sqrt(n * (n - 1) * (2 * n + 5) / 18)

REG = [("Australia", -45, -10, 110, 155), ("Europe", 35, 72, -12, 45), ("N America", 24, 72, -170, -50),
       ("E Asia", 18, 55, 95, 150), ("S+SE Asia", -11, 30, 60, 125), ("Africa", -36, 36, -20, 52),
       ("S America", -56, 13, -82, -34)]

def region(la, lo):
    for n, a, b, c, d in REG:
        if a <= la <= b and c <= lo <= d: return n
    return "other"

def main():
    T = gmst()
    st = [json.loads(l) for l in open(SRC)]
    res = []
    for s in st:
        ys = sorted(int(y) for y, v in s["years"].items() if int(y) in T and v["rx1"] > 0)
        if len(ys) < MINY: continue
        x = np.array([T[y] for y in ys]); r = np.array([s["years"][str(y)]["rx1"] for y in ys])
        b = np.polyfit(x, np.log(r), 1)[0]
        rec = None
        if "2026" in s["years"]:
            allv = [v["rx1"] for v in s["years"].values()]
            rec = (s["years"]["2026"]["rx1"] >= max(allv), 1 / len(allv))
        res.append({"id": s["id"], "reg": region(s["lat"], s["lon"]), "n": len(ys), "pct": 100 * (np.exp(b) - 1),
                    "z": kendall_z(x, r), "x": x, "r": r, "ys": ys, "rec": rec})
    print("stations used", len(res), "of", len(st), "(>=%d valid years with GMST)" % MINY)
    def summ(rs, label):
        if not rs: return
        p = np.array([q["pct"] for q in rs]); z = np.array([q["z"] for q in rs])
        print("%-10s n=%4d median %+.1f %%/K  positive %.0f%%  sig+ %.1f%%  sig- %.1f%%" % (
            label, len(rs), np.median(p), 100 * np.mean(p > 0), 100 * np.mean(z > 1.96), 100 * np.mean(z < -1.96)))
    summ(res, "all")
    for n, *_ in REG + [("other",)]: summ([q for q in res if q["reg"] == n], n)
    # null: shuffle the GMST series across years (same permutation for all stations) -> share positive, sig+
    rng = np.random.default_rng(20261028); years = sorted(T); Tv = np.array([T[y] for y in years])
    obs_pos = np.mean([q["pct"] > 0 for q in res]); obs_med = np.median([q["pct"] for q in res])
    nul_pos, nul_med = [], []
    for _ in range(500):
        perm = dict(zip(years, rng.permutation(Tv)))
        bs = [np.polyfit([perm[y] for y in q["ys"]], np.log(q["r"]), 1)[0] for q in res]
        nul_pos.append(np.mean(np.array(bs) > 0)); nul_med.append(np.median(100 * (np.exp(bs) - 1)))
    print("null (years shuffled, 500x): share positive 95%% range %.2f-%.2f vs observed %.2f; median %%/K 95%% range %+.1f..%+.1f vs %+.1f" % (
        *np.percentile(nul_pos, [2.5, 97.5]), obs_pos, *np.percentile(nul_med, [2.5, 97.5]), obs_med))
    rc = [q["rec"] for q in res if q["rec"]]
    if rc:
        k = sum(a for a, _ in rc); e = sum(b for _, b in rc)
        print("2026 record Rx1day: %d of %d stations with 2026 data (expected %.1f by chance)" % (k, len(rc), e))
    json.dump([{k: v for k, v in q.items() if k not in ("x", "r", "ys")} for q in res],
              open(os.path.join(HERE, "result_ghcn.json"), "w"), default=float, indent=0)

if __name__ == "__main__":
    main()
