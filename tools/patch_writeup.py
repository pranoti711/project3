"""
patch_writeup.py - brings 00_docs/10_results_writeup.md in line with the advanced layers.
Run from the project3 folder:  python tools/patch_writeup.py
Each edit must match exactly once (whitespace and line wraps are ignored when matching), otherwise nothing is written.
"""
import re
import sys
from pathlib import Path

root = Path.cwd()
f = root / "00_docs" / "10_results_writeup.md"
if not f.exists():
    sys.exit("Run from the project3 folder.")
text = f.read_text(encoding="utf-8")
if "## 12. Second advanced layer" in text:
    sys.exit("Already patched.")

EDITS = [
 # 1 section 11 header line
 ("Scripts 19-26; numbers in",
  "Scripts 19-26 (the second layer, script 27, is section 12); numbers in"),
 # 2 gradient boosting numbers were stale
 ("Gradient boosting with fixed settings: B - A = -0.004 (95% CI -0.044 to +0.033); D - A = +0.006 "
  "(-0.039 to +0.047). The boosted model uses the all-cause mortality deviation (shuffling it lowers AUC by about 0.035)",
  "Gradient boosting with fixed settings (models A, B and D): B - A = -0.009 (95% CI -0.043 to +0.023); "
  "D - A = -0.009 (-0.054 to +0.033). The boosted model uses the all-cause mortality deviation "
  "(shuffling it lowers AUC by about 0.033)"),
 # 3 specification curve statement
 ("only the confounded first pass (original outcome, no population baseline) sits outside +/-0.02.",
  "only the confounded first pass (original outcome, no population baseline; +0.025 to +0.036) and the 0.70 "
  "stand-in cut-off (-0.025) sit outside +/-0.02, the first in the positive and the second in the negative direction."),
 # 4 county size wording
 ("so detectability explains only part of the population effect.",
  "so detectability may explain only part of the population effect (the cells hold between 1 and 17 events, so this is "
  "descriptive)."),
 # 5 file names
 ("`22_tripod_probast.md` maps", "`20_tripod_probast.md` maps"),
 ("`tests/test_leakage.py` checks", "`04_scripts/test_leakage.py` checks"),
 # 6 duplicated stage-3 sentence in the conclusion, plus the second layer
 ("An exploratory third stage using the other diseases' transition signatures in the same and adjacent counties also "
  "showed no gain (pooled B - A +0.004, 95% CI -0.022 to +0.031). With 81 scored events the study has low power, so "
  "small effects cannot be excluded.",
  "Two advanced evaluation layers (equivalence and power, gradient boosting, decision curves, proper scoring rules and "
  "calibration intervals) also showed no gain (sections 11 and 12). With 81 scored events the study has low power: gains "
  "below about 0.045 AUC could not be reliably detected, so small effects cannot be excluded."),
 # 7 limitations
 ("(Part B of the prereg is the plan for that).",
  "(Part B of the prereg is the plan for that).\n"
  "- The equivalence margins (+/-0.02, 0.03, 0.05), the supplementary diagnostics and the second advanced layer (script 27) "
  "were chosen after seeing stage 1 results, so they are post-hoc. Equivalence within +/-0.02 holds only for the context "
  "contrast (C - A); for mortality (B - A) and the combined model (D - A) it holds within +/-0.03.\n"
  "- Bootstrap shares reported in section 12 are frequentist approximations to a region-of-practical-equivalence "
  "statement, not posterior probabilities."),
]

def pat(s):
    return r"\s+".join(re.escape(t) for t in s.split())

for i, (old, new) in enumerate(EDITS, 1):
    hits = list(re.finditer(pat(old), text))
    if len(hits) != 1:
        sys.exit(f"Edit {i} matched {len(hits)} times (needs exactly 1): {old[:70]}...  Nothing written.")
    m = hits[0]
    text = text[:m.start()] + new + text[m.end():]

SECTION12 = """
## 12. Second advanced layer (proper scoring rules and influence; post-hoc, no new hypotheses)

Script 27 (`27_proper_scoring_and_influence.py`, numbers in `23_proper_scoring_results.md`, tables `adv2_*.csv`). Same
stage 1 out-of-fold predictions and 81 events; 1,000 county-cluster bootstrap draws. Added after the first advanced layer
and not part of `19_advanced_evaluation_plan.md`, so it is post-hoc. AUC only looks at ranking; proper scoring rules also
see calibration and are a stricter test of whether mortality adds information.

| Contrast with A | Log-loss difference (95% CI) | Brier difference (95% CI) |
|---|---|---|
| B (mortality) | +0.0007 [-0.0007, +0.0018] | +0.0001 [-0.0000, +0.0002] |
| C (context) | -0.0002 [-0.0004, +0.0001] | -0.0000 [-0.0000, +0.0000] |
| D (all) | +0.0005 [-0.0009, +0.0017] | +0.0001 [-0.0000, +0.0002] |

Positive differences mean the model is worse than A. No interval excludes zero, and B and D are on the worse side of zero
in 81% and 76% of bootstrap draws for log-loss.

- **Calibration.** Calibration slope: A 1.030 (95% CI 0.783 to 1.299), B 0.881 (0.637 to 1.144). Intercept in the large
  with the slope fixed at 1: A -0.098 (-0.33 to +0.095), B -0.108 (-0.35 to +0.087). B's slope is lower than A's, but its
  interval includes 1, so over-confidence of B is not demonstrated. The B intercept of -0.524 in
  `21_supplementary_results.md` comes from a fit with a free slope and is not comparable to the fixed-slope intercept here.
- **Bootstrap probability statements** (shares of draws, not posterior probabilities). B - A lies inside +/-0.02 AUC in 81% of
  draws, inside +/-0.03 in 94% and inside +/-0.05 in 99%; the share of draws with a gain above 0.05 is 0.5%. For D - A the
  shares are 79%, 93% and 99%. C - A lies inside +/-0.02 in all draws.
- **Leave-one-disease-out.** Dropping each of the 16 diseases in turn moves B - A between -0.004 and +0.006, and no interval
  excludes zero, so no single disease drives or hides an effect. Four diseases (Listeriosis, Lyme Disease, Salmonellosis,
  Vibrio Infection) leave the estimate unchanged, consistent with having no scored events.

Taken together with section 11, the proper-scoring and calibration checks agree with the AUC result: no evidence that
mortality improves out-of-sample prediction, within the limits of 81 events.
"""
text = text.rstrip() + "\n" + SECTION12
f.write_text(text, encoding="utf-8", newline="\r\n")
print("Patched", f, "- 7 edits and section 12 added.")
