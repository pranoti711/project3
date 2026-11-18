import json, re, urllib.parse, urllib.request
from pathlib import Path
UA = {"User-Agent": "project3-refs/1.0"}
url = "https://api.crossref.org/works/" + urllib.parse.quote("10.1111/add.16674")
it = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))["message"]
auth = " and ".join((a.get("family", "") + ", " + a.get("given", "")).strip(", ") for a in it.get("author", []))
f = {"author": auth, "title": it["title"][0], "journal": it["container-title"][0], "year": "2025",
     "volume": it.get("volume"), "number": it.get("issue"),
     "pages": re.sub(r"\s*[-\u2013]\s*", "--", it["page"]) if it.get("page") else None, "doi": it["DOI"]}
entry = "@article{patton2025,\n" + ",\n".join("  %-8s= {%s}" % (k, v) for k, v in f.items() if v) + "\n}\n"
bib = Path("06_paper/references.bib")
s = bib.read_text(encoding="utf-8")
s, n = re.subn(r"@article\{patton2025,.*?\n\}\n*", "", s, count=1, flags=re.S)
bib.write_text(s.rstrip() + "\n\n" + entry, encoding="utf-8")
print("removed old entry:", n)
print(entry)
