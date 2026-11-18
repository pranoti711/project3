import json, re, urllib.parse, urllib.request
from pathlib import Path

QUERIES = {
 "abara2019":     "Abara opioid prescribing trends gonorrhea counties Annals of Epidemiology 2019",
 "cohen2003":     "Cohen boarded-up housing gonorrhea premature death 107 US cities American Journal of Public Health 2003",
 "gizamba2026":   "Gizamba BMC Public Health 2026 hepatitis C Los Angeles ZIP codes machine learning",
 "gonsalves2021": "Gonsalves overdose HIV Lawrence Lowell Massachusetts Open Forum Infectious Diseases 2021",
 "gonsalves2023": "Gonsalves Clinical Infectious Diseases 2023 Massachusetts ZIP code HIV predict outbreaks",
 "kidd2019":      "Kidd syphilis methamphetamine injection drug use 2019",
 "marks2021tr":   "Marks Translational Research 2021 opioid epidemic detection risk assessment prediction review",
 "patton2025":    "Patton 2025 overdose mortality forecasting",
 "pencina2008":   "Pencina D'Agostino Vasan Evaluating the added predictive ability of a new marker Statistics in Medicine 2008",
 "rickles2018":   "Rickles Tennessee vulnerability assessment HCV HIV opioid Clinical Infectious Diseases 2018",
 "shover2020":    "Shover steep increases fentanyl-related mortality west of the Mississippi River Drug and Alcohol Dependence 2020",
 "sumetsky2021":  "Sumetsky 2021 opioid overdose mortality forecast spatial",
}
CHOICE = {}   # key -> 0, 1 or 2 if the top hit is wrong, then rerun

def search(q):
    url = ("https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(q))
    req = urllib.request.Request(url, headers={"User-Agent": "project3-refs/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["message"]["items"]

def bibtex(key, it):
    auth = " and ".join((a.get("family", "") + ", " + a.get("given", "")).strip(", ") for a in it.get("author", [])) or "Unknown"
    title = (it.get("title") or ["?"])[0]
    jr = (it.get("container-title") or ["?"])[0]
    year = (it.get("issued", {}).get("date-parts") or [[""]])[0][0]
    f = {"author": auth, "title": title, "journal": jr, "year": year,
         "volume": it.get("volume"), "number": it.get("issue"),
         "pages": re.sub(r"\s*[-\u2013]\s*", "--", it["page"]) if it.get("page") else None,
         "doi": it.get("DOI"), "note": "AUTO from Crossref: check this is the right paper"}
    body = ",\n".join("  %-8s= {%s}" % (k, v) for k, v in f.items() if v)
    return "@article{%s,\n%s\n}\n" % (key, body)

out = []
for key, q in QUERIES.items():
    try:
        items = search(q)
    except Exception as e:
        print(key, "FAILED:", e); continue
    print("\n==", key)
    for i, it in enumerate(items):
        a = it.get("author", [{}])[0].get("family", "?")
        y = (it.get("issued", {}).get("date-parts") or [[""]])[0][0]
        print("  [%d] %s %s | %s | %s | %s" % (i, a, y, (it.get("title") or ["?"])[0][:80], (it.get("container-title") or ["?"])[0][:30], it.get("DOI")))
    if items:
        out.append(bibtex(key, items[CHOICE.get(key, 0)]))
Path("06_paper/references_auto.bib").write_text("\n".join(out), encoding="utf-8")
print("\nwrote 06_paper/references_auto.bib with", len(out), "entries")
