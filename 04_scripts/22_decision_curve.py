"""
22_decision_curve.py - is any model useful in practice? Decision-curve (net benefit) analysis. (advanced evaluation layer)

Net benefit weighs correct alarms against false alarms at a chosen alarm threshold pt:
    NB(pt) = TP/N - FP/N * pt/(1 - pt)
A model is worth using at pt only if its NB beats both "alarm for every county" and "never alarm" (NB = 0).
Reads  05_results/tables/oof_predictions_lfo.csv (the saved out-of-sample predictions of the main models).
Writes 05_results/tables/adv_decision_curve.csv (NB per model and threshold) and adv_decision_diff.csv
       (NB difference of B, C, D versus A with a 95% county-cluster bootstrap interval, at selected thresholds).
Run    python 04_scripts/22_decision_curve.py [--boot 500]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adv_common import find_root, load_oof, wide_preds  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=500)
    ap.add_argument("--seed", type=int, default=22)
    a = ap.parse_args()
    root = find_root()
    tab = root / "05_results" / "tables"
    df, preds = wide_preds(load_oof(root))
    y = df["up"].values.astype(float)
    pts = np.round(np.arange(0.01, 0.1501, 0.005), 3)
    odds = pts / (1 - pts)
    counties = pd.Index(sorted(df["fips"].unique()))
    cid = counties.get_indexer(df["fips"])
    models = list(preds)
    ind = {m: (preds[m][:, None] >= pts[None, :]).astype(float) for m in models}

    def nb(m, w):
        N = w.sum()
        tp = (w * y) @ ind[m]
        fp = (w * (1 - y)) @ ind[m]
        return tp / N - fp / N * odds

    w1 = np.ones(len(y))
    rows = []
    for m in models:
        for pt, v in zip(pts, nb(m, w1)):
            rows.append(dict(model=m, pt=pt, net_benefit=v))
    prev = y.mean()
    for pt, o in zip(pts, odds):
        rows.append(dict(model="treat_all", pt=pt, net_benefit=prev - (1 - prev) * o))
        rows.append(dict(model="treat_none", pt=pt, net_benefit=0.0))
    dc = pd.DataFrame(rows)
    dc.to_csv(tab / "adv_decision_curve.csv", index=False)

    rng = np.random.default_rng(a.seed)
    boots = {m: np.empty((a.boot, len(pts))) for m in models if m != "A"}
    for b in range(a.boot):
        mult = np.bincount(rng.integers(0, len(counties), len(counties)), minlength=len(counties)).astype(float)
        w = mult[cid]
        base = nb("A", w)
        for m in boots:
            boots[m][b] = nb(m, w) - base
    sel = [0.02, 0.03, 0.05, 0.08, 0.10]
    out = []
    for m in boots:
        for pt in sel:
            j = int(np.argmin(np.abs(pts - pt)))
            point = nb(m, w1)[j] - nb("A", w1)[j]
            lo, hi = np.percentile(boots[m][:, j], [2.5, 97.5])
            out.append(dict(contrast=f"{m}-A", pt=pts[j], nb_diff=point, ci95_lo=lo, ci95_hi=hi))
    od = pd.DataFrame(out)
    od.to_csv(tab / "adv_decision_diff.csv", index=False)
    print(f"Event rate in scored rows: {prev:.4f}")
    print(od.round(5).to_string(index=False))
    best_pts = dc[dc["model"] == "A"].merge(dc[dc["model"] == "treat_all"], on="pt", suffixes=("_A", "_all"))
    print("Thresholds where model A beats treat-all:", int((best_pts["net_benefit_A"] > best_pts["net_benefit_all"]).sum()),
          "of", len(best_pts))


if __name__ == "__main__":
    main()
