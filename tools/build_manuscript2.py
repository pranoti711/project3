import re
from pathlib import Path
import pypandoc

TAG = "final-draft-v28"   # set to the tag you push after this commit
D = Path("00_docs")
rd = lambda n: (D / n).read_text(encoding="utf-8-sig")

def sections(text):
    out = {}
    for part in re.split(r"(?m)^## ", text)[1:]:
        title, _, body = part.partition("\n")
        out[title.strip()] = body.strip()
    return out

def get(secs, prefix):
    for t, b in secs.items():
        if t.startswith(prefix):
            return t, b
    raise SystemExit("section not found: " + prefix)

def clean(t):
    t = re.sub(r"^\d+b?\.\s*", "", t)
    t = re.sub(r"\s*\([^()]*\)\s*$", "", t)
    return t.strip()

res = sections(rd("10_results_writeup.md"))

def block(prefix):
    t, b = get(res, prefix)
    return "## " + clean(t) + "\n\n" + b + "\n"

# abstract
abs_ = rd("26_abstract_draft.md").split("\n", 1)[1].strip()
abs_ = re.sub(r"(?m)^(Background|Methods|Results|Conclusions)\.", r"**\1.**", abs_)

# introduction = related work, without the internal verification note
_, rel = get(res, "8.")
rel = re.sub(r"(?ms)^Verification status\..*?(?:\n\s*\n|\Z)", "", rel).strip()

# methods
_, meth = get(res, "1.")

# HIV section: results part only (its limitations live in the discussion)
_, hiv = get(res, "HIV exploratory")
hiv = hiv.partition("### Limitations added 17 Nov 2026")[0].strip()

results = "\n".join([
    block("2."), block("3."), block("4."), block("4b."), block("5."),
    block("9."), block("10."), block("11."), block("12."),
    "## HIV exploratory extension\n\n" + hiv + "\n",
])

_, lim = get(res, "6.")
_, concl = get(res, "7.")

dis = rd("27_discussion_draft.md")
dis = dis[dis.index("\n## "):].strip()
dis = dis.replace("## Limitations", "## Limitations specific to the HIV extension and missing data", 1)

md = (
'---\n'
'title: "County mortality adds no out-of-sample predictive value for infectious-disease up-transitions in California: a pre-specified leave-future-out analysis"\n'
'author: "Pranoti Munjankar (IIT Tirupati)"\n'
'bibliography: 06_paper/references.bib\n'
'nocite: |\n  @*\n'
'---\n\n'
"# Abstract\n\n" + abs_ + "\n\n"
"# Introduction\n\n" + rel + "\n\n"
"# Methods\n\n" + meth + "\n\n"
"# Results\n\n" + results + "\n"
"# Discussion\n\n" + dis + "\n\n"
"# Limitations\n\n" + lim + "\n\n"
"# Conclusion\n\n" + concl + "\n\n"
"# Code and data availability\n\n"
"Code, processed data, logs and the pre-registration are at https://github.com/pranoti711/project3 (tag " + TAG + ").\n\n"
"# References\n\n::: {#refs}\n:::\n"
)

out = Path("06_paper/manuscript_draft.docx")
pypandoc.convert_text(md, "docx", format="markdown", outputfile=str(out),
                      extra_args=["--citeproc", "--standalone"])
Path("06_paper/manuscript_draft.md").write_text(md, encoding="utf-8")
print("wrote", out, "-", len(md.split()), "words")

















