"""
patch_related_work.py - rewrites section 8 (Related work) of 00_docs/10_results_writeup.md after the 2026-11-12 literature screen
and writes 00_docs/24_novelty_search_log.md (search strings, dates, hit counts, screening decisions).
Run from the project3 folder:  python tools/patch_related_work.py
Matches section 8 up to the heading of section 9; if either heading is missing or repeated, nothing is written.
"""
import re
import sys
from pathlib import Path

root = Path.cwd()
f = root / "00_docs" / "10_results_writeup.md"
log = root / "00_docs" / "24_novelty_search_log.md"
if not f.exists():
    sys.exit("Run from the project3 folder.")
text = f.read_text(encoding="utf-8")
if "screened 2026-11-12" in text:
    sys.exit("Already patched.")
if len(re.findall(r"^## 8\. Related work", text, flags=re.M)) != 1 or len(re.findall(r"^## 9\. ", text, flags=re.M)) != 1:
    sys.exit("Could not find exactly one section 8 and one section 9 heading. Nothing written.")

SECTION8 = """## 8. Related work (screened 2026-11-12; verify every entry against the full paper before citing)

Sources: PubMed searches on 2026-11-12 (two strings, see `24_novelty_search_log.md`) plus web searches. Most entries below were
judged from titles and abstracts only. Full entries for the earlier references are in `06_paper/references.bib`.

- **Vulnerability assessments for HIV and hepatitis C outbreaks.** County or ZIP-code assessments for rapid dissemination of HIV or
  HCV among people who inject drugs use acute hepatitis C as a proxy outcome and overdose-related indicators among predictors
  (Van Handel et al., 2016; Rickles et al., 2018 for Tennessee). They rank areas at one time point and do not evaluate
  forecasts of next-year transitions out of sample.
- **Lagged associations with infection.** In Pennsylvania ZIP codes, previous-year opioid-related hospitalisations were associated
  with higher HCV and HIV hospitalisations after adjustment (Sumetsky et al., 2019). In Northeast US counties, opioid death rates
  were studied against gonorrhoea, chlamydia and HIV rates in 2012-2017 (Drewes et al., 2020); the pattern by urbanicity must be
  checked against the full text before it is described. Older ecological work linked premature mortality with gonorrhoea rates
  across US cities (Cohen et al., 2003). These are association studies, not tests of incremental out-of-sample prediction.
- **Area-level prediction with a temporal holdout.** In South Carolina ZIP codes, models trained on 2016-2020 predicted 2021
  opioid-related and HCV-related hospitalisations, and an area mortality measure was among the associated factors (Gezer et al.,
  2024). This is the closest study found. It differs from ours in outcome (hospitalisation counts, not transition events), geography
  (one state), number of diseases (one) and design (no placebo or held-out-disease controls, no population-adjusted
  incremental comparison).
- **Forecasting overdose itself.** County and small-area forecasts of overdose mortality (Marks et al., 2021, Lancet Public Health;
  Bauer et al., 2023) and early-warning alerts for overdose outbreaks (Patton et al., 2025) predict mortality, not infectious
  disease. A narrative review covers prediction methods for opioid-related epidemics (Marks et al., 2021, Transl Res); its included
  studies still need to be checked for infectious-disease outcomes.
- **Methods behind the design.** Flagging areas by posterior probability of elevated risk with a 70-80% cut-off is established in
  disease mapping and is conservative for small counts (Richardson et al., 2004). Negative-control exposures and outcomes
  (Lipsitch et al., 2010) and leave-future-out validation (Burkner et al., 2020) underlie the placebo, surrogate-disease and
  temporal validation designs.

Removed from the earlier draft: a "distributed-lag study in Massachusetts" that was never traced to a source.

**How the results relate to earlier work.** Prior area-level studies mostly report positive associations of opioid-related
indicators with HCV, HIV or STI outcomes. Our question is different: whether mortality adds out-of-sample predictive value after
adjusting for county population. Our first-pass confounded run showed how county size can create an apparent gain; whether size or
detectability also partly explains earlier associations is a hypothesis, not a finding, because the exposures, outcomes and
geographies differ.

**Position, with the limits of the search stated.** To our knowledge, and after PubMed searches on 2026-11-12 supplemented by web
searches, we found no study that tests whether county mortality adds out-of-sample predictive value for infectious-disease
up-transition events across multiple diseases, against a population-adjusted baseline, with placebo and held-out-disease controls.
Limits: only PubMed was searched systematically; Embase, Web of Science, Scopus and preprint servers are not yet searched; the full
texts of Gezer et al. 2024, the Marks et al. 2021 review and Gizamba et al. 2026 are not yet read; and the narrow search string
missed at least one relevant paper that a web search found. This must be re-checked before any claim of novelty in a submission.

"""

LOG = """# 24_novelty_search_log.md - literature search record for the novelty claim

Claim tested: no prior study tests whether county mortality adds out-of-sample predictive value for infectious-disease up-transition
events across multiple diseases, against a population-adjusted baseline, with placebo and held-out-disease controls.

## Search 1 (broad), PubMed, run 2026-11-12
Blocks: mortality/overdose/suicide/homicide terms AND infectious-disease terms AND county/small-area terms AND forecasting/prediction terms
(MeSH plus title/abstract; see the string given in the project chat). Records screened: 73 (total hit count not recorded).
Precision was low: about 8 of 73 relevant; many COVID and non-human results.

## Search 2 (tight), PubMed, run 2026-11-12 - 14 hits
```
(overdose*[tiab] OR "opioid-related"[tiab] OR suicide[tiab] OR homicide[tiab] OR "drug-related death*"[tiab])
AND (hepatitis[tiab] OR HIV[tiab] OR "sexually transmitted"[tiab] OR gonorrhea[tiab] OR syphilis[tiab] OR "infectious disease*"[tiab] OR notifiable[tiab])
AND (county[tiab] OR counties[tiab] OR "ZIP code*"[tiab] OR "small area*"[tiab] OR spatiotemporal[tiab])
AND (forecast*[tiab] OR predict*[tiab] OR "early warning"[tiab] OR "out-of-sample"[tiab] OR lagged[tiab] OR "previous-year"[tiab])
NOT (COVID-19[tiab] OR "SARS-CoV-2"[tiab])
```
Screening of the 14 (title and abstract only):
| # | Record | Decision |
|---|---|---|
| 4 | Sumetsky 2019, Pennsylvania, opioid hospitalisations and HCV/HIV | Related: lagged association, no out-of-sample test |
| 5 | Gezer 2024, South Carolina ZIP, HCV hospitalisations | Closest: temporal holdout, one disease, count outcome |
| 6 | Marks 2021 Transl Res, review of prediction methods | Read in full; check included studies |
| 8 | Rickles 2018, Tennessee vulnerability assessment | Related: cross-sectional ranking |
| 9 | Gizamba 2026, hepatitis C risk in Los Angeles ZIP codes (machine learning) | Read in full; predictors not yet checked |
| 7 | Kajeepeta 2021, jail incarceration and cause-specific mortality | Not relevant: mortality outcomes, no prediction of incidence |
| 1, 2, 3, 10-14 | Syringe access, imputation, decision support, qualitative and unrelated records | Excluded |

Both strings returned the same core set (Sumetsky, Gezer, Marks review, Rickles), which suggests the core is found. Search 2 was too narrow:
a web search found a further relevant paper (a machine-learning neighbourhood vulnerability study using overdose deaths as the outcome
proxy for an overdose, HIV and HCV outbreak; authors and year to be traced) that Search 2 did not return.

## Still to do
- Run a looser string (drop the forecasting block or add "risk" and "vulnerab*") and record the hit count.
- Search Embase, Web of Science, Scopus, medRxiv and arXiv; record strings and counts.
- Citation-chase from Gezer 2024, Sumetsky 2019, Rickles 2018 and the Marks 2021 review.
- Read in full: Gezer 2024, Marks 2021 review, Gizamba 2026. Check what mortality measure Gezer used.
"""

m = re.search(r"^## 8\. Related work.*?(?=^## 9\. )", text, flags=re.M | re.S)
text = text[:m.start()] + SECTION8 + text[m.end():]
f.write_text(text, encoding="utf-8", newline="\r\n")
log.write_text(LOG, encoding="utf-8", newline="\r\n")
print("Rewrote section 8 and wrote", log)
