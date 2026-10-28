# Result: China and Thailand, ERA5 points (scored 2026-10-28T10:36Z against PREREG-era5asia.md)

Data: 30 Chinese points and 11 of 12 Thai points. Chanthaburi was not fetched: the free API's hourly limit was reached
and I stopped instead of retrying. Window 1 Jan–30 Sep, 1979–2026. Output: run.out, result.json.

- **P1 holds.** China: 2026 is the Jan–Sep Rx1day record at 0 of 30 points (0.62 expected by chance).
- **P2 holds.** Thailand: 0 of 11 (0.23 expected).
- **P3 holds.** China median percentile of 2026: 0.43, an ordinary year. Thailand 0.60.
- **P4 holds, but tells us little.** China scaling 1979–2025: -1.5 %/K, 95% CI over years -12.2 to +7.1. The CI includes
  7 %/K only because it is wide. ERA5 at 30 points cannot resolve the scaling, so the stations in ghcn/ remain the
  measurement.

Reading: in reanalysis, 2026 was not an extreme-rain year at any of these Chinese or Thai cities. This matches the gridded
CPC result for East Asia (3.8% of land with a 2026 record, not a record share). ERA5 smooths daily extremes: Beijing's
2023 Doksuri maximum is 83.7 mm/day at this point (I have not compared it with station records here). So the ranks compare each point with itself, and
the absolute values mean nothing.
