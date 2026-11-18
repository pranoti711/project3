import json, re, urllib.parse, urllib.request
from pathlib import Path

UA = {"User-Agent": "project3-refs/1.0"}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)["message"]
def by_doi(d):  return get("https://api.crossref.org/works/" + urllib.parse.quote(d))
def search(q):  return get("https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(q))["items"]

def bibtex(key, it, year=None):
    auth = " and ".join((a.get("family", "") + ", " + a.get("given", "")).strip(", ") for a in it.get("author", [])) or "Unknown"
    y = year or (it.get("issued", {}).get("date-parts") or [[""]])[0][0]
    pg = it.get("page") or it.get("article-number")
    f = {"author": auth, "title": (it.get("title") or ["?"])[0], "journal": (it.get("container-title") or ["?"])[0],
         "year": y, "volume": it.get("volume"), "number": it.get("issue"),
         "pages": re.sub(r"\s*[-\u2013]\s*", "--", pg) if pg else None, "doi": it.get("DOI")}
    return "@article{%s,\n%s\n}\n" % (key, ",\n".join("  %-8s= {%s}" % (k, v) for k, v in f.items() if v))

bib = Path("06_paper/references.bib")
s = bib.read_text(encoding="utf-8")
def drop(key):
    global s
    s, n = re.subn(r"@article\{" + key + r",.*?\n\}\n*", "", s, count=1, flags=re.S)
    return n

DOIS = {
  "sumetsky2019": ("10.1136/jech-2019-212551", None),
  "marks2021lph": ("10.1016/S2468-2667(21)00080-3", None),
  "bauer2023":    ("10.2196/41450", None),
  "marks2021tr":  ("10.1016/j.trsl.2021.03.018", None),
  "sumetsky2021": ("10.1097/ede.0000000000001264", "2021"),
}
SEARCH = {
  "cohen2003":  "Cohen Mason Bedimo Scribner Basolo Farley Neighborhood physical conditions and health American Journal of Public Health 2003",
  "baker2014":  "Baker Schuit Steyerberg How to interpret a small increase in AUC with an additional risk prediction marker decision analysis comes through Statistics in Medicine 2014",
  "patton2025": "Patton overdose outbreak early warning alerts county 2025",
}

new = []
for key, (doi, yr) in DOIS.items():
    drop(key)
    it = by_doi(doi)
    new.append(bibtex(key, it, yr))
    print("DOI  ", key, "->", (it.get("title") or ["?"])[0][:70])
for key, q in SEARCH.items():
    drop(key)
    items = search(q)
    print("\n==", key)
    for i, it in enumerate(items):
        a = it.get("author", [{}])[0].get("family", "?")
        y = (it.get("issued", {}).get("date-parts") or [[""]])[0][0]
        print("  [%d] %s %s | %s | %s | %s" % (i, a, y, (it.get("title") or ["?"])[0][:75], (it.get("container-title") or ["?"])[0][:28], it.get("DOI")))
    new.append(bibtex(key, items[0]))

for key, yr in {"pencina2008": "2008", "rickles2018": "2018"}.items():
    s, n = re.subn(r"(@article\{" + key + r",.*?year\s*=\s*\{)\d{4}", r"\g<1>" + yr, s, count=1, flags=re.S)
    print("year fix", key, n)

bib.write_text(s.rstrip() + "\n\n" + "\n".join(new), encoding="utf-8")

for f in ["10_results_writeup.md", "27_discussion_draft.md"]:
    p = Path("00_docs") / f
    t = p.read_text(encoding="utf-8-sig")
    for old, rep in [("Marks et al. (2021) review", "Marks et al. (2021a) review"),
                     ("(Marks et al., 2021), and the California", "(Marks et al., 2021a), and the California"),
                     ("Marks et al., 2021, Lancet", "Marks et al., 2021b, Lancet")]:
        print(f, repr(old[:32]), t.count(old))
        t = t.replace(old, rep)
    p.write_text(t, encoding="utf-8")
