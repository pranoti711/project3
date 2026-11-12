# 24_novelty_search_log.md - literature search record for the novelty claim (updated 2026-11-12)

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
