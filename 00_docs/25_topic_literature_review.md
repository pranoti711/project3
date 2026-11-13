# 25_topic_literature_review.md - topic-level literature review (13 Nov 2026)

Purpose: place the project (does county mortality add out-of-sample predictive value for next-year infectious-disease up-transitions?) in the
wider literature, beyond the closest prior studies in `24_novelty_search_log.md`. Method: structured PubMed screens (see the log) plus about 15
web searches on 12-13 Nov 2026. Verification level is given per source: FULL = full text read; ABSTRACT = abstract or full-text snippets;
TITLE = title or citation only. Verify every entry against the paper before citing it in a manuscript.

## 1. Substantive evidence: mortality and opioid indicators versus infection
- Cross-sectional vulnerability work treats overdose mortality as an indicator of infection risk. Van Handel et al. (2016) regressed county acute
  hepatitis C (a proxy for injection drug use) on 15 indicators; six were retained, including drug-overdose deaths (ABSTRACT). Rickles et al.
  (2018) used opioid-related mortality in Tennessee (ABSTRACT, Marks review table).
- Associations at area level are mixed. Sumetsky et al. (2019): previous-year opioid hospitalisations, rate ratios about 1.09 (HCV) and 1.10 (HIV)
  in Pennsylvania ZIP codes (ABSTRACT). Gezer et al. (2024): all-cause mortality per 1,000 residents associated with opioid-related and
  HCV-related hospitalisations, rate ratio 1.18 per SD (ABSTRACT). Drewes et al. (2021): after adjustment, opioid death rates were not
  associated with gonorrhoea, chlamydia or HIV except for gonorrhoea in urban counties (rate ratio 1.11, 95% CI 1.02 to 1.20); homicide rate
  also associated with urban gonorrhoea (FULL). Gonsalves et al. (2021): fatal overdoses about 8 months earlier associated with HIV counts in
  Lawrence and Lowell (rate ratio 1.03, 90% CrI 1.00 to 1.06); Gonsalves et al. (2023): no overdose association statewide (ABSTRACT).
- Abara et al. (opioid prescribing trends and gonorrhoea in US counties, 2010-2015): positive association that weakened over the period; the
  authors note possible confounding by men who have sex with men (ABSTRACT).
- Individual-level link: methamphetamine and injection drug use among people with primary and secondary syphilis (Kidd et al., MMWR 2019; ABSTRACT, details in section 8). Individual links do not imply that county mortality predicts county infection counts.
Reading: the link is plausible and sometimes significant in association models, but no study reports a test of added predictive value.

## 2. Prediction and validation evidence
- Marks et al. (2021, Transl Res; FULL): 46 studies on detection, risk assessment and prediction of opioid-related epidemics (search to
  January 2021). Risk assessments such as Van Handel were fitted and scored on the same data without validation; geospatial methods were mainly
  explanatory; bloodborne-infection prediction used dynamic models.
- Gezer et al. (2024): fully adjusted negative binomial mixed models trained on 2016-2020 and checked on 2021 hospitalisations; accuracy is the
  median percent agreement between predicted and observed ZIP-code counts (about 80% opioid-related, 75% HCV-related). There is no ablation
  of mortality and no placebo design (ABSTRACT and snippets; Table 2 not read).
- Ma et al. (2026, Front Public Health 14:1888674; FULL): state-level forecasting of primary and secondary syphilis with gradient boosting,
  neural network, Bayesian and baseline models. Co-STI, HIV, poverty, unemployment and income covariates improved holdout error modestly
  (XGBoost WAPE 22.7% to 20.0%); mortality or overdose was not used. State counts, not county transitions.
Reading: the missing piece is an incremental, out-of-sample, placebo-controlled test at county level, which this project provides.

## 3. Outcome definition and detectability
- Richardson et al. (2004, Environ Health Perspect; ABSTRACT): classifying areas by the posterior probability that relative risk exceeds a
  threshold, with a 70-80% cut-off, is specific; the models are conservative, with low sensitivity when the true excess is under 2-fold or
  expected counts are not substantial (about 50 per area). This explains why small counties rarely register an up-transition and why population
  acts as a detectability marker.
- Abellan, Richardson and Best (2008, Environ Health Perspect 116:1111) extend decision rules to space-time disease mapping (TITLE; cited from
  memory, verify).

## 4. Exposure data quality
- CDC WONDER suppresses county counts of 1 to 9 deaths and flags counts under 20 as unreliable; suppression falls mostly on small, rural counties
  (ABSTRACT-level sources, including County Health Rankings documentation). In this panel 43% of drug-overdose and suicide rows and 66% of
  homicide rows were missing (write-up section 5).
- Fentanyl-related mortality rose steeply west of the Mississippi later than in the East (Shover et al., Drug Alcohol Depend 2020;216:108314; ABSTRACT, details in section 8). Whether this
  limited exposure variation in California during 2017-2020 is a hypothesis, not a finding.

## 5. Evaluation and reporting methods
- A small change in AUC can hide decision value, and a very large association is needed to move AUC (Pencina et al., 2008; Cook, 2007); decision
  analysis answers whether a small AUC change is worthwhile (Baker et al., 2014); reclassification measures have known limits (Leening et al., 2014)
  (all ABSTRACT or TITLE). The project already reports decision curves, calibration and proper scores.
- Reporting and bias tools: TRIPOD+AI (Collins et al., BMJ 2024;385:e078378, 27 items, supersedes TRIPOD 2015), PROBAST+AI (BMJ 2025;388),
  TRIPOD-Cluster (Debray et al., 2023) for clustered data.
- Negative controls (Lipsitch et al., 2010, Epidemiology 21:383) and leave-future-out validation (Burkner et al., 2020, J Stat Comput Simul) are
  verified (ABSTRACT).

## 6. Implications for the paper
1. Novelty wording: to our knowledge, no study tests whether county mortality adds out-of-sample predictive value for infectious-disease
   up-transition events across multiple diseases, against a population-adjusted baseline, with placebo and held-out-disease controls. State the
   search dates and limits (`24_novelty_search_log.md`).
2. Framing: a stress test of the assumption behind overdose-indicator vulnerability assessments, not a claim that mortality and infection are unrelated.
3. Scope limits to state: no HCV or HIV among the 16 diseases; 81 events; stage 1 pre-specified and later layers post hoc; mortality suppressed in
   small counties.
4. Do not claim: that prior associations are explained by county size (a hypothesis); that the null covers bloodborne outbreaks; that the study is
   an operational early-warning system.

## 7. Still to verify
Gezer 2024 Table 2 and the accuracy formula (PMC blocked automated access); Sumetsky 2019, Gonsalves 2021 and 2023 full text; Gizamba 2025 systematic synthesis; the Oklahoma county study; Abellan 2008; Leening 2014 page numbers; Embase, Web of Science and Scopus (not accessible).

## 8. Second verification pass (13 Nov 2026)
- Gizamba et al. (2026, BMC Public Health 26:2297; FULL): cross-sectional study of 245 Los Angeles County ZIP code tabulation areas, first-time
  RNA-positive hepatitis C among ages 18-39, January 2020 to December 2023; 31 predictors covering socioeconomic conditions, healthcare access and
  opioid-related morbidity (hospitalisations and emergency visits for 2022, new HIV diagnoses). Overdose mortality was not a predictor. Validation was
  random 5-fold nested cross-validation (RMSE 11, pseudo R-squared 0.34); agreement between predicted and observed risk categories was modest
  (accuracy 34.6%, kappa 0.18); calibration was not assessed. The authors say the map supports prioritisation and hypothesis generation, not
  fine-scale allocation. It is not a temporal holdout and does not test mortality.
- California Department of Public Health vulnerability assessment (2017 data; FULL): all 58 counties; separate models for fatal opioid overdose and for
  HIV or HCV vulnerability. The HIV or HCV model retained race and ethnicity, heroin emergency visits (ages 15-29), estimated HCV prevalence (age 40+),
  felony drug arrests and households without a vehicle; overdose mortality was not in that model. The report states that its findings are not
  predictive. Twelve counties were high risk for HIV or HCV and 11 for fatal overdose, concentrated in northern California and small counties. This is the
  closest California precedent and shares the project's 58 counties.
- CDC jurisdictional assessments (CDC web pages and Shrestha et al., Prev Med 2023;170:107490; ABSTRACT): core indicators used by states include drug
  overdose mortality, prescriptions, arrests and acute HCV; these are ranking tools, not forecasts.
- Kidd et al. (MMWR 2019;68:144; ABSTRACT and CDC summary): among women with primary and secondary syphilis, methamphetamine use rose from 6.2% to 16.6%
  during 2013-2017, injection drug use from 4.0% to 10.5% and heroin use from 2.1% to 5.8%; among men who have sex with men methamphetamine use fell from
  9.2% to 8.0%. Stimulants matter for syphilis, so a mortality series dominated by opioids may be a weak proxy. A California report notes that
  amphetamine-related overdose deaths rose 198% in 2012-2018.
- Shover et al. (Drug Alcohol Depend 2020;216:108314; ABSTRACT and partial full text): in 2018 states east of the Mississippi had 88% of synthetic opioid
  deaths; available 2020 data showed a 63% rise in fentanyl mortality over 2019. A 2025 JAMA Netw Open report (abstract level) found that states such as
  California had rapidly rising drug mortality after 2019 relative to pre-2020 trends. The steepest California rise therefore falls mostly after the scored
  test years (a hypothesis, not a finding).
- Gezer et al. (2024; ABSTRACT, Table 2 not accessible): 41,691 opioid-related and 26,860 HCV-related hospitalisations in South Carolina, 2016-2021; per
  standard deviation, relative risks 1.24 (uninsured, poverty), 1.18 (mortality, 95% CI 1.12 to 1.25) and 1.17 (social vulnerability), and 0.79 (income);
  trained on 2016-2020, median accuracy for 2021 was 80.4% (IQR 66.8 to 91.1) for opioid-related and 75.2% (61.2 to 87.7) for HCV-related
  hospitalisations. Whether the mortality estimate is mutually adjusted, and the exact accuracy formula, remain unconfirmed (the paper cites the "Table 2
  fallacy" literature, which hints at a multivariable model).
- Others (ABSTRACT or title level): Yedinak et al., Int J Drug Policy 2021;96:103395 (statewide neighbourhood machine-learning vulnerability scores using overdose
  deaths as a proxy outcome); an Oklahoma county vulnerability index using drug-related mortality as an indicator (PubMed 38722958, 2024; findings not
  retrieved); a July 2026 medRxiv preprint on surveillance-adjusted syphilis risk across US counties (cross-sectional Bayesian spatial model, no
  mortality predictor); Gizamba et al. 2025 systematic synthesis of area-level hepatitis C determinants (BMC Public Health 25:687; not read).
- Search coverage: Embase, Web of Science and Scopus could not be accessed with the tools used; PubMed was screened systematically and medRxiv and arXiv were
  covered only through web searches. No study testing incremental out-of-sample value of mortality for infection transitions was found.
