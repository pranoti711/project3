"""
05c_add_stage2_features.py - STAGE 2 (exploratory): neighbour-county and static socioeconomic features.

Reads : 02_data/processed/<input>   (default model_table_local.csv, built by 05b v2)
        02_data/interim/ca_county_adjacency.csv   (queen contiguity pairs, made by 05_transitions.R)
        02_data/processed/analysis_long.csv       (static AHRF county traits)
        optional 02_data/raw/socio/saipe_ca_county.csv  (fips, year, poverty_pct)
        optional 02_data/raw/socio/laus_ca_county.csv   (fips, year, unemp_rate)
Writes: 02_data/processed/<output>  (default model_table_stage2.csv)  = input + new columns

New columns (all known at year t; nothing from year t+1 or later):
  nbr_lag_rate, nbr_trend_slope, nbr_prev_up       mean of the same disease's values in adjacent counties, year t
  nbr_allcause_dev, nbr_drug_od_dev,
  nbr_suicide_dev, nbr_homicide_dev                mean of adjacent counties' lagged mortality deviations
  urban_pct, median_age, log_density, rural_urban  static county traits (AHRF 2020/2023 vintage; time-invariant,
                                                   so they act as county characteristics, not time-varying data)
  poverty_l1, unemp_l1                             only if the optional files exist; value of year t-1

Counties with no neighbour value get NaN (the models set missing features to 0 after standardising).
Run : python 04_scripts/05c_add_stage2_features.py
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def find_root():
    p = Path.cwd().resolve()
    for q in [p, *p.parents]:
        if (q / "04_scripts").is_dir():
            return q
        if (q / "project3" / "04_scripts").is_dir():
            return q / "project3"
    raise SystemExit("Run from inside project3.")


NBR_HIST = ["lag_rate", "trend_slope", "prev_up"]
NBR_DEV = ["allcause_dev", "drug_od_dev", "suicide_dev", "homicide_dev"]


def key(s):
    return s.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="model_table_local.csv")
    ap.add_argument("--output", default="model_table_stage2.csv")
    a = ap.parse_args()
    root = find_root()
    proc = root / "02_data" / "processed"
    df = pd.read_csv(proc / a.input)
    need = ["fips", "year", "disease", *NBR_HIST, *NBR_DEV]
    miss = [c for c in need if c not in df]
    if miss:
        raise SystemExit(f"{a.input} lacks {miss}. Build it with 05b_build_model_table.py (v2) first.")
    df["_k"] = key(df["fips"])

    adj = pd.read_csv(root / "02_data" / "interim" / "ca_county_adjacency.csv", dtype=str)
    edges = pd.concat([adj.rename(columns={"fips_a": "_k", "fips_b": "_n"}),
                       adj.rename(columns={"fips_b": "_k", "fips_a": "_n"})], ignore_index=True).drop_duplicates()
    edges["_k"] = key(edges["_k"]); edges["_n"] = key(edges["_n"])
    n_nb = edges.groupby("_k").size()
    print(f"Counties in adjacency: {n_nb.size}; with no neighbour: {df['_k'].nunique() - n_nb.size}")

    # --- neighbour means, same disease and year
    feat = df[["_k", "disease", "year", *NBR_HIST]].rename(columns={"_k": "_n"})
    m = edges.merge(feat, on="_n", how="inner")
    nb_hist = m.groupby(["_k", "disease", "year"])[NBR_HIST].mean().add_prefix("nbr_").reset_index()
    dev = df[["_k", "year", *NBR_DEV]].drop_duplicates(["_k", "year"]).rename(columns={"_k": "_n"})
    m2 = edges.merge(dev, on="_n", how="inner")
    nb_dev = m2.groupby(["_k", "year"])[NBR_DEV].mean().add_prefix("nbr_").reset_index()
    out = (df.merge(nb_hist, on=["_k", "disease", "year"], how="left")
             .merge(nb_dev, on=["_k", "year"], how="left"))

    # --- static county traits (time-invariant)
    cols = ["fips", "ahrf_urban_popn_pct_20", "ahrf_medn_age_20", "ahrf_cens_popn_20",
            "ahrf_land_area_mi2_20", "ahrf_rural_urban_contnm_23"]
    st = pd.read_csv(proc / "analysis_long.csv", usecols=cols, dtype={"fips": str}).drop_duplicates("fips")
    st["_k"] = key(st["fips"])
    st["urban_pct"] = st["ahrf_urban_popn_pct_20"]
    st["median_age"] = st["ahrf_medn_age_20"]
    st["log_density"] = np.log(st["ahrf_cens_popn_20"] / st["ahrf_land_area_mi2_20"])
    st["rural_urban"] = st["ahrf_rural_urban_contnm_23"]
    out = out.merge(st[["_k", "urban_pct", "median_age", "log_density", "rural_urban"]], on="_k", how="left")

    # --- optional time-varying socioeconomic series, lagged one year
    for fname, col, newname in [("saipe_ca_county.csv", "poverty_pct", "poverty_l1"),
                                ("laus_ca_county.csv", "unemp_rate", "unemp_l1")]:
        f = root / "02_data" / "raw" / "socio" / fname
        if f.exists():
            s = pd.read_csv(f, dtype={"fips": str})
            s["_k"] = key(s["fips"]); s["year"] = s["year"].astype(int) + 1   # value of t-1 attached to year t
            out = out.merge(s[["_k", "year", col]].rename(columns={col: newname}), on=["_k", "year"], how="left")
            print(f"Added {newname} from {fname}: {out[newname].notna().mean():.0%} non-missing")
        else:
            print(f"(optional file not found, skipped: 02_data/raw/socio/{fname})")

    out = out.drop(columns="_k")
    assert len(out) == len(df), "row count changed - merge went wrong"
    new = [c for c in out.columns if c not in df.columns.drop("_k")]
    print("New columns:", new)
    print(out[new].notna().mean().round(2).to_string())
    out.to_csv(proc / a.output, index=False)
    print(f"Wrote {proc / a.output} ({len(out):,} rows)")


if __name__ == "__main__":
    main()