# 01_final_combined_version.md

**Project 3 - Cross-domain mortality signals and infectious-disease up-transitions, California counties**
Version of record: 2026-11-05 (v2: reflects the corrected pipeline run of 2026-11-04, plus the plan it came from).

> How to read this file. Sections marked **[PLAN]** are the design that was decided before modelling.
> Sections marked **[AS RUN]** are what the code did. Where they differ, the difference is listed in
> `07_deviations_log.md`. This file does not claim anything the results do not support.

## 1. Question [PLAN]

Does county-level mortality (drug overdose, suicide, homicide; all-cause as a benchmark) improve
out-of-sample prediction of next-year **up-transitions** in county infectious-disease burden, beyond
the disease's own history and local context? The study is **predictive, not causal**.

- RQ1: How well does a disease-history baseline (model A) predict up-transitions?
- RQ2: Does adding lagged / concurrent mortality (model B) improve on A, and is any gain specific to
  disease groups with a plausible link (drug-linked) rather than comparison diseases?
- RQ3: Is any gain stable under temporal (leave-future-out), spatial (block CV) and unseen-disease /
  unseen-group validation?

## 2. Unit, outcome, and transitions [PLAN] / [AS RUN]

- Unit: county x disease x year. California, 58 counties, years 2001-2023.
- Transition model (script `05_transitions.R`): negative binomial, RW2 trend, BYM2 spatial effect,
  county-specific RW2 deviations (space-time interaction), fitted per disease in R-INLA.
- Primary outcome **[PLAN]**: `upcross_0.80` - the posterior probability that the underlying trend is
  rising crosses 0.80 upward (sensitivity: 0.70 and 0.90).
- **[AS RUN, added after first results]**: `upcross_local_0.80` - the same crossing after removing the
  statewide change in each year (per posterior sample). Reason: the original outcome was dominated by
  the shared statewide trend, so events occurred in the same years everywhere. Both outcomes are kept.

## 3. Data [PLAN] / [AS RUN]

| Layer | Source | Status |
|---|---|---|
| Disease | CDPH county-year infectious-disease counts (Disease, County, Year, Sex, Cases, Population) | Used; 56 diseases screened, 16 pass the data gate (full window) |
| Mortality (primary) | CDC WONDER final counts, county-year 1999-2024: drug overdose, suicide, homicide, all-cause | Used; 23 usable overlap years, suppression handled in `01b_build_wonder_mortality.py` |
| Mortality (sensitivity) | NCHS model-based county estimates | **Not run** (listed as sensitivity in the plan) |
| Context | AHRF 2024-2025 (population), EPA annual AQI, US Drought Monitor (DSCI) | Used; physician supply dropped from models (about 96% missing) |
| Drug-linked diseases | County hepatitis B/C, injection-related infections | **Missing.** AtlasPlus hepatitis export is state-level only; the drug-linked group has 1 disease and 0 pass the gate |

## 4. Disease groups [PLAN] / [AS RUN]

Pre-set groups: drug-linked, ambiguous, environment-linked, comparison. Two review groups were added by
the draft rules in `03_disease_groups.py` (review_sti, review_travel). Groups used in modelling:
ambiguous (1 disease), comparison (8), environment (4), review_sti (2), review_travel (1) = 16 diseases.
**The drug-linked group is empty, so the central drug-linked vs comparison contrast cannot be tested.**

## 5. Models [PLAN] / [AS RUN]

| Model | Predictors | Notes |
|---|---|---|
| A | own history (`lag_rate`, `trend_slope`, `prev_up`) plus county population (`pop_log`) | baseline; **[AS RUN change]** population added because the first pass showed it explains the apparent mortality gain |
| B | A + lagged within-county mortality deviations (4 series) | the test of interest; **[AS RUN change]** levels and missing-flags removed |
| C | A + context (`aqi_median`, `drought_dsci`) | physician supply dropped (about 96% missing) |
| D | A + mortality + context | |

Fitted as binomial models in R-INLA with disease, county (BYM2) and year effects. **[AS RUN change]** the
year effect is `iid` (not RW2) so the hidden test year gets a neutral level.

## 6. Evaluation [PLAN] / [AS RUN]

- Leave-future-out: rolling test years (2017-2022 planned; **only 2017-2020 scored**, because 2021 and
  2022 have no local events).
- Headline metric **[AS RUN change]**: AUC computed within each year x disease cell and averaged with
  pair-count weights (`auc`); pooled AUC kept as `auc_pooled`. Brier and log loss also reported.
- County-cluster bootstrap (500) for delta-AUC vs A.
- Leave-one-disease-out (16), leave-one-group-out (5), spatial-block CV (6 blocks).
- Early warning at matched false-alarm rate (5%, 10%, 20%) plus an operational split-year variant.
- Lead-time test: mortality alarm (>= 1.0 / 1.5 SD above own trailing 5-year mean) vs events; county-swap
  permutation null (1000), Holm-adjusted.
- Nulls and checks: within-county year-shuffle (N1, **[AS RUN change]** from county-swap) and outcome-shuffle (N2)
  placebos (1000), surrogate diseases, residual Moran's I, confound check (`13_confound_check.py`), simulation
  (`04_simulation.py`).
- Multiplicity: Holm across groups (`12_multiplicity.py`).

## 7. Stop / go rules [PLAN]

- Stop if fewer than ~10 usable overlapping years of county mortality. **Result: 23 years, gate passed.**
- A group is "supported" only if the gain beats both placebo nulls after Holm correction and the surrogate
  diseases do not show the same gain.

## 8. Status of results [AS RUN, corrected run of 2026-11-04]

- Mortality adds no out-of-sample predictive value: B - A = +0.001 (95% CI -0.028 to +0.034); C - A = +0.003
  (-0.005 to +0.013); D - A = +0.003 (-0.028 to +0.037).
- No consistent transfer to held-out diseases (B: 7/16, sign p = 0.77) or groups (B: 2/5, p = 0.81).
- Spatial-block CV: B better than A in 2 of 6 blocks, C in 2 of 6, D in 1 of 6.
- No early-warning gain at any matched false-alarm rate (B at 20%: -7.4 points, CI -14.3 to 0.0).
- No lead-time signal (0/40 Holm-significant) and no supported group (0/4 tested).
- Context features (model C) show no lead any more (the earlier 5/6 blocks result came from the baseline lacking
  population).
- A first pass with the original outcome, levels and no population in A looked positive (B - A = +0.025;
  environment "supported"); the confound check shows that was county size (`00_docs/10_results_writeup.md` s.5).
- Power is low: 81 scored test events over 2017-2020 (CI width about +/-0.03).

Honest summary: **a well-controlled null result** on the tested design; the drug-linked hypothesis is untested
for lack of county-level data.

## 9. Folder layout [PLAN]

`00_docs`, `01_literature`, `02_data` (raw, interim, processed), `03_config`, `04_scripts`, `05_results`, `06_paper`.
Run order: `01_build_panel` -> `01b_build_wonder_mortality` -> `03_disease_groups` -> `02_data_gate` ->
`01c_build_analysis_panel` -> `05_transitions.R --full` -> `05b_build_model_table` -> `run_from_07.py --from 6`.
