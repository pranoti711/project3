# 12_run_order.md - what to run, in which order (v3)

Run every command from the `project3` folder in PowerShell. Paste commands only, not output lines.
Keep the project outside OneDrive if you can.

## Part A - Freeze stage 1 (about 10 minutes)
1. `Copy-Item -Recurse 05_results 05_results_stage1_final`
2. `python 04_scripts/14_make_report_tables.py`
3. `powershell -ExecutionPolicy Bypass -File tools/git_freeze.ps1`  (prints the commit hash and date)
4. Write the hash and date into `00_docs/13_stage2_plan.md` (the **FILL** line).

## Part B - Threshold sensitivity (fast stand-in, about 15 minutes)
Use `--n_test 6` everywhere so the scored window is 2017-2022 (the same events as the main pipeline). `--n_test 4`
only scores 2019-2022 (31 events at tau 0.80) and should not be used.
```powershell
python 04_scripts/13_confound_check.py --input model_table_local.csv --n_test 6 --tag _n6_t080
python 04_scripts/13_confound_check.py --input model_table_local_070.csv --n_test 6 --tag _n6_t070
python 04_scripts/13_confound_check.py --input model_table_local_090.csv --n_test 6 --tag _n6_t090
python 04_scripts/11_placebos_surrogates.py --input model_table_local_070.csv --perms 200 --n_test 6 --tag n6_t070
python 04_scripts/11_placebos_surrogates.py --input model_table_local_090.csv --perms 200 --n_test 6 --tag n6_t090
```
(The 0.70 and 0.90 tables are built with `python 04_scripts/05b_build_model_table.py --outcome=upcross_local_0.70
--output=02_data/processed/model_table_local_070.csv`, and the same with 0.90.)
Read the `B_dev - A` line of each `confound_check_n6_*.csv`. Report the three values side by side.

## Part C - Stage 2, exploratory (about 3-6 hours of compute)
Before starting, check that these two things are true, otherwise stop:
- `04_scripts/05c_add_stage2_features.py` exists, and `Select-String -Path 04_scripts/p3_common.R -Pattern P3_STAGE2` finds a line.
- `05_results_stage1_final` exists (made in Part A) and is the real stage 1 result.

```powershell
# 1. Build the stage 2 table (optional: first put saipe_ca_county.csv / laus_ca_county.csv in 02_data/raw/socio/)
python 04_scripts/05c_add_stage2_features.py
# STOP here if this printed an error or did not write model_table_stage2.csv. Do not continue.

# 2. Run the full pipeline with the stage 2 switch on
$env:P3_STAGE2 = "1"
python run_from_07.py --from 6 --table model_table_stage2.csv
Remove-Item Env:P3_STAGE2

# 3. Keep stage 2 results apart, then restore stage 1 as the main results (robocopy copies exactly; do not delete folders)
robocopy 05_results 05_results_stage2 /E
robocopy 05_results_stage1_final 05_results /MIR
Copy-Item 02_data/processed/model_table_local.csv 02_data/processed/model_table.csv

# 4. Tables for stage 2
python 04_scripts/14_make_report_tables.py --results 05_results_stage2 --out 15_stage2_results_tables.md
```
Robocopy prints a summary and uses exit codes below 8 for success; that is normal.
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
