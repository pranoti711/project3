import re
from pathlib import Path

bib = Path("06_paper/references.bib")
s = bib.read_text(encoding="utf-8")
if "cdph_va" not in s:
    s = s.rstrip() + """

@techreport{cdph_va,
  author      = {{California Department of Public Health}},
  title       = {California Fatal Opioid Overdose and {HIV} or Hepatitis {C} Virus ({HCV}) Vulnerability Assessment: Public Report},
  institution = {California Department of Public Health},
  year        = {n.d.},
  url         = {https://www.cdph.ca.gov/Programs/CID/DCDC/Pages/ViralHepatitisData.aspx}
}
"""
    bib.write_text(s, encoding="utf-8")
    print("bib entry added")

p = Path("00_docs/27_discussion_draft.md")
t = p.read_text(encoding="utf-8-sig")
old = "the California assessment for the same 58 counties states that its results are not predictive."
new = "the California Department of Public Health (CDPH) assessment for the same 58 counties states that its results are not predictive (CDPH, n.d.)."
print("text replaced:", t.count(old))
p.write_text(t.replace(old, new), encoding="utf-8")
