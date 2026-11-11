"""
adv_common.py - shared helpers for the advanced evaluation layer (scripts 20-24).

Everything here works on a long table with one row per (county, year, disease, model) and the columns
  fips, year, disease, up (0/1 outcome), plus predictions.  AUC is always computed WITHIN year x disease cells and
averaged with pair-count weights (the same definition as the main pipeline). Uncertainty comes from a
county-cluster bootstrap: whole counties are resampled with replacement, implemented with row weights.
"""
from pathlib import Path

import numpy as np
import pandas as pd


def find_root():
    p = Path.cwd().resolve()
    for q in [p, *p.parents]:
        if (q / "04_scripts").is_dir():
            return q
        if (q / "project3" / "04_scripts").is_dir():
            return q / "project3"
    raise SystemExit("Run from inside project3.")


def weighted_auc(y, p, w):
    """AUC with row weights and ties counted as half. Returns (auc, weighted_pair_count)."""
    y = np.asarray(y); p = np.asarray(p, float); w = np.asarray(w, float)
    keep = w > 0
    y, p, w = y[keep], p[keep], w[keep]
    if len(y) == 0:
        return np.nan, 0.0
    wp = w * (y == 1)
    wn = w * (y == 0)
    W1, W0 = wp.sum(), wn.sum()
    if W1 == 0 or W0 == 0:
        return np.nan, 0.0
    order = np.argsort(p, kind="mergesort")
    p, wp, wn = p[order], wp[order], wn[order]
    starts = np.r_[0, np.flatnonzero(np.diff(p)) + 1]          # first index of each tie group
    gp = np.add.reduceat(wp, starts)                            # positive weight in group
    gn = np.add.reduceat(wn, starts)                            # negative weight in group
    neg_before = np.cumsum(gn) - gn                             # negative weight strictly below the group
    num = np.sum(gp * (neg_before + 0.5 * gn))
    return num / (W1 * W0), W1 * W0


class Cells:
    """Year x disease cells for one set of predictions, ready for fast weighted AUC / bootstrap."""

    def __init__(self, df, preds, years=None):
        """df: columns fips, year, disease, up. preds: dict name -> array aligned with df rows."""
        d = df.reset_index(drop=True)
        if years is not None:
            keep = d["year"].isin(years).values
        else:
            keep = np.ones(len(d), bool)
        self.counties = pd.Index(sorted(d["fips"].unique()))
        cid = self.counties.get_indexer(d["fips"])
        self.cells = []
        for (yr, dis), g in d[keep].groupby(["year", "disease"]):
            idx = g.index.values
            y = d["up"].values[idx]
            if y.sum() == 0 or y.sum() == len(y):
                continue
            self.cells.append(dict(year=yr, disease=dis, idx=idx, y=y, cid=cid[idx]))
        self.preds = {k: np.asarray(v, float) for k, v in preds.items()}
        self.n_counties = len(self.counties)

    def strat_auc(self, name, mult=None, disease=None):
        num = den = 0.0
        p_all = self.preds[name]
        for c in self.cells:
            if disease is not None and c["disease"] != disease:
                continue
            w = np.ones(len(c["y"])) if mult is None else mult[c["cid"]]
            a, pairs = weighted_auc(c["y"], p_all[c["idx"]], w)
            if pairs > 0 and not np.isnan(a):
                num += a * pairs
                den += pairs
        return num / den if den else np.nan

    def bootstrap_deltas(self, base, others, B=500, seed=1, disease=None):
        """County-cluster bootstrap of strat AUC(other) - strat AUC(base). Returns dict name -> array(B)."""
        rng = np.random.default_rng(seed)
        out = {o: np.empty(B) for o in others}
        for b in range(B):
            pick = rng.integers(0, self.n_counties, self.n_counties)
            mult = np.bincount(pick, minlength=self.n_counties).astype(float)
            a0 = self.strat_auc(base, mult, disease)
            for o in others:
                out[o][b] = self.strat_auc(o, mult, disease) - a0
        return out


def summarize(draws, point, level=0.95):
    lo, hi = np.nanpercentile(draws, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return dict(delta=point, lo=lo, hi=hi, se=float(np.nanstd(draws, ddof=1)))


def load_oof(root, name="oof_predictions_lfo.csv"):
    f = root / "05_results" / "tables" / name
    if not f.exists():
        raise SystemExit(f"Missing {f}. Run the main pipeline (steps 6-12) or restore 05_results first.")
    o = pd.read_csv(f, dtype={"fips": str})
    o["fips"] = o["fips"].str.zfill(5)
    return o


def wide_preds(o):
    """Long OOF table -> (df of rows with outcome, dict model -> p) aligned row by row."""
    base = o[o["model"] == o["model"].iloc[0]][["fips", "county", "year", "disease", "group", "up"]].reset_index(drop=True)
    key = ["fips", "year", "disease"]
    preds = {}
    for m, g in o.groupby("model"):
        merged = base[key].merge(g[key + ["p"]], on=key, how="left")
        preds[m] = merged["p"].values
    return base, preds


def logit(p):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return np.log(p / (1 - p))


def expit(x):
    return 1 / (1 + np.exp(-x))
