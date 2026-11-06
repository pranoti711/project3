"""01d_make_drug_linked_csv.py - turn ANY county-year disease table into the long format that
01_build_panel.py already reads (columns: Disease, County, Year, Sex, Cases, Population).

Use it for the missing drug-linked series (county hepatitis B/C, injection-related infections, ...).
Population is borrowed from the CDPH rows already in disease_ca_long_all_sex.csv.

1. Put your downloaded file anywhere (e.g. 02_data/raw/downloads/).
2. Edit the CONFIG block below.
3. python 04_scripts/01d_make_drug_linked_csv.py
4. Re-run: 01_build_panel.py, 03_disease_groups.py (review -> copy to disease_groups_frozen.csv),
   02_data_gate.py, 01c_build_analysis_panel.py, 05_transitions.R --full, 05b_build_model_table.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# ------------------------------- CONFIG (edit) -------------------------------
SRC = ROOT / "02_data" / "raw" / "downloads" / "hepatitis_c_county_year.csv"
COLUMNS = {"county": "County", "year": "Year", "cases": "Cases"}   # your column names
DISEASE = "Hepatitis C, acute"     # name must contain 'hepatitis c' / 'hepatitis b' for the drug_linked rule
OUT_NAME = "hepatitis_c_county.csv"
# -----------------------------------------------------------------------------

d = pd.read_csv(SRC, dtype=str, encoding="utf-8-sig")
missing = [v for v in COLUMNS.values() if v not in d.columns]
if missing:
    raise SystemExit(f"Columns not found in {SRC.name}: {missing}. Available: {list(d.columns)}")
d = d.rename(columns={v: k for k, v in COLUMNS.items()})[["county", "year", "cases"]]

d["County"] = d["county"].str.replace(r",\s*CA$", "", regex=True).str.replace(r"\s+County$", "", regex=True).str.strip()
d["Year"] = pd.to_numeric(d["year"].str.extract(r"((?:19|20)\d\d)")[0], errors="coerce")
d = d[d["County"].ne("California") & d["Year"].notna()].copy()
d["Year"] = d["Year"].astype(int)
d["Cases"] = d["cases"].str.replace(",", "", regex=False)          # suppressed text stays non-numeric -> NA
d["Disease"] = DISEASE
d["Sex"] = "Total"

old = pd.read_csv(ROOT / "02_data" / "processed" / "disease_ca_long_all_sex.csv", low_memory=False)
pop = (old[old["Sex"] == "Total"].dropna(subset=["Population"])
       .groupby(["County", "Year"], as_index=False)["Population"].first())
d = d.merge(pop, on=["County", "Year"], how="left")

print(f"rows {len(d):,} | counties {d['County'].nunique()} | years {d['Year'].min()}-{d['Year'].max()} "
      f"| rows without population {int(d['Population'].isna().sum())} "
      f"| non-numeric (suppressed) cases {int(pd.to_numeric(d['Cases'], errors='coerce').isna().sum())}")
out = ROOT / "02_data" / "raw" / "disease" / OUT_NAME
out.parent.mkdir(parents=True, exist_ok=True)
d[["Disease", "County", "Year", "Sex", "Cases", "Population"]].to_csv(out, index=False)
print("wrote", out)
