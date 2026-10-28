# Pre-registration: China and Thailand, ERA5 point series (written 2026-10-28T10:25Z, before any data was fetched)

**Why ERA5:** NOAA's station feeds for China end in 2025. In GHCN-Daily, Beijing CHM00054511 has 233 days in 2025 and
none in 2026; 92 of 228 Chinese PRCP stations list 2025 as their last year. In GSOD, Beijing's last day is 2025-08-24 and
there is no 2026 directory. Thai GHCN stations are patchy (TH000048455: 103 days in 2026). So the only consistent 2026
series is reanalysis.

**Data:** Open-Meteo archive API, `models=era5`, daily precipitation_sum, 1979-01-01 to 2026-09-30. 30 Chinese and 12 Thai
city points (points.json, chosen for spread, not for known 2026 events). Window: 1 Jan–30 Sep, the same in every year.
Caveat: ERA5 underestimates absolute daily extremes. A point is ranked only against its own history.

**Metric:** per point, Rx1day = the window maximum of daily precipitation. The rank of 2026 is taken among 1979–2026
(48 years; ties broken against 2026). If years were exchangeable, the chance that 2026 is the record is 1/48 = 2.1%.

**Predictions:**
- P1: China: 2026 is the record at ≤ 3 of 30 points (≤ 10%).
- P2: Thailand: 2026 is the record at ≤ 2 of 12 points.
- P3: China: median percentile of 2026 among the 48 years lies between 0.35 and 0.80 (unremarkable).
- P4: China scaling, 1979–2025: log Rx1day regressed on the GISTEMP annual mean with point fixed effects (gistemp.csv as
  in ghcn/). Slope between -3 and +12 %/K. The 95% CI from a bootstrap over years contains 7 %/K.
- Null for P1/P2: binomial(n, 1/48). I will report the exact tail probability whatever the outcome.

**Addendum 2026-10-28T10:29Z, before any analysis (fetch still running, no data read):** the 2025 cutoff is not
specific to China. Tokyo JA000047662 also has 235 days in 2025 and none in 2026. GSOD has no 2026 directory at all.
So "NOAA China feeds end" should read: NOAA's international station feeds stop around mid-2025. Predictions unchanged.
