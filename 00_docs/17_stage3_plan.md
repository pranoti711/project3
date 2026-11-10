# 17_stage3_plan.md - Stage 3 (EXPLORATORY): cross-disease transition signatures

Commit this file to git BEFORE running stage 3, then write the hash here: ee54e5fbbdf490186ed910e1e616dd589607dc23.

## Status
Stages 1 and 2 are frozen (commits bbc9ebe and 75268e1) and are null results. Stage 3 returns to your Proposal 3:
cross-disease epidemiological transition signatures for early warning. It needs no new data. The 2017-2020 test
years and their 81 events were already seen in stages 1 and 2, so every stage 3 result is **exploratory**.
Stage 3 is the last stage; no further feature sets are added after it.

## Question (fixed before running)
S3: Is a county's next-year up-transition in disease d predicted by what the other diseases in the same county, and in
adjacent counties, were doing in the prediction year, beyond disease d's own history and county population?

## Features (built by `04_scripts/05d_add_crossdisease_features.py`, all known at year t, disease d always excluded)
| Block | Columns | Used in |
|---|---|---|
| Same-county signature | xd_n_up, xd_share_rising, xd_share_rising_same, xd_share_rising_other | model B (replaces the mortality block) and D |
| Adjacent-county signature | nbr_xd_n_up, nbr_xd_share_rising | model C and D |

All of these get one pooled slope. Model A is unchanged (own history + population). Run with `P3_STAGE3=1`.

## Contrasts and decision rule (fixed now)
- Primary contrasts: B - A (same-county signature) and C - A (adjacent-county signature); within year x disease AUC,
  county-cluster bootstrap (500 repetitions); Holm correction over these 2 contrasts.
- A contrast counts as suggestive only if its CI excludes 0 AND the group-level placebo tests (within-county year
  shuffle N1 and outcome shuffle N2) do not reject it as noise.
- Descriptive only: group-level and single-disease gains.
- Disease groups share sources, seasons and reporting systems (for example the enteric diseases), so co-movement
  within a group is expected and not a new finding. Any positive result must be reported by group, and the
  novelty claim limited to the transition-event early-warning design, not to co-movement itself.

## Known limits (state them in any write-up)
- Same 81 test events as before. Power is low.
- The "up-transition" feature (prev_up) comes from the smoother that uses all years (hindsight), as for the own history.
- Steps 07 (lead time) and 13 (confound check) still use mortality, so their stage 3 output is not meaningful and is ignored.
- Log messages and table headings still say "mortality" for the block that holds the cross-disease signature.

## Outcome (added after the run, 2026-11-09; nothing above this line was changed)
Run with `P3_STAGE3=1` on `model_table_stage3.csv`. Primary contrasts: B - A = +0.004 (95% CI -0.022 to +0.031);
C - A = -0.003 (-0.020 to +0.013). Both intervals include 0, so by the rule above neither is suggestive, and no group
beat the placebos after Holm correction. Stage 3 is an exploratory null. Tables: `05_results_stage3/` and
`00_docs/18_stage3_results_tables.md`. As stated in the plan, this is the last stage.
