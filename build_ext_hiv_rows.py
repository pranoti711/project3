#!/usr/bin/env python3
"""
build_ext_hiv_rows.py - add the Office of AIDS HIV series to a COPY of analysis_long.csv.

    python build_ext_hiv_rows.py

Reads : 02_data/processed/analysis_long.csv            (left untouched)
        02_data/processed/hiv_new_dx_county_year.csv   (from build_hiv_hcv_panels.py)
Writes: 02_data/processed/analysis_long_ext_hiv.csv    (original rows + new HIV rows, identical columns)
        02_data/processed/hiv_oa_rows_only.csv         (just the new rows)

New rows: disease "HIV diagnoses (Office of AIDS)", slug hiv_diagnoses_oa, group injection_linked,
years 2012-2023, 58 counties, counts not suppressed. Mortality / AHRF / population columns are copied from
an existing full-coverage disease on the same (fips, year), so the new rows line up with the others.
"""
import pathlib, sys
import pandas as pd

P = pathlib.Path("02_data/processed")
if not P.exists():
    P = pathlib.Path("data/processed")
REF_DISEASE = "Campylobacteriosis"      # any disease with all counties and years 2002-2023

al = pd.read_csv(P / "analysis_long.csv", low_memory=False)
hiv = pd.read_csv(P / "hiv_new_dx_county_year.csv")

fips_map = al.drop_duplicates("county").set_index("county")["fips"]
ref = al[al.disease == REF_DISEASE]
if ref.empty:
    sys.exit(f"reference disease {REF_DISEASE!r} not found in analysis_long.csv")
ctx_cols = [c for c in al.columns if c not in
            ("disease", "disease_slug", "cases", "cases_suppressed", "source_file", "group")]
ctx = ref[ctx_cols].drop_duplicates(["fips", "year"])

h = hiv[["county", "year", "cases"]].copy()
h["fips"] = h["county"].map(fips_map)
unmatched = sorted(h.loc[h.fips.isna(), "county"].unique())
if unmatched:
    print("WARNING counties not found in analysis_long:", unmatched)
h = h.dropna(subset=["fips"])
h["fips"] = h["fips"].astype(int)
h["year"] = h["year"].astype(int)

new = h.merge(ctx.drop(columns=["county"]), on=["fips", "year"], how="left")
new["county"] = h["county"].values if len(new) == len(h) else new["fips"].map(
    al.drop_duplicates("fips").set_index("fips")["county"])
new["disease"] = "HIV diagnoses (Office of AIDS)"
new["disease_slug"] = "hiv_diagnoses_oa"
new["cases_suppressed"] = False
new["source_file"] = "OA_surveillance_reports"
new["group"] = "injection_linked"
new = new[al.columns]                    # identical column order

out = pd.concat([al, new], ignore_index=True)
out.to_csv(P / "analysis_long_ext_hiv.csv", index=False)
new.to_csv(P / "hiv_oa_rows_only.csv", index=False)
print("original rows:", len(al), "| new HIV rows:", len(new), "| combined:", len(out))
print("years:", new.year.min(), "-", new.year.max(), "| counties:", new.fips.nunique())
print("population_cdph missing in new rows:", int(new["population_cdph"].isna().sum()),
      "(fill from population_wonder if your transitions code needs it)")
print(new.groupby("year")["cases"].sum().to_string())