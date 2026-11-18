from pathlib import Path

old = Path("00_docs/29_previous_readme.md").read_text(encoding="utf-8-sig")
old = old.split("\n", 1)[1].strip()  # drop the old "# Project 3: County Data Collection" title
old = old.replace("\n## ", "\n### ").replace("## Run the data", "### Run the data", 1)

head = """# Does county mortality add predictive value for infectious-disease up-transitions? (California, 2001-2023)

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
Small-count suppression leaves cause-specific mortality missing in 42-70% of scored rows (2% for all-cause; mean-imputed);
HCV is absent; power is limited (minimum detectable gain about 0.045 AUC). The result applies to publicly available,
suppressed county-level data.

## Data (02_data/raw)
- Mortality: CDC WONDER county-level multiple-cause-of-death files for drug overdose, suicide, homicide and all-cause, 1999-2020 and 2018-2024.
- Context: EPA annual AQI by county (California), US Drought Monitor weekly county data, HRSA AHRF, NOAA county climate; CDC NCHS county drug-poisoning estimates (sensitivity analysis only).
- Disease: California county notifiable-disease counts (`disease/`); HIV and HCV county series (`hiv_hcv/`, exploratory).
- Geography: Census county boundaries.

## Software
Python 3.10.0 (pandas 2.3.3, numpy 2.2.6, scipy 1.15.3, scikit-learn 1.7.2); R 4.6.1 with INLA 26.8.7, data.table 1.18.6.1, sf 1.1.3, spdep 1.4.2.
Seeds: `03_config/seeds.yaml`. Full list: `00_docs/19_environment.md`.

## Repository layout
- `00_docs/` pre-registration, results write-up, deviations log, abstract and discussion drafts, `manifest.csv` (SHA-256 of key files)
- `02_data/` raw and processed data; `04_scripts/` R and Python analysis scripts (run order: `00_docs/12_run_order.md`)
- `05_results/` result tables and logs; `tools/` helper and patch scripts
- Freeze tags: `stage1-freeze`, `advanced-freeze`, `hiv-ext`

## How to reproduce
"""
Path("README.md").write_text(head + old + "\n", encoding="utf-8")
print("README.md written,", len((head + old).splitlines()), "lines")
