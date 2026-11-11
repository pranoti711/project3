# run_advanced.ps1 - runs the whole advanced layer in order. Run from the project3 folder:
#   powershell -ExecutionPolicy Bypass -File tools/run_advanced.ps1
# Needs: 05_results restored to the stage 1 results (oof_predictions_lfo.csv), 02_data/processed/model_table_local.csv,
#        and: pip install -r requirements.txt
# Commit 00_docs/19_advanced_evaluation_plan.md to git BEFORE running this (it fixes the choices in advance).
$ErrorActionPreference = "Stop"
function Step($name, $cmd) {
  Write-Host "`n=== $name ===" -ForegroundColor Cyan
  Invoke-Expression $cmd
  if ($LASTEXITCODE -ne 0) { Write-Host "FAILED: $name" -ForegroundColor Red; exit 1 }
}
Step "0  unit tests"            "python -m pytest tests -q"
Step "19 positive control"      "python 04_scripts/19_positive_control_power.py"
Step "20 equivalence + power"   "python 04_scripts/20_equivalence_power.py --boot 1000"
Step "21 gradient boosting"     "python 04_scripts/21_gbm_robustness.py --boot 500"
Step "22 decision curve"        "python 04_scripts/22_decision_curve.py --boot 500"
Step "23 figures and map"       "python 04_scripts/23_make_figures.py"
Step "24 advanced report"       "python 04_scripts/24_write_advanced_report.py"
Step "25 supplementary"         "python 04_scripts/25_supplementary_diagnostics.py"
Step "26 maps and co-movement"  "python 04_scripts/26_maps_and_comovement.py"
Step "environment record"       "python tools/record_environment.py"
Step "file manifest"            "python tools/make_manifest.py"
Write-Host "`nDone. Read 00_docs/20_advanced_results.md and 00_docs/21_supplementary_results.md; figures are in 05_results/figures_report/" -ForegroundColor Green
