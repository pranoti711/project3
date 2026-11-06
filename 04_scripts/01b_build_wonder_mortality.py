"""01b_build_wonder_mortality.py (v2) - read CDC WONDER exports for California counties.
Reads every .xls / .xlsx / .txt / .csv file in 02_data/raw/mortality/wonder_final/ (top level only).
NO renaming needed: for each file the script reads the query notes at the bottom of the export and works out
  - which series it is: drug_od | suicide | homicide | all_cause (benchmark only)
  - which database it is: 1999_2020 or 2018_2024
and prints what it found so you can check it. Files that are exact repeats (e.g. 'name (1).xls') are de-duplicated.
Rules: 'Suppressed' deaths (1-9) are kept as a RANGE (lo=1, hi=9), never zero; 'Unreliable' rates are blanked and flagged.
Years <= 2020 come from the 1999_2020 database, 2021+ from the 2018_2024 database; 2018-2020 overlap is cross-checked.
Outputs (02_data/processed): mortality_wonder_long.csv, mortality_ca_wide_wonder.csv
"""
from pathlib import Path
import io, re, numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "02_data/raw/mortality/wonder_final", ROOT / "02_data/processed"
OUT.mkdir(parents=True, exist_ok=True)
SPLIT_YEAR = 2020
EXTS = {".xls", ".xlsx", ".txt", ".csv"}

def read_any(path):
    head = path.read_bytes()[:8]
    if head.startswith(b"\xd0\xcf\x11\xe0") or head.startswith(b"PK"):          # real Excel file
        df = pd.read_excel(path, dtype=str)
        df.columns = [str(c).strip().strip('"') for c in df.columns]
        cc = df["County Code"] if "County Code" in df.columns else pd.Series(dtype=str)
        foot_rows = df[cc.isna()] if len(cc) else df
        footer = "\n".join(" ".join(str(v) for v in row if pd.notna(v)) for row in foot_rows.itertuples(index=False))
    else:                                                                          # tab-delimited text (WONDER default)
        text = path.read_bytes().decode("utf-8-sig", errors="replace")
        df = pd.read_csv(io.StringIO(text), sep="\t", dtype=str, engine="python", on_bad_lines="skip")
        df.columns = [c.strip().strip('"') for c in df.columns]
        footer = "\n".join(l for l in text.splitlines() if not re.search(r'"?06\d{3}"?', l))
    df = df.apply(lambda s: s.str.strip().str.strip('"') if s.dtype == object else s)
    if "County Code" not in df.columns:
        raise ValueError(f"no 'County Code' column; columns are {list(df.columns)} - was the export grouped by County?")
    df = df[df["County Code"].notna() & (df["County Code"] != "")]
    return df, footer

def query_block(footer):
    """lines of the 'Query Parameters' section only (general numbered footnotes are ignored)"""
    lines = [l.strip().strip('"').strip() for l in footer.splitlines()]
    idx = next((i for i, l in enumerate(lines) if re.search(r"query parameters", l, re.I)), None)
    if idx is None: return [l for l in lines if l and not re.match(r"^\d+\.\s", l)]
    blk = []
    for l in lines[idx + 1:]:
        if l.startswith("---") or l.lower().startswith("help"): break
        if l: blk.append(l)
    return blk
def cause_lines(footer):
    """cause-related query lines whose value is NOT 'All ...' (i.e. a filter was really chosen)"""
    out = []
    for l in query_block(footer):
        if l.lower().startswith("title") or not re.search(r"cause|intent|icd|mechanism|drug|alcohol", l, re.I) or ":" not in l: continue
        key, val = l.split(":", 1)
        if val.strip().lower().lstrip("*").startswith("all") or not val.strip(): continue
        out.append(l)
    return out
STD_KEYS = re.compile(r"^(group by|show totals|show zero|show suppressed|calculate rates|rate options|title|export|precision|year|month|dataset|query date|help)", re.I)
def other_filters(footer):
    """query lines for demographic / place / time filters that are NOT 'All ...' (a stray Race, Sex, Age ... filter)"""
    out = []
    for l in query_block(footer):
        if ":" not in l: continue
        key, val = l.split(":", 1)
        if STD_KEYS.match(key.strip()) or re.search(r"cause|intent|mechanism|icd|drug|alcohol", key, re.I): continue
        if re.match(r"^(residence |occurrence )?states?$", key.strip(), re.I) and "california" in val.lower(): continue
        if not val.strip() or val.strip().lower().lstrip("*").startswith("all"): continue
        out.append(l)
    return out
def cause_notes(series, footer):
    ct = " ".join(cause_lines(footer)).lower(); hard, soft = [], []
    if series == "drug_od":
        if re.search(r"(?<![/\w])alcohol[- ]induced causes\b", ct):
            hard.append("alcohol-induced causes are included (select only drug poisonings)")
        if "drug-induced causes" in ct and "drug poisoning" not in ct:
            soft.append("whole 'Drug-induced causes' group (adds ~5% non-overdose); fine if both databases use the same choice")
    return hard, soft
def detect_series(footer, max_deaths):
    c = " ".join(cause_lines(footer)).lower()
    if re.search(r"drug poison|x40|overdose|drug/alcohol|drug-induced|drug induced", c): return "drug_od"
    if re.search(r"suicide|x6\d|x7\d|x8[0-4]|u03|y87\.?0", c) and not re.search(r"homicide|x85|x9\d|y0\d", c): return "suicide"
    if re.search(r"homicide|x85|x9\d|y0\d|u0[12]|y87\.?1", c) and not re.search(r"suicide", c): return "homicide"
    return "all_cause" if (max_deaths is not None and max_deaths > 20000) else "unknown"

def detect_db(footer, years):
    m = re.search(r"multiple cause of death,\s*(\d{4})\s*-\s*(\d{4})", footer.lower())
    if m: return f"{m.group(1)}_{m.group(2)}"
    return "2018_2024" if years.min() >= 2018 else "1999_2020"

frames, report = [], []
for f in sorted(RAW.iterdir()):
    if not f.is_file() or f.suffix.lower() not in EXTS or f.name.startswith("~$"): continue
    try:
        df, footer = read_any(f)
    except Exception as e:
        print(f"SKIPPED {f.name}: {e}"); continue
    out = pd.DataFrame({
        "fips": df["County Code"].str.zfill(5), "county_name": df["County"],
        "year": pd.to_numeric(df["Year Code"], errors="coerce").astype("Int64"),
        "deaths_raw": df["Deaths"], "population": pd.to_numeric(df["Population"], errors="coerce"),
        "rate_raw": df["Crude Rate"] if "Crude Rate" in df.columns else np.nan})
    if not out.fips.str.startswith("06").all():
        print(f"SKIPPED {f.name}: contains non-California counties"); continue
    num = pd.to_numeric(out.deaths_raw, errors="coerce")
    series = detect_series(footer, num.max())
    db = detect_db(footer, out.year)
    of = other_filters(footer); hard, soft = cause_notes(series, footer)
    if of or hard:
        print(f"SKIPPED {f.name}: " + "; ".join([f"extra filter ({x})" for x in of] + hard)); continue
    for sn in soft: print(f"NOTE {f.name}: {sn}")
    cause_line = "; ".join(cause_lines(footer))[:160] or "(no cause filter found in the query notes)"
    report.append(dict(file=f.name, series=series, database=db, rows=len(out), years=f"{out.year.min()}-{out.year.max()}",
                       max_deaths=int(num.max()) if num.notna().any() else 0, cause_line=cause_line))
    if series == "unknown":
        print(f"SKIPPED {f.name}: could not tell which cause was selected (see cause_line below)"); continue
    out["series"], out["source_db"], out["file"] = series, db, f.name
    frames.append(out)

print("\nWONDER files found:")
print(pd.DataFrame(report).to_string(index=False))
assert frames, f"no usable WONDER files in {RAW}"
w = pd.concat(frames, ignore_index=True)

# de-duplicate identical series/database (e.g. 'file (1).xls'): keep the file with most rows
keep = (w.groupby(["series", "source_db", "file"]).size().reset_index(name="n")
          .sort_values("n", ascending=False).drop_duplicates(["series", "source_db"]))
dups = w.groupby(["series", "source_db"]).file.nunique()
for (s, d), k in dups[dups > 1].items(): print(f"NOTE: {k} files for {s} {d}; using the one with most rows")
w = w.merge(keep[["series", "source_db", "file"]], on=["series", "source_db", "file"])

for s, g in w.groupby("series"):
    a, b = g[g.source_db == "1999_2020"], g[g.source_db == "2018_2024"]
    if len(a) and len(b):
        j = a.merge(b, on=["fips", "year"], suffixes=("_a", "_b"))
        j = j[j.year.between(2018, 2020)]
        both = j[pd.to_numeric(j.deaths_raw_a, errors="coerce").notna() & pd.to_numeric(j.deaths_raw_b, errors="coerce").notna()]
        diff = (pd.to_numeric(both.deaths_raw_a) != pd.to_numeric(both.deaths_raw_b)).sum()
        print(f"overlap check {s}: {len(both)} comparable county-years 2018-2020, {diff} differ")
for s in ["drug_od", "suicide", "homicide"]:
    if s not in set(w.series): print(f"WARNING: no file found for series '{s}' yet")

w["keep"] = np.where(w.year <= SPLIT_YEAR, w.source_db == "1999_2020", w.source_db == "2018_2024")
only = w.groupby("series").source_db.transform("nunique") == 1
w = w[w.keep | only].drop(columns="keep")

num = pd.to_numeric(w.deaths_raw, errors="coerce")
w["status"] = np.where(num.notna(), "observed", np.where(w.deaths_raw.str.lower().str.contains("suppress", na=False), "suppressed", "other"))
w["deaths"] = num
w["deaths_lo"] = np.where(w.status == "observed", num, np.where(w.status == "suppressed", 1, np.nan))
w["deaths_hi"] = np.where(w.status == "observed", num, np.where(w.status == "suppressed", 9, np.nan))
rate = pd.to_numeric(w.rate_raw, errors="coerce")
w["crude_rate"] = rate
w["rate_flag"] = np.where(w.rate_raw.astype(str).str.lower().str.contains("unreliable"), "unreliable", np.where(rate.notna(), "ok", "none"))
long = w[["series", "fips", "county_name", "year", "deaths", "deaths_lo", "deaths_hi", "status", "population",
          "crude_rate", "rate_flag", "source_db"]].sort_values(["series", "fips", "year"])
long.to_csv(OUT / "mortality_wonder_long.csv", index=False)

fips_all = sorted(long.fips.unique()); years = range(int(long.year.min()), int(long.year.max()) + 1)
wide = pd.MultiIndex.from_product([fips_all, years], names=["fips", "year"]).to_frame(index=False)
for s, g in long.groupby("series"):
    g = g.set_index(["fips", "year"])
    t = pd.DataFrame({f"mort_{s}_count": g.deaths, f"mort_{s}_lo": g.deaths_lo, f"mort_{s}_hi": g.deaths_hi,
                      f"mort_{s}_suppressed": g.status.eq("suppressed"), f"mort_{s}_rate": g.crude_rate}).reset_index()
    wide = wide.merge(t, on=["fips", "year"], how="left")
pop = long.drop_duplicates(["fips", "year"]).set_index(["fips", "year"]).population.rename("population_wonder").reset_index()
wide = wide.merge(pop, on=["fips", "year"], how="left")
wide.to_csv(OUT / "mortality_ca_wide_wonder.csv", index=False)

print("\ncounties per year with an observed (>=10) count:")
print(long[long.status == "observed"].groupby(["series", "year"]).fips.nunique().unstack(0).to_string())
print("\nwrote mortality_wonder_long.csv and mortality_ca_wide_wonder.csv")
