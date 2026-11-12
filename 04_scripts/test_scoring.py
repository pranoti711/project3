"""Unit tests for 27_proper_scoring_and_influence.py helpers."""
import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location("s27", Path(__file__).resolve().parent / "27_proper_scoring_and_influence.py")
s27 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s27)


def test_calibration_recovers_slope():
    rng = np.random.default_rng(0)
    n = 40000
    lp = rng.normal(-3, 1, n)
    y = (rng.random(n) < 1 / (1 + np.exp(-lp))).astype(float)
    slope, icpt = s27.calib(y, 1 / (1 + np.exp(-lp)), np.ones(n))
    assert abs(slope - 1) < 0.08 and abs(icpt) < 0.08


def test_overconfident_model_has_slope_below_one():
    rng = np.random.default_rng(1)
    n = 40000
    lp = rng.normal(-3, 1, n)
    y = (rng.random(n) < 1 / (1 + np.exp(-lp))).astype(float)
    p_over = 1 / (1 + np.exp(-(1.6 * lp + 1.0)))        # stretched predictions
    slope, _ = s27.calib(y, p_over, np.ones(n))
    assert slope < 0.75


def test_scores_and_weights():
    y = np.array([0., 1.])
    p = np.array([0.1, 0.9])
    assert abs(s27.wmean(s27.brier_vec(y, p), np.ones(2)) - 0.01) < 1e-12
    w = np.array([3., 1.])
    assert abs(s27.wmean(np.array([0., 4.]), w) - 1.0) < 1e-12
