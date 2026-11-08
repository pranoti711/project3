# 07_deviations_log.md

## California hepatitis indicators are descriptive-only at state level

- **Decision date:** 2026-10-29
- **Decision:** Retain the available California AtlasPlus hepatitis A and acute
  hepatitis B/C annual series for a separate state-level descriptive summary.
- **Reason:** The available export contains California in its title metadata but
  has no county or FIPS column. AtlasPlus marks these indicators as region-level;
  they cannot be joined to the county-year panel or distributed among counties.
- **Implementation:** The panel builder writes
  `02_data/processed/hepatitis_ca_state_annual.csv` separately. These series are
  excluded from county-level disease tables and models. The source covers acute
  hepatitis B/C, not chronic hepatitis B/C burden.
- **County-level status:** No county-level hepatitis A/B/C series is available
  from this export. County-level hepatitis analyses remain out of scope unless a
  valid county source is supplied and the deviation is updated.

## Mortality-overlap gate: five-year deviation withdrawn

- **Date withdrawn:** 2026-11-02
- **Earlier decision (2026-10-30):** used 5 usable overlap years instead of the
  registered 10.
- **Why withdrawn:** Gate 1 shows 23 usable overlap years (1999-2024 mortality vs
  2001-2023 disease data) for all four mortality series, so the registered
  threshold of 10 is met. The deviation was not needed.
- **Implementation:** `03_config/gate_thresholds.json` now sets
  `min_overlap_years = 10`, equal to the registered value. `02_data_gate.py` was
  re-run and prints no deviation.

## Predictive-model scoring and year effect (changed after seeing first results)

- **Date:** 2026-11-02
- **What changed:** (1) Headline AUC is now computed within each year x disease
  cell and averaged with pair-count weights (`auc_strat`); pooled AUC is kept as
  `auc_pooled`. (2) The year term in the predictive models changed from RW2 to iid
  so the hidden test year gets a neutral level (`--year_effect=rw2` restores it).
  (3) A second outcome, `upcross_local_0.80`, removes the statewide change in each
  year; results are reported for both outcomes.
- **Reason:** First run gave pooled AUC of 0.355 (< 0.5) because predicted
  year-level event rates did not match observed ones (for example 2020: observed
  51.7%, predicted 0.1%). Within-disease-year AUC was 0.72.
- **Note:** This change was made after looking at the first results, so it is
  reported as a post-hoc analysis choice, not as pre-registered.

## Corrective re-run: population baseline, mortality deviations, new placebo null (changed after seeing results)

- **Date:** 2026-11-04 (scripts patched and full pipeline re-run the same day)
- **Trigger:** The run on `model_table.csv` (the original statewide-trend outcome, event rate 0.139) gave
  small positive mortality gains (pooled B - A = +0.025, 95% CI -0.015 to +0.065; environment group
  "supported" after Holm). Inspection showed that (a) that table was the original outcome, in which 480 of
  745 test events fall in 2020; (b) model A had no population term while model C (which has `pop_log`)
  gained most; (c) mortality is suppressed (missing) for 43% of county-year rows for drug overdose and
  suicide and 66% for homicide, concentrated in small counties, so the `_miss` flags acted as a
  small-county indicator; (d) the county-swap placebo cannot separate mortality from a time-invariant
  county trait such as size.
- **What changed (all in code, all re-run):**
  1. `pop_log` moved into the baseline (HIST) so B/C/D are compared with an A that already knows county size
     (`p3_common.R`, `11_placebos_surrogates.py`).
  2. Mortality enters as lagged within-county deviations (`allcause_dev`, `drug_od_dev`, `suicide_dev`,
     `homicide_dev` = rate in t-1 minus the county's own mean over t-6..t-2, at least 3 years), built in
     `05b_build_model_table.py`. Levels are kept in the table for `07_leadtime.R` only.
  3. Mortality missing-value indicators removed (missing deviation = 0 after standardising).
  4. `physicians_per_100k` removed from the context set: about 96% missing, so it was a constant.
  5. Placebo N1 changed from county-swap to a within-county shuffle of the mortality-deviation series across
     years. N2 (outcome shuffle within year x disease) and the surrogate-disease test are unchanged.
  6. New diagnostic `13_confound_check.py` (fast logistic stand-in; direction only, not exact AUC).
- **Headline outcome:** `upcross_local_0.80` on `model_table_local.csv`. The original-outcome run is kept in
  `05_results_origoutcome_run/` and reported only as the explanation of why a first pass looked positive.
- **Result of the corrected run:** pooled B - A = +0.001 (95% CI -0.028 to +0.034); no group supported after
  Holm; 0 of 40 lead-time tests significant after Holm.
- **Status:** post-hoc. These are corrections made after seeing results and are reported as such.

## Groups tested in the placebo step

- **Date:** 2026-11-04
- **Observation:** The `review_travel` group (Malaria only) has 4 scored events in 2017-2020 and `ambiguous`
  (Early Syphilis) has 8. Script 11 tests 4 groups (comparison, review_sti, environment, ambiguous); the
  `review_travel` group is left out of the placebo tests, so Holm is over 4 groups, not 5.
- **Reason:** too few events for a stable within-year AUC difference.
- **Consequence:** the placebo floor is p of about 0.001 and 0.004 after Holm over 4 groups.

## Scoring window

- **Date:** 2026-11-04
- **Observation:** The local outcome has 0 events in 2001, 2021 and 2022 (smoother edge effects), so only
  2017-2020 are scored (81 events). Script 06 skips 2021 and 2022 with a message. This is the "test years
  reduced to 2017-2020" change in `04_prereg.md` A3.

## Outcome depends on estimate precision (observed after the corrected run)

- **Date:** 2026-11-06
- **Observation:** Because an event requires the posterior probability of a rise to reach 0.80, small counties
  (wider posteriors) rarely cross it. Median slope uncertainty is 0.134 in the smallest population quartile and
  0.080 in the largest; local-outcome event rates are 1.1% and 2.8%. Uncertainty also widens at the end of the
  series, which explains the zero events in 2022-2023.
- **Consequence:** reported as a limitation. No analysis choice was changed. A threshold-sensitivity check (tau 0.70
  and 0.90, same pipeline settings) is run as a robustness check and is not a replacement for the headline result.

## Stage 2 declared exploratory

- **Date:** 2026-11-06
- **What:** Neighbour-county features (own-disease history and mortality deviations of adjacent counties) and static
  county socioeconomic traits, as listed in `00_docs/13_stage2_plan.md`.
- **Status:** exploratory. The 2017-2020 test years were already seen in stage 1, so stage 2 results cannot be
  confirmatory. They are reported separately from the stage 1 headline result and labelled exploratory.
- **Freeze:** stage 1 results are tagged `stage1-freeze` in git (`tools/git_freeze.ps1`) before stage 2 is run.

## Stage 2 run (exploratory)

- **Date:** 2026-11-08
- **What:** Full pipeline run with the stage 2 features on `model_table_stage2.csv` (neighbour-county history and
  mortality deviations, static county traits). Poverty and unemployment were not available and were skipped.
- **Result:** no gain over model A (pooled B - A +0.006, C - A -0.011, intervals include 0); no group supported after
  Holm; lead-time results unchanged (step 07 does not use the new features). Results kept in `05_results_stage2/`.
- **Note:** step 13 ran with `--n_test 4` (the runner's default), so its output is the 31-event window; the 81-event
  checks are in `confound_check_n6_*.csv`.

## Known limitations

- Transition labels come from a smoother fitted on all years up to 2023 (hindsight). A fully clean forecast
  evaluation would refit the transition model at each forecast origin.
- Mortality is the lagged within-county deviation and uses final CDC data; final counts are published one to
  two years late, so this is an association study, not an operational early-warning system.
- Only 81 events are scored; the study has low power for small effects.
- Time-varying poverty and unemployment are not in the AHRF extract before 2022 (about 9% non-missing), so stage 2 uses static
  county traits unless the optional SAIPE/LAUS files are added.