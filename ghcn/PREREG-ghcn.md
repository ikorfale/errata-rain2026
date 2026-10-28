# Pre-registration: Rx1day vs global temperature on long GHCN-Daily stations

Written before any station file of the full run was read (only a 3-station code test). The commit time is the timestamp.

**Data.** GHCN-Daily, one station per 2.5° cell with PRCP from 1979 or earlier to 2026 (714 candidates), quality-flagged days dropped,
window 1 Jan – 26 Oct each year, a year counts with ≥90% valid days. Stations with ≥35 valid years enter.
GMST = GISTEMP v4 Jan–Sep mean. Code: `fetch.py`, `analyze_ghcn.py` (this commit).

**References I will compare with:** Westra, Alexander & Zwiers 2013 (8,326 stations, 1900–2009): about 2/3 positive,
10.0% significant positive, 2.2% significant negative, median 5.9–7.7 %/K. Sun et al. 2021 (to 2018): median 6.6 %/K (5.1–8.2).

**Predictions** (each is right or wrong; I will report all five):
1. Median scaling of Rx1day with GMST lies between +2 and +12 %/K (point guess +6).
2. Share of stations with positive scaling is between 55% and 70%.
3. Significant positive share (Kendall |z|>1.96) is larger than significant negative share, and lies between 6% and 15%.
4. Observed share positive lies above the 97.5th percentile of the year-permutation null.
5. Stations whose 2026 Rx1day is their 1979–2026 record number at least 1.3× the count expected by chance (sum of 1/n);
   CPC gridded data gave about 2× (9.5% vs 4.8% of land), so a ratio under 1.3 means the station data do not back that.

**Known weakness, stated now:** any monotone drift at a station (instrument, siting) correlates with GMST; the
permutation null does not remove it. 47 years is a short record, so per-station tests are weak; the result is about the field.
