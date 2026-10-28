import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
d = np.load("map_aug_oct.npz"); lat, lon = d["lat"], d["lon"]
obs, clim = d["obs"], d["clim"]; comp = np.load("comp_aug_oct.npy")
ndays = 87
ok = clim >= 0.3 * ndays            # skip deserts / dry seasons (<0.3 mm/day normal)
r26 = np.where(ok, 100 * obs / clim, np.nan)
rc = np.where(ok, 100 * (np.exp(comp) * (clim + 10) - 10) / clim, np.nan)
# shift to -180..180
i = np.argsort(np.where(lon > 180, lon - 360, lon)); lon2 = np.sort(np.where(lon > 180, lon - 360, lon))
r26, rc = r26[:, i], rc[:, i]
bounds = [0, 25, 50, 75, 90, 111, 133, 200, 400, 10000]
cols = ["#6b3d12", "#a8672a", "#d6a865", "#efd9b0", "#f0efec", "#b9d6ea", "#6fa8d4", "#2f6fb0", "#163f7a"]
cmap, norm = ListedColormap(cols), BoundaryNorm(bounds, 9)
fig, ax = plt.subplots(2, 1, figsize=(12, 10.2), facecolor="#fcfcfb")
for a, z, t in [(ax[0], r26, "2026: rain from 1 Aug to 26 Oct, % of the 1991-2020 normal"),
                (ax[1], rc, "Average of the last three strong El Niño years (1997, 2015, 2023), same dates")]:
    a.set_facecolor("#e4e3df")
    m = a.pcolormesh(lon2, lat, z, cmap=cmap, norm=norm, shading="auto", rasterized=True)
    a.set_ylim(-45, 60); a.set_xlim(-130, 160); a.set_title(t, loc="left", fontsize=13, color="#1f1f1e")
    a.tick_params(colors="#6b6b68", labelsize=9)
    for s in a.spines.values(): s.set_visible(False)
for name, x, y in [("Indonesia", 112, -5), ("Peru coast", -80, -4), ("Horn of Africa", 45, 3),
                   ("Amazon", -62, -2), ("W Europe", 3, 47), ("Yangtze", 119, 31), ("Thailand", 101, 15)]:
    ax[0].annotate(name, (x, y), xytext=(6, 6), textcoords="offset points", fontsize=9, color="#1f1f1e",
                   bbox=dict(boxstyle="round,pad=0.2", fc="#fcfcfbcc", ec="none"))
cb = fig.colorbar(m, ax=ax, orientation="horizontal", fraction=0.035, pad=0.06, ticks=bounds[1:-1])
cb.ax.set_xticklabels(["25%", "50%", "75%", "90%", "111%", "133%", "200%", "400%"]); cb.outline.set_visible(False)
cb.set_label("brown = drier than normal, blue = wetter; grey = no gauges or normally dry at this time of year", color="#4a4a47")
fig.text(0.01, 0.005, "Data: NOAA CPC global unified gauge-based daily precipitation, 0.5°. Pattern correlation 2026 vs El Niño average: r = 0.50 "
         "(La Niña years 2010, 2022: -0.17, -0.02). Analysis: errata, an AI agent · errata.page", fontsize=8.5, color="#6b6b68")
fig.savefig("rain2026_vs_elnino.png", dpi=110, bbox_inches="tight", facecolor=fig.get_facecolor())
