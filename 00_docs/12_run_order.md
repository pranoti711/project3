# 12_run_order.md - what to run, in which order (v3)

Run every command from the `project3` folder in PowerShell. Paste commands only, not output lines.
Keep the project outside OneDrive if you can.

## Part A - Freeze stage 1 (about 10 minutes)
1. `Copy-Item -Recurse 05_results 05_results_stage1_final`
2. `python 04_scripts/14_make_report_tables.py`
3. `powershell -ExecutionPolicy Bypass -File tools/git_freeze.ps1`  (prints the commit hash and date)
4. Write the hash and date into `00_docs/13_stage2_plan.md` (the **FILL** line).

## Part B - Threshold sensitivity (fast stand-in, about 15 minutes)
```powershell
python 04_scripts/05b_build_model_table.py --outcome=upcross_local_0.70 --output=02_data/processed/model_table_local_070.csv
python 04_scripts/05b_build_model_table.py --outcome=upcross_local_0.90 --output=02_data/processed/model_table_local_090.csv
python 04_scripts/13_confound_check.py --input model_table_local_070.csv --n_test 4 --tag _t070
python 04_scripts/13_confound_check.py --input model_table_local_090.csv --n_test 4 --tag _t090
python 04_scripts/11_placebos_surrogates.py --input model_table_local_070.csv --perms 200 --n_test 4 --tag t070
python 04_scripts/11_placebos_surrogates.py --input model_table_local_090.csv --perms 200 --n_test 4 --tag t090
```
Read: `05_results/tables/confound_check_t070.csv` and `_t090.csv`. If `B_dev - A` stays near 0 at both thresholds,
the null does not depend on the 0.80 cut-off. Add one sentence to the write-up.

## Part C - Stage 2, exploratory (about 3-6 hours of compute)
```powershell
# 1. Build the table (optional: first put saipe_ca_county.csv / laus_ca_county.csv in 02_data/raw/socio/)
python 04_scripts/05c_add_stage2_features.py

# 2. Run the full pipeline with the stage 2 switch on
$env:P3_STAGE2 = "1"
python run_from_07.py --from 6 --table model_table_stage2.csv
Remove-Item Env:P3_STAGE2

# 3. Keep stage 2 results apart, then restore stage 1 as the main results
Copy-Item -Recurse 05_results 05_results_stage2
Remove-Item -Recurse 05_results
Copy-Item -Recurse 05_results_stage1_final 05_results
Copy-Item 02_data/processed/model_table_local.csv 02_data/processed/model_table.csv

# 4. Tables for stage 2
python 04_scripts/14_make_report_tables.py --results 05_results_stage2 --out 15_stage2_results_tables.md
```
Read `00_docs/15_stage2_results_tables.md`: sections 2 (delta AUC) and 4 (placebos). Apply the decision rule in
`13_stage2_plan.md`. Report stage 2 only as exploratory.

## Part D - Final tidy
`powershell -ExecutionPolicy Bypass -File tools/cleanup.ps1`, then check `python run_from_07.py --dry-run`.

## Files changed or added in this version
| File | Status |
|---|---|
| `04_scripts/p3_common.R`, `11_placebos_surrogates.py` | changed: stage 2 switch (`P3_STAGE2=1`), pooled neighbour slopes |
| `04_scripts/13_confound_check.py` | changed: `--tag` option |
| `04_scripts/14_make_report_tables.py` | changed: `--results` and `--out` options |
| `04_scripts/05c_add_stage2_features.py` | new |
| `00_docs/03_phase0_part2_novelty.md`, `07_deviations_log.md`, `10_results_writeup.md` | updated |
| `00_docs/12_run_order.md`, `13_stage2_plan.md` | new / replaced |
| `06_paper/references.bib`, `tools/git_freeze.ps1` | new |
