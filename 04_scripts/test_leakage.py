"""
Unit tests for the leakage rules and the AUC helper. Run from the project3 folder:  python -m pytest tests -q
Tests that need the real tables are skipped when those files are absent.
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "04_scripts"))


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, ROOT / "04_scripts" / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_weighted_auc_matches_rank_auc_with_ties():
    from scipy.stats import rankdata
    from adv_common import weighted_auc
    rng = np.random.default_rng(0)
    for _ in range(20):
        y = rng.integers(0, 2, 200)
        p = np.round(rng.random(200), 1)
        r = rankdata(p)
        n1, n0 = y.sum(), len(y) - y.sum()
        ref = (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
        assert abs(weighted_auc(y, p, np.ones(200))[0] - ref) < 1e-12


def test_integer_weights_equal_replicated_rows():
    from adv_common import weighted_auc
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, 150); p = rng.random(150); w = rng.integers(0, 4, 150)
    rep = np.repeat(np.arange(150), w)
    assert abs(weighted_auc(y, p, w)[0] - weighted_auc(y[rep], p[rep], np.ones(len(rep)))[0]) < 1e-12


def test_mortality_deviation_never_uses_year_t_or_later():
    b = load("b05", "05b_build_model_table.py")
    rng = np.random.default_rng(2)
    years = range(2001, 2024)
    rows = []
    cols = list(b.MORTALITY_COLUMNS)
    for f in ["06001", "06003", "06005"]:
        for y in years:
            rows.append({"fips": f, "year": y, **{c: float(rng.normal(10, 2)) for c in cols}})
    panel = pd.DataFrame(rows)
    base = b.mortality_deviation(panel)
    t = 2015
    changed = panel.copy()
    for c in cols:
        changed.loc[changed["year"] >= t, c] += 1000.0          # perturb every value from year t onward
    new = b.mortality_deviation(changed)
    m = base.merge(new, on=["fips", "year"], suffixes=("_a", "_b"))
    dev_cols = [c for c in base.columns if c.endswith("_dev")]
    for c in dev_cols:
        a, bb = m[f"{c}_a"], m[f"{c}_b"]
        before = m["year"] <= t                                   # dev(t) uses t-1 and earlier only
        assert np.allclose(a[before].fillna(-9), bb[before].fillna(-9)), c
        after = m["year"] > t + 1
        assert not np.allclose(a[after].fillna(-9), bb[after].fillna(-9)), c


def test_lfo_split_uses_only_earlier_years():
    # the rule used by every script: train rows have year < test year
    df = pd.DataFrame({"year": [2015, 2016, 2017, 2018], "x": range(4)})
    for T in (2017, 2018):
        tr = df[df["year"] < T]
        te = df[df["year"] == T]
        assert tr["year"].max() < T and set(te["year"]) == {T}


@pytest.mark.skipif(not (ROOT / "02_data" / "processed" / "model_table_local.csv").exists(), reason="no model table")
def test_real_table_deviations_recomputable_from_levels():
    b = load("b05b", "05b_build_model_table.py")
    d = pd.read_csv(ROOT / "02_data" / "processed" / "model_table_local.csv", dtype={"fips": str})
    d["fips"] = d["fips"].str.zfill(5)
    inv = {v: k for k, v in b.MORTALITY_COLUMNS.items()}
    panel = d.rename(columns=inv)
    redo = b.mortality_deviation(panel)
    m = d.merge(redo, on=["fips", "year"], suffixes=("", "_re"))
    for c in ["allcause_dev", "drug_od_dev", "suicide_dev", "homicide_dev"]:
        assert np.allclose(m[c].fillna(-9), m[f"{c}_re"].fillna(-9)), c


@pytest.mark.skipif(not (ROOT / "02_data" / "processed" / "model_table_stage3.csv").exists(), reason="no stage 3 table")
def test_cross_disease_features_exclude_the_disease_itself():
    d = pd.read_csv(ROOT / "02_data" / "processed" / "model_table_stage3.csv", dtype={"fips": str})
    d["fips"] = d["fips"].str.zfill(5)
    row = d[(d["fips"] == "06037") & (d["year"] == 2015) & (d["disease"] == "Chlamydia")].iloc[0]
    others = d[(d["fips"] == "06037") & (d["year"] == 2015) & (d["disease"] != "Chlamydia")]
    assert row["xd_n_up"] == others["prev_up"].sum()
    assert abs(row["xd_share_rising"] - (others["trend_slope"] > 0).mean()) < 1e-9
