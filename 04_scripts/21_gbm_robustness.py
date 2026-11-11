"""
21_gbm_robustness.py - is the null caused by using (generalised) linear models? (advanced evaluation layer)

Refits the same comparison with gradient boosting (scikit-learn HistGradientBoostingClassifier), which can find
non-linear effects and interactions between mortality and disease, group or county size. Same leave-future-out
design as the main analysis: for test year T the model is trained on rows with year < T only.

Models   A_gbm : own history (lag_rate, trend_slope, prev_up) + pop_log + disease + group
         B_gbm : A_gbm + the four lagged within-county mortality deviations
         D_gbm : B_gbm + air quality + drought
Reads    02_data/processed/<input>  (default model_table_local.csv, the headline outcome table)
Writes   05_results/tables/adv_gbm_scores.csv, adv_gbm_delta.csv, adv_gbm_importance.csv, adv_gbm_oof.csv
Run      python 04_scripts/21_gbm_robustness.py [--boot 500] [--n_test 6]

Mortality features are missing for many small counties; gradient boosting handles missing values natively (no flags,
no filling). Hyper-parameters are fixed in advance (shallow trees, small learning rate); nothing is tuned on the test years.
"""
import argparse
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adv_common import Cells, find_root, summarize  # noqa: E402

warnings.filterwarnings("ignore")
HIST = ["lag_rate", "trend_slope", "prev_up", "pop_log"]
DEV = ["allcause_dev", "drug_od_dev", "suicide_dev", "homicide_dev"]
CTX = ["aqi_median", "drought_dsci"]


def make_model(seed):
    return HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200, min_samples_leaf=40,
                                          l2_regularization=1.0, random_state=seed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="model_table_local.csv")
    ap.add_argument("--boot", type=int, default=500)
    ap.add_argument("--n_test", type=int, default=6)
    ap.add_argument("--repeats", type=int, default=10)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    root = find_root()
    tab = root / "05_results" / "tables"
    df = pd.read_csv(root / "02_data" / "processed" / a.input, dtype={"fips": str})
    df["fips"] = df["fips"].str.zfill(5)
    df = df[df["up"].notna()].reset_index(drop=True)
    df["up"] = df["up"].astype(int)
    miss = [c for c in DEV if c not in df]
    if miss:
        raise SystemExit(f"{a.input} lacks {miss}. Rebuild it with 05b_build_model_table.py (v2).")
    df["disease_code"] = df["disease"].astype("category").cat.codes
    df["group_code"] = df["group"].astype("category").cat.codes
    CAT = ["disease_code", "group_code"]
    specs = {"A": HIST + CAT, "B": HIST + DEV + CAT, "D": HIST + DEV + CTX + CAT}
    years = sorted(df["year"].unique())[-a.n_test:]
    preds = {k: np.full(len(df), np.nan) for k in specs}
    keep_B = {}
    for T in years:
        tr = (df["year"] < T).values
        te = (df["year"] == T).values
        if df.loc[tr, "up"].sum() < 10:
            continue
        for k, cols in specs.items():
            cat_mask = [c in CAT for c in cols]
            m = make_model(a.seed).set_params(categorical_features=cat_mask)
            m.fit(df.loc[tr, cols].values.astype(float), df.loc[tr, "up"].values)
            Xte = df.loc[te, cols].values.astype(float)
            preds[k][te] = m.predict_proba(Xte)[:, 1]
            if k == "B":
                keep_B[T] = (m, Xte, np.flatnonzero(te), cols)
        print(f"test year {T}: done")
    cells = Cells(df, preds, years=years)
    sc = {k: cells.strat_auc(k) for k in specs}
    draws = cells.bootstrap_deltas("A", ["B", "D"], B=a.boot, seed=a.seed)
    rows = []
    for k in ("B", "D"):
        s = summarize(draws[k], sc[k] - sc["A"])
        rows.append(dict(contrast=f"{k}_gbm - A_gbm", delta=s["delta"], ci95_lo=s["lo"], ci95_hi=s["hi"]))
    pd.DataFrame([dict(model=f"{k}_gbm", strat_auc=v) for k, v in sc.items()]).to_csv(tab / "adv_gbm_scores.csv", index=False)
    pd.DataFrame(rows).to_csv(tab / "adv_gbm_delta.csv", index=False)
    print({k: round(v, 4) for k, v in sc.items()})
    print(pd.DataFrame(rows).round(4).to_string(index=False))

    # permutation importance of the mortality features in B_gbm (drop in strat AUC when a column is shuffled)
    rng = np.random.default_rng(a.seed)
    base = cells.strat_auc("B")
    imp = []
    for j, f in enumerate(DEV):
        drops = []
        for _ in range(a.repeats):
            p2 = preds["B"].copy()
            for T, (m, Xte, rows_idx, cols) in keep_B.items():
                X2 = Xte.copy()
                col = cols.index(f)
                X2[:, col] = rng.permutation(X2[:, col])
                p2[rows_idx] = m.predict_proba(X2)[:, 1]
            c2 = Cells(df, {"B": p2}, years=years)
            drops.append(base - c2.strat_auc("B"))
        imp.append(dict(feature=f, mean_auc_drop=float(np.mean(drops)), sd=float(np.std(drops, ddof=1))))
    pd.DataFrame(imp).to_csv(tab / "adv_gbm_importance.csv", index=False)
    print(pd.DataFrame(imp).round(4).to_string(index=False))
    out = df.loc[df["year"].isin(years), ["fips", "year", "disease", "group", "up"]].copy()
    for k in specs:
        out[f"p_{k}"] = preds[k][out.index]
    out.to_csv(tab / "adv_gbm_oof.csv", index=False)


if __name__ == "__main__":
    main()
