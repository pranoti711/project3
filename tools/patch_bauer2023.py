"""
patch_bauer2023.py - records the full-text reading of Bauer et al. 2023 (JMIR Public Health Surveill), 14 Nov 2026.
Run AFTER patch_verified_papers.py and patch_gonsalves2023.py, from the project3 folder:  python tools/patch_bauer2023.py
"""
import re
import sys
from pathlib import Path

docs = Path.cwd() / "00_docs"
w = docs / "10_results_writeup.md"
if not w.exists():
    sys.exit("Run from the project3 folder.")
if "shuffled predictors and fatal automobile accidents as negative controls" not in w.read_text(encoding="utf-8"):
    sys.exit("Run patch_verified_papers.py and patch_gonsalves2023.py first. Nothing written.")

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
 ("predict mortality, not infection.",
  "predict mortality, not infection. Bauer et al. (2023) forecast Massachusetts ZIP-code opioid deaths one year ahead (2016-2019) with Bayesian "
  "spatiotemporal models; adding demographic and socioeconomic covariates improved only the model without spatial dependence, forecast errors were "
  "larger in rural than urban ZIP codes (the small-area problem), and the model under-predicted 2020-2021 after the COVID-19 disruption (full text read)."),
 ("Abara et al. 2019; Gonsalves et al. 2023", "Abara et al. 2019; Gonsalves et al. 2023; Bauer et al. 2023"),
 ("(abstract level), Bauer et al. 2023, Patton et al. 2025", "(abstract level), Patton et al. 2025"),
], marker="forecast Massachusetts ZIP-code opioid deaths one year ahead")

patch("27_discussion_draft.md", [
 ("most often suppressed (43% of drug-overdose and suicide rows and 66% of homicide rows missing).",
  "most often suppressed (43% of drug-overdose and suicide rows and 66% of homicide rows missing). Bauer et al. (2023) likewise found larger "
  "forecast errors in rural ZIP codes and little gain from covariates once spatial dependence was modelled."),
], marker="likewise found larger forecast errors in rural ZIP codes")

REVIEW_ADD = """
## 11. Fifth verification pass (14 Nov 2026)
- Bauer et al. (JMIR Public Health Surveill 2023;9:e41450; FULL text read): Bayesian spatiotemporal dynamic models (R-INLA) for opioid-related deaths in
  537 Massachusetts ZIP code tabulation areas, 2005-2019 (16,377 deaths, ages 20 and over), evaluated one year ahead for 2016-2019 with mean absolute
  error, root mean square error and a quintile rank-agreement measure. The model with full spatiotemporal dependence (AR(1) with conditional autoregressive
  space) performed best; adding demographic and socioeconomic covariates improved prediction only for the model without spatial dependence, because the
  spatial structure already captured the patterns tied to those covariates. Errors were larger in rural than urban ZIP codes, where rates are unstable
  (small-area problem). The model under-predicted 2020-2021, which the authors attribute to disruption by COVID-19; they also note missing toxicology
  (fentanyl) data. The outcome is mortality, not infection. Gezer et al. describe it correctly as a ZIP-code opioid-mortality forecast with modest covariate gain.
- This section supersedes the earlier "still unverified" lists for Bauer 2023. Still unverified: Patton 2025 (own text), Sumetsky 2019 and Gonsalves 2021
  full text, the Gezer appendix, the Gizamba 2025 synthesis.
"""
patch("25_topic_literature_review.md", [], marker="Fifth verification pass (14 Nov 2026)", appendix=REVIEW_ADD)

patch("24_novelty_search_log.md", [], marker="Bauer 2023 (full text read 2026-11-14)", line_edits=[
 (r"^\| Marks et al\., Lancet Public Health 2021; Bauer 2023; Patton 2025; Sumetsky 2021 \|.*$",
  "| Marks et al., Lancet Public Health 2021; Bauer 2023 (full text read 2026-11-14); Patton 2025; Sumetsky 2021 | Forecast overdose itself | Abstracts; Bauer full text | Related, outcome is mortality. Bauer: MA ZIP codes 2005-2019, one year ahead; covariates helped only the non-spatial model; rural errors larger; 2020-21 under-predicted. |"),
])

patch("28_final_checklist.md", [
 ("Verify Bauer 2023 and Patton 2025 (Abara 2019, Cohen 2003 and Gonsalves 2023 checked 14 Nov 2026)",
  "Verify Patton 2025 (Abara 2019, Bauer 2023, Cohen 2003 and Gonsalves 2023 checked 14 Nov 2026)"),
], marker="Verify Patton 2025 (Abara 2019, Bauer 2023")
print("Done.")
