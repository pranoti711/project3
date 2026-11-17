#!/usr/bin/env python3
"""
build_hiv_hcv_panels.py - rebuild clean HIV new-diagnosis and HCV county-year tables from
data/processed/hiv_hcv_rows_raw.csv (written by get_hiv_hcv.py). Years come from the table title,
or from the report year when the title was cut off.
"""
import re, pathlib
import pandas as pd

P = pathlib.Path("02_data/processed")
raw = pd.read_csv(P / "hiv_hcv_rows_raw.csv")
CITY = {"Berkeley", "Long Beach", "Pasadena"}
NUM = re.compile(r"^\d[\d,]*\.?\d*$")


def years_from_title(t):
    m = re.search(r"(20\d\d)\s*[–—-]\s*(20\d\d)", str(t))
    return list(range(int(m.group(1)), int(m.group(2)) + 1)) if m else []


def build(sel, label, window):
    """window = years per report table, used when the title has no year range.
    HIV: 5 years ending in the report year. HCV 2016 report: 3 years (2014-2016)."""
    rows = []
    for r in raw[sel].itertuples():
        rep = int(re.search(r"(20\d\d)", r.file).group(1))
        ys = years_from_title(r.table) or list(range(rep - window + 1, rep + 1))
        all_toks = str(r.tokens).split()
        toks = [t for t in all_toks if not t.endswith("%")]
        # blank count cell for a true zero: tokens are only "0.0% 0.0" per year
        if (len(toks) == len(ys) and len(all_toks) == 2 * len(ys)
                and all(t in ("0.0%", "0%") for t in all_toks[0::2])
                and all(t in ("0.0", "0") for t in toks)):
            toks = [x for _ in ys for x in ("0", "0.0")]
        if len(toks) < 2 * len(ys):
            continue
        for k, y in enumerate(ys):
            c, rate = toks[2 * k], toks[2 * k + 1]
            rows.append(dict(county=r.county, year=y,
                             cases=float(c.replace(",", "")) if NUM.match(c) else None,
                             rate=float(rate.replace(",", "")) if NUM.match(rate) else None,
                             flag=c if not NUM.match(c) else "", report_year=rep, file=r.file))
    d = pd.DataFrame(rows)
    if d.empty:
        print(label, ": nothing found"); return None
    cnt = d[~d.county.isin(CITY | {"Total"})]
    chk = cnt.groupby(["report_year", "year"]).agg(counties=("county", "nunique"), sum_cases=("cases", "sum"),
                                                    n_missing=("cases", lambda s: s.isna().sum()))
    tot = d[d.county == "Total"].set_index(["report_year", "year"])["cases"].rename("report_total")
    chk = chk.join(tot)
    chk["diff"] = chk["sum_cases"] - chk["report_total"]
    print(f"\n=== {label}: county sums per report and year ===")
    print(chk.to_string())
    chk.to_csv(P / f"check_by_report_{label}.csv")
    best = cnt.sort_values("report_year", ascending=False).drop_duplicates(["county", "year"], keep="first")
    g = cnt.groupby(["county", "year"])["cases"].agg(["nunique", "min", "max"])
    print(f"county-years reported in more than one report with different counts: {(g['nunique'] > 1).sum()}")
    return best.sort_values(["county", "year"])


hiv = build((raw.disease == "HIV") & raw.table.str.contains("newly diagnosed", case=False, na=False),
            "hiv_new_dx", 5)
if hiv is not None:
    hiv.to_csv(P / "hiv_new_dx_county_year.csv", index=False)
    hiv.pivot(index="county", columns="year", values="cases").to_csv(P / "panel_hiv_new_dx.csv")
    print("\nFINAL HIV new diagnoses, statewide sum by year (newest report wins):")
    print(hiv.groupby("year")["cases"].sum().to_string())
    print("counties per year:", hiv.groupby("year")["county"].nunique().unique())

hcv = build(raw.file.str.lower().str.startswith("hcv"), "hcv_chronic", 3)
if hcv is not None:
    hcv.to_csv(P / "hcv_chronic_county_year.csv", index=False)
    print("\nFINAL HCV rows:", len(hcv), "years", sorted(hcv.year.unique()))
    
