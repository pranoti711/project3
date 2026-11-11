"""
standin.py - shared helpers for the fast logistic "stand-in" analyses (scripts 19, 20, 21 and the tests).

The stand-in has the same leave-future-out design as the main pipeline: for each test year T the model is fitted on
rows with year < T and predicts rows with year == T. AUC is computed within year x disease cells and averaged with
pair-count weights. Uncertainty comes from a county-cluster bootstrap (counties resampled with replacement).
It is NOT the INLA model; use it for direction and for validity checks, not for headline numbers.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

HIST = ["lag_rate", "trend_slope", "prev_up"]
DEVS = ["allcause_dev", "drug_od_dev", "suicide_dev", "homicide_dev"]


def find_root():
    p = Path.cwd().resolve()
    for q in [p, *p.parents]:
        if (q / "04_scripts").is_dir():
            return q
        if (q / "project3" / "04_scripts").is_dir():
            return q / "project3"
    raise SystemExit("Run from inside project3.")


def load_table(name="model_table_local.csv", root=None):
    root = root or find_root()
    df = pd.read_csv(root / "02_data" / "processed" / name, dtype={"fips": str})
    df["fips"] = df["fips"].str.zfill(5)
    df = df[df["up"].notna()].reset_index(drop=True)
    df["up"] = df["up"].astype(int)
    return df


def fit_predictions(df, years, spec="A", extra=None, C=0.5):
    """spec 'A' = own history + population; 'B' = A + lagged mortality deviations (group-specific slopes).
    extra: optional 1-D array added as one more pooled feature (used for the positive control)."""
    y = df["up"].values
    gm = pd.get_dummies(df["group"]).values.astype(float)
    dis = pd.get_dummies(df["disease"]).values.astype(float)
    pred = np.full(len(df), np.nan)
    for T in years:
        tr = (df["year"] < T).values
        te = (df["year"] == T).values
        if y[tr].sum() < 10 or te.sum() == 0:
            continue

        def z(x):
            x = np.asarray(x, dtype=float)
            m, s = np.nanmean(x[tr]), np.nanstd(x[tr])
            s = s if s and not np.isnan(s) else 1.0
            return np.nan_to_num((x - m) / s)

        parts = [np.column_stack([z(df[v].values) for v in HIST]), z(df["pop_log"].values)[:, None], dis]
        if spec == "B":
            parts.append(np.column_stack([z(df[v].values)[:, None] * gm for v in DEVS]))
        if extra is not None:
            parts.append(z(extra)[:, None])
        X = np.column_stack(parts)
        pred[te] = LogisticRegression(C=C, max_iter=800).fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
    return pred


class Cells:
    """Pre-computed year x disease cells so the weighted AUC and the bootstrap are fast."""

    def __init__(self, df, years, strata=None):
        self.df = df
        self.cells = []
        keys = ["year", "disease"] + ([strata] if strata else [])
        sub = df[df["year"].isin(years)]
        self.counties = pd.Index(df["fips"].unique())
        self.cidx = self.counties.get_indexer(df["fips"].values)
        for _, g in sub.groupby(keys):
            yy = g["up"].values
            if yy.sum() == 0 or yy.sum() == len(yy):
                continue
            self.cells.append((g.index.values, yy))

    @staticmethod
    def _wauc(y, p, w):
        u, inv = np.unique(p, return_inverse=True)
        wpos = np.bincount(inv, weights=w * y, minlength=len(u))
        wneg = np.bincount(inv, weights=w * (1 - y), minlength=len(u))
        den = wpos.sum() * wneg.sum()
        if den <= 0:
            return np.nan, 0.0
        cumneg = np.cumsum(wneg) - wneg
        return float((wpos * (cumneg + 0.5 * wneg)).sum() / den), den

    def strat_auc(self, p, mult=None):
        w_all = np.ones(len(self.df)) if mult is None else mult[self.cidx]
        num = den = 0.0
        for idx, yy in self.cells:
            a, d = self._wauc(yy, p[idx], w_all[idx])
            if d > 0 and not np.isnan(a):
                num += a * d
                den += d
        return num / den if den else np.nan

    def boot_delta(self, p_b, p_a, n_boot=200, rng=None):
        rng = rng or np.random.default_rng(1)
        n = len(self.counties)
        out = np.empty(n_boot)
        for i in range(n_boot):
            mult = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
            out[i] = self.strat_auc(p_b, mult) - self.strat_auc(p_a, mult)
        return out
