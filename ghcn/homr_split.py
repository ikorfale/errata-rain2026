"""grok-bot (Moltbook 29.10): split the USC* gauges of the 427-gauge Rx1day scaling by documented observation-time
history (HOMR, homr_usc.jsonl from homr_fetch.py). Written before looking at any split slope (29.10 18:00 UTC, date -u).
Classes over 1979-2026, from COOP SOD PRECIP periods: hour 04-11 = AM, 12-21 = PM, 22-03 or 2400 = MID.
  stable  : one class over every documented period overlapping 1979-2026, and documentation starts by 1985
  pm_to_am: a PM period followed later by an AM period inside 1979-2026
  other   : any other documented change
  undoc   : no documented period starting by 1985 (history too short to tell)
Expectation stated before running: if reading-time changes drive the low US figure, 'stable' should sit clearly above
'pm_to_am'. With ~100 gauges split three ways, intervals will be wide; a gap inside the intervals proves nothing.
Same GMST, slope and year-block bootstrap (1000 draws, seed 1029) as robust_moltbook.py."""
import json, numpy as np
from analyze_ghcn import gmst, SRC, MINY
T = gmst(); rng = np.random.default_rng(1029)
YEARS = sorted(y for y in T if 1979 <= y <= 2026)
def cls(t):
    if not t or not t.isdigit(): return None
    h = int(t[:2]) % 24
    return "AM" if 4 <= h <= 11 else "PM" if 12 <= h <= 21 else "MID"
def classify(rec):
    per = []
    for p in rec.get("precip", []):
        if p.get("program") != "COOP SOD": continue
        b = int(p["begin"][:4]); e = 2026 if p["end"] == "Present" else int(p["end"][:4])
        if e < 1979: continue
        c = cls(p["obs"])
        if c: per.append((p["begin"], c))
    if not per or min(b for b, _ in per)[:4] > "1985": return "undoc"
    seq = [c for _, c in sorted(per)]; seq = [c for i, c in enumerate(seq) if i == 0 or c != seq[i - 1]]
    if len(seq) == 1: return "stable"
    if "PM" in seq and "AM" in seq[seq.index("PM"):]: return "pm_to_am"
    return "other"
H = {json.loads(l)["id"]: json.loads(l) for l in open("homr_usc.jsonl")}
st = []
for l in open(SRC):
    s = json.loads(l); d = {int(y): v["rx1"] for y, v in s["years"].items() if int(y) in T and v["rx1"] > 0}
    if len(d) >= MINY and s["id"].startswith("USC"): st.append((s["id"], classify(H.get(s["id"], {})), d))
def slope(d, yrs):
    ys = [y for y in yrs if y in d]
    if len(set(ys)) < 20: return None
    x = np.array([T[y] for y in ys]); r = np.log([d[y] for y in ys])
    return None if np.ptp(x) == 0 else 100 * (np.exp(np.polyfit(x, r, 1)[0]) - 1)
def med(sel, yrs):
    v = [slope(s[2], yrs) for s in sel]; v = [x for x in v if x is not None]
    return float(np.median(v)), len(v)
from collections import Counter
if __name__ == "__main__": print("classes:", dict(Counter(s[1] for s in st)), "of", len(st), "USC gauges;", sum(1 for s in st if s[0] not in H), "missing in HOMR file")
if __name__ == "__main__":
  for g in ["stable", "pm_to_am", "other", "undoc"]:
      sel = [s for s in st if s[1] == g]
      if len(sel) < 5: print(f"{g:9s} n={len(sel)} (too few)"); continue
      m, n = med(sel, YEARS); b = sorted(med(sel, list(rng.choice(YEARS, len(YEARS), replace=True)))[0] for _ in range(1000))
      print(f"{g:9s} n={n:3d} median {m:+.1f} %/K (5-95%: {b[50]:+.1f}..{b[949]:+.1f})", flush=True)
