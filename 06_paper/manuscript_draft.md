---
title: "County mortality adds no out-of-sample predictive value for infectious-disease up-transitions in California: a pre-registered leave-future-out analysis"
author: "Pranoti Munjankar (IIT Tirupati)"
bibliography: 06_paper/references.bib
nocite: |
  @*
---

# Abstract

**Background.** Overdose, suicide and homicide mortality are often assumed to signal rising infectious disease in the same communities, but it is unknown whether county mortality improves out-of-sample forecasts of infectious disease increases.

**Methods.** We used 2001–2023 data for 16 notifiable diseases in California’s 58 counties. The outcome was an up-transition: the posterior probability of a rising local trend crossing 0.80, after removing the statewide yearly change. A baseline (own history plus county population) was compared with models adding lagged within-county mortality deviations, air quality and drought, or both. Validation was leave-future-out over 2017–2020 (81 events in 3,712 county-disease-year rows), using within-year-and-disease AUC with county-cluster bootstrap intervals. Stage 1 was pre-specified (protocol frozen at git tag stage1-freeze); all other analyses, including placebo, equivalence and decision-curve checks, were exploratory or post hoc.

**Results.** Mortality did not improve discrimination (ΔAUC +0.001, 95% CI −0.028 to +0.034); context features gave +0.003 (−0.005 to +0.013) and the combined model +0.003 (−0.028 to +0.037). No disease group survived placebo testing with Holm correction, and results did not transfer to held-out diseases. The 90% interval for mortality lay within ±0.03 AUC, and the minimum detectable gain was 0.045. Log-loss and Brier differences were indistinguishable from zero. An exploratory HIV extension (4 test events) was also null (pooled ΔAUC −0.007, 95% CI −0.039 to +0.023). An initial apparent gain (ΔAUC +0.025) was explained by county population, which marks detectability in small counties.

**Conclusions.** County mortality showed no detectable added predictive value. With 81 events, gains below about 0.045 AUC cannot be excluded. Baselines should include population, and placebo tests must be able to separate the hypothesis from county size.

# Introduction

- **Vulnerability assessments (cross-sectional).** Van Handel et al. (2016) regressed county acute hepatitis C in 2012-2013, a proxy
  for injection drug use, on 15 county indicators; six were retained, including drug-overdose deaths, prescription opioid sales,
  income, race and ethnicity, unemployment and buprenorphine capacity, and 220 counties in 26 states were ranked as most vulnerable.
  Tennessee (Rickles et al., 2018) and Utah versions followed, and Rickles et al. used opioid-related mortality as an indicator. The
  Marks et al. (2021a) review notes that the scores were computed on the same data used to fit the models and that no internal or external
  validation was applied. These assessments therefore assume that overdose mortality marks infection risk but did not test it out of sample. Cross-sectional machine-learning risk mapping continues (Gizamba et al., 2026: hepatitis C in 245 Los Angeles County ZIP codes with Elastic Net and random forest; its predictors included opioid-related hospitalisations and emergency visits and new HIV diagnoses but not overdose mortality, validation was random 5-fold cross-validation, and agreement between predicted and observed risk categories was modest). The California Department of Public Health assessment of all 58 counties (2017 data) used indicators such as heroin emergency visits, hepatitis C prevalence and drug arrests, did not include overdose mortality in its HIV or HCV model, and states that its results are not predictive.
- **Association and lag studies.** Drewes et al. (2021) analysed 245 Northeast US counties in three two-year windows (2012-2017) with
  negative binomial mixed models. After adjustment, opioid death rates were not associated with gonorrhoea, chlamydia or HIV, except
  for gonorrhoea in urban counties (rate ratio 1.11, 95% CI 1.02 to 1.20; none in rural counties); the homicide rate was also associated
  with urban gonorrhoea (1.28). In Pennsylvania ZIP codes (2004-2014), Bayesian spatiotemporal Poisson models found previous-year opioid-related hospitalisations associated with higher HCV and HIV hospitalisations (rate ratios about 1.09 and 1.10; Sumetsky et al., 2019); the exposure is hospitalisation, not mortality, and the paper reports association, not prediction. In Lawrence and Lowell, Massachusetts, fatal overdoses about 8 months earlier
  were associated with current-month HIV counts (rate ratio 1.03 per additional overdose, 90% credible interval 1.00 to 1.06), and the authors propose that such complications could serve as input to a sentinel system to trigger early intervention (Gonsalves et al., 2021; the rate ratio is from a search snippet and is not yet checked in the full text). In a statewide Massachusetts analysis at ZIP-code level (2005-2018, monthly presence of HIV), an additional HCV case 5 or 7 months earlier was associated with about 4% higher odds of an HIV case (odds ratio 1.04, 90% credible interval 1.01 to 1.10), skin and soft tissue infections and drainage procedures also preceded HIV, overdose showed no such association, and the authors concluded the lagged associations cannot be described as causal or predictive of HIV outbreaks; they used shuffled predictors and fatal automobile accidents as negative controls (Gonsalves et al., 2023). An older ecological study of 107 US cities modelled both gonorrhoea and premature death as outcomes of boarded-up housing (Cohen et al., 2003), and county opioid prescribing trends were associated with gonorrhoea rates (Abara et al., 2019); in the Abara study of male gonorrhoea rates in US counties, opioid prescribing (a proxy for misuse) was positively associated with gonorrhoea (coefficient 0.068, 95% CI 0.031 to 0.105, cases per 100,000 males per prescription per 100 persons), the association weakened over 2010-2015, and the authors noted possible confounding by men who have sex with men (full text read; the Cohen description is from the abstract).
- **Area-level prediction with a temporal holdout.** In South Carolina ZIP codes, mixed-effects negative binomial models trained on
  2016-2020 hospitalisations were validated on 2021 (median percent agreement between predicted and observed counts about 80% for opioid-related and 75% for HCV-related hospitalisations, using fully adjusted models and previous hospitalisation counts), and all-cause mortality per 1,000 residents was among the associated factors (rate ratio 1.18, 95% CI 1.12 to 1.25, per standard deviation for the combined outcome, alongside poverty and uninsured rate; Gezer et al., 2024). This is the closest study found. It differs from ours in outcome
  (hospitalisation counts, not transition events), geography (one state), diseases (HCV and opioid-related admissions) and design (the mortality measure is all-cause and each association was estimated one predictor at a time, adjusting for time and a population offset; community-level covariates were compared with a history-only model as a block and gave only a mild accuracy gain, so the contribution of mortality itself was not isolated; and there are no placebo or held-out-disease controls).
- **Forecasting overdose itself.** County and small-area forecasts of overdose mortality (Marks et al., 2021b, Lancet Public Health; Bauer
  et al., 2023; Sumetsky et al., 2021) and early-warning alerts for overdose outbreaks (Patton et al., 2025) predict mortality, not infection. Bauer et al. (2023) forecast Massachusetts ZIP-code opioid deaths one year ahead (2016-2019) with Bayesian spatiotemporal models; adding demographic and socioeconomic covariates improved only the model without spatial dependence, forecast errors were larger in rural than urban ZIP codes (the small-area problem), and the model under-predicted 2020-2021 after the COVID-19 disruption (full text read). The Marks et al. review (46 included studies, search to January 2021) places infection outcomes in risk assessment or
  mechanistic modelling and notes that geospatial methods have been used mainly to explain rather than predict; in its prediction
  category, bloodborne-infection studies used dynamic models.
- **Methods behind the design.** Flagging areas by posterior probability of elevated risk with a 70-80% cut-off is established in
  disease mapping and is conservative for small counts (Richardson et al., 2004); its sensitivity is low when the true excess is under 2-fold or expected counts are small, which is consistent with the county-size pattern seen here. Negative-control exposures and outcomes (Lipsitch et al.,
  2010) and leave-future-out validation (Burkner et al., 2020) underlie the placebo, surrogate-disease and temporal validation designs.

**How the results relate to earlier work.** Prior area-level studies mostly report positive associations of opioid-related indicators
with HCV, HIV or STI outcomes, and Van Handel-type assessments rely on overdose mortality as an indicator. Our question is different:
whether mortality adds out-of-sample predictive value after adjusting for county population. Our first-pass confounded run showed how
county size can create an apparent gain; whether size or detectability also partly explains earlier associations is a hypothesis, not a
finding, because the exposures, outcomes and geographies differ. Our 16 diseases include three STIs (chlamydia, gonorrhoea, early
syphilis) but not HCV, and HIV only as an exploratory group with 4 test events (see the HIV extension section), so the null result does not speak to bloodborne outbreaks.

**Position, with the limits of the search stated.** To our knowledge, and after PubMed searches on 2026-11-12, reading of the Marks et al.
review and web searches, we found no study that tests whether county mortality adds out-of-sample predictive value for infectious-disease
up-transition events across multiple diseases, against a population-adjusted baseline, with placebo and held-out-disease controls. The
closest work is Gezer et al. (2024). Limits: only PubMed was searched systematically; Embase, Web of Science and Scopus could not be accessed and medRxiv was reached only through web search; the Marks et al. review ends in January 2021; and the narrow search string missed relevant papers that web searches found.
This must be re-checked before any claim of novelty in a submission.

# Methods

Does adding county mortality (drug overdose, suicide, homicide, all-cause) improve out-of-sample prediction of
next-year up-transitions in 16 notifiable infectious diseases in California counties (2001-2023)?
Models: A = own history plus county population; B = A plus mortality; C = A plus air quality and drought;
D = all. Outcome: up-crossing of Pr(rising) at 0.80 after removing the statewide yearly change
(local up-crossing definition, threshold 0.80). Evaluation: leave-future-out over 2017-2020 (81 events in 3,712 county-disease-year
rows), AUC computed within each year x disease cell and averaged with pair-count weights. Mortality enters
as the lagged within-county deviation: the county's rate in year t-1 minus its own mean over t-6 to t-2.

# Results

## Primary result: no detectable gain

| Comparison with A | Delta AUC | 95% county-cluster bootstrap CI |
|---|---|---|
| B (mortality) | +0.001 | [-0.028, +0.034] |
| C (context) | +0.003 | [-0.005, +0.013] |
| D (all) | +0.003 | [-0.028, +0.037] |

By group, B - A was -0.012 (comparison), +0.001 (review_sti), +0.029 (environment) and -0.039 (ambiguous); every
interval included 0. Model calibration is good: in 2017-2019 the mean predicted probability of model A is
0.023-0.024 against observed rates of 2.4-2.9%.

## Placebo and multiplicity tests

Four groups were tested (comparison, review_sti, environment, ambiguous). The environment group, the only
group with a positive point estimate (+0.017 within year x disease), did not beat either null: N1 (within-county
year shuffle) p = 0.20, N2 (outcome shuffle) p = 0.43; after Holm correction 0.81 and 1.00. No group was
supported. Among surrogate diseases the largest gain was Legionellosis (+0.043, rank p = 0.17). The
travel-associated group (Malaria) had 4 scored events and was left out of the placebo tests.

## Transfer, spatial validation, early warning and lead time

- **Held-out diseases (leave-one-disease-out):** mean gain of B over A -0.00006 (7 of 16 improved, sign-test
  p = 0.77); C +0.0025 (10 of 16, p = 0.23); D +0.0030 (12 of 16, unadjusted p = 0.038). The D result is not
  significant after allowing for the six transfer tests run (6 x 0.038 = 0.23) and the mean gain is negligible.
- **Held-out groups:** B +0.0025 (2 of 5 groups improved, p = 0.81); C +0.0005 (3 of 5, p = 0.50); D +0.0043
  (2 of 5, p = 0.81).
- **Spatial-block CV:** B better than A in 2 of 6 blocks (mean -0.007); C 2 of 6 (-0.002); D 1 of 6 (-0.018).
  Residual spatial autocorrelation (Moran's I) was slightly higher with mortality (B 0.160, p = 0.017; D 0.168,
  p = 0.013) than without (A 0.102, p = 0.075), consistent with mortality adding noise.
- **Early warning at matched false-alarm rate:** no gain. At 20% false alarms B caught 7.4 points fewer events
  than A (95% CI -14.3 to 0.0); at 5% and 10% the intervals included 0.
- **Lead time:** 40 permutation tests, none significant after Holm (smallest Holm p = 1.0; smallest unadjusted
  p = 0.073).

## Threshold sensitivity

The headline outcome uses a posterior-probability cut-off of 0.80. The same check at 0.70 and 0.90 gives the same
picture. Population raises within-year AUC at every cut-off, and mortality deviations never improve on it.

| Cut-off | Events scored | A without population | A (with population) | B (mortality deviations) minus A | Mortality levels + flags + population minus A |
|---|---|---|---|---|---|
| 0.70 | 91 | 0.551 | 0.650 | -0.025 | -0.031 |
| 0.80 | 81 | 0.524 | 0.625 | -0.012 | -0.002 |
| 0.90 | 50 | 0.558 | 0.612 | -0.012 | +0.008 |

These are point estimates from a simplified logistic model without confidence intervals, so they show direction only.
The one positive entry (levels at 0.90, +0.008) is far smaller than the sampling uncertainty reported for the main
pipeline (about +/-0.03) and is not treated as a finding. An earlier run of the same check on only 2019-2022
(15 events at 0.90) showed +0.034 for the same entry; it shrank to +0.008 on the full window, which is what noise on
very few events looks like. The 0.70 and 0.90 outcomes were checked with this stand-in only; the full INLA pipeline
was run on the 0.80 outcome.

## Methods finding: why a first pass looked positive

A first run used the original outcome (statewide trend dominated; 480 of 745 test events in 2020), mortality
levels, no population in model A and mortality missing-value flags. It gave B - A = +0.025 (CI -0.015 to
+0.065), C - A = +0.036, and the environment group passed both placebos after Holm (p = 0.005). Four things
explained it:

1. **County size.** In a fast logistic stand-in with the same design (test years 2017-2022, the same 81
   events), population alone raised within-year AUC from 0.524 to 0.625. Adding mortality deviations on top
   changed AUC by -0.012, and adding mortality levels plus missing flags on top of population by -0.002.
2. **Suppression flags.** Drug-overdose and suicide rates are missing for 43% of county-year rows and homicide
   for 66%, mostly in the smallest counties, so the missing flags were a small-county marker.
3. **The old county-swap placebo.** Swapping mortality between counties also destroys a fixed county trait such
   as size, so a size proxy passes that test. The year-shuffle null within each county does not.
4. **The outcome.** The original outcome contained the statewide yearly change.

The lesson for the write-up: always include the obvious confounder (here, population) in the baseline before
interpreting any gain, and check that any placebo can actually separate the hypothesis from that confounder.

## Stage 2 (exploratory): neighbour counties, context and static county traits

Pre-specified in a written plan committed before the run (repository tag stage2-plan-frozen; stage 1 frozen at tag stage1-freeze). Same test years and events as stage 1, so
this is exploratory. Model A is unchanged; B adds own plus neighbour-county mortality deviations; C adds
neighbour-county disease history, air quality, drought and static county traits (urban share, median age, log
density, rural-urban code); D adds all. Poverty and unemployment were not available (not in the AHRF extract before 2022).

| Result | Stage 1 | Stage 2 |
|---|---|---|
| B - A, pooled (95% CI) | +0.001 [-0.028, +0.034] | +0.006 [-0.030, +0.046] |
| C - A, pooled | +0.003 [-0.005, +0.013] | -0.011 [-0.048, +0.020] |
| D - A, pooled | +0.003 [-0.028, +0.037] | +0.007 [-0.037, +0.053] |
| Held-out diseases, better than A (sign p): B / C / D | 7/16 (0.77), 10/16 (0.23), 12/16 (0.04) | 6/16 (0.89), 8/16 (0.60), 11/16 (0.11) |
| Held-out groups, better than A: B / C / D | 2/5, 3/5, 2/5 | 1/5, 3/5, 0/5 |
| Spatial-block CV, blocks better than A: B / C / D | 2/6, 2/6, 1/6 | 1/6, 2/6, 1/6 |
| Early warning at 20% false alarms, hit-rate change: B / C / D | -7.4, -1.2, -6.2 points | -6.2, -1.2, -2.5 points (all CIs include 0) |
| Groups supported after Holm | 0 of 4 | 0 of 4 (environment N1 p_holm 0.64) |

Decision rule from the plan: both primary contrasts (B - A and C - A) have intervals that include 0, so nothing is
suggestive. One descriptive observation: residual spatial autocorrelation of the out-of-sample errors (Moran's I)
is 0.10 (p = 0.076) for A and 0.12 (p = 0.056) for B, but about 0 (p of 0.40-0.45) for C and D. The neighbour
and context features absorb the leftover spatial pattern, yet do not improve discrimination. This is a
hypothesis for new data, not a finding.

## Stage 3 (exploratory): cross-disease transition signatures

Pre-specified in a written plan committed before the run (repository tag stage3-plan-frozen). Same test years and 81 events, so
exploratory. Model A is unchanged. B adds the same county's cross-disease signature (number of other diseases
with an up-transition, and the share of other diseases, same-group diseases and other-group diseases with a rising
trend). C adds the same signature for adjacent counties. D adds both. The mortality block is not used in stage 3.

| Result | Stage 3 |
|---|---|
| B - A, pooled (95% CI) | +0.004 [-0.022, +0.031] |
| C - A, pooled | -0.003 [-0.020, +0.013] |
| D - A, pooled | -0.005 [-0.032, +0.023] |
| Held-out diseases, better than A (sign p): B / C / D | 7/16 (0.77), 5/16 (0.96), 7/16 (0.77) |
| Held-out groups, better than A: B / C / D | 2/5, 2/5, 1/5 |
| Spatial-block CV, blocks better than A (mean change): B / C / D | 3/6 (-0.006), 3/6 (-0.007), 2/6 (-0.014) |
| Early warning, hit-rate change at 10% false alarms: B / C / D | 0.0, +3.7, +1.2 points (all CIs include 0) |
| Groups supported after Holm | 0 of 4 (smallest N1 p_holm 0.61) |

Decision rule from the plan: both primary contrasts include 0, so nothing is suggestive. The comparison group, where
co-movement among enteric diseases would be expected, shows B - A = +0.010 [-0.027, +0.051], also not distinguishable
from 0. Descriptive only: the residual spatial autocorrelation of errors is 0.10 (p = 0.076) for A and B but 0.047
(p = 0.22) for C and D; the adjacent-county signature absorbs part of the spatial pattern without improving discrimination.
Steps 07 (lead time) and 13 (confound check) use mortality and are not meaningful in stage 3.

Across the three exploratory stages no contrast was positive, so correcting for the number of stages tried does not
change the conclusion. A possible reason for the weak cross-disease result (a hypothesis, not tested) is that the
local outcome removes the statewide yearly change, which also removes much of the shared year-to-year co-movement
between diseases.

## Advanced evaluation layer

Choices fixed in 19_advanced_evaluation_plan.md before running. Scripts 19-26 (the second layer, script 27, is the second advanced layer); numbers in 20_advanced_results.md and
21_supplementary_results.md; figures in 05_results/figures_report/. All use the stage 1 out-of-fold predictions and the
same 81 test events, so they describe how informative the null is; they are not new tests. The equivalence margins and the
supplementary diagnostics were chosen or added after seeing stage 1 results, so they are post-hoc.

- **How small an effect is ruled out.** The 90% interval for the gain of mortality (B) over A is [-0.026, +0.026] AUC: inside
  +/-0.03 but not inside +/-0.02. For context (C) it is [-0.004, +0.013], inside +/-0.02. The minimum detectable gain was about
  0.045 AUC (80% power). A signal-injection test (a synthetic predictor of known strength added to model A) detected gains of
  about 0.06 AUC in 80% of runs, and flagged a zero-strength predictor in 1 of 10 runs (expected for a 5% error rate with so
  few runs). Smaller gains could exist and would not have been detected.
- **Between-disease consistency.** Random-effects pooling of the per-disease gain of B over 12 diseases: -0.001 (95% CI -0.023 to
  +0.020), no detectable heterogeneity (I2 = 0%), 95% prediction interval -0.025 to +0.023.
- **A non-linear learner.** Gradient boosting with fixed settings (models A, B and D): B - A = -0.009 (95% CI -0.043 to +0.023); D - A = -0.009 (-0.054 to +0.033). The boosted model uses the all-cause mortality deviation (shuffling it lowers AUC by about 0.033), but
  using a feature is not the same as improving out-of-sample prediction.
- **Practical value.** Net-benefit differences against model A are indistinguishable from zero at alarm thresholds of 2-10%.
  Model A is well calibrated (slope 1.03, intercept 0.01) but barely beats predicting the average rate (Brier skill 0.005). Because a small change in AUC can hide decision value (Pencina et al., 2008; Baker et al., 2014), net benefit was assessed directly.
- **Specification curve.** Every estimate of the headline mortality gain lies around zero; only the confounded first pass (original outcome, no population baseline; +0.025 to +0.036) and the 0.70 stand-in cut-off (-0.025) sit outside +/-0.02, the first in the positive and the second in the negative direction.
- **County size.** Events per quartile of county size rise from 6 (smallest) to 19, 27 and 29 (largest), and discrimination of
  model A is 0.71, 0.61, 0.54 and 0.59. Posterior uncertainty of the trend falls with county size (Spearman -0.46), but event
  rates still differ by county size inside each uncertainty band, so detectability may explain only part of the population effect (the cells hold between 1 and 17 events, so this is descriptive).
- **Spatial and cross-disease detail.** County maps of events, predicted risk and observed-minus-predicted risk are in
  figures_report/map_*.png. The average correlation between diseases' county-year trend slopes is only 0.05 (range -0.07 to
  0.31), which fits the null cross-disease result of stage 3.
- **Reporting.** 20_tripod_probast.md maps the project to reporting-guideline topics and gives a risk-of-bias self-assessment
  (outcome and analysis domains rated high concern); 04_scripts/test_leakage.py checks the leakage rules in code.

## Second advanced layer

Script 27 (27_proper_scoring_and_influence.py, numbers in 23_proper_scoring_results.md, tables adv2_*.csv). Same
stage 1 out-of-fold predictions and 81 events; 1,000 county-cluster bootstrap draws. Added after the first advanced layer
and not part of 19_advanced_evaluation_plan.md, so it is post-hoc. AUC only looks at ranking; proper scoring rules also
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
  21_supplementary_results.md comes from a fit with a free slope and is not comparable to the fixed-slope intercept here.
- **Bootstrap probability statements** (shares of draws, not posterior probabilities). B - A lies inside +/-0.02 AUC in 81% of
  draws, inside +/-0.03 in 94% and inside +/-0.05 in 99%; the share of draws with a gain above 0.05 is 0.5%. For D - A the
  shares are 79%, 93% and 99%. C - A lies inside +/-0.02 in all draws.
- **Leave-one-disease-out.** Dropping each of the 16 diseases in turn moves B - A between -0.004 and +0.006, and no interval
  excludes zero, so no single disease drives or hides an effect. Four diseases (Listeriosis, Lyme Disease, Salmonellosis,
  Vibrio Infection) leave the estimate unchanged, consistent with having no scored events.

Taken together with the advanced evaluation layer, the proper-scoring and calibration checks agree with the AUC result: no evidence that
mortality improves out-of-sample prediction, within the limits of 81 events.

<!-- hiv-ext-patch -->

## HIV exploratory extension

HIV new diagnoses (California Office of AIDS, county-year, 2012-2023) were added as an
exploratory disease in the ambiguous scope, using the same transition method (negative
binomial RW2 + BYM2 + space-time interaction), threshold 0.80, and the same leave-future-out
evaluation. The extension adds 232 county-year rows and 4 test events (all scopes: n = 3944,
85 events; ambiguous: n = 464, 12 events). It is underpowered by design and is reported as exploratory.

| Scope | Model | Delta AUC vs A | 95% CI |
|---|---|---|---|
| all | B (+ mortality) | -0.007 | -0.039 to +0.023 |
| all | C (+ context) | +0.0004 | -0.007 to +0.009 |
| all | D (all) | -0.008 | -0.037 to +0.020 |
| ambiguous | B | -0.065 | -0.166 to +0.041 |
| ambiguous | C | -0.009 | -0.031 to +0.016 |
| ambiguous | D | -0.069 | -0.167 to +0.035 |

All intervals include 0. Brier score and log-loss are essentially identical across models
A-D (Brier about 0.0210, log-loss about 0.099). Adding HIV therefore does not change the
conclusion: mortality deviations give no out-of-sample gain. The more negative point estimate
for B in the ambiguous scope (-0.065, 12 events) is within sampling noise. No positive result
arose, so the placebo/surrogate step was not required for this run. Outputs: 05_results/tables/*__hiv17*
(repository tag hiv-ext).

<!-- hiv-ext-patch -->

# Discussion

## Principal findings
After controlling for county population, lagged within-county mortality deviations did not improve out-of-sample prediction of next-year
infectious-disease up-transitions in California counties (change in AUC +0.001, 95% CI -0.028 to +0.034; 81 scored events). Context features gave
+0.003 (-0.005 to +0.013) and the combined model +0.003 (-0.028 to +0.037). Placebo, held-out-disease, spatial-block, lead-time, gradient-boosting,
decision-curve and proper-scoring analyses agreed. The 90% interval for mortality lay inside +/-0.03 AUC, and the minimum detectable gain was about 0.045.
The group of sexually transmitted infections, the diseases most plausibly linked to drug use, gave B - A of +0.001. An earlier apparent gain
(+0.025) was explained by county size.

## Why mortality may add so little (hypotheses)
1. The baseline already carries the signal. Own disease history and population capture persistence and size; mortality deviations add little beyond them.
2. Detectability. An up-transition needs the posterior probability of a rise to reach 0.80. Posterior-probability rules have low sensitivity for modest
   excess risk or small expected counts (Richardson et al., 2004), so small counties rarely register events, and small counties are where mortality is
   most often suppressed (missing in 42% of drug-overdose, 46% of suicide and 70% of homicide rows). Bauer et al. (2023) likewise found larger forecast errors in rural ZIP codes and little gain from covariates once spatial dependence was modelled.
3. Exposure variation. The steepest rise in California drug-related mortality came after 2019, after fentanyl reached western markets late
   (Shover et al., 2020), mostly beyond the scored test years.
4. Proxy mismatch. For syphilis, individual-level links are strongest for methamphetamine and injection drug use (Kidd et al., 2019), so an opioid-heavy
   county mortality series may be a weak proxy.
5. Power. With 81 events, gains below about 0.045 AUC could not be reliably detected.

## Relation to earlier work
Vulnerability assessments rely on overdose mortality as an indicator (Van Handel et al., 2016) but were fitted and scored on the same data without validation
(Marks et al., 2021a), and the California Department of Public Health (CDPH) assessment for the same 58 counties states that its results are not predictive (CDPH, n.d.). Area-level studies report
positive associations (Sumetsky et al., 2019; Gezer et al., 2024, which also validated predictions on a later year) or mixed ones (Drewes et al., 2021,
significant only for urban gonorrhoea; Gonsalves et al., 2021 and 2023, local but not statewide). Gezer et al. compared community-level covariates as a block with a history-only model and found only a mild accuracy gain, which is compatible with our result, but none isolated the added predictive value of mortality for infection events against a population-adjusted baseline. Our result is compatible with earlier associations: an association can exist without adding predictive value.
Whether county size or detectability partly explains earlier associations is a hypothesis. Gonsalves et al. (2023) also used shuffled predictors and fatal automobile accidents as negative controls, the same logic as our placebo tests, and concluded that their lagged associations were not predictive of outbreaks.

## What the result does and does not cover
It covers next-year county up-transitions in 16 notifiable diseases, including chlamydia, gonorrhoea and early syphilis, in California. It does not cover hepatitis C or confirmatory HIV analysis (HIV was added only as an exploratory group with 4 test events), other states, shorter lags, finer geography, or operational early warning (the mortality series is published one to
two years late). Small effects below the detection limit are not excluded.

## Limitations specific to the HIV extension and missing data
HIV was included only as an exploratory group (Office of AIDS county series, 2012-2023; 4 test events in the leave-future-out
window, pooled B - A -0.007, 95% CI -0.039 to +0.023), and hepatitis C is absent because county data exist only for 2014-2016.
County mortality deviations were missing in 2% (all-cause), 42% (drug overdose), 46% (suicide) and 70% (homicide) of scored county-disease-years because of small-count suppression. Missing values were set to the mean after z-scoring, with no missing
indicator, so model B had the all-cause deviation for nearly all rows but no cause-specific mortality information for the 42-70% of rows with those values suppressed. This probably biases B - A toward the null. The null
result therefore applies to publicly available, suppressed county-level data and does not show that mortality has no
predictive value in principle.

## Implications
Overdose mortality should not be assumed to improve prediction of county infection transitions without out-of-sample testing. Baselines should include
population, and placebo tests should be able to separate the hypothesis from county size.

## Future work
Add hepatitis C and a fuller HIV series; test finer geography; extend the window beyond 2020 when events can be scored; use stimulant-specific and opioid-specific
mortality; pre-specify an urban-county stratum (Drewes et al.) with enough events; repeat with a decision-analytic endpoint.

# Limitations

- Low power: 81 scored events (2017-2020), 12 in the environment group and 8 in the ambiguous group. The study
  can exclude large effects only, not small ones.
- 2021-2022 have no local-outcome events (smoother edge effect), so they cannot be scored.
- Transition labels use hindsight (smoother fitted through 2023).
- Mortality is the final CDC series, published one to two years late: this is an association study, not an
  operational early-warning system.
- Changes after seeing results are all logged in 07_deviations_log.md and 04_prereg.md (retrospective record).
- The confound check uses a stand-in logistic model, not the INLA models; use it for direction only.
- The outcome depends on estimate precision. An "up-transition" needs the posterior probability of a rise to
  reach 0.80, so counties with noisy estimates rarely cross it: median slope uncertainty is 0.134 in the smallest
  population quartile and 0.080 in the largest, and local-outcome event rates rise from 1.1% to 2.8% across the
  same quartiles. Part of the predictive value of population therefore reflects detectability, not only
  epidemiology. Posterior-probability decision rules are known to be conservative when counts are small
  (Richardson et al., 2004). Uncertainty also widens at the end of the series (median 0.085 in 2019, 0.117 in
  2023), which is the likely reason 2021-2023 have no events.
- Threshold sensitivity (tau 0.70 and 0.90) was run with the fast stand-in only (no intervals, no full INLA run), as a
  robustness check; the headline analysis is tau 0.80.
- The drug-linked hypothesis (H2) could not be tested because no county-level drug-linked series is available
  (Part B of the prereg is the plan for that).
- The equivalence margins (+/-0.02, 0.03, 0.05), the supplementary diagnostics and the second advanced layer (script 27) were chosen after seeing stage 1 results, so they are post-hoc. Equivalence within +/-0.02 holds only for the context contrast (C - A); for mortality (B - A) and the combined model (D - A) it holds within +/-0.03.
- Bootstrap shares reported in the second advanced layer are frequentist approximations to a region-of-practical-equivalence statement, not posterior probabilities.
- The 16 diseases include three STIs (chlamydia, gonorrhoea, early syphilis) but not hepatitis C or HIV, the infections most often linked to opioid-related outbreaks, so the result does not address bloodborne outbreaks.
- County mortality counts are suppressed by CDC WONDER when fewer than 10 deaths occur (rates from fewer than 20 deaths are flagged unreliable), and suppression falls mostly on small, rural counties. Missing mortality therefore tracks county size (see the section on why a first pass looked positive) and weakens the exposure where events are hardest to detect. Whether limited year-to-year variation in California mortality during 2017-2020 also reduced the signal is a hypothesis, not a finding: fentanyl reached western illicit drug markets late (Shover et al., 2020) and California's steepest rise in drug-related mortality came after 2019, mostly after the scored test years.

# Conclusion

After controlling for county population and using within-county lagged mortality deviations, county mortality
adds no detectable out-of-sample predictive value for next-year infectious-disease up-transitions in California
(pooled change in AUC +0.001, 95% CI -0.028 to +0.034). No disease group survived placebo and Holm correction,
the result did not transfer to held-out diseases or groups, spatial-block validation did not improve, and
lead-time tests were null. An earlier apparent gain was explained by county size. An exploratory second stage adding neighbouring counties' disease history and mortality, air quality, drought and static county traits also showed no gain (pooled C - A -0.011, 95% CI -0.048 to +0.020). A third exploratory stage using cross-disease transition signatures of the same and adjacent counties also showed no gain (pooled B - A +0.004, 95% CI -0.022 to +0.031; C - A -0.003, 95% CI -0.020 to +0.013). Two advanced evaluation layers (equivalence and power, gradient boosting, decision curves, proper scoring rules and calibration intervals) also showed no gain (sections 11 and 12). With 81 scored events the study has low power: gains below about 0.045 AUC could not be reliably detected, so small effects cannot be excluded.

# Code and data availability

Code, processed data, logs and the pre-registration are at https://github.com/pranoti711/project3 (tag final-draft-v22). File names mentioned in the text (for example 13_stage2_plan.md) refer to documents in this repository.

# References

::: {#refs}
:::
