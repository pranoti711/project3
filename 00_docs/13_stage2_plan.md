# 13_stage2_plan.md - Stage 2 (EXPLORATORY): neighbour-county and socioeconomic layer

Write the date and git commit of this file BEFORE running stage 2: **FILL date / commit**.

## Status
Stage 1 (own history + population, mortality deviations, context) is frozen and reported as a null result. Stage 2
adds the parts of the original plan that were not built. The 2017-2020 test years were already seen in stage 1, so
every stage 2 result is **exploratory** and must be labelled that way in any write-up.

## Questions (fixed before running)
- S1: Do neighbouring counties' recent disease history, air quality, drought and static county traits improve
  prediction of a county's up-transitions beyond model A? (model C)
- S2: Do neighbouring counties' lagged mortality deviations, added to the county's own, improve prediction beyond
  model A? (model B)

## Features (built by `04_scripts/05c_add_stage2_features.py`; all known at year t)
| Block | Columns | Notes |
|---|---|---|
| Neighbour history (in C, D) | nbr_lag_rate, nbr_trend_slope, nbr_prev_up | unweighted mean over adjacent counties, same disease and year |
| Neighbour mortality (in B, D) | nbr_allcause_dev, nbr_drug_od_dev, nbr_suicide_dev, nbr_homicide_dev | one pooled slope each (not per group) |
| Static traits (in C, D) | urban_pct, median_age, log_density, rural_urban | AHRF 2020/2023 vintage, time-invariant |
| Optional (in C, D) | poverty_l1, unemp_l1 | only if `02_data/raw/socio/saipe_ca_county.csv` and `laus_ca_county.csv` exist; value of year t-1 |

Models: A is unchanged from stage 1 (own history + population). B = A + own mortality deviations + neighbour
mortality deviations. C = A + stage 1 context + the neighbour-history and socioeconomic columns. D = all.

## Contrasts and decision rule (fixed now)
- Primary contrasts: B - A (S2) and C - A (S1), within year x disease AUC, county-cluster bootstrap (500).
- Holm correction over these 2 contrasts. A contrast counts as "suggestive" only if its CI excludes 0 AND it also
  beats the stage 1 placebos in `11_placebos_surrogates.py` (run in stage 2 mode).
- Anything else (group-level gains, single diseases, other features) is descriptive only.
- No new features, thresholds or test years may be added after seeing stage 2 results; if they are, log them in
  `07_deviations_log.md` as a further exploratory step.

## Interpretation limits (write these in the report)
- Test years are the same as stage 1 (2017-2020, 81 events). Power is low.
- A positive result is a hypothesis for new data, not a finding.
- Static traits are county characteristics; the INLA models already contain a spatial county effect.
