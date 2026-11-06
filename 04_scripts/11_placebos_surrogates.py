"""
11_placebos_surrogates.py - is the mortality gain (model B minus model A) bigger than
what chance and the pipeline itself would produce?

Uses a fast logistic-regression stand-in for the INLA models (same features, same
leave-future-out design) so thousands of refits are affordable. Compare to 06 for
direction, not for exact AUC values.

Statistic (CHANGED): delta_AUC(group) = AUC(B) - AUC(A), where AUC is computed inside each
(test year x disease) cell and averaged with pair-count weights (the same 'auc_strat' used in
p3_common.R). The old pooled-over-years AUC is still written as observed_delta_auc_pooled for
comparison, because pooling across years and diseases let year-level base-rate drift create
spurious gains (and AUC < 0.5) in the first run.

Nulls
  N1 year-permutation (CHANGED): each county's own mortality-deviation series is shuffled across its
     years. Keeps the county's level and variance, breaks the timing. The old county-swap null could
     not tell mortality from a time-invariant county trait such as size, so it is no longer used.
  N2 outcome-shuffle: up-transitions shuffled across counties within disease-year
  N3 surrogate diseases: per-disease delta_AUC of the comparison group (diseases with no
     plausible mortality link) vs the drug_linked / ambiguous / other diseases (rank test)

Input : 02_data/processed/model_table.csv  (or --input)
Output: 05_results/tables/placebo_group_tests.csv, placebo_disease_delta.csv,
        05_results/figures/placebo_null.png   (a --tag adds a suffix to all three names)
Run   : python 04_scripts/11_placebos_surrogates.py [--perms 1000] [--n_test 6] [--input FILE] [--tag orig]
Then  : python 04_scripts/12_multiplicity.py   (Holm correction across groups; reads the untagged file)
"""
import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
# CHANGED (v2): population in the baseline; mortality = lagged within-county deviations (see 05b)
HIST = ["lag_rate", "trend_slope", "prev_up", "pop_log"]
MORT = ["allcause_dev", "drug_od_dev", "suicide_dev", "homicide_dev"]
# STAGE 2 (exploratory): P3_STAGE2=1 adds neighbour-county mortality deviations (one pooled slope each)
import os
if os.environ.get("P3_STAGE2") == "1":
    MORT = MORT + ["nbr_allcause_dev", "nbr_drug_od_dev", "nbr_suicide_dev", "nbr_homicide_dev"]


def find_root():
    p = Path.cwd().resolve()
    for q in [p, *p.parents]:
        if (q / "04_scripts").is_dir():
            return q
        if (q / "project3" / "04_scripts").is_dir():
            return q / "project3"
    raise SystemExit("Run from inside project3 or its parent folder.")


def load(root, input_name):
    path = Path(input_name)
    path = path if path.is_absolute() else root / "02_data" / "processed" / input_name
    df = pd.read_csv(path)
    for c in ["county", "year", "disease", "group", "up"]:
        if c not in df:
            raise SystemExit(f"{path.name} lacks column {c}")
    df = df[df["up"].notna()].copy()
    df["up"] = df["up"].astype(int)
    df["county"] = df["county"].astype(str)
    df["group"] = df["group"].astype(str)
    print(f"Loaded {path.name}: {len(df):,} rows, {df['disease'].nunique()} diseases, event rate {df['up'].mean():.4f}")
    return df.reset_index(drop=True)


def design(df, spec, train, hist, mort, groups):

    def z(v):
        x = df[v].astype(float).values
        m, s = np.nanmean(x[train]), np.nanstd(x[train])
        s = s if (s and not np.isnan(s)) else 1.0
        return np.nan_to_num((x - m) / s)

    parts = [z(v)[:, None] for v in hist]
    if spec == "B":
        for v in mort:
            zz = z(v)
            if v.startswith("nbr_"):
                parts.append(zz[:, None])
                continue
            for g in groups:
                parts.append((zz * (df["group"].values == g))[:, None])
    parts.append(pd.get_dummies(df["disease"]).values.astype(float))
    return np.hstack(parts)


def lfo_predict(df, spec, test_years, hist, mort, groups, y):
    p = np.full(len(df), np.nan)
    for T in test_years:
        tr = (df["year"] < T).values
        te = (df["year"] == T).values
        if y[tr].sum() < 10 or te.sum() == 0:
            continue
        X = design(df, spec, tr, hist, mort, groups)
        clf = LogisticRegression(C=0.5, max_iter=500).fit(X[tr], y[tr])
        p[te] = clf.predict_proba(X[te])[:, 1]
    return p


# ---------------------------------------------------------------- AUC helpers
def auc_fast(y, p):
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return np.nan
    r = rankdata(p)
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def build_cells(df, test_years):
    """One entry per (test year, disease) cell: (year, disease, group, row positions).
    A disease belongs to exactly one group, so every cell lies inside one group."""
    sub = df[df["year"].isin(test_years)]
    return [(yr, dis, g["group"].iloc[0], g.index.values) for (yr, dis), g in sub.groupby(["year", "disease"])]


def strat_delta(cells, pA, pB, y, by="group", min_events=5):
    """Pair-count-weighted mean over cells of AUC(B) - AUC(A). Returns {key: (delta, events, group)}."""
    acc = {}
    for yr, dis, grp, ix in cells:
        if np.isnan(pA[ix]).any() or np.isnan(pB[ix]).any():
            continue
        yy = y[ix]
        n1 = int(yy.sum())
        n0 = len(yy) - n1
        if n1 == 0 or n0 == 0:
            continue
        w = n1 * n0
        s = acc.setdefault(grp if by == "group" else dis, [0.0, 0.0, 0, grp, 0])  # sumA, sumB, events, group, weight
        s[0] += auc_fast(yy, pA[ix]) * w
        s[1] += auc_fast(yy, pB[ix]) * w
        s[2] += n1
        s[4] += w
    out = {}
    for k, (sa, sb, ev, grp, w) in acc.items():
        if ev >= min_events:
            out[k] = ((sb - sa) / w, ev, grp)
    return out


def pooled_group_deltas(df, pA, pB, y):
    """OLD statistic (pooled AUC over years and diseases) - kept only for comparison."""
    ok = ~np.isnan(pA) & ~np.isnan(pB)
    out = {}
    for g in sorted(df["group"].unique()):
        m = ok & (df["group"].values == g)
        if y[m].sum() >= 5 and (1 - y[m]).sum() >= 5:
            out[g] = roc_auc_score(y[m], pB[m]) - roc_auc_score(y[m], pA[m])
    return out


def permute_years_within_county(df, mort, rng):
    """N1: shuffle each county's mortality-deviation series across that county's years."""
    cy = df[["county", "year"]].drop_duplicates().copy()
    cy["src_year"] = cy.groupby("county")["year"].transform(lambda s: rng.permutation(s.values))
    mt = (df[["county", "year"] + mort].drop_duplicates(["county", "year"])
          .rename(columns={"year": "src_year"}))
    d2 = (df.drop(columns=mort)
            .merge(cy, on=["county", "year"], how="left")
            .merge(mt, on=["county", "src_year"], how="left"))
    d2.index = df.index
    return d2


def shuffle_outcome(df, rng):
    return df.groupby(["disease", "year"])["up"].transform(lambda s: rng.permutation(s.values)).values


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perms", type=int, default=1000)
    ap.add_argument("--n_test", type=int, default=6)
    ap.add_argument("--input", default="model_table.csv")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    sfx = f"_{args.tag}" if args.tag else ""

    root = find_root()
    tabs, figs = root / "05_results" / "tables", root / "05_results" / "figures"
    tabs.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    df = load(root, args.input)
    hist = [c for c in HIST if c in df]
    mort = [c for c in MORT if c in df]
    if not hist or not mort:
        raise SystemExit("Need at least one HIST and one MORT column.")
    groups = sorted(df["group"].unique())
    test_years = sorted(df["year"].unique())[-args.n_test:]
    y = df["up"].values
    rng = np.random.default_rng(2026)
    cells = build_cells(df, test_years)
    print("Test years:", test_years, "| (year x disease) cells:", len(cells))

    # observed
    pA = lfo_predict(df, "A", test_years, hist, mort, groups, y)
    pB = lfo_predict(df, "B", test_years, hist, mort, groups, y)
    obs_full = strat_delta(cells, pA, pB, y, by="group")
    obs = {g: v[0] for g, v in obs_full.items()}
    obs_pooled = pooled_group_deltas(df, pA, pB, y)
    print("Observed delta AUC (B - A), stratified:", {k: round(v, 4) for k, v in obs.items()})
    print("Observed delta AUC (B - A), OLD pooled :", {k: round(v, 4) for k, v in obs_pooled.items()})

    # N1 within-county year permutation
    n1 = {g: [] for g in obs}
    for i in range(args.perms):
        d2 = permute_years_within_county(df, mort, rng)
        pBp = lfo_predict(d2, "B", test_years, hist, mort, groups, y)
        for g, v in strat_delta(cells, pA, pBp, y, by="group").items():
            if g in n1:
                n1[g].append(v[0])
        if (i + 1) % 25 == 0:
            print(f"  N1 {i+1}/{args.perms}", flush=True)

    # N2 outcome shuffle
    n2 = {g: [] for g in obs}
    for i in range(args.perms):
        ys = shuffle_outcome(df, rng)
        d3 = df.copy()
        d3["up"] = ys
        pAs = lfo_predict(d3, "A", test_years, hist, mort, groups, ys)
        pBs = lfo_predict(d3, "B", test_years, hist, mort, groups, ys)
        for g, v in strat_delta(cells, pAs, pBs, ys, by="group").items():
            if g in n2:
                n2[g].append(v[0])
        if (i + 1) % 25 == 0:
            print(f"  N2 {i+1}/{args.perms}", flush=True)

    rows = []
    for g, o in obs.items():
        a1, a2 = np.array(n1[g]), np.array(n2[g])
        rows.append(dict(group=g, observed_delta_auc=o,
                         observed_delta_auc_pooled=obs_pooled.get(g, np.nan),
                         events=obs_full[g][1],
                         n1_null_mean=a1.mean() if len(a1) else np.nan,
                         n1_p=(1 + (a1 >= o).sum()) / (len(a1) + 1) if len(a1) else np.nan,
                         n2_null_mean=a2.mean() if len(a2) else np.nan,
                         n2_p=(1 + (a2 >= o).sum()) / (len(a2) + 1) if len(a2) else np.nan,
                         perms=args.perms))
    gt = pd.DataFrame(rows)
    gt.to_csv(tabs / f"placebo_group_tests{sfx}.csv", index=False)

    # N3 surrogate diseases: per-disease delta AUC (stratified over test years)
    dis_full = strat_delta(cells, pA, pB, y, by="disease")
    dd = pd.DataFrame([dict(disease=k, group=v[2], events=v[1], delta_auc=v[0]) for k, v in sorted(dis_full.items())])
    dd.to_csv(tabs / f"placebo_disease_delta{sfx}.csv", index=False)
    ref = dd[dd.group == "comparison"]["delta_auc"].values if len(dd) else np.array([])
    print("\n=== Surrogate-disease test (rank vs comparison-group diseases) ===")
    if len(ref) >= 4:
        for _, r in dd[dd.group != "comparison"].iterrows():
            p = (1 + (ref >= r.delta_auc).sum()) / (len(ref) + 1)
            print(f"{r.disease:35s} group={r.group:14s} dAUC={r.delta_auc:+.4f} rank_p={p:.3f}")
    else:
        print("Fewer than 4 testable comparison diseases; surrogate test not informative.")

    # figure for the drug_linked group if present
    focus = "drug_linked" if "drug_linked" in obs else (list(obs)[0] if obs else None)
    if focus and len(n1[focus]) and len(n2[focus]):
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(n1[focus], bins=25, alpha=0.6, label="N1 year-permutation")
        ax.hist(n2[focus], bins=25, alpha=0.6, label="N2 outcome-shuffle")
        ax.axvline(obs[focus], color="k", lw=2, label="observed")
        ax.set_xlabel("delta AUC (B - A), within year x disease")
        ax.set_title(f"Null distributions: {focus}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(figs / f"placebo_null{sfx}.png", dpi=150)

    pd.set_option("display.width", 200)
    print("\n=== Group tests ===")
    print(gt.round(4).to_string(index=False))
    print("\nTreat a group as supported only if the observed gain beats N1 AND N2 and the surrogate "
          "\ndiseases do not show the same gain. Correct for the number of groups tested "
          "(python 04_scripts/12_multiplicity.py).")


if __name__ == "__main__":
    main()
