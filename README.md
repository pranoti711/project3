# Does county mortality add predictive value for infectious-disease up-transitions? (California, 2001-2023)

## Question
Overdose, suicide and homicide mortality are often assumed to signal rising infectious disease. This project tests whether
lagged within-county mortality deviations improve **out-of-sample** prediction of next-year county up-transitions in
16 notifiable diseases across California's 58 counties, compared with a baseline that already includes own disease history and county population.

## Design
- Outcome: up-transition (posterior probability of a rising local trend crossing 0.80, after removing the statewide yearly change).
- Models: A (history + population), B (+ mortality), C (+ air quality and drought), D (all), fitted with INLA (BYM2 spatial model).
- Validation: leave-future-out over 2017-2020 (81 events in 3,712 county-disease-year rows); within-year-and-disease AUC with county-cluster bootstrap intervals.
- Stage 1 was pre-registered; placebo, held-out-disease, spatial-block, equivalence, power, gradient-boosting, decision-curve and proper-scoring analyses are exploratory or post hoc.

## Main result (null)
| Model vs baseline | Delta AUC | 95% CI |
|---|---|---|
| B (+ mortality) | +0.001 | -0.028 to +0.034 |
| C (+ context) | +0.003 | -0.005 to +0.013 |
| D (all) | +0.003 | -0.028 to +0.037 |

An exploratory HIV extension (4 test events) was also null (pooled B - A -0.007, 95% CI -0.039 to +0.023).
An early apparent gain (+0.025) was explained by county population.

## Limitations
Small-count suppression leaves cause-specific mortality missing in 42-70% of scored rows (mean-imputed); HCV is absent; power is limited
(minimum detectable gain about 0.045 AUC). The result applies to publicly available, suppressed county-level data.

## Repository layout
- 00_docs/ pre-registration, results write-up, deviations log, abstract and discussion drafts, manifest.csv
- 02_data/ processed model tables ([CHECK: raw data sources and where they are downloaded from])
- 04_scripts/ R and Python analysis scripts (run order in 00_docs/12_run_order.md)
- 05_results/ result tables and logs
- tools/ helper and patch scripts

## Reproduce
See 00_docs/12_run_order.md. Software: R with INLA, Python 3.10 ([CHECK: exact versions in 00_docs/19_environment.md]).
Fingerprints of key files: 00_docs/manifest.csv. Tags: stage1-freeze, advanced-freeze, hiv-ext, final-draft-v3.
