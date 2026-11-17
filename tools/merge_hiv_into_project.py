#!/usr/bin/env python3
"""
merge_hiv_into_project.py - merge HIV (Office of AIDS series) into the ORIGINAL project pipeline as a 17th disease.

Original idea kept: your own panel already classifies HIV diagnoses in group "ambiguous" (with Early Syphilis), so the new
HIV rows get group = "ambiguous". They are NOT put in a new group.

Run from the project root:  python merge_hiv_into_project.py

Steps (the four pipeline stages, 17-disease version, all NEW files; frozen 16-disease files are untouched):
  1  analysis_long_17.csv         = analysis_long.csv + HIV (OA) rows, group ambiguous
  2  transitions_17.csv           = transitions.csv + transitions_ext_hiv.csv (same method, group relabelled)
  3  model_table_17_local.csv     = 05b_build_model_table.py on (1)+(2), outcome upcross_local_0.80
     model_table_17.csv           = same, outcome upcross_0.80
  4  (models)  06_models_ABCD.R is run on these tables - see the instructions printed at the end

Integrity check: the 16 original diseases in the new model table must reproduce model_table_local.csv / model_table.csv.
"""
import importlib.util
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
PROC = ROOT / "02_data" / "processed"
HIV = "HIV diagnoses (Office of AIDS)"
GROUP = "ambiguous"


def z5(s):
    return s.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


# ---- 1. panel ----
al = pd.read_csv(PROC / "analysis_long.csv", low_memory=False)
ext = pd.read_csv(PROC / "analysis_long_ext_hiv.csv", low_memory=False)
new = ext[ext["disease"] == HIV].copy()
new["group"] = GROUP
al17 = pd.concat([al, new[al.columns]], ignore_index=True)
al17.to_csv(PROC / "analysis_long_17.csv", index=False)
print(f"1. analysis_long_17.csv: {len(al)} + {len(new)} HIV rows = {len(al17)}")

# ---- 2. transitions ----
tr = pd.read_csv(PROC / "transitions.csv")
te = pd.read_csv(PROC / "transitions_ext_hiv.csv")
te["group"] = GROUP
for d in (tr, te):
    d["fips"] = z5(d["fips"])
tr17 = pd.concat([tr, te[tr.columns]], ignore_index=True)
tr17.to_csv(PROC / "transitions_17.csv", index=False)
print(f"2. transitions_17.csv: {len(tr)} + {len(te)} = {len(tr17)} rows, {tr17.disease.nunique()} diseases")

# ---- 3. model tables via the unchanged 05b script ----
spec = importlib.util.spec_from_file_location("b05", ROOT / "04_scripts" / "05b_build_model_table.py")
b05 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b05)
b05.PANEL_PATH = PROC / "analysis_long_17.csv"
jobs = [("upcross_local_0.80", "model_table_17_local.csv", "model_table_local.csv"),
        ("upcross_0.80", "model_table_17.csv", "model_table.csv")]
for outcome, outname, ref_name in jobs:
    out = PROC / outname
    print(f"\n3. {outcome} -> {outname}")
    b05.build_model_table(PROC / "transitions_17.csv", out, outcome)
    m = pd.read_csv(out)
    ref_path = PROC / ref_name
    if ref_path.exists():
        ref = pd.read_csv(ref_path)
        old = m[m["disease"].isin(ref["disease"].unique())]
        keys = ["fips", "year", "disease"]
        j = old.merge(ref, on=keys, suffixes=("", "_ref"), how="outer", indicator=True)
        both = j[j["_merge"] == "both"]
        cols = [c for c in ["up", "lag_rate", "trend_slope", "prev_up", "allcause_dev", "drug_od_dev",
                            "suicide_dev", "homicide_dev", "pop_log"]
                if c in old.columns and f"{c}_ref" in j.columns]
        worst = max((both[c] - both[f"{c}_ref"]).abs().max(skipna=True) for c in cols)
        print(f"   integrity vs {ref_name}: rows only-in-new {int((j._merge == 'left_only').sum())}, "
              f"only-in-old {int((j._merge == 'right_only').sum())}, max |diff| over features {worst:.2e}")
        print("   -> OK, frozen 16-disease rows reproduce" if worst < 1e-6 and (j._merge != 'both').sum() == 0
              else "   -> CHECK: the 16 original diseases did not reproduce exactly (send me this output)")
    ev = m.groupby("group")["up"].agg(rows="size", events="sum")
    ev["event_share"] = (ev["events"] / ev["rows"]).round(4)
    print(ev.to_string())

print("""
4. Models: run 06_models_ABCD.R on model_table_17_local.csv (your main outcome). p3_common.R reads
   02_data/processed/model_table.csv, so do NOT overwrite that file. Send me the output of:
   Select-String -Path 04_scripts\\*.R -Pattern "model_table|get_arg\\(|commandArgs"
   and I will give the exact command (or a one-line change) to point 06 at model_table_17_local.csv.
""")
