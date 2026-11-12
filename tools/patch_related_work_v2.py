"""
patch_related_work_v2.py - second pass on section 8 (Related work) after reading full texts and abstracts on 2026-11-12.
Replaces section 8, adds one limitation bullet to section 6, and rewrites 00_docs/24_novelty_search_log.md.
Run from the project3 folder:  python tools/patch_related_work_v2.py
Nothing is written unless every anchor matches exactly once.
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
if "checked 2026-11-12 against full text" in text:
    sys.exit("Already patched.")

def pat(s):
    return r"\s+".join(re.escape(t) for t in s.split())

if len(re.findall(r"^## 8\. Related work", text, flags=re.M)) != 1 or len(re.findall(r"^## 9\. ", text, flags=re.M)) != 1:
    sys.exit("Need exactly one section 8 and one section 9 heading. Nothing written.")
anchor = "region-of-practical-equivalence statement, not posterior probabilities."
if len(re.findall(pat(anchor), text)) != 1:
    sys.exit("Limitation anchor not found exactly once. Nothing written.")

SECTION8 = """## 8. Related work (checked 2026-11-12 against full text or abstracts; see `24_novelty_search_log.md`)

Verification status. Full text read: Drewes et al. 2021; Marks et al. 2021 (Transl Res review). Abstract and parts of the full text seen:
Van Handel et al. 2016, Gezer et al. 2024, Sumetsky et al. 2019, Rickles et al. 2018, Gonsalves et al. 2021 and 2023. Not yet checked: Cohen et al.
2003, Abara et al. 2019, Bauer et al. 2023, Patton et al. 2025, Gizamba et al. 2026, and the methods references. Full entries for the
earlier references are in `06_paper/references.bib`.

- **Vulnerability assessments (cross-sectional).** Van Handel et al. (2016) regressed county acute hepatitis C in 2012-2013, a proxy
  for injection drug use, on 15 county indicators; six were retained, including drug-overdose deaths, prescription opioid sales,
  income, race and ethnicity, unemployment and buprenorphine capacity, and 220 counties in 26 states were ranked as most vulnerable.
  Tennessee (Rickles et al., 2018) and Utah versions followed, and Rickles et al. used opioid-related mortality as an indicator. The
  Marks et al. (2021) review notes that the scores were computed on the same data used to fit the models and that no internal or external
  validation was applied. These assessments therefore assume that overdose mortality marks infection risk but did not test it out of
  sample.
- **Association and lag studies.** Drewes et al. (2021) analysed 245 Northeast US counties in three two-year windows (2012-2017) with
  negative binomial mixed models. After adjustment, opioid death rates were not associated with gonorrhoea, chlamydia or HIV, except
  for gonorrhoea in urban counties (rate ratio 1.11, 95% CI 1.02 to 1.20; none in rural counties); the homicide rate was also associated
  with urban gonorrhoea (1.28). In Pennsylvania ZIP codes, previous-year opioid-related hospitalisations were associated with higher
  HCV and HIV hospitalisations (Sumetsky et al., 2019). In Lawrence and Lowell, Massachusetts, fatal overdoses about 8 months earlier
  were associated with current-month HIV counts, although the authors state they were not making short-term predictions (Gonsalves
  et al., 2021). In a statewide Massachusetts analysis, earlier HCV and skin and soft tissue infections preceded HIV rises, overdose
  showed no such association, and the authors concluded the lagged associations cannot be described as predictive of HIV outbreaks
  (Gonsalves et al., 2023). Older ecological studies linked premature mortality (Cohen et al., 2003) and opioid prescribing trends
  (Abara et al., 2019) with gonorrhoea rates; these two are not yet verified.
- **Area-level prediction with a temporal holdout.** In South Carolina ZIP codes, mixed-effects negative binomial models trained on
  2016-2020 hospitalisations were validated on 2021 (median accuracy about 80% for opioid-related and 75% for HCV-related
  hospitalisations), and all-cause mortality per 1,000 residents was among the associated factors (rate ratio 1.18 per standard
  deviation for the combined outcome; Gezer et al., 2024). This is the closest study found. It differs from ours in outcome
  (hospitalisation counts, not transition events), geography (one state), diseases (HCV and opioid-related admissions) and design (the
  mortality measure is all-cause, there is no incremental comparison against a population-adjusted baseline, and there are no placebo or
  held-out-disease controls).
- **Forecasting overdose itself.** County and small-area forecasts of overdose mortality (Marks et al., 2021, Lancet Public Health; Bauer
  et al., 2023; Sumetsky et al., 2021) and early-warning alerts for overdose outbreaks (Patton et al., 2025) predict mortality, not
  infection. The Marks et al. review (46 included studies, search to January 2021) places infection outcomes in risk assessment or
  mechanistic modelling and notes that geospatial methods have been used mainly to explain rather than predict; in its prediction
  category, bloodborne-infection studies used dynamic models.
- **Methods behind the design.** Flagging areas by posterior probability of elevated risk with a 70-80% cut-off is established in
  disease mapping and is conservative for small counts (Richardson et al., 2004). Negative-control exposures and outcomes (Lipsitch et al.,
  2010) and leave-future-out validation (Burkner et al., 2020) underlie the placebo, surrogate-disease and temporal validation designs.

**How the results relate to earlier work.** Prior area-level studies mostly report positive associations of opioid-related indicators
with HCV, HIV or STI outcomes, and Van Handel-type assessments rely on overdose mortality as an indicator. Our question is different:
whether mortality adds out-of-sample predictive value after adjusting for county population. Our first-pass confounded run showed how
county size can create an apparent gain; whether size or detectability also partly explains earlier associations is a hypothesis, not a
finding, because the exposures, outcomes and geographies differ. Our 16 diseases include three STIs (chlamydia, gonorrhoea, early
syphilis) but not HCV or HIV, so the null result does not speak to bloodborne outbreaks.

**Position, with the limits of the search stated.** To our knowledge, and after PubMed searches on 2026-11-12, reading of the Marks et al.
review and web searches, we found no study that tests whether county mortality adds out-of-sample predictive value for infectious-disease
up-transition events across multiple diseases, against a population-adjusted baseline, with placebo and held-out-disease controls. The
closest work is Gezer et al. (2024). Limits: only PubMed was searched systematically; Embase, Web of Science, Scopus and preprint servers are
not yet searched; the Marks et al. review ends in January 2021; and the narrow search string missed relevant papers that web searches found.
This must be re-checked before any claim of novelty in a submission.

"""

BULLET = ("\n- The 16 diseases include three STIs (chlamydia, gonorrhoea, early syphilis) but not hepatitis C or HIV, the infections most "
          "often linked to opioid-related outbreaks, so the result does not address bloodborne outbreaks.")

m = re.search(r"^## 8\. Related work.*?(?=^## 9\. )", text, flags=re.M | re.S)
text = text[:m.start()] + SECTION8 + text[m.end():]
m2 = re.search(pat(anchor), text)
text = text[:m2.end()] + BULLET + text[m2.end():]

LOG = """# 24_novelty_search_log.md - literature search record for the novelty claim (updated 2026-11-12)

Claim tested: no prior study tests whether county mortality adds out-of-sample predictive value for infectious-disease up-transition
events across multiple diseases, against a population-adjusted baseline, with placebo and held-out-disease controls.

## Searches
1. PubMed broad string (mortality/overdose/suicide/homicide AND infectious disease AND county/small area AND forecasting terms, MeSH plus
   title/abstract), run 2026-11-12. 73 records screened (total hit count not recorded). About 8 of 73 relevant.
2. PubMed tight string, run 2026-11-12: 14 hits.
```
(overdose*[tiab] OR "opioid-related"[tiab] OR suicide[tiab] OR homicide[tiab] OR "drug-related death*"[tiab])
AND (hepatitis[tiab] OR HIV[tiab] OR "sexually transmitted"[tiab] OR gonorrhea[tiab] OR syphilis[tiab] OR "infectious disease*"[tiab] OR notifiable[tiab])
AND (county[tiab] OR counties[tiab] OR "ZIP code*"[tiab] OR "small area*"[tiab] OR spatiotemporal[tiab])
AND (forecast*[tiab] OR predict*[tiab] OR "early warning"[tiab] OR "out-of-sample"[tiab] OR lagged[tiab] OR "previous-year"[tiab])
NOT (COVID-19[tiab] OR "SARS-CoV-2"[tiab])
```
3. Web searches (several, 2026-11-12): county mortality predicting infection; Drewes; Gezer; Van Handel; Marks review; lagged overdose and
   hepatitis C, HIV or syphilis; Massachusetts distributed-lag HIV.

Both PubMed strings returned the same core set. The tight string missed relevant work (the Massachusetts distributed-lag studies by
Gonsalves et al. and a machine-learning neighbourhood vulnerability study) that web searches found, so it is too narrow.

## Papers and verification status
| Paper | What it does | Status | Bearing on the claim |
|---|---|---|---|
| Drewes et al., IJERPH 2021 18(1):62 (online 23 Dec 2020) | 245 NE counties 2012-2017, NB mixed models; opioid deaths vs gonorrhoea, chlamydia, HIV | Full text read | Association only. Significant only for urban gonorrhoea (RR 1.11, 1.02-1.20). Earlier doubt about urban vs rural resolved: urban is correct. |
| Marks et al., Transl Res 2021 (review) | 46 studies on detection, risk assessment, prediction of opioid epidemics; search to Jan 2021 | Full text read | Risk assessments lack validation; geospatial work mainly explanatory; infection prediction used dynamic models. Supports gap. |
| Van Handel et al., JAIDS 2016 | Acute HCV as IDU proxy, 15 indicators, 6 retained incl. overdose deaths; 220 counties ranked | Abstract and summaries | Cross-sectional; mortality is an indicator; no validation per Marks review. |
| Rickles et al., CID 2018 | Tennessee version; opioid-related mortality an indicator | Abstract and Marks table | Cross-sectional ranking. |
| Sumetsky et al., JECH 2019 | PA ZIP codes 2004-2014; previous-year opioid hospitalisations vs HCV/HIV | Abstract | Lagged association; no out-of-sample test. |
| Gezer et al., Lancet Public Health 2024 | SC ZIP codes; train 2016-20, validate 2021; all-cause mortality among factors (RR 1.18 per SD) | Abstract and snippets of full text | Closest study; one state, hospitalisation counts, no incremental or placebo design. |
| Gonsalves et al., OFID 2021 and CID 2023 | Massachusetts distributed-lag models; overdose lagged ~8 months vs HIV in Lawrence/Lowell; statewide no overdose association | Abstracts | Lagged mortality-infection association in one setting, not predictive per the authors. |
| Marks et al., Lancet Public Health 2021; Bauer 2023; Patton 2025; Sumetsky 2021 | Forecast overdose itself | Abstracts | Related, outcome is mortality. |
| Gizamba et al., BMC Public Health 2026 | HCV risk in LA County ZIP codes with machine learning | Not read (abstract not seen) | Check predictors. |
| Cohen 2003; Abara 2019 | Premature mortality and gonorrhoea (cities); opioid prescribing and gonorrhoea (counties) | Titles only | Verify. |

## Notes for the discussion
- Our 16 diseases include chlamydia, gonorrhoea and early syphilis but not HCV or HIV; the null does not address bloodborne outbreaks.
- Gezer used all-cause mortality; our boosted-model check also found the all-cause deviation to be the only mortality feature with importance,
  yet no incremental AUC gain (consistent with an association that does not translate to added prediction).
- Van Handel-type scores use overdose deaths as an indicator without validation; our design is a temporal, population-adjusted test of that assumption.

## Still to do
- Run a looser PubMed string (drop the forecasting block; add "risk" and "vulnerab*") and record the hit count.
- Search Embase, Web of Science, Scopus, medRxiv and arXiv; record strings and counts.
- Read in full: Gezer 2024, Sumetsky 2019, Gonsalves 2021 and 2023, Gizamba 2026; verify Cohen 2003, Abara 2019, Bauer 2023, Patton 2025.
- Citation-chase forward from Gezer 2024 and from the Marks et al. review for 2021-2026 studies.
"""
f.write_text(text, encoding="utf-8", newline="\r\n")
log.write_text(LOG, encoding="utf-8", newline="\r\n")
print("Section 8 rewritten, limitation bullet added, search log updated.")
