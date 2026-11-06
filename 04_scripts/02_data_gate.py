"""02_data_gate.py - the five Phase 0 gates, run on the real processed files.
Reads  02_data/processed/disease_ca_long_all_sex.csv, mortality_ca_wide_*.csv (made by 01_build_panel.py)
       02_data/interim/disease_groups_frozen.csv (else disease_groups_draft.csv)
Writes 05_results/tables/data_gate_disease_screen.csv and 00_docs/06_data_gate_results.md
Gates are the registered thresholds: edit CONFIG only through the deviations log.
"""
from pathlib import Path
import glob, json, numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC, INTERIM = ROOT / "02_data/processed", ROOT / "02_data/interim"
TABLES, DOCS = ROOT / "05_results/tables", ROOT / "00_docs"
TABLES.mkdir(parents=True, exist_ok=True); DOCS.mkdir(parents=True, exist_ok=True)

# Registered (frozen) thresholds from the Phase 0 plan. To use a different value, put it in 03_config/gate_thresholds.json
# (e.g. {"min_overlap_years": 5}). Any difference from the registered value is printed as a DEVIATION in the report.
REGISTERED = dict(min_overlap_years=10, min_counties_per_year=20, min_usable_counties=20, max_missing=0.30, max_zero=0.70, min_diseases_per_group=3)
used = dict(REGISTERED)
cfg_file = ROOT / "03_config/gate_thresholds.json"
if cfg_file.exists():
    used.update({k: v for k, v in json.loads(cfg_file.read_text(encoding="utf-8")).items() if k in REGISTERED})
DEVIATIONS = {k: (REGISTERED[k], used[k]) for k in used if used[k] != REGISTERED[k]}
CONFIG = dict(used, windows={"full_2001_2023": (2001, 2023), "overlap_2019_2023": (2019, 2023)})


# ---------- disease screen (Gates 2-4) ----------
d = pd.read_csv(PROC / "disease_ca_long_all_sex.csv", dtype={"fips": str}, low_memory=False)
d = d[d.Sex == "Total"].copy()
n_counties = d.fips.nunique()
rows = []
for wname, (y0, y1) in CONFIG["windows"].items():
    w = d[d.Year.between(y0, y1)]
    ny = y1 - y0 + 1
    for dis, g in w.groupby("Disease"):
        cy = n_counties * ny
        missing = g.Cases_n.isna().sum() + (cy - len(g))           # suppressed + absent county-years
        obs = g.Cases_n.dropna()
        zero = (obs == 0).mean() if len(obs) else np.nan
        nz = (g.assign(nz=g.Cases_n > 0).groupby("fips").nz.sum() >= np.ceil(ny / 2)).sum()
        rows.append(dict(window=wname, disease=dis, years_present=g.Year.nunique(), missing_pct=100 * missing / cy,
                         zero_pct=100 * zero, usable_counties=int(nz)))
scr = pd.DataFrame(rows)
scr["g2_counties"] = scr.usable_counties >= CONFIG["min_usable_counties"]
scr["g3_missing"] = scr.missing_pct <= 100 * CONFIG["max_missing"]
scr["g4_zeros"] = scr.zero_pct <= 100 * CONFIG["max_zero"]
scr["pass_2_3_4"] = scr[["g2_counties", "g3_missing", "g4_zeros"]].all(axis=1)
scr.round(1).to_csv(TABLES / "data_gate_disease_screen.csv", index=False)

# ---------- Gate 1: mortality overlap ----------
wf = PROC / "mortality_ca_wide_wonder.csv"
mfiles = [str(wf)] if wf.exists() else sorted(glob.glob(str(PROC / "mortality_ca_wide_*.csv")))
mort_source = wf.name if wf.exists() else "mortality_ca_wide_2019_2024.csv (WONDER not built yet)"
m = pd.concat([pd.read_csv(f, dtype={"fips": str}) for f in mfiles]).drop_duplicates(["fips", "year"])
dz_years = set(d.Year.unique())
g1 = []
for col in [c for c in m.columns if c.endswith("_count")]:
    per_year = m.groupby("year")[col].apply(lambda s: s.notna().sum())
    usable = [y for y, n in per_year.items() if n >= CONFIG["min_counties_per_year"] and y in dz_years]
    g1.append(dict(mortality_series=col.replace("mort_", "").replace("_count", "") + (" (benchmark)" if "all_cause" in col else ""), years_in_file=f"{m.year.min()}-{m.year.max()}",
                   usable_overlap_years=len(usable), pass_gate1=len(usable) >= CONFIG["min_overlap_years"]))
g1 = pd.DataFrame(g1)

# ---------- Gate 5: groups (proxy) ----------
gf = INTERIM / "disease_groups_frozen.csv"
gdraft = INTERIM / "disease_groups_draft.csv"
gsrc = gf if gf.exists() else (gdraft if gdraft.exists() else None)
g5 = None
if gsrc is not None:
    grp = pd.read_csv(gsrc)[["disease", "group_draft" if gsrc == gdraft else "group"]]
    grp.columns = ["disease", "group"]
    full = scr[scr.window == "full_2001_2023"].merge(grp, on="disease", how="left")
    g5 = (full.groupby("group").agg(diseases=("disease", "size"), passing_2_3_4=("pass_2_3_4", "sum")).reset_index())
    g5["pass_gate5_proxy"] = g5.passing_2_3_4 >= CONFIG["min_diseases_per_group"]

# ---------- report ----------
def md(df): return df.round(1).to_markdown(index=False) if df is not None else "_groups file not found - run 03_disease_groups.py first_"
dev_lines = (["**DEVIATION FROM THE REGISTERED PLAN** (log it in 07_deviations_log.md before looking at any result):"] +
             [f"- {k}: registered {r}, used {u}" for k, (r, u) in DEVIATIONS.items()] + [""]) if DEVIATIONS else []
lines = ["# Data gate results", "", f"Mortality source: {mort_source}", ""] + dev_lines + [
          f"Counties: {n_counties}. Thresholds: {CONFIG}", ""]
lines += [f"## Gate 1 - overlap of usable county mortality (need >= {CONFIG['min_overlap_years']} years; registered value {REGISTERED['min_overlap_years']})", md(g1), ""]
for w in CONFIG["windows"]:
    s = scr[scr.window == w]
    lines += [f"## Gates 2-4 - {w}: {int(s.pass_2_3_4.sum())} of {len(s)} diseases pass", ""]
lines += ["Full per-disease table: 05_results/tables/data_gate_disease_screen.csv", ""]
lines += [f"## Gate 5 - disease groups (proxy: diseases passing gates 2-4 in full window; source: {gsrc.name if gsrc else 'none'})", md(g5), ""]
lines += ["Gate 5 is a proxy. The real test is transition events per group, available after step 4 (transitions)."]
(DOCS / "06_data_gate_results.md").write_text("\n".join(lines), encoding="utf-8")

print(open(DOCS / "06_data_gate_results.md", encoding="utf-8").read())
