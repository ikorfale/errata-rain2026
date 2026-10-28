# Addendum to PREREG-ghcn.md: observed scaling vs climate-model scaling

Written 2026-10-28 before the full GHCN-Daily run started (the fetch job was still queued; no station file of the
full run read). The commit time is the timestamp. It adds one comparison; the five predictions in PREREG-ghcn.md are unchanged.

**Question.** A common public frame is that observed extremes run "worse than the models". For heavy daily rain, is the
observed station scaling of Rx1day with global temperature above what climate models give?

**Model reference values** (all %/K of global mean surface warming, land):
- IPCC AR6 WG1 Ch. 11: Rx1day changes about +7 %/K; CMIP6 multi-model median for 10- and 50-year return values +5 to +6 %/K.
- CMIP6 land, Rx1day scaled by GSAT (Sci. direct S2212094722000238, table): 10% / 50% / 90% quantiles 1.5 / 5.8 / 11.1 %/K.
- Earlier observation-vs-model work: Asadieh & Krakauer 2015 (HadEX2, 1901-2010) observed 10 %/K vs CMIP5 mean 8.3 %/K;
  Borodina, Fischer & Knutti 2017: models likely underestimate the increase in extratropical regions with high intensity.

**Prediction 6.** The observed station median (`analyze_ghcn.py`, all stations) lies within 5.8 ± 3 %/K (2.8 to 8.8).
- Above 8.8: the stations scale faster than the CMIP6 land median, in line with Asadieh & Krakauer and Borodina.
- Above 11.1 (the CMIP6 90% land quantile): only then would "worse than the models" be the right words for this field.
- Below 2.8: slower than models.
The width of the year-permutation null for the median (printed by the script) is reported next to the answer as its noise
scale; a gap smaller than that width is called "not distinguishable", whatever side it falls on.

**Known weaknesses.** Model numbers are per-gridcell area means for 21st-century warming; station Rx1day over 1979-2026
is a point value with a short record. Station siting drift correlates with GMST. GMST (GISTEMP) is used, not GSAT; the
difference is small next to the noise. This compares a field median, it is not a detection study.
