# 02_phase0_audit.md - Data and pipeline audit

Audit date: 2026-11-03; status updated 2026-11-05 after the corrected run. Scope: everything needed before the cross-domain result can be believed.
Status key: PASS / FAIL / PARTIAL / OPEN.

## A. Data gate (from `02_data_gate.py`, `data_gate_disease_screen.csv`)

| Check | Result | Status |
|---|---|---|
| Counties | 58 | PASS |
| Gate 1 - usable overlapping mortality years (registered: >= 10) | 23 for all four series (1999-2024 mortality vs 2001-2023 disease) | PASS |
| Gates 2-4 - diseases passing missingness / zero rules, full window 2001-2023 | 16 of 56 | PARTIAL |
| Same, window 2019-2023 | 18 of 56 | PARTIAL |
| Gate 5 - at least 3 diseases per group (proxy) | comparison 8 of 11 pass, environment 4 of 15 pass; ambiguous 1, review_sti 2, review_travel 1, **drug_linked 0** | **FAIL for drug-linked** |

Notes
- The earlier gate report printed "registered 10, used 5". That deviation was unnecessary and is withdrawn
  (`07_deviations_log.md`). Re-run `02_data_gate.py` so `06_data_gate_results.md` is regenerated at 10 years.
- HIV fails the full window (about 47% missing) and passes only 2019-2023; it was not used.

## B. Source audit

| Source | Finding | Status |
|---|---|---|
| CDPH disease file | 56 diseases, county-year, sex strata; Total used | PASS |
| CDC WONDER mortality | 20-45% of small-county cells suppressed for drug, suicide, homicide; handled by the gate (max missing 0.3, max zero 0.7) | PARTIAL - check how suppression enters rates |
| Hepatitis A/B/C (AtlasPlus) | State-level only, no county column | **FAIL** (kept as descriptive file only) |
| AHRF | Time-varying variables cover only recent years in this release; static county variables available | PARTIAL |
| EPA AQI, USDM drought | County-year, merged on FIPS | PASS |
| NCHS model-based mortality | Planned as sensitivity; no output | OPEN |

## C. Pipeline audit - problems found and fixed

| # | Problem | Evidence | Fix |
|---|---|---|---|
| 1 | Pooled AUC below 0.5 (0.355) | Observed vs predicted event rate by year did not match (2020: 51.7% vs 0.1%); within-disease-year AUC was 0.72 | Stratified AUC; year effect iid; `calibration_by_year.csv` |
| 2 | Outcome dominated by the statewide trend | Event rates swung from 0.2% to 52% across years | Added local outcome `upcross_local_0.80` |
| 3 | Gate-1 deviation to 5 years | Gate 1 shows 23 years | Withdrawn; threshold back to 10 |
| 4 | No multiplicity control across groups | Placebo p-values uncorrected | `12_multiplicity.py` (Holm) |
| 5 | Script 11 uses pooled AUC and a logistic stand-in | Disagrees with INLA models on sign for the comparison group | **PARTIAL** - stratified AUC now the headline (pooled kept); still a stand-in logistic model, not INLA |
| 6 | Transition labels use a smoother fitted on all years | Hindsight in labels | **ACCEPTED** - stated as a limitation in `07_deviations_log.md` and the write-up |
| 7 | 2021 and 2022 have zero local events | Log: "No events in 2021, skipped" | **OPEN** - probably end-of-series smoother effect; unverified; stated as a limitation |
| 8 | Simulation assumed 5 mortality years | `08_simulation_summary.md` | **OPEN** - re-run with 23 years and the real pipeline |
| 9 | Mortality gain explained by county size (population missing from A, suppression flags, county-swap placebo) | Confound check: population alone raised AUC 0.504 to 0.644; mortality deviations on top -0.004 | **FIXED** 2026-11-04 (see `07_deviations_log.md`) |
| 10 | Original-outcome table analysed by mistake | `model_table.csv` was byte-identical to `model_table_original.csv` | **FIXED**; headline is `model_table_local.csv` |

## D. Repository hygiene
Remove `*_smoke*` result files, the duplicate `01c build analysis panel .py`, and check imports before
renaming `utils/eonder.py`.

## E. Audit conclusion
The pipeline now runs end to end and is calibrated. The data cannot test the drug-linked hypothesis.
Items C5, C7 and C8 are still open and should be closed, or stated as limitations, before any number goes into a paper.
