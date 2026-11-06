"""01c_build_analysis_panel.py - the full-period merge (2001-2023) on County + Year.
Outputs (02_data/processed):
  analysis_panel_2001_2023.csv : wide, one row per county-year (QC / exploration)
  analysis_long.csv            : one row per county-disease-year (Total sex) with mortality predictors, group and context
Run after 01_build_panel.py, 01b_build_wonder_mortality.py and 03_disease_groups.py.
"""
from pathlib import Path
import re, numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC, INTERIM, RAW = ROOT / "02_data/processed", ROOT / "02_data/interim", ROOT / "02_data/raw"
YEARS = range(2001, 2024)
slug = lambda s: re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40]

# disease (Total sex)
d = pd.read_csv(PROC / "disease_ca_long_all_sex.csv", dtype={"fips": str}, low_memory=False)
d = d[(d.Sex == "Total") & d.Year.between(YEARS.start, YEARS.stop - 1)].copy()
d["year"] = d.Year; d["disease_slug"] = d.Disease.map(slug)
d["population_cdph"] = pd.to_numeric(d.Population, errors="coerce")
dl = d[["fips", "County", "year", "Disease", "disease_slug", "Cases_n", "suppressed", "population_cdph", "source_file"]].rename(
    columns={"County": "county", "Disease": "disease", "Cases_n": "cases", "suppressed": "cases_suppressed"})

# mortality predictors (WONDER if present, else the 2019-2024 export)
wf = PROC / "mortality_ca_wide_wonder.csv"
mort = pd.read_csv(wf if wf.exists() else PROC / "mortality_ca_wide_2019_2024.csv", dtype={"fips": str})
print("mortality source:", wf.name if wf.exists() else "mortality_ca_wide_2019_2024.csv (WONDER not built yet)")

# context: AHRF static columns + time-varying (2022-2023 only in this release)
ahrf = pd.read_csv(RAW / "context/ahrf_2024_2025/AHRF2025.csv", dtype=str, encoding="latin1", low_memory=False)
ahrf = ahrf[ahrf.fips_st == "06"].copy(); ahrf["fips"] = ahrf.fips_st_cnty.str.zfill(5)
static_cols = [c for c in ["rural_urban_contnm_23", "cbsa_ind_23", "urban_influnc_13", "area_mi2_20",
                           "land_area_mi2_20", "urban_popn_pct_20", "medn_age_20", "cens_popn_20"] if c in ahrf.columns]
ahrf_static = ahrf[["fips"] + static_cols].rename(columns={c: "ahrf_" + c for c in static_cols})
tvl = pd.read_csv(PROC / "ahrf_ca_long_2019_2025.csv", dtype={"fips": str}, low_memory=False)
tvl = tvl[tvl.variable.isin(["hosp", "hosp_beds", "phys_nf_prim_care_pc_exc_rsdt", "md_nf_prim_care_pc_excl_rsdnt",
                             "pers_povty_stats_detrmnd", "unemply_clf_ge16", "hpsa_prim_care"])]
tvl["value"] = pd.to_numeric(tvl.value, errors="coerce")
ahrf_tv = tvl.pivot_table(index=["fips", "year"], columns="variable", values="value").add_prefix("ahrf_").reset_index()

# groups (frozen if it exists, else draft)
gf = INTERIM / "disease_groups_frozen.csv"; gd = INTERIM / "disease_groups_draft.csv"
if gf.exists(): grp = pd.read_csv(gf).rename(columns={"group": "group"})
elif gd.exists(): grp = pd.read_csv(gd).rename(columns={"group_draft": "group"})
else: grp = pd.DataFrame(columns=["disease", "group"])
grp = grp[["disease", "group"]]

# wide panel (QC)
wide_cases = dl.pivot_table(index=["fips", "year"], columns="disease_slug", values="cases", aggfunc="first").add_prefix("dz_").reset_index()
pop = dl.dropna(subset=["population_cdph"]).drop_duplicates(["fips", "year"])[["fips", "year", "population_cdph"]]
spine = pd.MultiIndex.from_product([sorted(ahrf.fips), YEARS], names=["fips", "year"]).to_frame(index=False)
panel = (spine.merge(pop, on=["fips", "year"], how="left").merge(wide_cases, on=["fips", "year"], how="left")
              .merge(mort, on=["fips", "year"], how="left").merge(ahrf_tv, on=["fips", "year"], how="left")
              .merge(ahrf_static, on="fips", how="left"))
panel.to_csv(PROC / "analysis_panel_2001_2023.csv", index=False)

# long modelling table
long = (dl.merge(grp, on="disease", how="left").merge(mort, on=["fips", "year"], how="left")
          .merge(ahrf_tv, on=["fips", "year"], how="left").merge(ahrf_static, on="fips", how="left"))
long["group"] = long["group"].fillna("unassigned")
long.to_csv(PROC / "analysis_long.csv", index=False)
mc = [c for c in mort.columns if c.endswith("_count")]
print(f"analysis_panel_2001_2023.csv {panel.shape} | analysis_long.csv {long.shape}")
print("years with any mortality count:", sorted(mort.loc[mort[mc].notna().any(axis=1), "year"].unique())[:3], "...",
      f"({mort.loc[mort[mc].notna().any(axis=1), 'year'].nunique()} years)")
