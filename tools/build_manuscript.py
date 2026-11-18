import re
from pathlib import Path
import pypandoc

TAG = "final-draft-v9"  # set to the tag you actually push after the last commit
D = Path("00_docs")


def read(n): return (D / n).read_text(encoding="utf-8-sig")


# abstract: drop the working title line, bold the section labels
abs_ = read("26_abstract_draft.md").split("\n", 1)[1].strip()
abs_ = re.sub(r"(?m)^(Background|Methods|Results|Conclusions)\.", r"**\1.**", abs_)

# results: drop the file-name title line
res = read("10_results_writeup.md")
res = re.sub(r"\A# [^\n]*\n", "", res).strip()

# discussion: start at the first section heading (drops the draft-note paragraph)
dis = read("27_discussion_draft.md")
dis = dis[dis.index("\n## "):].strip() if "\n## " in dis else dis

md = f"""---
title: "County mortality adds no out-of-sample predictive value for infectious-disease up-transitions in California: a pre-registered leave-future-out analysis"
author: "Pranoti Munjankar (IIT Tirupati)"
bibliography: 06_paper/references.bib
nocite: |
  @*
---

# Abstract

{abs_}

# Results

{res}

# Discussion

{dis}

# Code and data availability

Code, processed data, logs and the pre-registration are at https://github.com/pranoti711/project3 (tag {TAG}).

# References

::: {{#refs}}
:::
"""
out = Path("06_paper/manuscript_draft.docx")
pypandoc.convert_text(md, "docx", format="markdown", outputfile=str(out),
                      extra_args=["--citeproc", "--standalone"])
print("wrote", out)
