"""
fix_cohen.py - corrects the description of Cohen et al. 2003 in section 8 and the novelty log.
Cohen et al. studied boarded-up housing as a predictor of BOTH gonorrhoea and premature mortality (107 US cities); mortality was an outcome, not a predictor.
Run from the project3 folder:  python tools/fix_cohen.py
"""
import re
import sys
from pathlib import Path

docs = Path.cwd() / "00_docs"
w = docs / "10_results_writeup.md"
g = docs / "24_novelty_search_log.md"
if not w.exists() or not g.exists():
    sys.exit("Run from the project3 folder.")

def pat(s):
    return r"\s+".join(re.escape(t) for t in s.split())

wt = w.read_text(encoding="utf-8")
if "boarded-up housing (Cohen" in wt:
    sys.exit("Already patched.")
edits = [
 ("Older ecological studies linked premature mortality (Cohen et al., 2003) and opioid prescribing trends (Abara et al., 2019) with gonorrhoea rates;",
  "An older ecological study of 107 US cities modelled both gonorrhoea and premature death as outcomes of boarded-up housing (Cohen et al., 2003), "
  "and county opioid prescribing trends were associated with gonorrhoea rates (Abara et al., 2019);"),
 ("Cohen is not verified.", "the Cohen description is also abstract level."),
 ("Not yet checked: Cohen et al. 2003, Abara et al. 2019,", "Not yet checked in full: Cohen et al. 2003 and Abara et al. 2019 (abstract level),"),
]
for i, (old, new) in enumerate(edits, 1):
    ms = list(re.finditer(pat(old), wt))
    if len(ms) != 1:
        sys.exit(f"Edit {i} matched {len(ms)} times ({old[:50]}...). Nothing written.")
    wt = wt[:ms[0].start()] + new + wt[ms[0].end():]

gt = g.read_text(encoding="utf-8")
rx = r"^\| Cohen 2003; Abara 2019 \|.*$"
ms = list(re.finditer(rx, gt, flags=re.M))
if len(ms) != 1:
    sys.exit("Log row not found exactly once. Nothing written.")
gt = gt[:ms[0].start()] + ("| Cohen et al., Am J Public Health 2003;93:467 (107 US cities); Abara et al. 2019 | Boarded-up housing as predictor of gonorrhoea and "
      "premature death; opioid prescribing trends vs gonorrhoea (counties) | Abstract level | Cohen: housing exposure, mortality is an outcome "
      "(description corrected 2026-11-13). Abara: positive but weakening association. |") + gt[ms[0].end():]

w.write_text(wt, encoding="utf-8", newline="\r\n")
g.write_text(gt, encoding="utf-8", newline="\r\n")
print("Corrected Cohen description in the write-up (3 edits) and the search log (1 row).")
