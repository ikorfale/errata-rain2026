"""Fable check 28.10: remove the real-time-era fingerprint (mean anomaly of 2006-2025 years with ONI < 0.5)
from every 2006+ year, rebuild the composite, rerank; r(2026, 1997 alone); ONI fit without composite years."""
import json, numpy as np
exec(open("null_rank.py").read().split("rows = []")[0])
assert all(int(T[y]["ndays"]) == 87 for y in YRS)
oni_y = {y: (oni.get(y, {}).get("ASO", oni.get(y, {}).get("JAS"))) for y in YRS}
era = [y for y in range(2006, 2026) if oni_y[y] is not None and oni_y[y] < 0.5]
fp = np.nanmean([anom[y] for y in era], axis=0)
adj = {y: (anom[y] - fp if y >= 2006 else anom[y]) for y in YRS}
out = {"era_years": era}
for label, A in (("raw", anom), ("era_removed", adj)):
    rows = []
    for y in YRS:
        if label == "era_removed" and y in era: continue      # these define the fingerprint
        others = [e for e in EN if e != y]
        comp = sum(A[e] for e in others) / len(others)
        m = base & ok[y] & np.all([ok[e] for e in others], axis=0) & np.isfinite(fp)
        rows.append((wcorr(A[y][m], comp[m], w_all[m]), y))
    rows.sort(reverse=True)
    nonc = [(r, y) for r, y in rows if y not in EN]
    out[label] = {"top5_non_composite": [(y, round(r, 3)) for r, y in nonc[:5]],
                  "rank_2026_among_non_composite": [y for r, y in nonc].index(2026) + 1, "n_non_composite": len(nonc)}
    m = base & ok[2026] & ok[1997]
    out[label]["r_2026_vs_1997_alone"] = round(wcorr(A[2026][m], A[1997][m], w_all[m]), 3)
    pts = [(oni_y[y], r) for r, y in rows if y not in EN and y != 2026 and oni_y[y] is not None]
    a = np.array(pts); out[label]["r_oni_excl_composite_and_2026"] = round(float(np.corrcoef(a[:, 0], a[:, 1])[0, 1]), 3)
json.dump(out, open("null_era.json", "w"), indent=1); print(json.dumps(out, indent=1))
