#!/usr/bin/env python3
"""
run_all_hiv_hcv.py - one command for the whole HIV/HCV extension.

    python run_all_hiv_hcv.py --cdph "data\\raw\\odp_idb_2001-2023_ddg_compliant.csv"
    (add --skip-download to reuse the PDFs and extraction you already have)
"""
import argparse, subprocess, sys, pathlib
import pandas as pd

P = pathlib.Path("02_data/processed")
P.mkdir(parents=True, exist_ok=True)
CITY = {"Berkeley", "Long Beach", "Pasadena"}


def run(script):
    if not pathlib.Path(script).exists():
        sys.exit(f"missing {script} - put it in the project root")
    print(f"\n>>> python {script}")
    if subprocess.call([sys.executable, script]) != 0:
        sys.exit(f"{script} failed - fix it before continuing")


def find_cdph(arg):
    if arg:
        p = pathlib.Path(arg)
        if not p.is_file():
            sys.exit(f"--cdph file not found: {p}")
        return p
    need = {"disease", "county", "year", "sex", "cases", "population"}
    for root in ("02_data", "data", "."):
        for p in pathlib.Path(root).rglob("*.csv"):
            if "processed" in p.parts:          # skip our own outputs
                continue
            try:
                cols = {c.strip().lower() for c in pd.read_csv(p, nrows=1).columns}
            except Exception:
                continue
            if need <= cols:
                print("using CDPH file:", p)
                return p
    sys.exit("CDPH infectious-disease CSV not found - pass --cdph 02_data\\raw\\<file>.csv")


def norm(df):
    df = df.rename(columns={c: c.strip() for c in df.columns})
    return df.rename(columns={c: c.title() if c.lower() in ("disease", "county", "year", "sex", "cases",
                                                              "population", "rate") else c for c in df.columns})


def merge(cdph_path):
    cdph = norm(pd.read_csv(cdph_path))
    cdph["County"] = cdph["County"].astype(str).str.strip().str.replace(r"\s+County$", "", regex=True)
    pop = (cdph[cdph["Sex"].astype(str).str.lower() == "total"].dropna(subset=["Population"]).drop_duplicates(["County", "Year"]).set_index(["County", "Year"])["Population"])
    known = set(cdph["County"])
    new, notes = [], []
    specs = [("hiv_new_dx_county_year.csv", "HIV (new diagnoses)", "OA surveillance reports (CDPH Office of AIDS)", False), ("hcv_chronic_county_year.csv", "Hepatitis C, chronic (newly reported)", "CDPH Chronic HCV surveillance report 2016", True)]
    for fn, name, src, hcv in specs:
        f = P / fn
        if not f.exists():
            notes.append(f"{name}: {fn} not found, skipped")
            continue
        d = pd.read_csv(f)
        d = d[~d["county"].isin(CITY)].copy()
        miss = sorted(set(d["county"]) - known)
        if miss:
            notes.append(f"{name}: counties not matching the CDPH file names: {miss}")
        d["Population"] = [pop.get((c, y)) for c, y in zip(d["county"], d["year"])]
        fb = d["Population"].isna() & d["rate"].gt(0) & d["cases"].gt(0)
        d.loc[fb, "Population"] = (d["cases"] / d["rate"] * 100000).round()
        out = pd.DataFrame({"Disease": name, "County": d["county"], "Year": d["year"].astype(int), "Sex": "Total",
                            "Cases": d["cases"], "Population": d["Population"],
                            "Rate": d["cases"] / d["Population"] * 100000,
                            "Source": src, "Disease_group": "injection_linked",
                            "Suppressed_flag": d.get("flag", ""), "Report_year": d["report_year"],
                            "Case_definition_changed": (d["year"] >= 2016) if hcv else False})
        new.append(out)
        notes.append(f"{name}: {len(out)} rows, years {int(out.Year.min())}-{int(out.Year.max())}, "f"{out.County.nunique()} counties")
    if not new:
        sys.exit("nothing to merge")
    new = pd.concat(new, ignore_index=True)
    new.to_csv(P / "hiv_hcv_cdph_format.csv", index=False)
    pd.concat([cdph, new], ignore_index=True).to_csv(P / "cdph_plus_hiv_hcv.csv", index=False)

    rows = []
    for dis, g in new.groupby("Disease"):
        for c, h in g.groupby("County"):
            h = h.dropna(subset=["Cases"])
            rows.append(dict(Disease=dis, County=c, years=h.Year.nunique(), median_cases=h.Cases.median(), years_with_cases=int((h.Cases > 0).sum()), small_count_flag=bool(h.Cases.median() < 5)))
    use = pd.DataFrame(rows)
    use.to_csv(P / "hiv_hcv_usability.csv", index=False)
    hv = new[new.Disease.str.startswith("HIV")].sort_values(["County", "Year"]).copy()
    hv["Cases_3yr"] = hv.groupby("County")["Cases"].transform(lambda s: s.rolling(3, min_periods=3).sum())
    hv.to_csv(P / "hiv_pooled3yr.csv", index=False)

    lines = ["HIV/HCV extension report", "", *notes, "",
            "Small-count counties (median annual cases < 5): " + 
            ", ".join(f"{r.Disease.split()[0]}:{r.County}" for r in use.itertuples() if r.small_count_flag)[:1500], "",
            "Copy into the deviations log:",
            "- HIV (new diagnoses) and chronic HCV county series were added after the null results (exploratory).",
            "- HIV from CDPH Office of AIDS reports; where reports overlap the newest report is used.",
            "- Berkeley, Long Beach and Pasadena excluded (subsets of Alameda and Los Angeles).",
            "- HCV covers 2014-2016 only; CSTE case definition changed in 2016; counts are newly reported cases.",
            "- County rates recomputed with the same population denominators as the CDPH file."]
    (P / "hiv_hcv_extension_report.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cdph", help="path to your CDPH infectious-disease CSV")
    ap.add_argument("--skip-download", action="store_true", help="reuse existing raw extraction")
    a = ap.parse_args()
    if not a.skip_download:
        run("get_hiv_hcv.py")
    run("build_hiv_hcv_panels.py")
    merge(find_cdph(a.cdph))
