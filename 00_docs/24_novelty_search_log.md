# 24_novelty_search_log.md - literature search record for the novelty claim

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
