"""
patch_related_work_v3.py - small corrections to section 8 and the novelty log after checking Gezer 2024, Sumetsky 2019,
Gonsalves 2021/2023 and Gizamba 2026 on 2026-11-12.
Run from the project3 folder:  python tools/patch_related_work_v3.py
Nothing is written unless every edit matches exactly once.
"""
import re
import sys
from pathlib import Path

root = Path.cwd()
f = root / "00_docs" / "10_results_writeup.md"
log = root / "00_docs" / "24_novelty_search_log.md"
if not f.exists() or not log.exists():
    sys.exit("Run from the project3 folder (needs 10_results_writeup.md and 24_novelty_search_log.md).")
text = f.read_text(encoding="utf-8")
ltxt = log.read_text(encoding="utf-8")
if "percent agreement between predicted and observed" in text:
    sys.exit("Already patched.")

def pat(s):
    return r"\s+".join(re.escape(t) for t in s.split())

EDITS = [
 ("Patton et al. 2025, Gizamba et al. 2026, and the methods references",
  "Patton et al. 2025, and the methods references"),
 ("but did not test it out of sample.",
  "but did not test it out of sample. Cross-sectional machine-learning risk mapping continues (Gizamba et al., 2026: hepatitis C "
  "in 245 Los Angeles County ZIP codes with Elastic Net and random forest; its predictor set has not been checked)."),
 ("In Pennsylvania ZIP codes, previous-year opioid-related hospitalisations were associated with higher HCV and HIV "
  "hospitalisations (Sumetsky et al., 2019).",
  "In Pennsylvania ZIP codes (2004-2014), Bayesian spatiotemporal Poisson models found previous-year opioid-related hospitalisations "
  "associated with higher HCV and HIV hospitalisations (rate ratios about 1.09 and 1.10; Sumetsky et al., 2019); the exposure is "
  "hospitalisation, not mortality, and the paper reports association, not prediction."),
 ("were associated with current-month HIV counts, although",
  "were associated with current-month HIV counts (rate ratio 1.03 per additional overdose, 90% credible interval 1.00 to 1.06), although"),
 ("In a statewide Massachusetts analysis, earlier HCV",
  "In a statewide Massachusetts analysis at ZIP-code level (2005-2018, monthly presence of HIV), earlier HCV"),
 ("were validated on 2021 (median accuracy about 80% for opioid-related and 75% for HCV-related hospitalisations)",
  "were validated on 2021 (median percent agreement between predicted and observed counts about 80% for opioid-related and 75% for "
  "HCV-related hospitalisations, using fully adjusted models and previous hospitalisation counts)"),
]
for i, (old, new) in enumerate(EDITS, 1):
    hits = list(re.finditer(pat(old), text))
    if len(hits) != 1:
        sys.exit(f"Edit {i} matched {len(hits)} times (needs 1): {old[:60]}... Nothing written.")
    m = hits[0]
    text = text[:m.start()] + new + text[m.end():]

ROWS = {
 r"^\| Sumetsky et al\., JECH 2019 \|.*$":
  "| Sumetsky et al., JECH 2019 | Bayesian spatiotemporal Poisson (CAR), PA ZIP codes 2004-2014; previous-year opioid hospitalisations vs HCV/HIV | Abstract checked 2026-11-12 | Association (RR 1.09 HCV, 1.10 HIV); exposure is hospitalisation, not mortality; no out-of-sample test. |",
 r"^\| Gezer et al\., Lancet Public Health 2024 \|.*$":
  "| Gezer et al., Lancet Public Health 2024 | SC ZIP codes; train 2016-20, validate 2021; accuracy = median percent agreement of predicted vs observed counts from fully adjusted NB mixed models using previous counts; all-cause mortality per 1,000 among factors (RR 1.18 per SD, combined outcome) | Abstract and full-text snippets (PMC blocked automated access) | Closest study; one state, hospitalisation counts, no ablation of mortality, no placebo design. Association models were adjusted for time and a population offset; whether mortality stays significant in the fully adjusted model is not verified (read Table 2). |",
 r"^\| Gonsalves et al\., OFID 2021 and CID 2023 \|.*$":
  "| Gonsalves et al., OFID 2021 and CID 2023 | OFID: Lawrence/Lowell 2005-2018, overdose 8 months earlier RR 1.03 (90% CrI 1.00-1.06) for HIV. CID: all Massachusetts ZIP codes 2005-2018, monthly HIV presence, ages 15-50; HCV and SSTI preceded HIV, no overdose association | Abstracts and methods snippets | Lagged mortality-infection association in one setting only; authors state the lagged associations are not predictive of outbreaks. |",
 r"^\| Gizamba et al\., BMC Public Health 2026 \|.*$":
  "| Gizamba et al., BMC Public Health 2026 | Cross-sectional, 245 LA County ZIP codes, Elastic Net and random forest, hepatitis C rate ages 18-39; 49 very high risk; nine variables of importance | Abstract only | Cross-sectional, no temporal holdout; predictor list not seen (check whether overdose mortality is included). |",
}
for rx, row in ROWS.items():
    ms = list(re.finditer(rx, ltxt, flags=re.M))
    if len(ms) != 1:
        sys.exit(f"Log row not found exactly once: {rx}. Nothing written.")
    ltxt = ltxt[:ms[0].start()] + row + ltxt[ms[0].end():]
old_todo = "- Read in full: Gezer 2024, Sumetsky 2019, Gonsalves 2021 and 2023, Gizamba 2026; verify Cohen 2003, Abara 2019, Bauer 2023, Patton 2025."
if ltxt.count(old_todo) != 1:
    sys.exit("To-do line not found. Nothing written.")
ltxt = ltxt.replace(old_todo,
  "- Read Table 2, Table 3 and the accuracy method in Gezer 2024 in a browser; read the Gizamba 2026 predictor list; verify Cohen 2003, Abara 2019, Patton 2025.")

f.write_text(text, encoding="utf-8", newline="\r\n")
log.write_text(ltxt, encoding="utf-8", newline="\r\n")
print("6 edits to section 8 and 5 updates to the search log written.")
