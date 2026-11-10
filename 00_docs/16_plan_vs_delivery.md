# 16_plan_vs_delivery.md - What was decided at the start vs what exists now (2026-11-08; updated 2026-11-09)

> Update 2026-11-09: stage 3 (cross-disease signatures, route 2 of the extension options) was run and is also a null result.
> The cross-disease row below is now DONE (exploratory, no gain). The drug-linked series and the precision-independent
> outcome remain the only untested routes.

Status key: DONE = built and run. PARTIAL = built with a limit. NOT DONE = missing. BLOCKED = data not available.
Sources for "what was decided": the Final Combined Version, Phase 0 audit, novelty matrix, and your decision notes
(full plan, no compromise on novelty, methods or technology; get the extra data rather than a reduced version).

## A. Design and methods
| Planned item | Status | Notes |
|---|---|---|
| Predictive (not causal) county-year panel, California | DONE | 58 counties, 2001-2023, 16 of 56 diseases pass the data gate |
| Transition outcome T(i,d,t+1) from NB RW2 + BYM2 + space-time model (R-INLA) | DONE | Outcome depends on estimate precision and uses hindsight smoothing (limitations written) |
| Models A (history), B (+ mortality), C (+ context), D (all) | DONE | A changed after results: population added (logged) |
| Leave-future-out validation | DONE | Only 2017-2020 are scoreable (81 events); 2021-2023 have no events |
| Spatial-block CV, residual Moran's I | DONE | |
| Unseen-disease and unseen-group validation | DONE | |
| Matched false-alarm early warning | DONE | |
| Lead-time model | DONE | 0 of 40 tests significant after Holm |
| Surrogate-disease null and placebos | PARTIAL | Uses a simple logistic stand-in, not the INLA models |
| Simulation before real results | PARTIAL | Done, but assumed 5 mortality years; the real data have 23. Re-run not done |
| Multiplicity control (Holm) | DONE | |
| Neighbouring-county features | DONE (exploratory) | Stage 2; no gain |
| Environmental layer | DONE | Air quality and drought only |
| Geographic layer | DONE | BYM2 space effect, adjacency, spatial blocks, static density and urban share |
| Socioeconomic layer | PARTIAL / BLOCKED | Poverty and unemployment only exist in the AHRF extract from 2022, so not usable for 2017-2020. Census SAIPE and BLS LAUS files would fill this (optional files are supported by `05c`) |
| NCHS model-based mortality sensitivity | NOT DONE | Listed in the plan as sensitivity |

## B. Data decisions
| Planned item | Status | Notes |
|---|---|---|
| CDC WONDER county mortality, 10+ years | DONE | 23 usable overlap years; suppression is a problem (43-66% missing in small counties) |
| County drug-linked disease series (hepatitis B/C, injection-related infections) | BLOCKED | Your decision was to get this data, not reduce the design. It has not been obtained. The drug-linked group is empty, so the central drug-linked vs comparison contrast was never tested |
| Pre-set disease groups | PARTIAL | Four groups planned; five used (two review groups added by draft rules). Drug-linked group empty |

## C. Prediction, space and time detail (outputs that exist)
| Output | Exists | Gap |
|---|---|---|
| Per-county, per-year out-of-sample predictions | `05_results/tables/oof_predictions_lfo.csv` | No county maps or per-county write-up |
| Calibration by year | `calibration_by_year.csv` | No calibration plot |
| Results by disease and by group | validation and score tables | Not summarised in a figure |
| Figures | 3 files (early warning, lead-time histogram, placebo null) | No map of events or errors, no per-year AUC plot, no figure of the population-versus-mortality finding |
If you meant a specific analysis I have not listed (the message said "spectormetail"), tell me which one.

## D. Paper and literature
| Item | Status |
|---|---|
| Literature search log | PARTIAL: 8 web searches logged; PubMed and Scholar rows (9-12) empty |
| references.bib | PARTIAL: 5 entries marked VERIFY, candidates listed, none read in full |
| Overleaf paper skeleton (RQ1-RQ3) | NOT DONE in the folder: `06_paper/overleaf` is empty, so the text lives only in Overleaf |
| Results write-up | DONE (`10_results_writeup.md`), not yet a manuscript |

## E. Novelty: what was intended vs what the evidence supports
| Intended claim | Evidence | Verdict |
|---|---|---|
| Mortality carries a leading signal for infectious-disease transitions (cross-domain) | B - A = +0.001 [-0.028, +0.034]; stage 2 also null | NOT SUPPORTED |
| The signal is specific to drug-linked diseases | Group empty | UNTESTED |
| Neighbouring counties and context add predictive value | Stage 2: C - A = -0.011 [-0.048, +0.020] | NOT SUPPORTED (exploratory) |
| Cross-disease signatures of the same and adjacent counties predict transitions (stage 3, exploratory) | Pooled B - A +0.004 [-0.022, +0.031], C - A -0.003 [-0.020, +0.013] | NOT SUPPORTED (exploratory) |
| Rigorous leakage-safe evaluation protocol for cross-domain signals | Built and run | SUPPORTED |
| Placebo and surrogate nulls plus confound checks prevent false positives | Caught a false signal in the first pass | SUPPORTED |
| Pooled AUC can mislead | Observed (pooled 0.355 vs within-cell 0.72) | SUPPORTED, but a known issue |
| Omitted size baseline plus county-swap placebo can create a false signal | First pass vs corrected run | SUPPORTED, worth reporting |

**Honest bottom line.** Your original aim was no compromise on novelty, methods and technology. Methods and
technology were delivered. The discovery-level novelty (a cross-domain signal) was not found: the best-supported
answer is a null. What remains novel, to my knowledge and subject to the literature search being finished, is the
specific combination of design plus the documented null plus the county-size case study. Do not write "first" or
"novel" until the PubMed and Scholar rows in `03_phase0_part2_novelty.md` are filled and read.

## F. Decisions you need to make
1. **Framing.** (a) Finish as a rigorous null-result and methods project (about 1-2 days of writing and the literature
   work), or (b) extend to restore discovery-level novelty.
2. **If (b), the three routes that exist:**
   - Get the county drug-linked series (county hepatitis or HIV data, or injection-related hospitalisations) and
     test the original drug-linked contrast. Availability of these data must be checked.
   - Return to your Proposal 3 idea: cross-disease transition signatures (does a rise in one disease predict a rise in
     another, with neighbouring counties and context). This needs no new data; the 16 diseases are already in the panel.
     Run the literature check first.
   - Fix the outcome's dependence on estimate precision (effect-size-based events) and re-run, to see whether any
     signal appears when detectability is not tied to county size.
3. **Remaining small items:** NCHS sensitivity, re-run the simulation with 23 years, result figures and maps.

## G. Update after stage 3 (2026-11-10)
Three exploratory extensions (neighbour counties and county traits, then cross-disease signatures) followed the stage 1
mortality analysis, and none showed a gain. The data-available routes to a discovery-level result are now used up.
What is left: (1) a county drug-linked series, which needs new data, and (2) an outcome that does not depend on
estimate precision, which needs the transition model re-run. Otherwise the project is a null-result and methods
study; finish it as that.

