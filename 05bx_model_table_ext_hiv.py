#!/usr/bin/env python3
"""
05bx_model_table_ext_hiv.py - build model tables for the exploratory HIV (Office of AIDS) group by REUSING
04_scripts/05b_build_model_table.py unchanged. Only the panel path is redirected to analysis_long_ext_hiv.csv.

Run from the project root:
    python 05bx_model_table_ext_hiv.py

Writes 02_data/processed/model_table_ext_hiv_<outcome>.csv for three outcomes and prints event counts, so you can see
whether an HIV-only model is feasible BEFORE running 06_models_ABCD.R. Existing model tables are not touched.
"""
import importlib.util
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
PROC = ROOT / "02_data" / "processed"
spec = importlib.util.spec_from_file_location("b05", ROOT / "04_scripts" / "05b_build_model_table.py")
b05 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b05)
b05.PANEL_PATH = PROC / "analysis_long_ext_hiv.csv"  # the only change

OUTCOMES = ["upcross_local_0.80", "upcross_local_0.70", "upcross_0.80"]
for oc in OUTCOMES:
    out = PROC / f"model_table_ext_hiv_{oc}.csv"
    print(f"\n=== outcome {oc} ===")
    b05.build_model_table(PROC / "transitions_ext_hiv.csv", out, oc)
    m = pd.read_csv(out)
    ev = m[m["up"] == 1]
    print(f"rows {len(m)} | events {len(ev)} ({len(ev) / len(m):.3f}) | counties with >=1 event {ev['fips'].nunique()} "
          f"| years with an event {ev['year'].nunique()} of {m['year'].nunique()}")
    for c in ["lag_rate", "trend_slope", "prev_up", "allcause_dev", "drug_od_dev", "suicide_dev", "homicide_dev",
              "aqi_median", "drought_dsci"]:
        print(f"   missing {c}: {int(m[c].isna().sum())} of {len(m)}")
