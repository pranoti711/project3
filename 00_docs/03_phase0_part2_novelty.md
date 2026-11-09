# 03_phase0_part2_novelty.md - Novelty matrix, search log, additions

**Important.** This file lists what the project *intends* to claim and what the evidence currently allows
(v2, updated 2026-11-05 after the corrected run). The literature search log below is a template: no prior-work
citation is asserted here, because none has been verified. **Do not use the words "novel", "first" or "new" for
any claim until the search log is filled from your own search.**

## 1. Literature search log (to complete)

Searches 1-8 were run on 2026-11-06 with a web search engine (snippets and abstracts only, no full texts read).
Everything in the "closest prior work" column must be verified. The PubMed searches (rows 9-12) are still to do.

| # | Date | Engine | Query (short) | Closest prior work found | Difference from this project |
|---|---|---|---|---|---|
| 1 | 2026-11-06 | web | county vulnerability HIV/HCV overdose indicators | Van Handel et al. 2016 (JAIDS); Oklahoma county index (Wendelboe et al. 2024, PLoS ONE, to verify) | cross-sectional ranking, not out-of-sample prediction of transitions |
| 2 | 2026-11-06 | web | forecasting county infection using overdose deaths | Rhode Island neighbourhood ML (to verify); national county overdose forecasting (Marks et al., Lancet Public Health, to verify) | targets overdose or hepatitis risk, not 16-disease up-transitions |
| 3 | 2026-11-06 | web | Bayesian change / increase detection, posterior probability | Richardson et al. 2004 (EHP) | method background for the 0.70-0.80 rule |
| 4 | 2026-11-06 | web | AUC pooled across clusters, within-cluster discrimination | within-cluster concordance literature (to verify) | known method; used as practice |
| 5 | 2026-11-06 | web | county overdose and syphilis/gonorrhea/chlamydia | Drewes et al. 2020 (IJERPH); Abara et al. 2019 (to verify) | association study, Northeast, adjusted null for most STIs |
| 6 | 2026-11-06 | web | negative control outcome / falsification | Lipsitch et al. 2010 | method background for surrogate-disease test |
| 7 | 2026-11-06 | web | external data streams vs autoregressive baseline | dengue and influenza nowcasting papers (to verify) | other diseases and data streams |
| 8 | 2026-11-06 | web | leave-future-out cross-validation | Burkner et al. 2020 | method background |
| 9 | 2026-11-08 | web | shared component / joint multi-disease spatio-temporal models | Knorr-Held and Best 2001 (JRSS-A 164:73-85); Gomez-Rubio et al. (joint spatio-temporal analysis of multiple diseases, to verify); Retegui et al. 2024 (arXiv, to verify) | descriptive joint disease mapping (mostly cancers); not predictive early warning of transition events |
| 10 | 2026-11-08 | web | one disease as leading indicator for another, lead-lag | Cheng, Buckeridge, Bloom 2007 (JAMIA 14:76-85); recent PMC recommendations for leading-indicator analysis (to verify); recent arXiv paper on cross-disease transfer learning for forecasting (to verify) | association vs predictive lead is already distinguished; cross-disease forecasting is an active area, so any cross-disease claim is NOT new by itself |
| 11 | todo | PubMed | county mortality AND infectious disease AND prediction | | |
| 12 | todo | PubMed | drug overdose AND hepatitis OR HIV AND county forecasting | | |
| 13 | todo | Scholar | cross-domain surveillance signals mortality leading indicator | | |
| 14 | todo | Scholar | California county notifiable disease transition early warning | | |

## 2. Novelty matrix - claim vs evidence

| # | Intended claim | Evidence in this project | Status |
|---|---|---|---|
| N1 | Mortality series (overdose, suicide, homicide) carry a leading signal for county infectious-disease up-transitions | B - A = +0.001 (CI -0.028, +0.034); 0/40 lead-time tests; 0/4 groups supported | **Not supported** |
| N2 | The signal is specific to drug-linked diseases | Group empty (no county data) | **Untestable now** |
| N3 | A leakage-safe, matched-false-alarm early-warning evaluation for cross-domain signals | Implemented (06-12); no gain found | Method delivered, effect null |
| N4 | Placebo and surrogate-disease nulls plus simulation guard against false positives | Implemented; the placebos plus the confound check removed the first-pass apparent signals | **Supported (as a methods contribution)** |
| N5 | Pooled AUC across years/diseases can create spurious cross-domain "signals" and even AUC < 0.5 | Observed in run 1 (pooled 0.355, within-cell 0.72) | **Supported, worth reporting** |
| N6 | Context features (AQI, drought) give a small spatial-transfer gain | In the corrected run C is better in 2 of 6 blocks, LOGO 3/5, not significant | **Withdrawn** (the earlier lead came from the baseline lacking population) |
| N7 | An apparent mortality signal can come entirely from county size: missing-value flags act as a small-county marker, and a county-swap placebo cannot detect this | First pass B - A = +0.025 and a "supported" group; population alone raised AUC 0.524 to 0.625; mortality deviations on top gave -0.012 (stand-in model, 81 events) | **Supported by your own results; worth reporting as a methods lesson** |
| N8 | Neighbouring counties' history, mortality and static traits improve prediction | Stage 2 (exploratory): pooled C - A -0.011 [-0.048, +0.020], B - A +0.006 [-0.030, +0.046]; residual spatial autocorrelation removed by C/D without a gain in AUC | **Not supported (exploratory)** |
| N9 | Cross-disease transition signatures of the same and adjacent counties predict a disease's next up-transition (stage 3) | Planned in `17_stage3_plan.md`; not yet run | **Open (exploratory)**; co-movement within source-sharing disease groups is expected and is not itself novel |

## 3. Additions to the base design (components as built)

| Component | Where | Status |
|---|---|---|
| Simulation before real results (false-positive rate and power) | `04_simulation.py` | Done with a stand-in test; assumed 5 mortality years; **re-run with 23 years not done** |
| Disease-group test (drug-linked vs comparison) | `03`, `11` | Group empty |
| Lead-time model | `07_leadtime.R` | Done, null |
| Leave-future-out validation | `06` | Done (4 scored test years) |
| Unseen-disease / unseen-group validation | `08` | Done, null |
| Spatial-block CV and residual Moran's I | `10` | Done, null |
| Matched false-alarm early warning | `09` | Done, null |
| Surrogate-disease and placebo nulls | `11` | Done (stand-in logistic, not INLA) |
| Confound check | `13` | Done |
| Multiplicity control | `12_multiplicity.py` | Done |
| NCHS model-based sensitivity | - | Not run |

## 4. What can honestly be claimed today
1. A reproducible, leakage-aware pipeline and evaluation protocol (N3).
2. A documented null: no out-of-sample predictive value of county mortality for disease up-transitions in
   California counties under this design and power (N1), with low power (81 scored events).
3. Two methodological warnings backed by your own runs: pooled AUC can mislead (N5), and an omitted size baseline
   plus a county-swap placebo can manufacture a "supported" signal (N7).

Do not claim a cross-domain discovery. Do not claim priority ("first", "novel") until section 1 is completed
from a real literature search.
