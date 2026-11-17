"""Patch docs for the exploratory HIV extension (hiv-ext) and the missingness limitation.
Run from the project root:  python tools\patch_hiv_ext.py
"""
import re
from pathlib import Path

DOCS = Path("00_docs")
MARK = "<!-- hiv-ext-patch -->"

RESULTS = f"""
{MARK}
## HIV exploratory extension (Office of AIDS series, 2012-2023)

HIV new diagnoses (California Office of AIDS, county-year, 2012-2023) were added as an
exploratory disease in the ambiguous scope, using the same transition method (negative
binomial RW2 + BYM2 + space-time interaction), threshold 0.80, and the same leave-future-out
evaluation. The extension adds 232 county-year rows and 4 test events (all scopes: n = 3944,
85 events; ambiguous: n = 464, 12 events). It is underpowered by design and is reported as exploratory.

| Scope | Model | Delta AUC vs A | 95% CI |
|---|---|---|---|
| all | B (+ mortality) | -0.007 | -0.039 to +0.023 |
| all | C (+ context) | +0.0004 | -0.007 to +0.009 |
| all | D (all) | -0.008 | -0.037 to +0.020 |
| ambiguous | B | -0.065 | -0.166 to +0.041 |
| ambiguous | C | -0.009 | -0.031 to +0.016 |
| ambiguous | D | -0.069 | -0.167 to +0.035 |

All intervals include 0. Brier score and log-loss are essentially identical across models
A-D (Brier about 0.0210, log-loss about 0.099). Adding HIV therefore does not change the
conclusion: mortality deviations give no out-of-sample gain. The more negative point estimate
for B in the ambiguous scope (-0.065, 12 events) is within sampling noise. No positive result
arose, so the placebo/surrogate step was not required for this run. Outputs: 05_results/tables/*__hiv17*
(git commit a1b6688, tag hiv-ext).
"""

LIMIT = f"""
{MARK}
### Limitations added 17 Nov 2026
- **Scope of diseases.** HIV is included only as an exploratory group (Office of AIDS, 2012-2023;
  4 test events in the leave-future-out window). HCV is still absent: county data exist only for 2014-2016.
- **Suppressed mortality exposure.** County mortality deviations were missing in 19% (all-cause),
  57% (drug overdose), 57% (suicide) and 74% (homicide) of county-years in the main model table
  (HIV rows: about 1%, 43%, 45% and 69%), because of small-count suppression. Missing values were set to the
  mean after z-scoring, with no missing indicator (by design, since suppression flags act as a county-size
  proxy), so model B carries no mortality information for those rows. This probably biases B-A toward the null.
  The null result should therefore be read as applying to publicly available, suppressed county-level data,
  not as evidence that mortality has no predictive value in principle.
- **Sparse context variable.** physicians_per_100k is about 91% missing in the HIV model table, which limits model C.
"""

DEVIATION = f"""
{MARK}
### 17 Nov 2026 - HIV exploratory extension
- Added HIV (Office of AIDS, 2012-2023) as an exploratory disease via 05x_transitions_ext_hiv.R and
  05b_build_model_table.py; ran 06_models_ABCD.R with the hiv17 suffix.
- Not pre-registered; reported as exploratory. Result null (pooled B-A -0.007, CI -0.039 to +0.023).
- Missing-value handling in p3_common.R (z-score, then set to 0, no missing indicator) was checked and left unchanged.
- Commit a1b6688, tag hiv-ext. Tags stage1-freeze and advanced-freeze untouched.
"""

SEARCH = f"""
{MARK}
### 17 Nov 2026 - data note
- HIV county series obtained from CDPH Office of AIDS reports (2012-2023); agrees with the CDPH HIV column for
  2019-2023 (r = 0.9999). HCV county series available for 2014-2016 only; AtlasPlus not downloaded.
"""


def append_once(name, text):
    p = DOCS / name
    s = p.read_text(encoding="utf-8")
    if MARK in s:
        print(f"[skip] {name}: already patched")
        return
    p.write_text(s.rstrip() + "\n" + text, encoding="utf-8")
    print(f"[ok]   {name}: appended")


def fix_old_limitation():
    p = DOCS / "10_results_writeup.md"
    lines = p.read_text(encoding="utf-8").split("\n")
    hits = [i for i, l in enumerate(lines)
            if re.search(r"\bHIV\b", l) and re.search(r"\bHCV\b", l)
            and re.search(r"\b(no|not|neither|nor|exclude|absent|lack)", l, re.I)
            and "hiv-ext-patch" not in l]
    if len(hits) == 1:
        i = hits[0]
        print("[ok]   replacing old limitation line:\n       ", lines[i][:200])
        lines[i] = ("The 16 core diseases include no HIV or HCV; HIV was added later as an exploratory "
                    "group (see the HIV extension section), and HCV remains absent.")
        p.write_text("\n".join(lines), encoding="utf-8")
    else:
        print(f"[warn] old HIV/HCV limitation: {len(hits)} candidate lines, not edited. Candidates:")
        for i in hits:
            print("       ", i + 1, lines[i][:160])


if __name__ == "__main__":
    fix_old_limitation()
    append_once("10_results_writeup.md", RESULTS + LIMIT)
    append_once("07_deviations_log.md", DEVIATION)
    append_once("24_novelty_search_log.md", SEARCH)
    print("Done. Review with: git diff --stat")
