import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows = [  # label, est, lo, hi, kind
 ("Rx1day, median station (this study)", 3.6, 1.2, 6.2, "me"),
 ("Rx1day, regions weighted equally", 4.6, 0.9, 7.7, "me"),
 ("Rx1day, pooled normalised", 3.0, 1.1, 4.8, "me"),
 ("Rx5day, median station", 2.9, -0.4, 5.5, "me"),
 ("Sun et al. 2021, Rx1day, 1950-2018", 6.6, 5.1, 8.2, "lit"),
 ("Sun et al. 2021, Rx5day", 5.7, 5.0, 8.0, "lit"),
 ("Westra et al. 2013, Rx1day (range over methods)", None, 5.9, 7.7, "lit"),
]
ink, mut, me, lit = "#1f2328", "#6e7781", "#2a6fdb", "#8c959f"
fig, ax = plt.subplots(figsize=(10, 4.6), dpi=150)
for i, (lab, e, lo, hi, k) in enumerate(rows):
    y = len(rows) - 1 - i; c = me if k == "me" else lit
    ax.plot([lo, hi], [y, y], color=c, lw=2, solid_capstyle="round")
    if e is not None: ax.plot(e, y, "o", ms=8, color=c, mec="white", mew=2)
    ax.text(hi + 0.25, y, ("%+.1f" % e) if k == "me" else ("%.1f" % e if e is not None else "%.1f-%.1f" % (lo, hi)), va="center", fontsize=9, color=ink)
ax.axvline(7, color=mut, lw=1, ls="--"); ax.text(7.1, -0.75, "Clausius-Clapeyron ~7 %/K", fontsize=8.5, color=mut)
ax.axvline(0, color=mut, lw=0.8)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=9.5, color=ink)
ax.set_xlabel("change in yearly maximum rain per 1 °C of global warming (%)", fontsize=9.5, color=ink)
ax.set_xlim(-2, 11); ax.set_ylim(-1, len(rows) - 0.5)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.tick_params(colors=mut, length=0); ax.grid(axis="x", color="#eaeef2", lw=0.8); ax.set_axisbelow(True)
fig.suptitle("Heavy rain at 427 long gauges, 1979-2026, per degree of warming (90% intervals)", x=0.01, ha="left", fontsize=11, color=ink)
fig.text(0.01, 0.01, "Blue: this study (GHCN-Daily, Jan 1-Oct 26 window, year-block bootstrap). Grey: published estimates. errata.page",
         fontsize=7.5, color=mut)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("rain_scaling.png")
