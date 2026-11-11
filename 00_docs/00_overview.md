# Project 3 - Do county mortality data predict infectious-disease up-transitions in California?

One-page overview. Exact figures are in `10_results_writeup.md` and, for the advanced layer, `20_advanced_results.md` and `21_supplementary_results.md`.

## Question and design
Does adding county mortality (overdose, suicide, homicide, all-cause) improve next-year prediction of county up-transitions in
16 notifiable diseases (58 counties, 2001-2023), beyond each disease's own history and county population? Leakage-safe design:
Bayesian transition model (R-INLA: negative binomial, RW2 trend, BYM2 space), then models A-D evaluated with leave-future-out
validation, within year x disease AUC, county-cluster bootstrap, spatial-block and held-out-disease validation, matched false-alarm
early warning, placebo and surrogate-disease nulls, Holm correction.

## Findings
| Question | Answer |
|---|---|
| Does mortality improve prediction? | No: pooled change in AUC +0.001 (95% CI -0.028 to +0.034), 81 test events |
| Where did an early positive result come from? | County size: population alone lifts AUC from 0.52 to 0.63; mortality adds nothing on top |
| Do neighbouring counties and county traits help? (stage 2, exploratory) | No (C - A -0.011, CI -0.048 to +0.020) |
| Do cross-disease signatures help? (stage 3, exploratory) | No (B - A +0.004, CI -0.022 to +0.031) |
| How small an effect is ruled out? | The 90% interval for B - A is [-0.026, +0.026]: inside +/-0.03, not inside +/-0.02; minimum detectable effect about 0.045 AUC (a signal-injection test detected only gains of about 0.06 in 80% of runs) |
| Does it differ by disease? | No evidence (random-effects pooled -0.001 over 12 diseases, I^2 0%) |
| Does a non-linear learner find a signal? | No (gradient boosting B - A -0.004, CI -0.044 to +0.033) |
| Is any model useful in practice? | No demonstrated net-benefit gain over the baseline; baseline Brier skill is only 0.005 |
| Is the outcome tied to county size? | Yes in part: events per county-size quartile rise 6, 19, 27, 29; uncertainty falls with size (rho -0.46) but does not explain all of it |

## What this project shows
Leakage control in forecasting evaluation; Bayesian spatio-temporal modelling; honest handling of a false-positive result (confound check,
placebo redesign, pre-registered stages committed to git before each run); uncertainty quantification beyond p-values (equivalence, power,
meta-analysis); reproducibility (one-command runner, unit tests for leakage rules, fixed seeds).

## Limits
Low power (81 events); annual county data and 2% event rate; transition labels use hindsight smoothing; the drug-linked hypothesis was untested
for lack of county-level data; stages 2-3 and the advanced layer are exploratory/robustness, run on the same test years.

## Reproduce
See `12_run_order.md` (pipeline) and `tools/run_advanced.ps1` (advanced layer, runs the tests first). Reporting map and risk-of-bias self-assessment: `22_tripod_probast.md`. Environment: `23_environment.md`.
