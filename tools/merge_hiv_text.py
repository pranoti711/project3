import re
from pathlib import Path
D = Path("00_docs")

def edit(name, pairs, strip_marker=True):
    p = D / name
    s = p.read_text(encoding="utf-8")
    if strip_marker:
        s = re.sub(r"\n*<!-- hiv-final-patch -->.*\Z", "\n", s, flags=re.S)
    for label, pattern, repl in pairs:
        s, n = re.subn(pattern, lambda m: repl, s, count=1, flags=re.S)
        print(("[ok]   " if n else "[MISS] ") + name + ": " + label)
    p.write_text(s, encoding="utf-8")

edit("26_abstract_draft.md", [
    ("HIV sentence in Results",
     r"Log-loss and Brier differences were indistinguishable from zero\.",
     "Log-loss and Brier differences were indistinguishable from zero. An exploratory HIV extension "
     "(4 test events) was also null (pooled \u0394AUC \u22120.007, 95% CI \u22120.039 to +0.023)."),
    ("shorter Methods sentence (word count)",
     r"Stage 1 was pre-specified; placebo, held-out-disease.*?exploratory or post hoc\.",
     "Stage 1 was pre-specified; all other analyses, including placebo, equivalence and decision-curve checks, "
     "were exploratory or post hoc."),
])

LIMITS = """## Limitations
HIV was included only as an exploratory group (Office of AIDS county series, 2012-2023; 4 test events in the leave-future-out
window, pooled B - A -0.007, 95% CI -0.039 to +0.023), and hepatitis C is absent because county data exist only for 2014-2016.
County mortality deviations were missing in many county-years because of small-count suppression, from under 20% for all-cause
mortality to about two-thirds or more for homicide. Missing values were set to the mean after z-scoring, with no missing
indicator, so model B carries no mortality information for those rows. This probably biases B - A toward the null. The null
result therefore applies to publicly available, suppressed county-level data and does not show that mortality has no
predictive value in principle.

## Implications"""

edit("27_discussion_draft.md", [
    ("coverage sentence",
     r"It does not\s+cover hepatitis C or HIV outbreaks, other states,",
     "It does not cover hepatitis C or confirmatory HIV analysis (HIV was added only as an exploratory group with 4 test events), other states,"),
    ("limitations section",
     r"## Implications",
     LIMITS),
    ("future work",
     r"Add hepatitis C and HIV series;",
     "Add hepatitis C and a fuller HIV series;"),
])

edit("28_final_checklist.md", [
    ("tick manifest", r"- \[ \] Manifest refreshed after the HIV additions", "- [x] Manifest refreshed after the HIV additions"),
    ("tick text merged", r"- \[ \] Abstract and discussion: HIV sentence and missingness limitation moved into the text",
     "- [x] Abstract and discussion: HIV sentence and missingness limitation moved into the text"),
])