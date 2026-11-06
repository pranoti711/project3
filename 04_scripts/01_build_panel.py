"""01_build_panel.py (v3) - merge disease + mortality + context into processed files.
NEW: reads EVERY csv in 02_data/raw/disease/ (CDPH infectious file, STD file, later HCV/HIV files),
     normalises column names, and stacks them into one long disease table.
California state-level hepatitis indicators are written separately and never merged into county data.
Run from anywhere: python 04_scripts/01_build_panel.py   (paths are found from this file's location)
Scope: California. Panel overlap years: 2019-2023.
"""
import re, glob, csv, numpy as np, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "02_data/raw", ROOT / "02_data/processed"
OUT.mkdir(parents=True, exist_ok=True)
AHRF_CSV = RAW / "context/ahrf_2024_2025/AHRF2025.csv"
MORT_CSV = RAW / "mortality/cdc_export_2019_2024/export.csv"
DIS_DIR = RAW / "disease"
YEARS = range(2019, 2024)

# ---- 1. AHRF (context): California rows + county name -> FIPS ----------------------
ahrf = pd.read_csv(AHRF_CSV, dtype=str, encoding="latin1", low_memory=False)
ahrf = ahrf[ahrf.fips_st == "06"].copy()
ahrf["fips"] = ahrf.fips_st_cnty.str.zfill(5)
name2fips = dict(zip(ahrf.cnty_name.str.strip(), ahrf.fips))

pat = re.compile(r"^(.*)_(\d{2})$")
rows = []
for c in ahrf.columns:
    m = pat.match(c)
    if m and 2019 <= 2000 + int(m.group(2)) <= 2025:
        t = ahrf[["fips", c]].rename(columns={c: "value"}).dropna()
        t["variable"], t["year"] = m.group(1), 2000 + int(m.group(2))
        rows.append(t)
ahrf_long = pd.concat(rows)[["fips", "variable", "year", "value"]]
ahrf_long = ahrf_long[ahrf_long.value.str.strip() != ""]
ahrf_long.to_csv(OUT / "ahrf_ca_long_2019_2025.csv", index=False)

curated = ["hosp", "hosp_beds", "phys_nf_prim_care_pc_exc_rsdt", "md_nf_prim_care_pc_excl_rsdnt",
           "pers_povty_stats_detrmnd", "pers_deep_povty_pct", "unemply_clf_ge16",
           "popn_mal", "popn_fem", "rural_hlth_clincs", "hpsa_prim_care"]
tv = ahrf_long[ahrf_long.variable.isin(curated)].copy()
tv["value"] = pd.to_numeric(tv.value, errors="coerce")
ahrf_tv = tv.pivot_table(index=["fips", "year"], columns="variable", values="value").add_prefix("ahrf_").reset_index()
static_cols = [c for c in ["rural_urban_contnm_23", "cbsa_ind_23", "urban_influnc_13", "area_mi2_20",
                           "land_area_mi2_20", "urban_popn_pct_20", "medn_age_20", "cens_popn_20"] if c in ahrf.columns]
ahrf_static = ahrf[["fips", "cnty_name"] + static_cols].rename(columns={c: "ahrf_" + c for c in static_cols})

# ---- 2. Disease: stack every csv in raw/disease -----------------------------------
CANON = {"disease": "Disease", "county": "County", "year": "Year", "sex": "Sex", "cases": "Cases",
         "population": "Population", "rate": "Rate", "lower_95_ci": "Lower_95__CI",
         "upper_95_ci": "Upper_95__CI", "annotation_code": "Annotation_Code"}

def atlas_header_row(path):
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as fh:
        lines = [fh.readline() for _ in range(150)]
    cnt = [len(next(csv.reader([l]), [])) if l.strip() else 0 for l in lines]
    for i in range(len(lines) - 3):
        if cnt[i] >= 3 and cnt[i] == cnt[i + 1] == cnt[i + 2] == cnt[i + 3]: return i
    return 0

def load_state_hepatitis(path):
    """Load California state-level AtlasPlus hepatitis data as a separate descriptive series."""
    with path.open("r", encoding="utf-8-sig", errors="replace") as fh:
        preamble = [fh.readline() for _ in range(20)]
    title = next((line for line in preamble if line.strip().lower().startswith("title:")), "")
    if not re.search(r"\bCalifornia\b", title, re.I):
        print(f"SKIPPED state hepatitis output for {path.name}: title does not identify California.")
        return None

    df = pd.read_csv(path, skiprows=atlas_header_row(path), dtype=str, encoding="utf-8-sig",
                     encoding_errors="replace", on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]
    columns = {c.lower(): c for c in df.columns}
    if not {"indicator", "year", "cases", "rate per 100000"} <= set(columns):
        print(f"SKIPPED state hepatitis output for {path.name}: expected Indicator, Year, Cases, and Rate per 100000.")
        return None
    if any(c in columns for c in ("geography", "fips", "county")):
        print(f"SKIPPED state hepatitis output for {path.name}: geography columns require county/state-specific parsing.")
        return None

    indicator = df[columns["indicator"]].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    keep = indicator.str.fullmatch(
        r"Hepatitis A|Acute Viral Hepatitis B|Acute Viral Hepatitis C", case=False, na=False
    )
    df = df.loc[keep].copy()
    indicator = indicator.loc[keep]
    year_text = df[columns["year"]].astype(str).str.extract(r"((?:19|20)\d{2})")[0]
    cases_text = df[columns["cases"]].astype(str).str.strip()
    cases = pd.to_numeric(cases_text.str.replace(",", "", regex=False), errors="coerce")
    rates_text = df[columns["rate per 100000"]].astype(str).str.strip()
    rates = pd.to_numeric(rates_text.str.replace(",", "", regex=False), errors="coerce")
    out = pd.DataFrame({
        "geography": "California",
        "geography_level": "state",
        "disease": indicator.to_numpy(),
        "year": pd.to_numeric(year_text, errors="coerce"),
        "cases": cases.to_numpy(),
        "rate_per_100000": rates.to_numpy(),
        "cases_source": cases_text.to_numpy(),
        "source_file": path.name,
    }).dropna(subset=["year"])
    out["year"] = out.year.astype(int)
    return out

# State-level hepatitis is descriptive only; it is deliberately not joined to county observations.
hepatitis_files = [f for f in DIS_DIR.rglob("*.csv") if "hepatitis" in f.stem.lower()]
state_hepatitis_paths = set()
if hepatitis_files:
    hepatitis_parts = []
    for f in hepatitis_files:
        part = load_state_hepatitis(f)
        if part is not None:
            hepatitis_parts.append(part)
            state_hepatitis_paths.add(f.resolve())
    if hepatitis_parts:
        hepatitis_state = pd.concat(hepatitis_parts, ignore_index=True).drop_duplicates(
            ["geography", "disease", "year"], keep="first"
        )
        hepatitis_state.to_csv(OUT / "hepatitis_ca_state_annual.csv", index=False)
        print(f"hepatitis_ca_state_annual.csv {hepatitis_state.shape} | state-level only (not county panel)")

LAST_YEAR = 2023     # AtlasPlus marks the latest years as preliminary; the study window ends in 2023
def load_atlasplus(path):
    """CDC AtlasPlus county export: Indicator, Year, Geography, FIPS, Cases, Rate per 100000 (+ preamble lines)."""
    try:
        df = pd.read_csv(path, skiprows=atlas_header_row(path), dtype=str, encoding="utf-8-sig", encoding_errors="replace", on_bad_lines="skip")
    except Exception:
        return None
    df.columns = [c.strip() for c in df.columns]
    low = [c.lower() for c in df.columns]
    if not (all(any(c.startswith(k) for c in low) for k in ["indicator", "year", "geography", "fips", "cases"])): return None
    col = lambda k: next(c for c in df.columns if c.lower().startswith(k))
    cases_txt = df[col("cases")].astype(str).str.strip()
    cases = pd.to_numeric(cases_txt.str.replace(",", "", regex=False), errors="coerce")
    out = pd.DataFrame({"Disease": df[col("indicator")].str.replace(r"\s+", " ", regex=True).str.strip(),
                        "County": df[col("geography")].str.replace(r",\s*CA$", "", regex=True).str.replace(r"\s+County$", "", regex=True).str.strip(),
                        "Year": df[col("year")].str.extract(r"((?:19|20)\d\d)")[0], "Sex": "Total", "Cases": cases,
                        "Population": np.nan, "Rate": df[next((c for c in df.columns if c.lower().startswith("rate")), df.columns[-1])],
                        "Lower_95__CI": np.nan, "Upper_95__CI": np.nan,
                        "Annotation_Code": np.where(cases.isna(), cases_txt, np.nan), "source_file": path.name})
    late = pd.to_numeric(out.Year, errors="coerce") > LAST_YEAR
    if late.any(): print(f"  AtlasPlus {path.name}: dropped {int(late.sum())} rows for preliminary years after {LAST_YEAR}")
    return out[~late]

def load_disease(path):
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig", encoding_errors="replace")
    df.columns = [re.sub(r"[^a-z0-9]+", "_", c.strip().lower()).strip("_") for c in df.columns]
    df = df.rename(columns=CANON)
    missing = {"Disease", "County", "Year", "Sex", "Cases"} - set(df.columns)
    if missing:
        print(f"SKIPPED {path.name}: not the CDPH long format (missing {sorted(missing)}). Columns: {list(df.columns)}")
        print(df.head(4).to_string()[:900])
        return None
    for c in CANON.values():
        if c not in df.columns: df[c] = np.nan
    df["source_file"] = path.name
    df["Disease"] = df.Disease.str.strip(); df["County"] = df.County.str.strip(); df["Sex"] = df.Sex.str.strip()
    return df[list(CANON.values()) + ["source_file"]]

files = sorted(DIS_DIR.rglob("*.csv"))      # includes subfolders
assert files, f"no csv files in {DIS_DIR}"
parts = []
for f in files:
    if f.resolve() in state_hepatitis_paths:
        print(f"separate state-level descriptive input; excluded from county panel: {f.name}")
        continue
    p = load_atlasplus(f)
    if p is None: p = load_disease(f)
    if p is None: continue
    print(f"disease file: {f.name} | rows {len(p):,} | diseases {p.Disease.nunique()} | years {p.Year.min()}-{p.Year.max()}")
    parts.append(p)
d = pd.concat(parts, ignore_index=True)
d = d.drop_duplicates(["Disease", "County", "Year", "Sex"], keep="first")

d = d[d.County != "California"].copy()                      # drop statewide rows
d["fips"] = d.County.map(name2fips)
bad = sorted(d[d.fips.isna()].County.unique())
if bad:
    print("WARNING: county names not matched to FIPS (rows dropped):", bad)
    d = d[d.fips.notna()].copy()
d["Year"] = d.Year.astype(int)
d["Cases_n"] = pd.to_numeric(d.Cases, errors="coerce")
d["suppressed"] = d.Cases_n.isna()                          # blank / non-numeric Cases
d.to_csv(OUT / "disease_ca_long_all_sex.csv", index=False)
print("annotation codes seen (inspect what they mean in the data dictionary):",
      d.Annotation_Code.value_counts(dropna=False).head(8).to_dict())

tot = d[(d.Sex == "Total") & d.Year.isin(YEARS)]
slug = lambda s: re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40]
tot = tot.assign(dz=tot.Disease.map(slug))
dz_cases = tot.pivot_table(index=["fips", "Year"], columns="dz", values="Cases_n", aggfunc="first").add_prefix("dz_")
dz_supp = tot.groupby(["fips", "Year"]).suppressed.sum().rename("dz_n_suppressed")
pop = tot.assign(_p=pd.to_numeric(tot.Population, errors="coerce")).dropna(subset=["_p"]).drop_duplicates(["fips", "Year"]).set_index(["fips", "Year"])._p.rename("population_cdph")
disease_wide = pd.concat([pop, dz_supp, dz_cases], axis=1).reset_index().rename(columns={"Year": "year"})

# ---- 3. Mortality (export.csv): California county x year ---------------------------
m = pd.read_csv(MORT_CSV, dtype=str)
m = m[(m.ST_NAME == "California") & (m.Period != "TTM")].copy()
m["year"] = m.Period.astype(int); m["fips"] = m.GEOID.str.zfill(5)
m["suppressed"] = m.Count.str.contains("-")                 # '1-9' = suppressed small count
m["count"] = pd.to_numeric(m.Count, errors="coerce")
m["rate"] = pd.to_numeric(m.Rate, errors="coerce").replace(-999, np.nan)
mw = m.pivot_table(index=["fips", "year"], columns="Intent", values=["count", "rate", "suppressed"], aggfunc="first")
mw.columns = [f"mort_{i.lower()}_{v}" for v, i in mw.columns]
mort_wide = mw.reset_index()
mort_wide.to_csv(OUT / "mortality_ca_wide_2019_2024.csv", index=False)

# ---- 4. Merge: county-year spine ---------------------------------------------------
spine = pd.MultiIndex.from_product([sorted(name2fips.values()), range(2019, 2025)], names=["fips", "year"]).to_frame(index=False)
panel = (spine.merge(disease_wide, on=["fips", "year"], how="left")
              .merge(mort_wide, on=["fips", "year"], how="left")
              .merge(ahrf_tv, on=["fips", "year"], how="left")
              .merge(ahrf_static, on="fips", how="left"))
panel["in_overlap_2019_2023"] = panel.year.between(2019, 2023)
panel.to_csv(OUT / "project3_ca_county_year_panel.csv", index=False)
print("panel", panel.shape, "| counties", panel.fips.nunique(), "| disease series in panel:",
      len([c for c in panel.columns if c.startswith("dz_") and c != "dz_n_suppressed"]))
print("Now run 03_disease_groups.py, then 02_data_gate.py")
