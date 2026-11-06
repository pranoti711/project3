"""run_from_07.py - runs steps 06-12 of Project 3 in order, with logs. Works in the VS Code terminal
(Windows, Mac or Linux). Put this file in the project3 root (the folder with 04_scripts, 02_data, 05_results).

Run from the VS Code terminal (Ctrl+`), inside the project3 folder:
    python run_from_07.py                    # steps 07-12 on model_table_local.csv
    python run_from_07.py --from 6           # also re-run step 06 (needed once after the p3_common.R change)
    python run_from_07.py --from 9           # restart at step 09 after a failure
    python run_from_07.py --table model_table.csv     # original outcome instead of the local one
    python run_from_07.py --dry-run          # only print what would run
    python run_from_07.py --rscript "C:/Program Files/R/R-4.4.1/bin/Rscript.exe"   # if Rscript is not on PATH

Scripts 07, 08, 10, 11 always read 02_data/processed/model_table.csv, so the chosen table is copied to
that name; the original is kept as model_table_original.csv.
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--from", dest="start", type=int, default=7)
ap.add_argument("--table", default="model_table_local.csv")
ap.add_argument("--rscript", default="Rscript")
ap.add_argument("--python", default=sys.executable)
ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()

proc = ROOT / "02_data" / "processed"
logs = ROOT / "05_results" / "logs"
active, original, chosen = proc / "model_table.csv", proc / "model_table_original.csv", proc / a.table

if not a.dry_run:
    logs.mkdir(parents=True, exist_ok=True)
    if not (ROOT / "05_results_v1").exists() and (ROOT / "05_results").exists():
        shutil.copytree(ROOT / "05_results", ROOT / "05_results_v1")
        print("Backed up 05_results -> 05_results_v1")

if a.table == "model_table.csv" and original.exists():
    chosen = original
if not chosen.exists():
    sys.exit(f"Missing {chosen}. Build it first:\n  python 04_scripts/05b_build_model_table.py "
             f"--outcome=upcross_local_0.80 --output=02_data/processed/model_table_local.csv")
if not a.dry_run:
    if not original.exists() and active.exists() and a.table != "model_table.csv":
        shutil.copy2(active, original)
        print("Kept the original table as model_table_original.csv")
    if chosen.resolve() != active.resolve():
        shutil.copy2(chosen, active)
print(f"Analysing table: {a.table}")

R, PY = a.rscript, a.python
steps = [
    (6, "06_models_ABCD", [R, "04_scripts/06_models_ABCD.R"]),
    (7, "07_leadtime", [R, "04_scripts/07_leadtime.R", "--perms=1000"]),
    (8, "08_validation", [R, "04_scripts/08_validation.R"]),
    (9, "09_early_warning", [PY, "04_scripts/09_early_warning.py", "--boot", "500"]),
    (10, "10_spatial_checks", [R, "04_scripts/10_spatial_checks.R"]),
    (11, "11_placebos", [PY, "04_scripts/11_placebos_surrogates.py", "--perms", "1000"]),
    (12, "12_multiplicity", [PY, "04_scripts/12_multiplicity.py"]),
    (13, "13_confound_check", [PY, "04_scripts/13_confound_check.py", "--n_test", "4"])
]

summary = []
for n, name, cmd in steps:
    if n < a.start:
        continue
    print(f"\n=== STEP {n}: {name} ===\n$ {' '.join(cmd)}", flush=True)
    if a.dry_run:
        continue
    t0 = time.time()
    with open(logs / f"{name}.log", "w", encoding="utf-8") as log:
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="replace")
        for line in p.stdout:
            print(line, end="")
            log.write(line)
        code = p.wait()
    mins = (time.time() - t0) / 60
    summary.append(f"{name}: {'ok' if code == 0 else f'FAILED (exit {code})'}  {mins:.1f} min")
    if code != 0:
        print(f"\nSTEP {n} FAILED. Log: 05_results/logs/{name}.log")
        break

print("\n=========== SUMMARY ===========")
print("\n".join(summary) or "(dry run)")
print("Logs: 05_results/logs   |   First check: 05_results/tables/calibration_by_year.csv, model_scores_lfo.csv")
