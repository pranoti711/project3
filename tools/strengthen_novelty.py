import json, re, urllib.parse, urllib.request
from pathlib import Path

UA = {"User-Agent": "project3-refs/1.0"}
import time
def get(url):
    last = None
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.load(r)["message"]
        except Exception as e:
            last = e
            print("  retry", i + 1, "after", type(e).__name__)
            time.sleep(3 * (i + 1))
    raise SystemExit("Crossref not reachable: " + str(last))
def by_doi(d): return get("https://api.crossref.org/works/" + urllib.parse.quote(d))
def search(q): return get("https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(q))["items"][0]
def year(it): return (it.get("issued", {}).get("date-parts") or [[0]])[0][0]
def bibtex(key, it):
    auth = " and ".join((a.get("family", "") + ", " + a.get("given", "")).strip(", ") for a in it.get("author", [])) or "Unknown"
    pg = it.get("page") or it.get("article-number")
    f = {"author": auth, "title": it["title"][0], "journal": it["container-title"][0], "year": year(it),
         "volume": it.get("volume"), "number": it.get("issue"),
         "pages": re.sub(r"\s*[-\u2013]\s*", "--", pg) if pg else None, "doi": it.get("DOI")}
    return "@article{%s,\n%s\n}\n" % (key, ",\n".join("  %-8s= {%s}" % (k, v) for k, v in f.items() if v))

targets = {
 "southdakota2020": (search("Assessing County-Level Vulnerability for Opioid Overdose and Rapid Spread of Human Immunodeficiency Virus and Hepatitis C Infection in South Dakota"), "infectious diseases", 2020),
 "illinois2021":    (by_doi("10.3389/fsoc.2021.652672"), "sociology", 2021),
 "oklahoma2024":    (by_doi("10.1371/journal.pone.0301442"), "plos one", 2024),
}
bib = Path("06_paper/references.bib")
s = bib.read_text(encoding="utf-8")
cites = {}
for key, (it, jr, yr) in targets.items():
    j = (it.get("container-title") or [""])[0].lower()
    ok = jr in j and abs(year(it) - yr) <= 1
    first = (it.get("author") or [{}])[0].get("family", "?")
    print(("OK   " if ok else "CHECK"), key, "|", first, year(it), "|", it["title"][0][:70], "|", j[:30])
    if ok:
        if ("{" + key + ",") not in s:
            s = s.rstrip() + "\n\n" + bibtex(key, it)
        cites[key] = "%s et al. (%d)" % (first, year(it))
bib.write_text(s, encoding="utf-8")

p = Path("00_docs/10_results_writeup.md")
t = p.read_text(encoding="utf-8-sig")
if len(cites) == 3:
    bullet = ("- **State vulnerability assessments.** The same county-regression approach has been applied in further states, "
              "including South Dakota (%s), Illinois (%s) and Oklahoma (%s), reporting associations between overdose-related "
              "indicators and county infection rates.\n" % (cites["southdakota2020"], cites["illinois2021"], cites["oklahoma2024"]))
    t, n = re.subn(r"(?m)^(- \*\*Association and lag studies\.\*\*)", lambda m: bullet + m.group(1), t, count=1)
    print(n, "x bullet inserted")
else:
    print("bullet NOT inserted: fix the CHECK lines above first")
t, n2 = re.subn(r"after\s+PubMed\s+searches\s+on\s+2026-11-12,",
                "after PubMed searches on 2026-11-12 and targeted web searches on 2026-11-19 that returned medRxiv and arXiv records,", t, count=1)
print(n2, "x search sentence widened")
p.write_text(t, encoding="utf-8")
