"""
05d_add_crossdisease_features.py - STAGE 3 (exploratory): cross-disease transition signatures.

Idea (your Proposal 3): is a county's next-year up-transition in disease d predicted by what the OTHER
diseases in the same county (and in adjacent counties) were doing in the prediction year?

Reads : 02_data/processed/<input>  (default model_table_stage2.csv; needs fips, year, disease, group, prev_up, trend_slope)
        02_data/interim/ca_county_adjacency.csv
Writes: 02_data/processed/<output> (default model_table_stage3.csv) = input + new columns

New columns (all known at year t; disease d is always EXCLUDED from its own signature):
  xd_n_up            number of OTHER diseases with an up-transition event in this county in year t   (prev_up == 1)
  xd_share_rising    share of OTHER diseases whose trend slope is positive in this county in year t
  xd_share_rising_same   same, among OTHER diseases in the same disease group (NaN if none)
  xd_share_rising_other  same, among diseases in OTHER groups
  nbr_xd_n_up, nbr_xd_share_rising   mean of the above over adjacent counties (same disease d excluded there too)
Missing values become 0 after standardising in the models. Note: prev_up comes from the transition smoother,
which uses all years (hindsight), the same limitation as the own-history features.
Run : python 04_scripts/05d_add_crossdisease_features.py
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


def key(s):
    return s.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="model_table_stage2.csv")
    ap.add_argument("--output", default="model_table_stage3.csv")
    a = ap.parse_args()
    root = find_root()
    proc = root / "02_data" / "processed"
    df = pd.read_csv(proc / a.input)
    need = ["fips", "year", "disease", "group", "prev_up", "trend_slope"]
    miss = [c for c in need if c not in df]
    if miss:
        raise SystemExit(f"{a.input} lacks {miss}.")
    df["_k"] = key(df["fips"])
    df["_up"] = df["prev_up"].astype(float)
    df["_rise"] = np.where(df["trend_slope"].isna(), np.nan, (df["trend_slope"] > 0).astype(float))

    diseases = sorted(df["disease"].unique())
    grp = df.drop_duplicates("disease").set_index("disease")["group"].to_dict()
    up = df.pivot_table(index=["_k", "year"], columns="disease", values="_up", aggfunc="first")
    rise = df.pivot_table(index=["_k", "year"], columns="disease", values="_rise", aggfunc="first")

    rows = []
    for d in diseases:
        others = [x for x in diseases if x != d]
        same = [x for x in others if grp[x] == grp[d]]
        oth = [x for x in others if grp[x] != grp[d]]
        r = pd.DataFrame(index=up.index)
        r["xd_n_up"] = up[others].sum(axis=1, min_count=1)
        r["xd_share_rising"] = rise[others].mean(axis=1)
        r["xd_share_rising_same"] = rise[same].mean(axis=1) if same else np.nan
        r["xd_share_rising_other"] = rise[oth].mean(axis=1) if oth else np.nan
        r["disease"] = d
        rows.append(r.reset_index())
    xd = pd.concat(rows, ignore_index=True)

    adj = pd.read_csv(root / "02_data" / "interim" / "ca_county_adjacency.csv", dtype=str)
    edges = pd.concat([adj.rename(columns={"fips_a": "_k", "fips_b": "_n"}),
                       adj.rename(columns={"fips_b": "_k", "fips_a": "_n"})], ignore_index=True).drop_duplicates()
    edges["_k"] = key(edges["_k"]); edges["_n"] = key(edges["_n"])
    nb = edges.merge(xd[["_k", "year", "disease", "xd_n_up", "xd_share_rising"]].rename(columns={"_k": "_n"}),
                     on="_n", how="inner")
    nbm = (nb.groupby(["_k", "year", "disease"])[["xd_n_up", "xd_share_rising"]].mean()
             .add_prefix("nbr_").reset_index())

    out = (df.merge(xd, on=["_k", "year", "disease"], how="left")
             .merge(nbm, on=["_k", "year", "disease"], how="left")
             .drop(columns=["_k", "_up", "_rise"]))
    assert len(out) == len(df), "row count changed - merge went wrong"
    new = [c for c in out.columns if c not in df.columns]
    print("New columns:", new)
    print(out[new].notna().mean().round(2).to_string())
    out.to_csv(proc / a.output, index=False)
    print(f"Wrote {proc / a.output} ({len(out):,} rows)")


if __name__ == "__main__":
    main()
