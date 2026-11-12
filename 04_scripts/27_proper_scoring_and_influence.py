"""
27_proper_scoring_and_influence.py - second advanced layer, still on existing results only (no refits, no new data).

Why: AUC only looks at ranking. Proper scoring rules (log-loss, Brier) also see calibration and are more sensitive,
so they are a stricter test of "does mortality add anything?". This script adds four checks:
  1. Log-loss and Brier differences of B, C, D versus A, with 95% county-cluster bootstrap intervals.
  2. Calibration slope and intercept of A and B with bootstrap intervals (is B over-confident?).
  3. Bootstrap probability that the AUC difference lies inside / beyond a margin (a bootstrap approximation to a
     Bayesian ROPE statement, NOT a true posterior; it ignores any prior).
  4. Leave-one-disease-out influence on the B - A AUC difference (is one disease driving or hiding anything?).
Reads  05_results/tables/oof_predictions_lfo.csv
Writes 05_results/tables/adv2_*.csv and 00_docs/23_proper_scoring_results.md
Run    python 04_scripts/27_proper_scoring_and_influence.py [--boot 1000]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adv_common import Cells, find_root, load_oof, logit, summarize, wide_preds  # noqa: E402

EPS = 1e-6


def wmean(x, w):
    return float(np.sum(w * x) / np.sum(w))


def logloss_vec(y, p):
    p = np.clip(p, EPS, 1 - EPS)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def brier_vec(y, p):
    return (y - p) ** 2


def wlogit_fit(X, y, w, offset=None, iters=50):
    """Weighted logistic regression by Newton/IRLS. X includes an intercept column. Returns coefficients."""
    off = np.zeros(len(y)) if offset is None else offset
    beta = np.zeros(X.shape[1])
    for _ in range(iters):
        eta = np.clip(X @ beta + off, -30, 30)
        mu = 1 / (1 + np.exp(-eta))
        W = w * mu * (1 - mu) + 1e-12
        grad = X.T @ (w * (y - mu))
        H = X.T @ (X * W[:, None]) + 1e-8 * np.eye(X.shape[1])
        step = np.linalg.solve(H, grad)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-8:
            break
    return beta


def calib(y, p, w):
    """Calibration slope (logit(p) as only predictor) and intercept with slope fixed at 1 (calibration-in-the-large)."""
    lp = logit(np.clip(p, EPS, 1 - EPS))
    slope = wlogit_fit(np.c_[np.ones(len(y)), lp], y, w)[1]
    intercept = wlogit_fit(np.ones((len(y), 1)), y, w, offset=lp)[0]
    return slope, intercept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=27)
    a = ap.parse_args()
    root = find_root()
    tab = root / "05_results" / "tables"
    df, preds = wide_preds(load_oof(root))
    y = df["up"].values.astype(float)
    models = list(preds)
    counties = pd.Index(sorted(df["fips"].unique()))
    cid = counties.get_indexer(df["fips"])
    nC = len(counties)
    rng = np.random.default_rng(a.seed)

    # ---- 1 and 2: proper scores and calibration, cluster bootstrap on counties -------------------------------
    ll = {m: logloss_vec(y, preds[m]) for m in models}
    br = {m: brier_vec(y, preds[m]) for m in models}
    ones = np.ones(len(y))
    point = {("logloss", m): wmean(ll[m], ones) for m in models}
    point.update({("brier", m): wmean(br[m], ones) for m in models})
    cal_point = {m: calib(y, preds[m], ones) for m in ("A", "B") if m in preds}

    draws_ll = {m: np.empty(a.boot) for m in models if m != "A"}
    draws_br = {m: np.empty(a.boot) for m in models if m != "A"}
    draws_cal = {m: np.empty((a.boot, 2)) for m in cal_point}
    for b in range(a.boot):
        pick = rng.integers(0, nC, nC)
        w = np.bincount(pick, minlength=nC).astype(float)[cid]
        l0, b0 = wmean(ll["A"], w), wmean(br["A"], w)
        for m in draws_ll:
            draws_ll[m][b] = wmean(ll[m], w) - l0
            draws_br[m][b] = wmean(br[m], w) - b0
        for m in cal_point:
            draws_cal[m][b] = calib(y, preds[m], w)

    rows = []
    for m in draws_ll:
        for name, dr, d0 in (("logloss", draws_ll[m], point[("logloss", m)] - point[("logloss", "A")]),
                             ("brier", draws_br[m], point[("brier", m)] - point[("brier", "A")])):
            s = summarize(dr, d0)
            rows.append(dict(score=name, contrast=f"{m}-A", delta=s["delta"], ci95_lo=s["lo"], ci95_hi=s["hi"],
                             se=s["se"], share_boot_worse=float(np.mean(dr > 0))))
    score_df = pd.DataFrame(rows)
    score_df.to_csv(tab / "adv2_proper_scores.csv", index=False)

    crow = []
    for m, (s0, i0) in cal_point.items():
        lo_s, hi_s = np.nanpercentile(draws_cal[m][:, 0], [2.5, 97.5])
        lo_i, hi_i = np.nanpercentile(draws_cal[m][:, 1], [2.5, 97.5])
        crow.append(dict(model=m, slope=s0, slope_lo=lo_s, slope_hi=hi_s,
                         intercept_in_the_large=i0, int_lo=lo_i, int_hi=hi_i))
    cal_df = pd.DataFrame(crow)
    cal_df.to_csv(tab / "adv2_calibration_ci.csv", index=False)

    # ---- 3: bootstrap probability statements for the AUC differences ------------------------------------------
    cells = Cells(df, preds)
    others = [m for m in models if m != "A"]
    pt = {o: cells.strat_auc(o) - cells.strat_auc("A") for o in others}
    dr = cells.bootstrap_deltas("A", others, B=a.boot, seed=a.seed)
    prow = []
    for o in others:
        d = dr[o]
        prow.append(dict(contrast=f"{o}-A", delta=pt[o],
                         p_inside_pm0_02=float(np.mean(np.abs(d) < 0.02)),
                         p_inside_pm0_03=float(np.mean(np.abs(d) < 0.03)),
                         p_inside_pm0_05=float(np.mean(np.abs(d) < 0.05)),
                         p_gain_above_0_02=float(np.mean(d > 0.02)),
                         p_gain_above_0_05=float(np.mean(d > 0.05)),
                         p_loss_below_minus_0_02=float(np.mean(d < -0.02))))
    prob_df = pd.DataFrame(prow)
    prob_df.to_csv(tab / "adv2_bootstrap_probabilities.csv", index=False)

    # ---- 4: leave-one-disease-out influence on B - A -----------------------------------------------------------
    diseases = sorted(df["disease"].unique())
    irow = []
    for dis in diseases:
        keep = (df["disease"] != dis).values
        sub = df[keep].reset_index(drop=True)
        sp = {m: preds[m][keep] for m in ("A", "B")}
        c2 = Cells(sub, sp)
        d0 = c2.strat_auc("B") - c2.strat_auc("A")
        dd = c2.bootstrap_deltas("A", ["B"], B=max(200, a.boot // 4), seed=a.seed)["B"]
        s = summarize(dd, d0)
        irow.append(dict(left_out=dis, delta_B_minus_A=d0, ci95_lo=s["lo"], ci95_hi=s["hi"]))
    infl = pd.DataFrame(irow)
    infl.to_csv(tab / "adv2_leave_one_disease_out.csv", index=False)

    # ---- report ---------------------------------------------------------------------------------------------
    f = lambda x: f"{x:+.4f}"
    md = ["# 23_proper_scoring_results.md - auto-generated by 04_scripts/27_proper_scoring_and_influence.py (do not edit by hand)\n",
          "Exploratory, built only on the saved out-of-sample predictions. Not new hypothesis tests.\n",
          "## 1. Proper scoring rules (lower is better; positive difference = model is worse than A)\n",
          "| score | contrast | delta | ci95_lo | ci95_hi | share of bootstrap draws worse than A |", "|---|---|---|---|---|---|"]
    for r in score_df.itertuples():
        md.append(f"| {r.score} | {r.contrast} | {f(r.delta)} | {f(r.ci95_lo)} | {f(r.ci95_hi)} | {r.share_boot_worse:.2f} |")
    md += ["", "## 2. Calibration with county-cluster 95% intervals\n",
           "| model | slope | slope 95% | intercept in the large | intercept 95% |", "|---|---|---|---|---|"]
    for r in cal_df.itertuples():
        md.append(f"| {r.model} | {r.slope:.3f} | {r.slope_lo:.3f} to {r.slope_hi:.3f} | {r.intercept_in_the_large:+.3f} | {r.int_lo:+.3f} to {r.int_hi:+.3f} |")
    md += ["", "A slope below 1 means predictions are too extreme (over-confident). Intercept in the large is the average miscalibration with slope fixed at 1.\n",
           "## 3. Bootstrap probability statements for the AUC difference\n",
           "These are shares of county-cluster bootstrap draws, a frequentist approximation to a ROPE statement. They are not posterior probabilities.\n",
           "| contrast | delta | P(|d|<0.02) | P(|d|<0.03) | P(|d|<0.05) | P(gain>0.02) | P(gain>0.05) | P(loss>0.02) |", "|---|---|---|---|---|---|---|---|"]
    for r in prob_df.itertuples():
        md.append(f"| {r.contrast} | {f(r.delta)} | {r.p_inside_pm0_02:.2f} | {r.p_inside_pm0_03:.2f} | {r.p_inside_pm0_05:.2f} | {r.p_gain_above_0_02:.2f} | {r.p_gain_above_0_05:.2f} | {r.p_loss_below_minus_0_02:.2f} |")
    rng_d = infl["delta_B_minus_A"]
    md += ["", "## 4. Leave-one-disease-out influence on B - A (AUC)\n",
           f"Across the {len(infl)} leave-one-out fits the B - A difference ranges from {f(rng_d.min())} to {f(rng_d.max())}; "
           f"{int((infl['ci95_lo'] > 0).sum())} intervals exclude zero on the positive side and {int((infl['ci95_hi'] < 0).sum())} on the negative side.\n",
           "| disease left out | delta B-A | ci95_lo | ci95_hi |", "|---|---|---|---|"]
    for r in infl.itertuples():
        md.append(f"| {r.left_out} | {f(r.delta_B_minus_A)} | {f(r.ci95_lo)} | {f(r.ci95_hi)} |")
    (root / "00_docs" / "23_proper_scoring_results.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(score_df.round(4).to_string(index=False))
    print(cal_df.round(3).to_string(index=False))
    print(prob_df.round(3).to_string(index=False))
    print(f"leave-one-disease-out B-A range: {rng_d.min():+.4f} to {rng_d.max():+.4f}")
    print("Wrote 00_docs/23_proper_scoring_results.md and 05_results/tables/adv2_*.csv")


if __name__ == "__main__":
    main()
