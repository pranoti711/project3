# 22_tripod_probast.md - Reporting map and risk-of-bias self-assessment

This is my own mapping and self-assessment, not an official audit. TRIPOD+AI (Collins et al., BMJ 2024) and PROBAST
(Wolff et al., Annals of Internal Medicine 2019) are the reference guidelines; check the item numbers against the
published checklists before citing (marked VERIFY). The topics below are grouped by what the guidelines ask for.

## A. Reporting map (where each topic is in this project)
| Topic | Where | Status |
|---|---|---|
| Title and aim: prediction (not causal), setting, outcome | `01_final_combined_version.md`, `10_results_writeup.md` s.1 | Done |
| Data sources, dates, geography | `05_data_dictionary.md`, `06_data_gate_results.md`, `09_raw_data_check.md` | Done |
| Outcome definition (up-transition at 0.80) and its limits | `01_final_combined_version.md`, `10_results_writeup.md` s.6 | Done; precision dependence stated |
| Predictors and timing (what is known at year t) | `p3_common.R`, `05b`, `05c`, `05d`, `03_config/context_variables.yaml` | Done |
| Sample size / events | s.1 of the write-up (81 scored events) | Reported; no formal calculation |
| Missing data handling | `07_deviations_log.md`, write-up s.5 | Suppressed counts treated as missing, flags removed |
| Model specification and fitting (INLA) | `05_transitions.R`, `06_models_ABCD.R` | Done |
| Pre-registration and changes | `04_prereg.md`, `07_deviations_log.md`, `13_`, `17_` stage plans, git commits | Done |
| Validation (temporal, spatial block, held-out disease and group) | steps 06, 08, 10 | Done |
| Performance: discrimination, calibration, net benefit | `20_advanced_results.md`, `21_supplementary_results.md` | Done (stage 1 predictions) |
| Uncertainty (bootstrap intervals), equivalence summary | `20_advanced_results.md` and `21_supplementary_results.md` s.1-2 | Done |
| Subgroup performance (county size) | `20_advanced_results.md` and `21_supplementary_results.md` s.4 | Done |
| Limitations | write-up s.6, this file | Done |
| Code, data and environment availability | `23_environment.md`, `manifest.csv`, `requirements.txt`, `tests/test_leakage.py` | Done; raw data are public sources, not redistributed |
| Funding, conflicts, patient involvement | - | Not applicable / to write |

## B. Risk-of-bias self-assessment (PROBAST-style, my ratings)
| Domain | Rating | Reason |
|---|---|---|
| Participants (units) | Low | All 58 counties and 23 years of public surveillance data; no selection of counties |
| Predictors | Moderate | Predictors are same-year or lagged and defined at prediction time; the transition-model features (`prev_up`) use a smoother fitted on all years (hindsight); mortality final counts arrive 1-2 years late, so not operational |
| Outcome | **High concern** | Outcome comes from the same smoother (hindsight) and depends on estimate precision, so small counties rarely register events; events are rare (about 2%) |
| Analysis | **High concern** | Only 81 scored events against dozens of model parameters (low events per parameter); stage 2 and 3 reuse the same test events; some placebo tests use a simple stand-in model |
| Overall | High risk of bias for any claim about operational forecasting | Bias would mainly inflate apparent performance, which makes the null result more, not less, convincing |

## C. What would lower the risk
- Re-estimate the transition model at each forecast origin (removes hindsight in outcome and in `prev_up`).
- An outcome defined by effect size and count, not posterior probability (removes the dependence on precision).
- More events (longer series, finer time resolution, or more geographies) and a pre-registered sample-size justification.
- A truly held-out period (new years of data) for any exploratory finding.
