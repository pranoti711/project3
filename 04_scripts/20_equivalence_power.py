"""
20_equivalence_power.py - how small an effect can this study rule out? (advanced evaluation layer)

Uses the saved out-of-sample predictions of the main INLA models (05_results/tables/oof_predictions_lfo.csv). No refit.

1. Equivalence: for each contrast (B-A, C-A, D-A) the 90% county-cluster bootstrap interval is compared with margins
   delta = 0.02, 0.03, 0.05 AUC. If the whole interval lies inside (-delta, +delta) the effect is "practically zero" at that margin.
2. Heterogeneity: per-disease change in AUC (B-A) with a bootstrap standard error, then a DerSimonian-Laird
   random-effects meta-analysis (pooled effect, tau^2, I^2, 95% prediction interval).
3. Power: with the observed bootstrap standard error (SE) of B-A, the power to detect a true AUC gain d is
   Phi(d/SE - 1.96) + Phi(-d/SE - 1.96) (two-sided, alpha = 0.05). The minimum detectable effect at 80% power is
   about 2.8 x SE. This says how large a gain this study could have found, not that no smaller gain exists.

Outputs (05_results/tables/): adv_equivalence.csv, adv_per_disease_delta.csv, adv_meta_analysis.csv, adv_power_curve.csv
Run : python 04_scripts/20_equivalence_power.py [--boot 1000]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adv_common import Cells, expit, find_root, load_oof, logit, summarize, wide_preds  # noqa: E402


def dl_meta(est, se):
    """DerSimonian-Laird random-effects pooling. est, se: arrays. Returns dict."""
    est, se = np.asarray(est), np.asarray(se)
    w = 1 / se**2
    fixed = np.sum(w * est) / np.sum(w)
    Q = np.sum(w * (est - fixed) ** 2)
    k = len(est)
    c = np.sum(w) - np.sum(w**2) / np.sum(w)
    tau2 = max(0.0, (Q - (k - 1)) / c) if k > 1 else 0.0
    wr = 1 / (se**2 + tau2)
    pooled = np.sum(wr * est) / np.sum(wr)
    se_p = np.sqrt(1 / np.sum(wr))
    I2 = max(0.0, (Q - (k - 1)) / Q) * 100 if Q > 0 else 0.0
    # approximate 95% prediction interval (t distribution with k-2 df, normal if k<=3)
    from scipy import stats
    tcrit = stats.t.ppf(0.975, k - 2) if k > 3 else 1.96
    pi = tcrit * np.sqrt(tau2 + se_p**2)
    return dict(k=k, pooled=pooled, se=se_p, lo=pooled - 1.96 * se_p, hi=pooled + 1.96 * se_p,
                tau2=tau2, I2=I2, pred_lo=pooled - pi, pred_hi=pooled + pi, Q=Q)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20)
    a = ap.parse_args()
    root = find_root()
    tab = root / "05_results" / "tables"
    o = load_oof(root)
    df, preds = wide_preds(o)
    cells = Cells(df, preds)
    names = [m for m in ["B", "C", "D"] if m in preds]
    base_auc = {m: cells.strat_auc(m) for m in preds}
    print("Strat AUC:", {k: round(v, 4) for k, v in base_auc.items()})

    # ---- 1. equivalence
    draws = cells.bootstrap_deltas("A", names, B=a.boot, seed=a.seed)
    rows = []
    for m in names:
        d90 = np.percentile(draws[m], [5, 95])
        s = summarize(draws[m], base_auc[m] - base_auc["A"])
        row = dict(contrast=f"{m}-A", delta=s["delta"], ci95_lo=s["lo"], ci95_hi=s["hi"], se=s["se"],
                   ci90_lo=d90[0], ci90_hi=d90[1])
        for dm in (0.02, 0.03, 0.05):
            row[f"equiv_within_{dm:.2f}"] = bool(d90[0] > -dm and d90[1] < dm)
        rows.append(row)
    eq = pd.DataFrame(rows)
    eq.to_csv(tab / "adv_equivalence.csv", index=False)
    print(eq.round(4).to_string(index=False))

    # ---- 2. per-disease changes and random-effects meta-analysis (B - A)
    prow = []
    for dis in sorted(df["disease"].unique()):
        if not any(c["disease"] == dis for c in cells.cells):
            continue
        dd = cells.bootstrap_deltas("A", ["B"], B=min(a.boot, 500), seed=a.seed + 1, disease=dis)["B"]
        point = cells.strat_auc("B", disease=dis) - cells.strat_auc("A", disease=dis)
        grp = df.loc[df["disease"] == dis, "group"].iloc[0]
        ev = int(df.loc[df["disease"] == dis, "up"].sum())
        prow.append(dict(disease=dis, group=grp, events=ev, delta=point, se=np.nanstd(dd, ddof=1)))
    pdl = pd.DataFrame(prow)
    pdl = pdl[np.isfinite(pdl["se"]) & (pdl["se"] > 0)].reset_index(drop=True)
    pdl.to_csv(tab / "adv_per_disease_delta.csv", index=False)
    meta = dl_meta(pdl["delta"].values, pdl["se"].values)
    pd.DataFrame([meta]).to_csv(tab / "adv_meta_analysis.csv", index=False)
    print("Meta-analysis (B - A over diseases):", {k: round(v, 4) for k, v in meta.items()})

    # ---- 3. analytic power curve for the B - A contrast
    from scipy import stats
    se_obs = eq.loc[eq["contrast"] == "B-A", "se"].iloc[0]
    grid = np.round(np.arange(0.0, 0.1001, 0.005), 3)
    power = stats.norm.cdf(grid / se_obs - 1.96) + stats.norm.cdf(-grid / se_obs - 1.96)
    pw = pd.DataFrame(dict(true_delta=grid, power=power))
    pw.to_csv(tab / "adv_power_curve.csv", index=False)
    mde80 = 2.8 * se_obs
    pd.DataFrame([dict(observed_se=se_obs, mde_80pct_power=mde80, mde_90pct_power=3.24 * se_obs)]).to_csv(
        tab / "adv_mde.csv", index=False)
    print(pw.iloc[[0, 2, 4, 6, 8, 10, 12, 16, 20]].round(3).to_string(index=False))
    print(f"Observed SE of B-A: {se_obs:.4f}.  Minimum detectable effect: {mde80:.3f} AUC (80% power), "
          f"{3.24 * se_obs:.3f} AUC (90% power)")


if __name__ == "__main__":
    main()
