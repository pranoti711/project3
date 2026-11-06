"""00_check_raw_data.py - audit EVERYTHING in 02_data/raw in one command. Changes no data.
Run (PowerShell, from the PROJECT folder):
    & "C:\\Program Files\\Python310\\python.exe" ".\\project3\\04_scripts\\00_check_raw_data.py"
Checks: WONDER exports (series, database, years, counties), disease files (columns, counties, years, suppression,
which of hepatitis B/C/A, HIV, syphilis ... each file contains), AHRF releases (format, years covered for California),
environment files (variables, county, years, granularity), geography. Prints PASS / MISSING per requirement
and writes 00_docs/09_raw_data_check.md. Needs: pandas (+ openpyxl / xlrd only if you have real Excel files).
"""
import argparse, re, io, sys, csv, collections, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
try: sys.stdout.reconfigure(errors="replace")
except Exception: pass

ROOT = Path(__file__).resolve().parents[1]
RAW, DOCS = ROOT / "02_data/raw", ROOT / "00_docs"
DOCS.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser(description="Audit the project's raw data inputs.")
parser.add_argument(
    "--require-all",
    action="store_true",
    help="exit with status 2 when any raw-data requirement is missing",
)
REQUIRE_ALL = parser.parse_args().require_all
LINES = []
def say(s=""):
    s = str(s); print(s); LINES.append(s)
def show(df): say(df.to_string(index=False) if len(df) else "  (none)")

CA = ["Alameda","Alpine","Amador","Butte","Calaveras","Colusa","Contra Costa","Del Norte","El Dorado","Fresno","Glenn","Humboldt",
      "Imperial","Inyo","Kern","Kings","Lake","Lassen","Los Angeles","Madera","Marin","Mariposa","Mendocino","Merced","Modoc","Mono",
      "Monterey","Napa","Nevada","Orange","Placer","Plumas","Riverside","Sacramento","San Benito","San Bernardino","San Diego",
      "San Francisco","San Joaquin","San Luis Obispo","San Mateo","Santa Barbara","Santa Clara","Santa Cruz","Shasta","Sierra",
      "Siskiyou","Solano","Sonoma","Stanislaus","Sutter","Tehama","Trinity","Tulare","Tuolumne","Ventura","Yolo","Yuba"]
CA_SET = {c.lower() for c in CA}
def ca_match(v):
    s = str(v).strip()
    if re.fullmatch(r"6\d{3}", s): s = "0" + s
    if re.fullmatch(r"06\d{3}", s): return s
    n = re.sub(r"\s+county$", "", re.sub(r",\s*ca$", "", s.lower()))
    return n if n in CA_SET else None

CONCEPTS = {"hepatitis C": r"hepatitis[\s_\-]*c\b|\bhcv\b|\bhep[\s_\-]*c\b", "hepatitis B": r"hepatitis[\s_\-]*b\b|\bhbv\b|\bhep[\s_\-]*b\b",
            "hepatitis A": r"hepatitis[\s_\-]*a\b|\bhep[\s_\-]*a\b", "HIV": r"\bhiv\b|\baids\b", "syphilis": r"syphilis",
            "chlamydia": r"chlamydia", "gonorrhea": r"gonorrh"}
CRX = {k: re.compile(v, re.I) for k, v in CONCEPTS.items()}
DOC_PAT = re.compile(r"documentation|crosswalk|user.?guide|whats?.?new|dictionary|datapackage|readme|metadata", re.I)

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
        _, val = l.split(":", 1)
        if val.strip().lower().lstrip("*").startswith("all") or not val.strip(): continue
        out.append(l)
    return out
STD_KEYS = re.compile(r"^(group by|show totals|show zero|show suppressed|calculate rates|rate options|title|export|precision|year|month|dataset|query date|help)", re.I)
def other_filters(footer):
    """query lines for demographic / place / time filters that are NOT 'All ...' (a stray Race, Sex, Age ... filter)"""
    out = []
    filter_keys = re.compile(
        r"^(?:states?|counties|age groups?|sex|race|hispanic origin|"
        r"years?(?:\s*/\s*months?)?|months?|weekdays?|autopsy|place of death)$",
        re.I,
    )
    for l in query_block(footer):
        if ":" not in l: continue
        key, val = l.split(":", 1)
        key = key.strip()
        if STD_KEYS.match(key) or not filter_keys.fullmatch(key): continue
        if re.match(r"^(residence |occurrence )?states?$", key, re.I) and "california" in val.lower(): continue
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
    if series in {"suicide", "homicide"} and re.search(
        r"UCD\s*-\s*Injury Mechanism\s*&\s*All Other Leading Causes\s*:\s*(?!all\b)\S",
        " ".join(cause_lines(footer)),
        re.I,
    ):
        hard.append("extra Injury Mechanism / All Other Leading Causes selection; clear that selection and keep only Injury Intent")
    return hard, soft
def detect_series(footer, max_deaths):
    c = " ".join(cause_lines(footer)).lower()
    if re.search(r"drug poison|x40|overdose|drug/alcohol|drug-induced|drug induced", c): return "drug_od"
    if re.search(r"suicide|x6\d|x7\d|x8[0-4]|u03|y87\.?0", c) and not re.search(r"homicide|x85|x9\d|y0\d", c): return "suicide"
    if re.search(r"homicide|x85|x9\d|y0\d|u0[12]|y87\.?1", c) and not re.search(r"suicide", c): return "homicide"
    return "all_cause" if (max_deaths is not None and max_deaths > 20000) else "unknown"

def sniff(p):
    h = p.read_bytes()[:8]
    return "excel" if (h.startswith(b"\xd0\xcf\x11\xe0") or h.startswith(b"PK")) else "text"
def delim(p):
    with p.open("r", encoding="utf-8-sig", errors="replace") as f: first = f.readline()
    return "\t" if first.count("\t") > first.count(",") else ","
def header_row(p, sep):
    """index of the first real table header (skips 'Date Printed / Title / Footnote' lines at the top of exports)"""
    with p.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        lines = [f.readline() for _ in range(150)]
    cnt = [len(next(csv.reader([l], delimiter=sep), [])) if l.strip() else 0 for l in lines]
    for i in range(len(lines) - 3):
        if cnt[i] >= 3 and cnt[i] == cnt[i + 1] == cnt[i + 2] == cnt[i + 3]: return i
    return 0
def header(p):
    if sniff(p) == "excel": df = pd.read_excel(p, dtype=str, nrows=3000)
    else:
        sp = delim(p)
        df = pd.read_csv(p, sep=sp, dtype=str, nrows=3000, on_bad_lines="skip", encoding="utf-8-sig", encoding_errors="replace",
                         skiprows=header_row(p, sp))
    df.columns = [str(c).strip().strip('"') for c in df.columns]
    return df
def pick(cols, pats, prefer=()):
    for pr in prefer:
        for c in cols:
            if c.lower() == pr: return c
    for c in cols:
        if any(re.search(x, c, re.I) for x in pats): return c
    return None
def chunks(p, wanted):
    use = lambda c: str(c).strip().strip('"') in wanted
    if sniff(p) == "excel":
        df = pd.read_excel(p, dtype=str, usecols=use); df.columns = [str(c).strip().strip('"') for c in df.columns]; yield df
    else:
        sp = delim(p)
        for ch in pd.read_csv(p, sep=sp, dtype=str, usecols=use, chunksize=200_000, on_bad_lines="skip",
                              encoding="utf-8-sig", encoding_errors="replace", skiprows=header_row(p, sp)):
            ch.columns = [str(c).strip().strip('"') for c in ch.columns]; yield ch

def profile(p):
    """One table file -> dict of what it contains."""
    h = header(p); cols = list(h.columns)
    r = dict(file=p.name, path=p, hdr=[c.lower() for c in cols], rows=0, cols=len(cols), year_col=None, years=set(), cty_col=None, ca=set(), dis_col=None,
             miss=np.nan, concept={}, wide_years=[], raw_periods=set(), values=set())
    r["year_col"] = pick(cols, [r"year", r"period", r"date"], prefer=("year",))
    r["cty_col"] = pick(cols, [r"county code", r"fips", r"geoid", r"county", r"cnty", r"jurisdiction", r"lhj", r"geograph", r"area"],
                        prefer=("county code", "fips", "county"))
    r["dis_col"] = pick(cols, [r"disease", r"condition", r"cause", r"diagnos", r"indicator", r"measure", r"variable", r"parameter",
                               r"pollutant", r"topic", r"category", r"outcome"], prefer=("disease",))
    val = pick(cols, [r"^cases?$", r"cases", r"^counts?$", r"number", r"persons", r"deaths?", r"^total$", r"value"])
    r["wide_years"] = sorted({int(m.group(0)) for c in cols for m in [re.search(r"(?:19|20)\d\d", c)] if m})
    nm = re.sub(r"[_\-\[\]\.\(\)]", " ", p.stem)
    file_level = {k for k, x in CRX.items() if x.search(nm) or any(x.search(re.sub(r"[_\-]", " ", c)) for c in cols)}
    wanted = {c for c in (r["year_col"], r["cty_col"], r["dis_col"], val) if c}
    bad = tot = 0
    if wanted:
        for ch in chunks(p, wanted):
            r["rows"] += len(ch)
            ys = None
            if r["year_col"] in ch:
                raw = ch[r["year_col"]].astype(str)
                if len(r["raw_periods"]) < 20000: r["raw_periods"] |= set(raw.unique()[:5000])
                ys = pd.to_numeric(raw.str.extract(r"((?:19|20)\d\d)")[0], errors="coerce")
                r["years"] |= set(ys.dropna().astype(int))
            cm = ch[r["cty_col"]].map(ca_match) if r["cty_col"] in ch else None
            if cm is not None: r["ca"] |= set(cm.dropna())
            if r["dis_col"] in ch:
                col = ch[r["dis_col"]].astype(str)
                if len(r["values"]) < 400: r["values"] |= set(col.unique()[:400])
                for k, x in CRX.items():
                    m = col.str.contains(x, na=False)
                    if m.any():
                        s = r["concept"].setdefault(k, dict(rows=0, years=set(), ca=set()))
                        s["rows"] += int(m.sum())
                        if ys is not None: s["years"] |= set(ys[m].dropna().astype(int))
                        if cm is not None: s["ca"] |= set(cm[m].dropna())
            if val and val in ch:
                v = pd.to_numeric(ch[val], errors="coerce"); bad += int(v.isna().sum()); tot += len(v)
    r["miss"] = 100 * bad / tot if tot else np.nan
    for k in file_level:                                            # concept named in file name / column names
        if k not in r["concept"]:
            r["concept"][k] = dict(rows=r["rows"], years=set(r["years"]) or set(r["wide_years"]), ca=set(r["ca"]))
    return r

def atlas_title(path):
    """Return AtlasPlus title metadata from the CSV preamble, when present."""
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace") as f:
            for _ in range(20):
                line = f.readline()
                if line.lower().startswith("title:"):
                    return line.strip()
    except OSError:
        return ""
    return ""

def yrs(s): return f"{min(s)}-{max(s)} ({len(s)} yrs)" if s else "none found"
def level(n): return "county" if n >= 40 else ("partial" if n >= 10 else ("few/none" if n else "no CA county column"))

VERDICT = []
def verdict(item, ok, detail): VERDICT.append((item, "PASS" if ok else "MISSING", detail))

# ============================ 0. inventory ============================
say("=" * 78); say("0. FILES FOUND UNDER 02_data/raw"); say("=" * 78)
if not RAW.exists(): raise SystemExit(f"Folder not found: {RAW}. Run this from the PROJECT folder.")
inv = []
for f in sorted(RAW.rglob("*")):
    if f.is_file(): inv.append(dict(folder=str(f.parent.relative_to(RAW)), file=f.name, size_mb=round(f.stat().st_size / 1e6, 2)))
show(pd.DataFrame(inv))
zips = [i["file"] for i in inv if i["file"].lower().endswith(".zip")]
if zips: say(f"\nNOTE: ZIP files not extracted (extract them first): {zips}")
def nfiles(sub):
    d = RAW / sub
    return len([x for x in d.rglob("*") if x.is_file()]) if d.exists() else 0
for subs in [["disease"], ["mortality/wonder_final"], ["mortality/nchs_model_based_2003_2021"], ["context/ahrf_2024_2025"],
             ["context/ahrf_older_releases"], ["context/environment", "environment"], ["geography"]]:
    if sum(nfiles(x) for x in subs) == 0: say(f"  empty or missing folder: {' or '.join(subs)}")

# ============================ 1. WONDER ============================
say("\n" + "=" * 78); say("1. CDC WONDER mortality (02_data/raw/mortality/wonder_final)"); say("=" * 78)
WD = RAW / "mortality/wonder_final"
rows, detail, frames = [], [], {}
found_ok, found_bad = {}, {}
def wonder_read(p):
    if sniff(p) == "excel":
        df = pd.read_excel(p, dtype=str); df.columns = [str(c).strip().strip('"') for c in df.columns]
        cc = df["County Code"] if "County Code" in df.columns else pd.Series(dtype=str)
        foot = "\n".join(" ".join(str(v) for v in row if pd.notna(v)) for row in (df[cc.isna()] if len(cc) else df).itertuples(index=False))
    else:
        text = p.read_bytes().decode("utf-8-sig", errors="replace")
        df = pd.read_csv(io.StringIO(text), sep="\t" if text.count("\t") > text.count(",") else ",", dtype=str, engine="python", on_bad_lines="skip")
        df.columns = [c.strip().strip('"') for c in df.columns]
        foot = "\n".join(l for l in text.splitlines() if not re.search(r'"?06\d{3}"?', l))
    df = df.apply(lambda s: s.str.strip().str.strip('"') if s.dtype == object else s)
    cols = list(df.columns)
    if "County Code" not in cols: return None, foot, cols
    return df[df["County Code"].notna() & (df["County Code"] != "")], foot, cols
for f in (sorted(WD.iterdir()) if WD.exists() else []):
    if not f.is_file() or f.suffix.lower() not in {".xls", ".xlsx", ".txt", ".csv"} or f.name.startswith("~$"): continue
    try:
        d, foot, cols = wonder_read(f)
        qb = query_block(foot)
        gb = next((l.split(":", 1)[1].strip() for l in qb if l.lower().startswith("group by")), "?")
        ss = next((l.split(":", 1)[1].strip() for l in qb if l.lower().startswith("show suppressed")), "?")
        dset = (re.search(r"dataset:\s*([^\n]+)", foot, re.I) or [None, "?"])[1].strip()[:44]
        if d is None:
            msg = ("Not a WONDER export (no 'Notes' column): move it out of wonder_final." if "Notes" not in cols else
                   "No 'County Code' column. Set Group Results By = County, then Year (the cause goes in section 6, not in Group By).")
            rows.append(dict(file=f.name, series="NOT COUNTY-LEVEL" if "Notes" in cols else "NOT A WONDER FILE", group_by=gb, show_suppressed=ss, query=msg)); continue
        yr = pd.to_numeric(d["Year Code"], errors="coerce"); dn = pd.to_numeric(d["Deaths"], errors="coerce")
        ser = detect_series(foot, dn.max()); fl = foot.lower()
        m = re.search(r"multiple cause of death,\s*(\d{4})\s*-\s*(\d{4})", fl)
        db = f"{m.group(1)}_{m.group(2)}" if m else ("2018_2024" if yr.min() >= 2018 else "1999_2020")
        if "provisional" in dset.lower(): db = "provisional (not used)"
        cl_all = cause_lines(foot); of = other_filters(foot); hard, soft = cause_notes(ser, foot)
        issues = ([f"extra filter: {x}" for x in of] + hard)
        nm_l = f.name.lower().replace("_", " ")
        said = "homicide" if "homicide" in nm_l else ("suicide" if "suicide" in nm_l else ("drug_od" if "drug" in nm_l else None))
        name_note = (f"NAME SAYS {said.upper()} BUT QUERY SELECTS {ser.upper()} - rename or redo" if said and ser not in (said, "unknown") and "all_cause" not in ser else "")
        la = d[d["County Code"].str.zfill(5) == "06037"]
        la19 = la[pd.to_numeric(la["Year Code"], errors="coerce") == 2019]["Deaths"]
        al = d[d["County Code"].str.zfill(5) == "06001"]
        a19 = al[pd.to_numeric(al["Year Code"], errors="coerce") == 2019]["Deaths"]
        rows.append(dict(file=f.name, series=ser + (" (benchmark)" if ser == "all_cause" else ""), database=db, years=f"{int(yr.min())}-{int(yr.max())}",
                         counties=d["County Code"].nunique(), rows=len(d), alameda_2019=(a19.iloc[0] if len(a19) else "-"), LA_2019=(la19.iloc[0] if len(la19) else "-"),
                         suppressed_pct=round(100 * d["Deaths"].str.lower().str.contains("suppress", na=False).mean(), 1),
                         show_suppressed=ss, problems=("; ".join(issues + ([name_note] if name_note else [])) if (issues or name_note) else "none")))
        detail.append((f.name, ser, db, cl_all, of, soft, hard))
        key = (ser, db)
        if issues: found_bad.setdefault(key, []).append(f"{f.name}: {'; '.join(issues)}")
        else:
            found_ok.setdefault(key, []).append(f.name)
            frames[key] = pd.DataFrame({"fips": d["County Code"].str.zfill(5), "year": yr.astype("Int64"), "deaths": dn})
    except Exception as e:
        rows.append(dict(file=f.name, series=f"ERROR: {str(e)[:70]}"))
show(pd.DataFrame(rows))
say("\nFull query lines per file (cause selection and any non-default filter):")
for nm_, ser, db, cl_all, of, soft, hard in detail:
    say(f"  {nm_}  ->  {ser}, {db}")
    for l in cl_all: say(f"      cause : {l[:600]}")
    for l in of: say(f"      FILTER: {l}")
    for l in soft: say(f"      note  : {l}")
for r_ in rows:
    if r_.get("series", "").split(" ")[0] in ("drug_od", "suicide", "homicide") and str(r_.get("show_suppressed")).lower().startswith("false"):
        say(f"WARNING {r_['file']}: 'Show Suppressed' was False, so county-years with 1-9 deaths are missing. Tick 'Show Suppressed Values' and download again.")
say("\nDo the two databases agree for 2018-2020? (same county-years must have identical death counts)")
agree = {}
for s_ in ["drug_od", "suicide", "homicide"]:
    a_, b_ = frames.get((s_, "1999_2020")), frames.get((s_, "2018_2024"))
    if a_ is None or b_ is None: say(f"  {s_}: cannot compare (need a clean file from both databases)"); continue
    j = a_.merge(b_, on=["fips", "year"], suffixes=("_a", "_b"))
    j = j[j.year.between(2018, 2020)].dropna(subset=["deaths_a", "deaths_b"])
    n = len(j); nd = int((j.deaths_a != j.deaths_b).sum()); ratio = float((j.deaths_a / j.deaths_b.replace(0, np.nan)).median()) if n else np.nan
    agree[s_] = (n, nd, ratio)
    say(f"  {s_}: {n} comparable county-years, {nd} differ, median ratio 1999-2020 file / 2018-2024 file = {ratio:.2f}" + ("" if n and nd / n <= 0.02 else "   <-- MISMATCH: the two files were not made with the same selections"))
for s in ["drug_od", "suicide", "homicide"]:
    for db in ["1999_2020", "2018_2024"]:
        ok = bool(found_ok.get((s, db)))
        bad = "; ".join(found_bad.get((s, db), []))
        verdict(f"WONDER {s} {db}", ok, "; ".join(found_ok.get((s, db), [])) if ok else (f"file found but has problems: {bad}" if bad else "no file with that cause/database"))
    n_, nd_, _ = agree.get(s, (0, 0, np.nan))
    verdict(f"WONDER {s}: both databases agree 2018-2020", n_ >= 20 and nd_ / max(n_, 1) <= 0.02, f"{n_} county-years compared, {nd_} differ" if n_ else "needs a clean file from both databases")

# ============================ 2. DISEASE ============================
say("\n" + "=" * 78); say("2. DISEASE files (02_data/raw/disease, including subfolders)"); say("=" * 78)
DD = RAW / "disease"; profs = []
for f in (sorted(DD.rglob("*")) if DD.exists() else []):
    if not f.is_file() or f.suffix.lower() not in {".csv", ".txt", ".tsv", ".xls", ".xlsx"}: continue
    try:
        pr = profile(f); pr["doc"] = bool(DOC_PAT.search(f.name)); pr["atlas_title"] = atlas_title(f); profs.append(pr)
    except Exception as e:
        say(f"  ERROR reading {f.name}: {e}  (for Excel files try: pip install openpyxl xlrd)")
def disease_layout(pr):
    columns = set(pr["hdr"])
    if {"disease", "county", "year", "sex", "cases"} <= columns:
        return "CDPH long format"
    if {"indicator", "year", "geography", "fips", "cases"} <= columns:
        return "AtlasPlus county format"
    if {"indicator", "year", "cases"} <= columns:
        if re.search(r"\bCalifornia\b", pr.get("atlas_title", ""), re.I):
            return "AtlasPlus California state descriptive"
        return "AtlasPlus aggregate (not county-resolvable)"
    return "other layout"

tab = []
for pr in profs:
    fmt = "documentation" if pr["doc"] else disease_layout(pr)
    tab.append(dict(file=pr["file"][:46], layout=fmt, rows=pr["rows"], year_col=pr["year_col"], years=yrs(pr["years"]) if pr["years"] else (f"wide: {yrs(set(pr['wide_years']))}" if pr["wide_years"] else "-"),
                    CA_counties=f"{len(pr['ca'])}/58", level=level(len(pr["ca"])), missing_pct=("" if pd.isna(pr["miss"]) else round(pr["miss"], 1)),
                    mentions=", ".join(sorted(pr["concept"])) or "-"))
show(pd.DataFrame(tab))
say("\nWhich diseases each file covers (rows, years, California counties found):")
cs = []
for pr in profs:
    if pr["doc"]: continue
    for k, s in pr["concept"].items():
        cs.append(dict(disease=k, file=pr["file"][:44], rows=s["rows"], years=yrs(s["years"]), counties=f"{len(s['ca'])}/58", level=level(len(s["ca"]))))
show(pd.DataFrame(cs).sort_values(["disease", "file"]) if cs else pd.DataFrame())
def best(k):
    c = [(len(s["ca"]), len(s["years"]), pr["file"]) for pr in profs if not pr["doc"] for kk, s in pr["concept"].items() if kk == k]
    return max(c) if c else (0, 0, "")
for k, need in [("hepatitis B", "drug-linked"), ("hepatitis C", "drug-linked"), ("HIV", "ambiguous"), ("hepatitis A", "ambiguous"), ("syphilis", "ambiguous")]:
    n, y, fn = best(k)
    if k.startswith("hepatitis"):
        state_sources = [
            pr for pr in profs
            if not pr["doc"] and disease_layout(pr) == "AtlasPlus California state descriptive"
            and k in pr["concept"] and len(pr["concept"][k]["years"]) >= 10
        ]
        state_ok = bool(state_sources)
        state_detail = f"{state_sources[0]['file']}; California state-level descriptive series, not county data" if state_ok else "no California state-level series with at least 10 years"
        verdict(f"State descriptive: {k}", state_ok, state_detail)
        say(f"  County-level {k}: {n}/58 counties, {y} years; excluded from county panel.")
    else:
        verdict(f"Disease: {k} ({need} group)", n >= 40 and y >= 10, f"best file: {fn or 'none'}; counties {n}/58, years {y}" if fn else "not found in any file")
for pr in profs:
    layout = disease_layout(pr)
    if layout == "AtlasPlus California state descriptive":
        say(f"\nSTATE-LEVEL DESCRIPTIVE ONLY: {pr['file']} title identifies California; this series is not county-resolvable and is excluded from the county panel.")
    elif layout == "AtlasPlus aggregate (not county-resolvable)":
        say(f"\nNOT COUNTY-RESOLVABLE: {pr['file']} has no county geography/FIPS columns; it cannot be joined to the county panel.")
    elif layout == "other layout" and not pr["doc"]:
        say(f"\nLAYOUT NOT RECOGNISED as CDPH long format: {pr['file']}  -> paste the next lines to me so I can write its reader")
        say("  columns: " + " | ".join(header(pr["path"]).columns)[:400])
        say(header(pr["path"]).head(3).to_string()[:600])

# ============================ 3. AHRF ============================
say("\n" + "=" * 78); say("3. AHRF releases (context/ahrf_2024_2025 and context/ahrf_older_releases)"); say("=" * 78)
cover = collections.defaultdict(lambda: (0, ""))
arows = []
for d in [RAW / "context/ahrf_2024_2025", RAW / "context/ahrf_older_releases"]:
    for f in (sorted(d.rglob("*.csv")) if d.exists() else []):
        if DOC_PAT.search(f.name): continue
        try:
            h = pd.read_csv(f, nrows=0, encoding="latin1"); cols = list(h.columns)
            fc = next((c for c in cols if c.lower() in ("fips_st_cnty", "f00002", "f12424", "fips")), None)
            if fc is None: arows.append(dict(folder=d.name, file=f.name[:40], note="no county FIPS column - not a county AHRF file?")); continue
            df = pd.read_csv(f, dtype=str, encoding="latin1", low_memory=False)
            ca = df[df[fc].astype(str).str.zfill(5).str.startswith("06")]
            per = collections.Counter()
            for c in df.columns:
                m = re.match(r"^(.*?)[_\-](\d{2})$", c) or re.match(r"^([fF]\d{5})(\d{2})$", c)
                if m and ca[c].replace("", np.nan).notna().sum() >= 10:
                    yy = int(m.group(2)); per[2000 + yy if yy < 80 else 1900 + yy] += 1
            for y, n in per.items():
                if n > cover[y][0]: cover[y] = (n, f.name)
            arows.append(dict(folder=d.name, file=f.name[:40], format="descriptive names" if "fips_st_cnty" in cols else "coded names", cols=len(cols),
                              CA_rows=len(ca), **{str(y): per.get(y, 0) for y in range(2019, 2025)}))
        except Exception as e:
            arows.append(dict(folder=d.name, file=f.name[:40], note=f"ERROR {str(e)[:70]}"))
show(pd.DataFrame(arows))
say("(columns 2019..2024 = number of variables with data for California counties in that year)")
miss = [y for y in range(2019, 2024) if cover[y][0] < 50]
verdict("AHRF context covers 2019-2023", not miss, "all five years have 50+ variables" if not miss else f"years with <50 variables: {miss}")
verdict("AHRF older releases present", any((RAW / "context/ahrf_older_releases").rglob("*.csv")) if (RAW / "context/ahrf_older_releases").exists() else False, "files in ahrf_older_releases")

# ============================ 4. ENVIRONMENT ============================
say("\n" + "=" * 78); say("4. ENVIRONMENT source (drought, temperature, air quality, smoke ...)"); say("=" * 78)
ENV = {"temperature": r"temp|tmax|tmin|tavg", "precipitation": r"precip|rain|ppt|prcp", "drought": r"drought|pdsi|spi\b|usdm",
       "air quality / PM2.5": r"pm2|pm25|pm_2|aqi|ozone|air.?qual", "wildfire / smoke": r"wildfire|smoke|fire|burn", "humidity": r"humid|vpd"}
env_dirs = [RAW / "environment", RAW / "context/environment"]
env_files = [f for d in env_dirs if d.exists() for f in sorted(d.rglob("*")) if f.is_file() and f.suffix.lower() in {".csv", ".txt", ".xls", ".xlsx"} and not DOC_PAT.search(f.name)]
erows = []; env_ok = []
for f in env_files:
    try:
        pr = profile(f); h = header(f)
        text = " ".join(list(h.columns) + sorted(pr["values"])[:300] + [f.stem])
        vars_ = [k for k, x in ENV.items() if re.search(x, text, re.I)]
        per = len(pr["raw_periods"]) / max(len(pr["years"]), 1)
        gran = "annual" if per <= 1.5 else f"sub-annual (~{per:.0f} periods/yr: aggregate to annual)"
        erows.append(dict(file=f.name[:40], rows=pr["rows"], variables=", ".join(vars_) or "none recognised", county_col=pr["cty_col"] or "-",
                          CA_counties=f"{len(pr['ca'])}/58", years=yrs(pr["years"]), granularity=gran))
        env_ok.append((vars_, len(pr["ca"]), len(pr["years"])))
    except Exception as e:
        erows.append(dict(file=f.name[:40], variables=f"ERROR {str(e)[:60]}"))
show(pd.DataFrame(erows))
verdict("Environment file present", bool(env_files), f"{len(env_files)} file(s)")
verdict("Environment: variables recognised", any(v for v, _, _ in env_ok), "; ".join(sorted({x for v, _, _ in env_ok for x in v})) or "none")
verdict("Environment: California counties identifiable", any(n >= 40 for _, n, _ in env_ok), f"best {max([n for _, n, _ in env_ok], default=0)}/58 counties")
verdict("Environment: 15+ years", any(y >= 15 for _, _, y in env_ok), f"best {max([y for _, _, y in env_ok], default=0)} years")

# ============================ 5. other ============================
say("\n" + "=" * 78); say("5. Other folders"); say("=" * 78)
for sub, label in [("mortality/cdc_export_2019_2024", "CDC export (2019-2024)"), ("mortality/nchs_model_based_2003_2021", "NCHS model-based (sensitivity)"), ("geography", "geography (optional)")]:
    d = RAW / sub; n = len([x for x in d.rglob("*") if x.is_file()]) if d.exists() else 0
    say(f"  {label}: {n} file(s)")
verdict("NCHS model-based estimates (sensitivity)", (RAW / "mortality/nchs_model_based_2003_2021").exists() and any((RAW / "mortality/nchs_model_based_2003_2021").rglob("*.*")), "optional but in your plan")

# ============================ verdict ============================
say("\n" + "=" * 78); say("VERDICT"); say("=" * 78)
V = pd.DataFrame(VERDICT, columns=["requirement", "status", "detail"]); show(V)
nm = V[V.status == "MISSING"]
say(f"\n{len(V) - len(nm)} of {len(V)} requirements pass.")
if nm.empty:
    next_step = "run  python .\\project3\\04_scripts\\run_data_pipeline.py"
else:
    actions = []
    if nm.requirement.str.startswith("WONDER").any():
        wonder_missing = nm[nm.requirement.str.startswith("WONDER")]
        if wonder_missing["detail"].str.contains("extra Injury Mechanism / All Other Leading Causes selection", regex=False).any():
            actions.append("re-export both suicide and homicide files from each database with only Injury Intent selected; clear Injury Mechanism / All Other Leading Causes")
        else:
            actions.append("re-export the WONDER files flagged above with the correct query selections")
    if nm.requirement.str.startswith("Disease:").any():
        actions.append("supply county-resolvable disease data or revise the affected study scope; do not expand state totals to counties")
    if nm.requirement.str.startswith("Environment:").any():
        actions.append("add the missing supported environmental data")
    if not actions:
        actions.append("resolve the MISSING requirements above")
    next_step = "; ".join(actions)
say("NEXT: " + next_step)
(DOCS / "09_raw_data_check.md").write_text("```text\n" + "\n".join(LINES) + "\n```\n", encoding="utf-8")
print("\nReport saved to 00_docs/09_raw_data_check.md")
if REQUIRE_ALL and not nm.empty:
    raise SystemExit(2)
