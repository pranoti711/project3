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
| Sumetsky et al., JECH 2019 | Bayesian spatiotemporal Poisson (CAR), PA ZIP codes 2004-2014; previous-year opioid hospitalisations vs HCV/HIV | Abstract checked 2026-11-12 | Association (RR 1.09 HCV, 1.10 HIV); exposure is hospitalisation, not mortality; no out-of-sample test. |
| Gezer et al., Lancet Public Health 2024 | SC ZIP codes; train 2016-20, validate 2021; accuracy = median percent agreement of predicted vs observed counts from fully adjusted NB mixed models using previous counts; all-cause mortality per 1,000 among factors (RR 1.18 per SD, combined outcome) | Abstract and full-text snippets (PMC blocked automated access) | Closest study; one state, hospitalisation counts, no ablation of mortality, no placebo design. Association models were adjusted for time and a population offset; whether mortality stays significant in the fully adjusted model is not verified (read Table 2). |
| Gonsalves et al., OFID 2021 and CID 2023 | OFID: Lawrence/Lowell 2005-2018, overdose 8 months earlier RR 1.03 (90% CrI 1.00-1.06) for HIV. CID: all Massachusetts ZIP codes 2005-2018, monthly HIV presence, ages 15-50; HCV and SSTI preceded HIV, no overdose association | Abstracts and methods snippets | Lagged mortality-infection association in one setting only; authors state the lagged associations are not predictive of outbreaks. |
| Marks et al., Lancet Public Health 2021; Bauer 2023; Patton 2025; Sumetsky 2021 | Forecast overdose itself | Abstracts | Related, outcome is mortality. |
| Gizamba et al., BMC Public Health 2026 | Cross-sectional, 245 LA County ZIP codes, Elastic Net and random forest, hepatitis C ages 18-39 | Full text read 2026-11-13 | No overdose mortality predictor (opioid hospitalisations, emergency visits and HIV were); random 5-fold CV; modest category agreement; not temporal. |
| Cohen 2003; Abara 2019 | Premature mortality and gonorrhoea (cities); opioid prescribing and gonorrhoea (counties) | Titles only | Verify. |

## Notes for the discussion
- Our 16 diseases include chlamydia, gonorrhoea and early syphilis but not HCV or HIV; the null does not address bloodborne outbreaks.
- Gezer used all-cause mortality; our boosted-model check also found the all-cause deviation to be the only mortality feature with importance,
  yet no incremental AUC gain (consistent with an association that does not translate to added prediction).
- Van Handel-type scores use overdose deaths as an indicator without validation; our design is a temporal, population-adjusted test of that assumption.

## Still to do
- Run a looser PubMed string (drop the forecasting block; add "risk" and "vulnerab*") and record the hit count.
- Search Embase, Web of Science, Scopus, medRxiv and arXiv; record strings and counts.
- Read Table 2 and the accuracy formula in Gezer 2024 in a browser; read Sumetsky 2019, Gonsalves 2021 and 2023 in full; Gizamba 2025 synthesis; Embase, Web of Science, Scopus.
- Citation-chase forward from Gezer 2024 and from the Marks et al. review for 2021-2026 studies.

## Additional sources checked 2026-11-13 (see 25_topic_literature_review.md)
| Source | Level | Note |
|---|---|---|
| Abara et al., opioid prescribing trends and gonorrhoea, US counties 2010-2015 | Abstract | Positive but weakening association; possible confounding by MSM |
| Ma et al., Front Public Health 2026;14:1888674 | Full text | State-level syphilis forecasting; co-STI and socioeconomic covariates helped modestly; no mortality |
| Richardson et al., Environ Health Perspect 2004 | Abstract | Posterior-probability rule specific but low sensitivity under 2-fold excess |
| Lipsitch et al., Epidemiology 2010; Burkner et al., J Stat Comput Simul 2020 | Abstract | Methods references verified |
| Pencina 2008; Cook 2007; Baker 2014; Leening 2014 | Abstract or title | Small AUC change vs decision value; NRI limits |
| TRIPOD+AI (BMJ 2024); PROBAST+AI (BMJ 2025); TRIPOD-Cluster (2023) | Abstract or title | Reporting and risk-of-bias tools |
| CDC WONDER suppression rule (1-9 deaths; under 20 unreliable) | Documentation | Suppression concentrated in small rural counties |
| Kidd et al., MMWR 2019; Shover et al., Drug Alcohol Depend 2020 | Verified 2026-11-13 | See the second-pass table below |

## Second pass 2026-11-13: full-text and extra searches
| Source | Level | Note |
|---|---|---|
| Gizamba et al., BMC Public Health 2026;26:2297 | Full text | Cross-sectional; no overdose mortality predictor; random 5-fold CV; category accuracy 34.6%, kappa 0.18 |
| CDPH California fatal opioid overdose and HIV/HCV vulnerability assessment (2017 data) | Full text | 58 counties; not predictive by its own statement; overdose mortality not in the HIV/HCV model |
| Kidd et al., MMWR 2019;68:144 | Abstract and CDC summary | Meth, injection and heroin use rose among women and heterosexual men with syphilis |
| Shover et al., Drug Alcohol Depend 2020;216:108314 | Abstract and partial full text | Fentanyl reached western markets late; 63% rise 2019 to 2020 in available data |
| Gezer et al., Lancet Public Health 2024 | Abstract | Mortality RR 1.18 (1.12-1.25) per SD; Table 2 and accuracy formula still unseen |
| Yedinak 2021; Oklahoma county index 2024; medRxiv syphilis county mapping 2026 | Abstract | No competing incremental-prediction study |
Coverage: Embase, Web of Science and Scopus not accessible; medRxiv and arXiv reached only by web search.
