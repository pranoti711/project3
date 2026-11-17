#!/usr/bin/env python3
"""
get_hiv_hcv.py - download California HIV / HCV county reports and extract county-year tables.

    pip install pdfplumber pandas
    python get_hiv_hcv.py
    python get_hiv_hcv.py --atlas "02_data\\raw\\AtlasPlus_export.csv"   # optional, must be a real file

Outputs (data/processed/):
    text/<pdf>.txt            raw extracted text per PDF
    hiv_hcv_rows_raw.csv      every county line found
    hiv_hcv_county_year.csv   long table: disease, metric, county, year, cases, pct, rate, report_year
"""
import re, sys, time, pathlib, urllib.request
import pandas as pd
import pdfplumber

RAW = pathlib.Path("02_data/raw/hiv_hcv")
OUT = pathlib.Path("02_data/processed")
TXT = OUT / "text"
for p in (RAW, OUT, TXT):
    p.mkdir(parents=True, exist_ok=True)

DOA = "https://www.cdph.ca.gov/Programs/CID/DOA/CDPH%20Document%20Library/"
DCDC = "https://www.cdph.ca.gov/Programs/CID/DCDC/CDPH%20Document%20Library/"
URLS = {
    "hiv_2016.pdf": DOA + "California%20HIV%20Surveillance%20Report%20-%202016.pdf",
    "hiv_2017.pdf": DOA + "California%20HIV%20Surveillance%20Report%20-%202017.pdf",
    "hiv_2018.pdf": DOA + "California_HIV_Surveillance_Report2018.pdf",
    "hiv_2019.pdf": DOA + "California_HIV_Surveillance_Report2019_ADA.pdf",
    "hiv_2021.pdf": DOA + "California_HIV_Surveillance_Report2021_ADA.pdf",
    "hiv_2022.pdf": DOA + "California-HIV-Surveillance-Report-2022.pdf",
    "hiv_2023.pdf": "https://www.icphd.org/assets/Epidemiology/STI-resources-for-medical-providers/California-HIV-Surveillance-Report-2023.pdf",
    "hcv_2016.pdf": DCDC + "SurvReport_HCV_2016.pdf",
}

COUNTIES = ["Alameda", "Alpine", "Amador", "Butte", "Calaveras", "Colusa", "Contra Costa",
    "Del Norte", "El Dorado", "Fresno", "Glenn", "Humboldt", "Imperial", "Inyo", "Kern", "Kings",
    "Lake", "Lassen", "Los Angeles", "Madera", "Marin", "Mariposa", "Mendocino", "Merced", "Modoc",
    "Mono", "Monterey", "Napa", "Nevada", "Orange", "Placer", "Plumas", "Riverside", "Sacramento",
    "San Benito", "San Bernardino", "San Diego", "San Francisco", "San Joaquin", "San Luis Obispo",
    "San Mateo", "Santa Barbara", "Santa Clara", "Santa Cruz", "Shasta", "Sierra", "Siskiyou",
    "Solano", "Sonoma", "Stanislaus", "Sutter", "Tehama", "Trinity", "Tulare", "Tuolumne",
    "Ventura", "Yolo", "Yuba", "Berkeley", "Long Beach", "Pasadena"]
COUNTIES.sort(key=len, reverse=True)
CITY_LHJ = {"Berkeley", "Long Beach", "Pasadena"}
NUM = re.compile(r"^(?:\d[\d,]*\.?\d*%?|\*+|--|—|–|<5|<\d+)$")
YEAR = re.compile(r"^20[0-2]\d$")


def download():
    for name, url in URLS.items():
        f = RAW / name
        if f.exists() and f.stat().st_size > 10_000:
            print("have  ", f)
            continue
        for attempt in range(1, 4):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    f.write_bytes(r.read())
                print("got   ", f, f.stat().st_size, "bytes")
                break
            except Exception as e:
                print(f"try {attempt}/3 failed for {name}: {e}")
                time.sleep(3)
        else:
            print("FAILED", name, "-> download manually into", RAW, "as", name)


def year_header(line):
    toks = line.replace(",", " ").split()
    ys = [t for t in toks if YEAR.match(t)]
    if not ys:
        return None
    if len(ys) >= 3 or (len(ys) >= 2 and len(ys) / len(toks) >= 0.4):
        if any(line.startswith(c + " ") for c in COUNTIES):
            return None
        return ys
    return None


def clean_tok(t):
    return t.strip("()[]")


def parse_pdf(path, disease):
    rows, years, table = [], [], ""
    text_dump = []
    with pdfplumber.open(path) as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            text_dump.append(f"\n===== PAGE {pno} =====\n{text}")
            for line in text.splitlines():
                line = line.strip()
                if re.match(r"^(Table|Figure)\s+[\w.\-]+", line, re.I):
                    table = line[:120]
                    years = []
                    continue
                yh = year_header(line)
                if yh:
                    years = yh
                    continue
                for c in COUNTIES:
                    if line.startswith(c + " ") or line == c:
                        toks = []
                        for t in line[len(c):].split():
                            t = clean_tok(t)
                            if NUM.match(t):
                                toks.append(t)
                            else:
                                break
                        if toks:
                            rows.append(dict(disease=disease, file=path.name, page=pno, table=table,
                                             county=c, years=" ".join(years), tokens=" ".join(toks)))
                        break
    (TXT / (path.stem + ".txt")).write_text("\n".join(text_dump), encoding="utf-8")
    return rows


def num(s):
    return float(s.replace(",", "")) if s and re.fullmatch(r"[\d,]*\.?\d+", s) else None


def metric_of(table):
    t = table.lower()
    if "newly diagnosed" in t:
        return "diagnoses"
    if "living with" in t:
        return "prevalence"
    if "deaths" in t:
        return "deaths"
    return "other"


def to_long(r):
    ys = list(dict.fromkeys(r["years"].split()))  # 2014 2014 2014 2015 ... -> 2014 2015 ...
    toks = r["tokens"].split()
    n = len(ys)
    rep = int(re.search(r"(20\d\d)", r["file"]).group(1))
    metric = metric_of(r["table"]) if r["disease"] == "HIV" else "chronic_cases"
    groups, layout = [], "unclear"
    if n:
        if len(toks) == 3 * n:
            layout = "count_pct_rate"
            groups = [(toks[3 * i], toks[3 * i + 1], toks[3 * i + 2]) for i in range(n)]
        elif len(toks) == 2 * n:
            layout = "count_rate"
            groups = [(toks[2 * i], None, toks[2 * i + 1]) for i in range(n)]
        elif len(toks) == n:
            layout = "counts"
            groups = [(t, None, None) for t in toks]
        elif len(toks) > 2 * n:
            layout = "pairs"
            groups = [(toks[2 * i], None, toks[2 * i + 1]) for i in range(n)]
    out = []
    for y, (c, p, rate) in zip(ys, groups):
        out.append(dict(disease=r["disease"], metric=metric, table=r["table"], county=r["county"],
                        year=int(y), cases=num(c), pct=num(p.rstrip("%")) if p else None,
                        rate=num(rate), suppressed_or_flag=(c if num(c) is None else ""),
                        report_year=rep, layout=layout, city_lhj=r["county"] in CITY_LHJ,
                        file=r["file"], page=r["page"]))
    if not out:
        out.append(dict(disease=r["disease"], metric=metric, table=r["table"], county=r["county"],
                        year=None, cases=None, pct=None, rate=None, suppressed_or_flag=r["tokens"],
                        report_year=rep, layout="unclear", city_lhj=r["county"] in CITY_LHJ,
                        file=r["file"], page=r["page"]))
    return out


def read_atlas(path):
    p = pathlib.Path(path)
    if not p.is_file():
        print(f"AtlasPlus file not found: {p}\n  Skipping --atlas.")
        return
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    hdr = next((i for i, l in enumerate(lines) if "Year" in l and "Cases" in l), None)
    if hdr is None:
        print("Could not find a header row with 'Year' and 'Cases' in", p)
        return
    df = pd.read_csv(p, skiprows=hdr, engine="python", on_bad_lines="skip")
    if "FIPS" in df.columns:
        df = df[df["FIPS"].astype(str).str.zfill(5).str.startswith("06")]
    elif "Geography" in df.columns:
        df = df[df["Geography"].astype(str).str.contains(r"\bCA\b|California", regex=True)]
    df["Cases"] = pd.to_numeric(df["Cases"].astype(str).str.replace(",", ""), errors="coerce")
    df.to_csv(OUT / "atlasplus_hiv_ca_county.csv", index=False)
    print("AtlasPlus rows kept:", len(df), "->", OUT / "atlasplus_hiv_ca_county.csv")


def main():
    download()
    rows = []
    for f in sorted(RAW.glob("*.pdf")):
        n = f.name.lower()
        disease = "HIV" if n.startswith("hiv") else "HCV_chronic" if n.startswith("hcv") else None
        if not disease:
            continue
        got = parse_pdf(f, disease)
        with_years = sum(1 for r in got if r["years"])
        print(f"{f.name}: {len(got)} county lines, {len({r['county'] for r in got})} counties, "
              f"{with_years} with year header")
        rows += got
    if rows:
        pd.DataFrame(rows).to_csv(OUT / "hiv_hcv_rows_raw.csv", index=False)
        long = pd.DataFrame([x for r in rows for x in to_long(r)])
        long = long.sort_values("report_year", ascending=False)
        best = long.dropna(subset=["year"]).drop_duplicates(
            ["disease", "metric", "county", "year"], keep="first")
        best = best.sort_values(["disease", "metric", "county", "year"])
        best.to_csv(OUT / "hiv_hcv_county_year.csv", index=False)
        print("\nlong table:", len(best), "rows ->", OUT / "hiv_hcv_county_year.csv")
        if len(best):
            print(best.groupby(["disease", "metric"])["year"].agg(["min", "max", "count"]))
        print("rows needing manual check (layout unclear):", int((long["layout"] == "unclear").sum()))
    if "--atlas" in sys.argv:
        i = sys.argv.index("--atlas")
        if i + 1 < len(sys.argv):
            read_atlas(sys.argv[i + 1])
        else:
            print("--atlas needs a file path")


if __name__ == "__main__":
    main()
