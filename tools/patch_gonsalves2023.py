"""
patch_gonsalves2023.py - records the full-text reading of Gonsalves 2023 (CID) and the Gezer 2024 manuscript, 14 Nov 2026.
Run AFTER patch_verified_papers.py, from the project3 folder:  python tools/patch_gonsalves2023.py
Each file is changed only if all its anchors match exactly once.
"""
import re
import sys
from pathlib import Path

docs = Path.cwd() / "00_docs"
w = docs / "10_results_writeup.md"
if not w.exists():
    sys.exit("Run from the project3 folder.")
if "community-level covariates were compared with a history-only model" not in w.read_text(encoding="utf-8"):
    sys.exit("Run patch_verified_papers.py first (it has not been applied). Nothing written.")

def pat(s):
    return r"\s+".join(re.escape(t) for t in s.split())

def patch(name, edits, marker, line_edits=(), appendix=None):
    path = docs / name
    if not path.exists():
        print(f"SKIPPED {name}: file not found")
        return
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"SKIPPED {name}: already patched")
        return
    for i, (old, new) in enumerate(edits, 1):
        hits = list(re.finditer(pat(old), text))
        if len(hits) != 1:
            print(f"SKIPPED {name}: edit {i} matched {len(hits)} times ({old[:50]}...). File unchanged.")
            return
        m = hits[0]
        text = text[:m.start()] + new + text[m.end():]
    for rx, new in line_edits:
        ms = list(re.finditer(rx, text, flags=re.M))
        if len(ms) != 1:
            print(f"SKIPPED {name}: line pattern matched {len(ms)} times ({rx[:45]}). File unchanged.")
            return
        text = text[:ms[0].start()] + new + text[ms[0].end():]
    if appendix:
        text = text.rstrip() + "\n" + appendix
    path.write_text(text, encoding="utf-8", newline="\r\n")
    print(f"Patched {name}")

patch("10_results_writeup.md", [
 ("Gezer et al. 2024; Abara et al. 2019", "Gezer et al. 2024; Abara et al. 2019; Gonsalves et al. 2023"),
 ("Rickles et al. 2018, Gonsalves et al. 2021 and 2023.", "Rickles et al. 2018, Gonsalves et al. 2021 (abstract)."),
 ("earlier HCV and skin and soft tissue infections preceded HIV rises, overdose showed no such association, and the authors concluded the lagged "
  "associations cannot be described as predictive of HIV outbreaks (Gonsalves et al., 2023)",
  "an additional HCV case 5 or 7 months earlier was associated with about 4% higher odds of an HIV case (odds ratio 1.04, 90% credible interval "
  "1.01 to 1.10), skin and soft tissue infections and drainage procedures also preceded HIV, overdose showed no such association, and the authors "
  "concluded the lagged associations cannot be described as causal or predictive of HIV outbreaks; they used shuffled predictors and fatal "
  "automobile accidents as negative controls (Gonsalves et al., 2023)"),
], marker="shuffled predictors and fatal automobile accidents as negative controls")

patch("27_discussion_draft.md", [
 ("Whether county size or detectability partly explains earlier associations is a hypothesis.",
  "Whether county size or detectability partly explains earlier associations is a hypothesis. Gonsalves et al. (2023) also used shuffled predictors and "
  "fatal automobile accidents as negative controls, the same logic as our placebo tests, and concluded that their lagged associations were not "
  "predictive of outbreaks."),
], marker="fatal automobile accidents as negative controls, the same logic")

REVIEW_ADD = """
## 10. Fourth verification pass (14 Nov 2026)
- Gonsalves et al. (CID 2023;76:2134; FULL text read): hierarchical Bayesian distributed-lag logistic regression for the probability that a Massachusetts
  ZIP code tabulation area had at least one HIV case in a month, 2005-2018, predictors lagged over months (overdose, HCV, SSTI, endocarditis, procedures;
  ages 15-50 for clinical events; HIV and HCV counts of 1-4 were suppressed so both were binary). HCV 5 and 7 months earlier: OR 1.04 (90% CrI 1.01-1.10
  and 1.00-1.09); drainage procedures OR 1.02 and SSTI OR 1.01 at 10-12 months; no association for echocardiograms, endocarditis or overdose. Sensitivity
  analyses: shuffled lagged predictors (no positive significant estimates) and fatal automobile accidents as a negative control (no significant
  estimates). The authors state the associations cannot be described as causal or predictive of HIV outbreaks, that the odds ratios are conditional on
  the input data and should not be extrapolated, and that the earlier Lawrence and Lowell study first described the 8-month overdose lag.
- Gezer et al. (2024; manuscript PDF read): confirms Table 2 (each predictor fitted independently, adjusted for time and a population offset), the
  fully adjusted prediction models with lagged counts, the training and validation scenarios (Table 3), and that the accuracy metrics (median agreement
  percentage, median absolute error, root mean squared error, ranking agreement) are defined in appendix page 3, which was not in the file. Gezer
  describes Bauer et al. (2023) as a ZIP-code opioid-mortality forecast whose covariate gain was also modest (secondary description only).
- This section supersedes the "still unverified" list in section 9 for Gonsalves 2023. Still unverified: Bauer 2023 and Patton 2025 (own text),
  Sumetsky 2019 and Gonsalves 2021 full text, the Gezer appendix.
"""
patch("25_topic_literature_review.md", [
 ("Sumetsky 2019, Gonsalves 2021 and 2023 full text", "Sumetsky 2019 and Gonsalves 2021 full text"),
], marker="Fourth verification pass (14 Nov 2026)", appendix=REVIEW_ADD)

patch("24_novelty_search_log.md", [
 ("read Sumetsky 2019, Gonsalves 2021 and 2023 in full;", "read Sumetsky 2019 and Gonsalves 2021 in full;"),
], marker="OFID 2021 (abstract) and CID 2023;76:2134-2139", line_edits=[
 (r"^\| Gonsalves et al\., OFID 2021 and CID 2023 \|.*$",
  "| Gonsalves et al., OFID 2021 (abstract) and CID 2023;76:2134-2139 | Full text read 2026-11-14 (CID) | OFID: Lawrence/Lowell 2005-2018, overdose ~8 months before HIV counts. CID: all Massachusetts ZIP codes, monthly HIV presence; HCV OR 1.04, SSTI and drainage procedures precede HIV; no overdose association; shuffled predictors and car accidents as negative controls; authors say not predictive |"),
])

patch("28_final_checklist.md", [
 ("2. Read in full: Sumetsky 2019, Gonsalves 2021 and 2023, Gizamba 2025 synthesis.",
  "2. Read in full: Sumetsky 2019, Gonsalves 2021, Gizamba 2025 synthesis."),
 ("(Abara 2019 and Cohen 2003 checked 14 Nov 2026)", "(Abara 2019, Cohen 2003 and Gonsalves 2023 checked 14 Nov 2026)"),
], marker="Gonsalves 2023 checked 14 Nov 2026")
print("Done.")
