# 19_advanced_evaluation_plan.md - Advanced evaluation layer (robustness and uncertainty, NOT new hypotheses)

Commit this file to git before running the scripts, then write the hash here: **FILL commit hash**.

## Purpose
Stages 1-3 are frozen null results. This layer does not look for new effects. It answers four questions a reviewer
will ask, using the same test rows and 81 events:
1. How small an effect can this study rule out? (equivalence and power)
2. Does mortality help some diseases and not others? (random-effects meta-analysis)
3. Is the null an artefact of using linear models? (gradient boosting, fixed in advance)
4. Would any model be useful in practice? (decision-curve analysis)
Plus figures and county maps, unit tests for the leakage rules, and a one-command runner.

## Fixed choices (set now, before running)
- Equivalence margins: +/-0.02, +/-0.03, +/-0.05 AUC. A contrast is "practically zero" at a margin if its 90% county-cluster
  bootstrap interval lies inside it.
- Minimum detectable effect: 2.8 x the bootstrap standard error of B - A (80% power, two-sided alpha 0.05).
- Meta-analysis: DerSimonian-Laird random effects over diseases with at least one scoreable cell; bootstrap SE per disease.
- Gradient boosting: HistGradientBoostingClassifier, max_depth 3, learning rate 0.05, 200 iterations, min leaf 40, L2 = 1,
  random_state 2026. No tuning on test years. Models A_gbm (history + population + disease + group), B_gbm (+ mortality deviations),
  D_gbm (+ air quality, drought). Same leave-future-out split (train on years before the test year).
- Decision curves: alarm thresholds 0.01-0.15; net-benefit differences versus A reported at 0.02, 0.03, 0.05, 0.08, 0.10.
- Nothing in this layer is added to the headline analysis. It is reported separately as robustness.

## Interpretation rules
- An interval inside a margin supports "no effect larger than the margin"; it does not prove zero.
- If the boosted model improves over its baseline with an interval excluding 0, that is a new exploratory lead, to be reported as such
  and not as a confirmed finding.
- Permutation importance shows what a model uses, not what improves out-of-sample prediction.

## Outputs
Tables `05_results/tables/adv_*.csv`; figures `05_results/figures_report/`; auto-generated report `00_docs/20_advanced_results.md`.
