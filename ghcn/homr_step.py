"""Follow-up to homr_split.py (29.10, after seeing its output: stable +4.1, pm_to_am +11.4 %/K, intervals overlap).
Post-hoc checks, labelled as such:
1. switch years of the pm_to_am gauges;
2. stable split by its one class (AM / PM / MID);
3. pm_to_am slope with a step dummy at the first AM period (removes a level shift at the switch);
4. station bootstrap (resample gauges, 2000 draws, seed 1030) of median(pm_to_am) - median(stable)."""
import json, numpy as np
from collections import Counter
import homr_split as H
T = H.T; YEARS = H.YEARS; rng = np.random.default_rng(1030)
def switch_year(rec):
    per = sorted((p["begin"], H.cls(p["obs"])) for p in rec["precip"] if p.get("program") == "COOP SOD" and H.cls(p["obs"]))
    seenpm = False
    for b, c in per:
        if c == "PM": seenpm = True
        if c == "AM" and seenpm and int(b[:4]) >= 1979: return int(b[:4])
def onecls(rec):
    return Counter(H.cls(p["obs"]) for p in rec["precip"] if p.get("program") == "COOP SOD" and H.cls(p["obs"])).most_common(1)[0][0]
def step_slope(d, sy):
    ys = sorted(d); x = np.array([T[y] for y in ys]); s = np.array([1.0 if y >= sy else 0.0 for y in ys])
    A = np.c_[x, s, np.ones(len(ys))]; b = np.linalg.lstsq(A, np.log([d[y] for y in ys]), rcond=None)[0]
    return 100 * (np.exp(b[0]) - 1), 100 * (np.exp(b[1]) - 1)
sw = [(s, switch_year(H.H[s[0]])) for s in H.st if s[1] == "pm_to_am"]
print("switch years:", sorted(y for _, y in sw))
for c in ["AM", "PM", "MID"]:
    sel = [s for s in H.st if s[1] == "stable" and onecls(H.H[s[0]]) == c]
    if sel: print(f"stable {c:3s} n={len(sel):3d} median {H.med(sel, YEARS)[0]:+.1f} %/K")
st = [step_slope(s[2], y) for s, y in sw if y]
print(f"pm_to_am with step dummy: n={len(st)} median slope {np.median([a for a, _ in st]):+.1f} %/K, median step {np.median([b for _, b in st]):+.1f} %")
A = [H.slope(s[2], YEARS) for s in H.st if s[1] == "pm_to_am"]; B = [H.slope(s[2], YEARS) for s in H.st if s[1] == "stable"]
diff = sorted(np.median(rng.choice(A, len(A))) - np.median(rng.choice(B, len(B))) for _ in range(2000))
print(f"median(pm_to_am) - median(stable) = {np.median(A) - np.median(B):+.1f} (station bootstrap 5-95%: {diff[100]:+.1f}..{diff[1899]:+.1f})")
