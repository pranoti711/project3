"""
19_positive_control_power.py - Positive control (signal injection) and the smallest effect this study could detect.

Why: a null result is only informative if the pipeline WOULD have found a real signal. Here a synthetic predictor
with a known strength is added to model A and passed through the same leave-future-out evaluation and county-cluster
bootstrap. The share of injections whose 95% interval excludes 0 is the detection rate (power). The same script also
turns the observed intervals of the INLA runs (stages 1-3) into "effects larger than X are ruled out".

Synthetic predictor: x = N(0,1) + d * (next-year event), d = 0 is a negative control (must NOT be detected).
Reads : 02_data/processed/model_table_local.csv, 05_results*/tables/model_delta_auc_lfo.csv
Writes: 05_results_addons/tables/positive_control_power.csv, equivalence_bounds.csv
Run   : python 04_scripts/19_positive_control_power.py [--reps 10] [--boot 100]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from standin import Cells, find_root, fit_predictions, load_table  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="model_table_local.csv")
    ap.add_argument("--reps", type=int, default=10, help="injections per strength")
    ap.add_argument("--boot", type=int, default=100)
    ap.add_argument("--d", type=float, nargs="*", default=[0.0, 0.15, 0.3, 0.45, 0.6])
    a = ap.parse_args()
    root = find_root()
    out = root / "05_results_addons" / "tables"
    out.mkdir(parents=True, exist_ok=True)

    df = load_table(a.input, root)
    years = sorted(df["year"].unique())[-6:]
    cells = Cells(df, years)
    rng = np.random.default_rng(2026)
    p_a = fit_predictions(df, years, "A")
    p_b = fit_predictions(df, years, "B")
    real = cells.boot_delta(p_b, p_a, a.boot, rng)
    real_row = dict(delta=cells.strat_auc(p_b) - cells.strat_auc(p_a), lo=np.percentile(real, 2.5), hi=np.percentile(real, 97.5))
    print(f"Real stand-in B - A: {real_row['delta']:+.4f} [{real_row['lo']:+.3f}, {real_row['hi']:+.3f}]  "
          f"(events scored: {int(df[df['year'].isin(years)]['up'].sum())})")

    rows = []
    up = df["up"].values.astype(float)
    for d in a.d:
        deltas, detected = [], 0
        for r in range(a.reps):
            x = rng.normal(size=len(df)) + d * up
            p_inj = fit_predictions(df, years, "A", extra=x)
            dist = cells.boot_delta(p_inj, p_a, a.boot, rng)
            delta = cells.strat_auc(p_inj) - cells.strat_auc(p_a)
            deltas.append(delta)
            detected += int(np.percentile(dist, 2.5) > 0)
        rows.append(dict(strength_d=d, mean_delta_auc=np.mean(deltas), sd_delta_auc=np.std(deltas),
                         detection_rate=detected / a.reps, reps=a.reps))
        print(f"  d={d:<5} mean gain in AUC {np.mean(deltas):+.4f}   detected in {detected}/{a.reps} injections")
    pc = pd.DataFrame(rows)
    pc.to_csv(out / "positive_control_power.csv", index=False)

    # smallest gain detected in at least 80% of injections (linear interpolation)
    det = pc.sort_values("mean_delta_auc")
    mde = np.nan
    if (det["detection_rate"] >= 0.8).any():
        hi = det[det["detection_rate"] >= 0.8].iloc[0]
        lo_ = det[det["detection_rate"] < 0.8]
        if len(lo_):
            lo = lo_.iloc[-1]
            f = (0.8 - lo["detection_rate"]) / (hi["detection_rate"] - lo["detection_rate"])
            mde = lo["mean_delta_auc"] + f * (hi["mean_delta_auc"] - lo["mean_delta_auc"])
        else:
            mde = hi["mean_delta_auc"]
    print(f"Smallest gain detected in >= 80% of injections: about {mde:+.3f} AUC" if not np.isnan(mde)
          else "No injection strength reached 80% detection; increase --d.")

    # equivalence / bounds from the INLA runs
    eq = []
    for label, folder in [("stage 1", "05_results"), ("stage 2", "05_results_stage2"), ("stage 3", "05_results_stage3")]:
        f = root / folder / "tables" / "model_delta_auc_lfo.csv"
        if not f.exists():
            continue
        t = pd.read_csv(f)
        t = t[t["scope"] == "all"]
        for _, r in t.iterrows():
            eq.append(dict(stage=label, model=r["model"], delta_auc=r["delta_auc"], lo=r["lo"], hi=r["hi"],
                           gains_above_ruled_out=r["hi"], harms_below_ruled_out=r["lo"],
                           within_plus_minus_0_05=bool(max(abs(r["lo"]), abs(r["hi"])) <= 0.05)))
    eqd = pd.DataFrame(eq)
    eqd.to_csv(out / "equivalence_bounds.csv", index=False)
    print("\nWhat each interval rules out (pooled, INLA runs):")
    print(eqd.round(3).to_string(index=False))
    pd.DataFrame([dict(**real_row, mde_80=mde)]).to_csv(out / "standin_real_and_mde.csv", index=False)


if __name__ == "__main__":
    main()
