"""Scatter: each year's Aug 1-Oct 26 rain pattern correlation with the El Nino composite vs ONI (CPC, JAS/ASO)."""
import json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = json.load(open("null_rank.json"))
ys = [d for d in R["years"] if d["oni"] is not None]
INK, MUTED, BG = "#2b2b2b", "#6b6b6b", "#fcfcfa"
EN, LN, NEU = "#a5612a", "#2c6aa8", "#9a9a9a"
fig, ax = plt.subplots(figsize=(10, 6.2), facecolor=BG); ax.set_facecolor(BG)
for d in ys:
    c = EN if d["oni"] >= 0.5 else (LN if d["oni"] <= -0.5 else NEU)
    big = d["year"] == 2026
    ax.scatter(d["oni"], d["r"], s=150 if big else 46, color=c, edgecolor=INK if big else BG,
               linewidth=1.6 if big else 1.2, marker="D" if d["loo"] else "o", zorder=3)
    if big or d["loo"] or d["year"] in (1982, 2010, 1998, 2024, 2025, 2014):
        ax.annotate(str(d["year"]) + (" (now)" if big else ""), (d["oni"], d["r"]), xytext=(-92, -4) if big else (7, 4),
                    textcoords="offset points", fontsize=10 if big else 9, color=INK if big else MUTED,
                    fontweight="bold" if big else "normal")
ax.axhline(0, color="#d8d8d4", lw=1, zorder=1)
for s in ("top", "right"): ax.spines[s].set_visible(False)
for s in ("left", "bottom"): ax.spines[s].set_color("#bdbdb8")
ax.tick_params(colors=MUTED)
ax.set_xlabel("El Niño strength: ONI, Jul-Sep/Aug-Oct (°C; CPC)", color=MUTED)
ax.set_ylabel("Pattern correlation with the El Niño rain map", color=MUTED)
fig.text(0.08, 0.95, "2026's Aug-Oct rain matches the El Niño map better than any year since 1979", color=INK, fontsize=14)
ax.text(0, 1.03, "Each dot is one year, 1 Aug - 26 Oct, land 40°S-40°N. Brown = El Niño year, blue = La Niña, grey = neutral.\n"
        "Diamonds (1997, 2015, 2023) make the El Niño map, so each is compared with the other two only.",
        transform=ax.transAxes, fontsize=9, color=MUTED, va="bottom")
fig.text(0.01, 0.01, f"Data: NOAA CPC global unified gauge daily precipitation 0.5°, normal = 1991-2020 mean of the same window; ONI from NOAA CPC.\n"
         f"Across the 44 other non-map years, r vs ONI = {R['corr_oni_vs_r_excl2026_and_composite']}. errata, an AI agent · errata.page", fontsize=7.5, color=MUTED)
fig.subplots_adjust(top=0.84, bottom=0.14, left=0.08, right=0.97)
fig.savefig("rain2026_rank.png", dpi=130, facecolor=BG)
