"""Run implemented data and analysis scripts in dependency order.

Run from the project folder:
    python 04_scripts/run_data_pipeline.py

The runner validates raw inputs first, then builds analysis products and runs
the implemented simulation and transition analysis. It reports unfinished
analysis scripts instead of treating empty placeholders as successful runs.
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

PYTHON_STEPS = [
    ("00_check_raw_data.py", ["--require-all"]),
    ("01_build_panel.py", []),
    ("01b_build_wonder_mortality.py", []),
    ("03_disease_groups.py", []),
    ("01c_build_analysis_panel.py", []),
    ("02_data_gate.py", []),
    ("04_simulation.py", []),
]

UNIMPLEMENTED_STEPS = [
    ("06_models_ABCD.R", "placeholder; modeling method and implementation are not present"),
    ("07_leadtime.R", "placeholder; lead-time analysis is not implemented"),
    ("08_validation.R", "placeholder; validation analysis is not implemented"),
    ("09_early_warning.py", "stub; early-warning analysis is not implemented"),
    ("10_spatial_checks.R", "placeholder; spatial checks are not implemented"),
    ("11_placebos_surrogates.py", "stub; placebo/surrogate analysis is not implemented"),
]

statuses = []


def run_python_step(script, args):
    print("\n" + "=" * 70 + f"\n{script}\n" + "=" * 70, flush=True)
    result = subprocess.run(
        [sys.executable, str(HERE / script), *args],
        cwd=ROOT,
        check=False,
    )
    if result.returncode:
        if script == "00_check_raw_data.py" and result.returncode == 2:
            print(
                "\nSTOPPED: one or more raw-data requirements are missing. "
                "See 00_docs/09_raw_data_check.md, fix those inputs, and rerun."
            )
        else:
            print(
                f"\nSTOPPED at {script} (exit code {result.returncode}). "
                "Fix the error above, then rerun the pipeline."
            )
        raise SystemExit(result.returncode)
    statuses.append((script, "COMPLETED"))


def check_r_dependencies():
    rscript = shutil.which("Rscript")
    if not rscript:
        return None, ["Rscript (not found on PATH)"]

    required = ["INLA", "dplyr", "readr", "Matrix", "sn"]
    adjacency = ROOT / "02_data" / "interim" / "ca_county_adjacency.csv"
    if not adjacency.exists():
        required.extend(["sf", "spdep", "tigris"])
    expression = (
        "required <- c("
        + ", ".join(repr(package) for package in required)
        + "); missing <- required[!vapply(required, requireNamespace, "
        + "logical(1), quietly=TRUE)]; "
        + "if (length(missing)) { cat(paste(missing, collapse='\\n')); "
        + "quit(status=2) }"
    )
    result = subprocess.run(
        [rscript, "-e", expression],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        missing = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if not missing:
            missing = ["R package preflight failed"]
        return rscript, missing
    return rscript, []


def run_transition_analysis():
    print("\n" + "=" * 70 + "\n05_transitions.R\n" + "=" * 70, flush=True)
    rscript, missing = check_r_dependencies()
    if missing:
        detail = ", ".join(missing)
        print(f"BLOCKED: 05_transitions.R requires unavailable dependencies: {detail}")
        statuses.append(("05_transitions.R", f"BLOCKED ({detail})"))
        return False

    result = subprocess.run(
        [rscript, str(HERE / "05_transitions.R")],
        cwd=ROOT,
        check=False,
    )
    if result.returncode:
        statuses.append(("05_transitions.R", f"FAILED (exit code {result.returncode})"))
        print(f"FAILED: 05_transitions.R exited with code {result.returncode}.")
        return False
    statuses.append(("05_transitions.R", "COMPLETED"))
    return True


for script, args in PYTHON_STEPS:
    run_python_step(script, args)

transition_completed = run_transition_analysis()

for script, reason in UNIMPLEMENTED_STEPS:
    if script in {"06_models_ABCD.R", "07_leadtime.R", "08_validation.R"} and not transition_completed:
        reason = "not run because the prerequisite transition analysis did not complete; " + reason
    print(f"NOT IMPLEMENTED: {script} ({reason})")
    statuses.append((script, "NOT IMPLEMENTED"))

print("\nPipeline execution summary")
print("-" * 70)
for script, status in statuses:
    print(f"{status:16} {script}")

incomplete = [status for _, status in statuses if status != "COMPLETED"]
if incomplete:
    print(
        "\nPipeline is incomplete. Raw-data/build outputs and the simulation may "
        "be available, but the blocked or unimplemented analyses did not run."
    )
    raise SystemExit(1)

print("\nAll configured pipeline steps completed.")
