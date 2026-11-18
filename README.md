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
### Run the data pipeline

From the project folder, run:

```powershell
python .\04_scripts\run_data_pipeline.py
```

The runner first executes `00_check_raw_data.py --require-all`. It starts the
build only when all 21 raw-data requirements pass. It then runs the implemented
scripts in dependency order:

1. `01_build_panel.py`
2. `01b_build_wonder_mortality.py`
3. `03_disease_groups.py`
4. `01c_build_analysis_panel.py`
5. `02_data_gate.py`
6. `04_simulation.py`
7. `05_transitions.R` (only when `Rscript` and its required R packages are
   available)

The runner prints a completion summary for the numbered analysis scripts.
Scripts `06_models_ABCD.R` through `11_placebos_surrogates.py` are separate
follow-up analyses and are run after the transition and model-table steps.
The shared helpers are in `p3_common.R`; that file defines functions and does
not run a model on its own.

To run the one-disease smoke version of the model:

```powershell
Rscript .\04_scripts\05_transitions.R
python .\04_scripts\05b_build_model_table.py --transitions .\02_data\processed\transitions_smoke.csv --output .\02_data\processed\model_table_smoke.csv
Rscript .\04_scripts\06_models_ABCD.R --input=02_data/processed/model_table_smoke.csv --n_test=2 --boot=50 --tag=smoke
```

For the full set of eligible diseases, explicitly run the more expensive
transition fit and model:

```powershell
Rscript .\04_scripts\05_transitions.R --full
python .\04_scripts\05b_build_model_table.py
Rscript .\04_scripts\06_models_ABCD.R
```

The model-table builder aligns each transition with the preceding prediction
year, creates own-history features from cases available through that year, and
joins annual county AQI and drought context. Output metrics from the smoke run
are diagnostic only; assess full out-of-sample results with the follow-up
validation and placebo analyses before drawing scientific conclusions.

An incomplete analysis (including missing dependencies for
`05_transitions.R`) is reported and gives the runner a nonzero exit code, even
if the raw-data checks and earlier build steps passed. Raw-data validation is
separate from whether downstream statistical/model analyses are implemented
and complete. If raw-data checks are missing, the runner stops and points to
`00_docs/09_raw_data_check.md`; it does not continue with partial inputs.

### Download data

From the workspace root (`PROJECT`), run:

```sh
Rscript project3\04_scripts\00_download_supplemental_data.R
```

Or, from inside `project3`, run
`Rscript 04_scripts\00_download_supplemental_data.R`.

The script uses base R and downloads:

- HRSA AHRF county releases for 2020-21, 2021-22, 2022-23, and 2023-24
- The latest NOAA county monthly temperature and precipitation files (`tmpccy`,
  `tmaxcy`, `tmincy`, and `pcpncy`)
- CSV files linked from the CDC NCHS county drug-poisoning estimates page
  (2003-2021; sensitivity analysis only)
- The Census Bureau's national county boundary shapefile (optional)

Downloads are stored under `02_data/raw/`. Existing non-empty files are reused.
To force a fresh copy, set `FORCE_DOWNLOAD=true`; to skip Census boundaries, set
`DOWNLOAD_BOUNDARIES=false`. The Census boundary year defaults to 2025 and can be
changed with `CENSUS_YEAR`.

HRSA distributes the 2020-21 and 2021-22 county files as fixed-width `.asc`
data with SAS import programs and technical documentation in the same archive.
The downloader preserves those originals and converts them to wide CSV files
using the supplied SAS field positions and the Python standard library; values
remain strings to preserve leading zeros and suppression codes. Python 3 must
be installed and on `PATH` for this conversion. The 2022-23 and 2023-24
releases provide CSV archives directly.

### Interactive exports required

The script cannot choose filters or submit queries on the following interactive
sites. Save the exports to the paths shown; it creates their destination folders
and reports any files still missing.

1. **CDC WONDER:** use both the 1999-2020 and 2018-2024 Multiple Cause of Death
   databases. Export overdose, suicide, and homicide for each database as CSV:
   - `02_data/raw/mortality/wonder_final/mcd_1999_2020_overdose.csv`
   - `02_data/raw/mortality/wonder_final/mcd_1999_2020_suicide.csv`
   - `02_data/raw/mortality/wonder_final/mcd_1999_2020_homicide.csv`
   - `02_data/raw/mortality/wonder_final/mcd_2018_2024_overdose.csv`
   - `02_data/raw/mortality/wonder_final/mcd_2018_2024_suicide.csv`
   - `02_data/raw/mortality/wonder_final/mcd_2018_2024_homicide.csv`

   Select the radio button next to **Drug/Alcohol Induced Causes** for overdose
   or **Injury Intent** for suicide and homicide before selecting cause values.
   For suicide and homicide, select the intent cause only; do not also select
   **Injury Mechanism & All Other Leading Causes**.
   For an overdose-only series, select **Drug-induced causes** and do not also
   select alcohol-induced causes. Leave **Place of Death** unrestricted (all
   places), and do not add other demographic/location filters. The checker reads
   the query parameters saved in each export; filenames alone do not identify
   the selected cause or filters.
2. **U.S. Drought Monitor:** select **County**, **Percent Area**, and **California**;
   save the weekly export as
   `02_data/raw/environment/drought/drought_ca_county_weekly.csv`. Aggregate
   weekly observations to annual values in the analysis step.
3. **CDC AtlasPlus HIV diagnoses:** export annual California county data as CSV
   to `02_data/raw/disease/hiv_atlasplus/AtlasPlusTableData.csv`. The pipeline
   reads its county, FIPS, year, and case-count columns; preliminary 2025-2026
   rows are excluded. Some county values are suppressed.

The AtlasPlus hepatitis A/B/C table currently available in the workspace is
state-level and does not provide county observations. AtlasPlus marks these
hepatitis indicators as region-level, not county-level. The panel builder
writes the California hepatitis A and acute hepatitis B/C series separately
to `02_data/processed/hepatitis_ca_state_annual.csv`; they are not merged into
the county panel. These data support statewide descriptive trends only, not
county-level analysis or estimates of chronic hepatitis B/C burden. The scope
change is recorded in `00_docs/07_deviations_log.md`. The current suicide and
homicide WONDER exports select the correct Injury Intent but also select
**Injury Mechanism & All Other Leading Causes**. In the export, clear that
entire second cause selection and keep only Suicide or Homicide under Injury
Intent. Do this for both databases. Renaming an existing export does not change
its saved query. The current drug-overdose exports pass the cause-selection
check.

The data audit rejects exports with incorrect or extra query filters even when
all eight interactive export files are present. It does not attempt to infer or
fill suppressed values.
