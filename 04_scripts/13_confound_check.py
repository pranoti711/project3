"""
13_confound_check.py - is the 'mortality gain' just county size?

Fast logistic stand-in (same leave-future-out design as 11; NOT the INLA models, so read direction,
not exact AUC). All AUCs are within year x disease, pair-count weighted.

Specs
  A_nopop   : own history WITHOUT population   (what the old model A was)
  A         : own history + pop_log            (new baseline)
  B_dev     : A + lagged within-county mortality deviations (new model B)
  B_level   : A_nopop + mortality LEVELS + missing flags   (old model B)
  B_level+pop : A + mortality LEVELS + missing flags

Reading it: if B_level beats A_nopop but B_level+pop does not beat A, the old gain was county size.
Mortality "adds value" only if B_dev beats A.

Run : python 04_scripts/13_confound_check.py [--input model_table.csv] [--n_test 6] [--drop_years 2020]
Out : 05_results/tables/confound_check<tag>.csv
"""
import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore")
HIST_NOPOP = ["lag_rate", "trend_slope", "prev_up"]
LEVELS = ["allcause_rate", "drug_od_rate", "suicide_rate", "homicide_rate"]
DEVS = ["allcause_dev", "drug_od_dev", "suicide_dev", "homicide_dev"]


def find_root():
    p = Path.cwd().resolve()
    for q in [p, *p.parents]:
        if (q / "04_scripts").is_dir():
            return q
        if (q / "project3" / "04_scripts").is_dir():
            return q / "project3"
    raise SystemExit("Run from inside project3.")


def auc(y, p):
    n1 = int(y.sum()); n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return np.nan
    r = rankdata(p)
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def strat_auc(df, p, years):
    num = den = 0.0
    for (_, _), g in df[df["year"].isin(years)].groupby(["year", "disease"]):
        y = g["up"].values; n1 = y.sum(); n0 = len(y) - n1
        if n1 == 0 or n0 == 0 or np.isnan(p[g.index]).any():
            continue
        w = n1 * n0; num += auc(y, p[g.index]) * w; den += w
    return num / den if den else np.nan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="model_table.csv")
    ap.add_argument("--n_test", type=int, default=6)
    ap.add_argument("--drop_years", type=int, nargs="*", default=[])
    ap.add_argument("--tag", default="", help="suffix for the output file, e.g. _t070")
    a = ap.parse_args()
    root = find_root()
    df = pd.read_csv(root / "02_data" / "processed" / a.input)
    df = df[df["up"].notna()].reset_index(drop=True)
    df["up"] = df["up"].astype(int)
    for c in DEVS:
        if c not in df:
            raise SystemExit(f"{a.input} lacks {c}. Rebuild with 05b_build_model_table.py (v2).")
    y = df["up"].values
    years = [t for t in sorted(df["year"].unique())[-a.n_test:] if t not in a.drop_years]
    gm = pd.get_dummies(df["group"]).values.astype(float)
    dis = pd.get_dummies(df["disease"]).values.astype(float)
    miss = np.column_stack([df[v].isna().values.astype(float) for v in LEVELS[1:]])
    names = ["A_nopop", "A", "B_dev", "B_level", "B_level+pop"]
    pred = {k: np.full(len(df), np.nan) for k in names}
    for T in years:
        tr = (df["year"] < T).values; te = (df["year"] == T).values
        if y[tr].sum() < 10:
            continue

        def z(v):
            x = df[v].astype(float).values
            m, s = np.nanmean(x[tr]), np.nanstd(x[tr]); s = s if s and not np.isnan(s) else 1.0
            return np.nan_to_num((x - m) / s)

        H0 = np.column_stack([z(v) for v in HIST_NOPOP]); pop = z("pop_log")[:, None]
        inter = lambda X: np.column_stack([X[:, [j]] * gm for j in range(X.shape[1])])
        D = inter(np.column_stack([z(v) for v in DEVS]))
        L = inter(np.column_stack([z(v) for v in LEVELS]))
        specs = {"A_nopop": [H0, dis], "A": [H0, pop, dis], "B_dev": [H0, pop, D, dis],
                 "B_level": [H0, L, miss, dis], "B_level+pop": [H0, pop, L, miss, dis]}
        for k, parts in specs.items():
            X = np.column_stack(parts)
            pred[k][te] = LogisticRegression(C=0.5, max_iter=800).fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
    sc = {k: strat_auc(df, v, years) for k, v in pred.items()}
    rows = [dict(spec=k, strat_auc=sc[k], delta_vs_A=sc[k] - sc["A"], delta_vs_A_nopop=sc[k] - sc["A_nopop"])
            for k in names]
    out = pd.DataFrame(rows)
    tab = root / "05_results" / "tables"; tab.mkdir(parents=True, exist_ok=True)
    out.to_csv(tab / f"confound_check{a.tag}.csv", index=False)
    print(f"Test years used: {years}")
    print(out.round(3).to_string(index=False))
    print("\nIf B_level > A_nopop but B_level+pop <= A, the old mortality gain was county size.")
    print("Mortality adds value only if B_dev - A is clearly > 0 (then confirm with 06/11/12).")


if __name__ == "__main__":
    main()
