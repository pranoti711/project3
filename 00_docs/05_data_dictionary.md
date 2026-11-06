# 05_data_dictionary.md

Paths are relative to the project3 root. Rates are per 100,000 unless stated.

## 1. `02_data/processed/analysis_long.csv` (one row per county x disease x year, Total sex)
| Column | Meaning |
|---|---|
| fips | 5-digit county FIPS (string, zero-padded) |
| county | county name (no "County") |
| year | calendar year, 2001-2023 |
| disease, disease_slug | disease name; slugged name (max 40 chars) |
| cases | reported cases (Cases_n; NA if suppressed) |
| cases_suppressed | flag for suppressed cell |
| population_cdph | population denominator from the CDPH file |
| source_file | disease file the row came from |
| group | disease group (frozen file if present, else draft; `unassigned` if none) |
| mort_<series>_count / _lo / _hi / _suppressed / _rate | WONDER deaths, interval bounds, suppression flag, crude rate; series = all_cause, drug_od, suicide, homicide |
| ahrf_* | AHRF static (rural-urban, urban %, median age, area, population) and time-varying (hospitals, beds, primary-care physicians, poverty, unemployment, HPSA) |

## 2. `02_data/processed/transitions.csv` (output of `05_transitions.R`)
| Column | Meaning |
|---|---|
| fips, year, disease, group | keys |
| p_rising | posterior probability the underlying trend is rising |
| p_rising_local | same after removing the statewide change in that year |
| slope_sd | posterior sd of the year-to-year change |
| above_0.70 / 0.80 / 0.90 | 1 if p_rising >= threshold |
| upcross_0.70 / 0.80 / 0.90 | 1 if above now and not above in the previous year (**primary outcome at 0.80**) |
| above_local_*, upcross_local_* | same, using p_rising_local |

Other posterior-summary columns may be present; see the script. First year per county has `upcross` missing.

## 3. `02_data/processed/model_table.csv` / `model_table_local.csv` (output of `05b_build_model_table.py`)
One row per county x disease x year t; `up` is the transition from t to t+1.
| Column | Meaning | Known at t? |
|---|---|---|
| county, fips, year, disease, group | keys | yes |
| up | outcome: next-year up-crossing (0/1) | no (target) |
| lag_rate | case rate per 100k in year t | yes |
| trend_slope | case rate in t minus rate in t-1 (NA if gap) | yes |
| prev_up | up-crossing flag in year t | yes |
| allcause_rate, drug_od_rate, suicide_rate, homicide_rate | WONDER crude mortality rate in year t | yes |
| aqi_median | EPA annual median AQI | yes |
| drought_dsci | mean weekly Drought Severity and Coverage Index (D0-D4 weighted 1-5) | yes |
| physicians_per_100k | AHRF non-federal primary-care physicians per 100k | yes |
| pop_log | log of CDPH population | yes |

Local run: 19,938 rows, 16 diseases, event rate 0.0216. `model_table_original.csv` uses `upcross_0.80`.

## 4. Result tables (`05_results/tables/`)
| File | Columns |
|---|---|
| oof_predictions_lfo.csv | county, fips, year, disease, group, up, model, p |
| calibration_by_year.csv | year, events, rate, mean_p (model A) |
| model_scores_lfo.csv | scope, model, n, events, **auc** (within year x disease), auc_pooled, brier, logloss |
| model_delta_auc_lfo.csv | scope, model, delta_auc vs A, lo, hi (95% county-cluster bootstrap) |
| validation_lodo.csv / validation_logo.csv | unit_type, unit, group, model, n, events, auc, auc_pooled, brier, logloss |
| validation_summary.csv | scheme, model, n_units, mean/median delta_auc, n_improved, sign_test_p |
| spatial_block_cv.csv, county_blocks.csv | block-level scores; county-to-block map |
| residual_moran.csv | model, year, I, p, scope |
| leadtime_summary.csv | zthr, mortality, group, n_events, n_nonevents, p_alarm_event, p_alarm_nonevent, diff, null_mean, perm_p_one_sided, median_lead_years, perm_p_holm |
| early_warning_matched_far.csv | model, far, hit_rate (+CI), gain_vs_A (+CI), n_events, n_nonevents, scope |
| early_warning_operational.csv | model, target_far, threshold, realised_far, hit_rate, calibration_years, evaluation_years |
| placebo_group_tests.csv | group, observed_delta_auc, n1_null_mean, n1_p, n2_null_mean, n2_p, perms |
| placebo_group_tests_holm.csv | adds n1_p_holm, n2_p_holm, supported |
| placebo_disease_delta.csv | disease, group, events, delta_auc |
| transition_counts_by_disease / _group.csv | group, disease, county_years, events, event_share |
| data_gate_disease_screen.csv | window, disease, years_present, missing_pct, zero_pct, usable_counties, g2_counties, g3_missing, g4_zeros, pass_2_3_4 |

## 5. Definitions
- **Up-transition**: Pr(trend rising) crosses the threshold upward between consecutive years.
- **Local up-transition**: same, after subtracting the county-average change in that year.
- **auc (headline)**: AUC inside each (year, disease) cell, averaged weighted by events x non-events.
- **Matched false-alarm rate**: alarm threshold set per model so each raises the same share of false alarms.
- **Groups**: ambiguous, comparison, environment, review_sti, review_travel (drug_linked empty).
