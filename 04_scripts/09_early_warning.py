"""
09_early_warning.py - early-warning performance at a MATCHED false-alarm rate.

For each model (A, B, C, D) the alarm threshold is set so that every model raises
the same share of false alarms among county-disease-years with no up-transition.
Then we compare the hit rate (share of true up-transitions caught). County-cluster
bootstrap gives confidence intervals for the hit-rate gain over model A.

Also an "operational" variant: threshold fixed on the earlier half of the test years,
applied to the later half, reporting realised false-alarm rate and hit rate.

Input : 05_results/tables/oof_predictions_lfo.csv  (from 06_models_ABCD.R)
        columns: county, fips, year, disease, group, up, model, p
Output: 05_results/tables/early_warning_matched_far.csv
        05_results/tables/early_warning_operational.csv
        05_results/figures/early_warning_far10.png
Run   : python 04_scripts/09_early_warning.py [--boot 500] [--far 0.05,0.10,0.20]
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def find_root():
    p = Path.cwd().resolve()
    for q in [p, *p.parents]:
        if (q / "04_scripts").is_dir():
            return q
        if (q / "project3" / "04_scripts").is_dir():
            return q / "project3"
    raise SystemExit("Run from inside project3 or its parent folder.")


def tpr_at_far(y, p, far):
    neg, pos = p[y == 0], p[y == 1]
    if len(neg) == 0 or len(pos) == 0:
        return np.nan
    thr = np.quantile(neg, 1 - far)
    return float((pos > thr).mean())


def boot(sub, models, far, B, rng):
    y = sub["up"].values
    P = {m: sub[m].values for m in models}
    counties = sub["county"].values
    uniq = np.unique(counties)
    idx = {c: np.where(counties == c)[0] for c in uniq}
    obs = {m: tpr_at_far(y, P[m], far) for m in models}
    draws = {m: [] for m in models}
    for _ in range(B):
        pick = rng.choice(uniq, len(uniq), replace=True)
        ii = np.concatenate([idx[c] for c in pick])
        for m in models:
            draws[m].append(tpr_at_far(y[ii], P[m][ii], far))
    rows = []
    for m in models:
        d = np.array(draws[m], dtype=float)
        dA = d - np.array(draws["A"], dtype=float)
        rows.append(dict(model=m, far=far, hit_rate=obs[m],
                         hit_lo=np.nanpercentile(d, 2.5), hit_hi=np.nanpercentile(d, 97.5),
                         gain_vs_A=obs[m] - obs["A"],
                         gain_lo=np.nanpercentile(dA, 2.5), gain_hi=np.nanpercentile(dA, 97.5),
                         n_events=int(y.sum()), n_nonevents=int((1 - y).sum())))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=500)
    ap.add_argument("--far", type=str, default="0.05,0.10,0.20")
    args = ap.parse_args()
    fars = [float(x) for x in args.far.split(",")]

    root = find_root()
    tabs = root / "05_results" / "tables"
    figs = root / "05_results" / "figures"
    figs.mkdir(parents=True, exist_ok=True)

    oof = pd.read_csv(tabs / "oof_predictions_lfo.csv")
    models = [m for m in ["A", "B", "C", "D"] if m in oof["model"].unique()]
    if "A" not in models:
        raise SystemExit("Model A missing from predictions.")
    wide = (oof.pivot_table(index=["county", "year", "disease", "group", "up"],
                            columns="model", values="p").reset_index())
    rng = np.random.default_rng(7)

    rows = []
    for scope, sub in [("all", wide)] + [(g, wide[wide.group == g]) for g in sorted(wide.group.unique())]:
        if sub["up"].sum() < 5:
            continue
        for far in fars:
            for r in boot(sub, models, far, args.boot, rng):
                r["scope"] = scope
                rows.append(r)
    res = pd.DataFrame(rows)
    res.to_csv(tabs / "early_warning_matched_far.csv", index=False)

    # operational: threshold from early test years, applied to later test years
    years = sorted(wide.year.unique())
    half = len(years) // 2
    cal, ev = wide[wide.year.isin(years[:half])], wide[wide.year.isin(years[half:])]
    op = []
    for far in fars:
        for m in models:
            neg = cal.loc[cal.up == 0, m].values
            thr = np.quantile(neg, 1 - far)
            e_neg, e_pos = ev.loc[ev.up == 0, m].values, ev.loc[ev.up == 1, m].values
            op.append(dict(model=m, target_far=far, threshold=thr,
                           realised_far=float((e_neg > thr).mean()) if len(e_neg) else np.nan,
                           hit_rate=float((e_pos > thr).mean()) if len(e_pos) else np.nan,
                           calibration_years=f"{years[0]}-{years[half-1]}",
                           evaluation_years=f"{years[half]}-{years[-1]}"))
    pd.DataFrame(op).to_csv(tabs / "early_warning_operational.csv", index=False)

    # figure: hit rate at the 10% false-alarm level
    f10 = res[(res.scope == "all") & (np.isclose(res.far, 0.10))]
    if len(f10):
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(f10.model, f10.hit_rate,
               yerr=[f10.hit_rate - f10.hit_lo, f10.hit_hi - f10.hit_rate], capsize=4)
        ax.set_ylabel("hit rate at 10% false-alarm rate")
        ax.set_title("Early warning, matched false alarms")
        fig.tight_layout()
        fig.savefig(figs / "early_warning_far10.png", dpi=150)

    pd.set_option("display.width", 200)
    print("\n=== Matched false-alarm hit rates (all groups) ===")
    print(res[res.scope == "all"][["model", "far", "hit_rate", "hit_lo", "hit_hi",
                                    "gain_vs_A", "gain_lo", "gain_hi"]].round(3).to_string(index=False))
    print("\nA gain whose interval excludes 0 means the extra information catches more events at the same"
          "\nfalse-alarm cost. Check the drug_linked row against the placebo results from script 11.")


if __name__ == "__main__":
    main()
