"""
25_supplementary_diagnostics.py - supplementary diagnostics built only on results you already have (no new data, no refits).

Complements the advanced layer (19-24: positive control, equivalence, boosting, decision curve, figures); nothing here repeats it.

Reads : 05_results/tables/oof_predictions_lfo.csv   out-of-fold predictions of models A-D (stage 1, INLA)
        02_data/processed/model_table_local.csv      population per county-year
        02_data/processed/transitions.csv            posterior uncertainty of the trend (slope_sd)
        05_results*/tables/model_delta_auc_lfo.csv   for the specification curve (folders that exist are used)
        05_results/tables/confound_check_n6_t0*.csv  fast stand-in, thresholds 0.70 / 0.80 / 0.90
Writes: 05_results/tables/adv_supp_*.csv, 05_results/figures_report/specification_curve.png, 00_docs/21_supplementary_results.md

What it adds
  1. Specification curve: every estimate of the mortality (and extension) gain on one plot.
  2. Performance by county-size quartile (shows the outcome depends on estimate precision).
  3. Calibration summary (intercept, slope, Brier skill).
  4. Precision diagnostic: is the population effect a detectability effect? (diagnostic only, not a predictor)

Run : python 04_scripts/25_supplementary_diagnostics.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression


def find_root():
    p = Path.cwd().resolve()
    for q in [p, *p.parents]:
        if (q / "04_scripts").is_dir():
            return q
        if (q / "project3" / "04_scripts").is_dir():
            return q / "project3"
    raise SystemExit("Run from inside project3.")


ROOT = find_root()
TAB = ROOT / "05_results" / "tables"
OUT_T = ROOT / "05_results" / "tables"
OUT_F = ROOT / "05_results" / "figures_report"
OUT_T.mkdir(parents=True, exist_ok=True)
OUT_F.mkdir(parents=True, exist_ok=True)
MD = []


def md_table(df, nd=3):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    isint = {c: pd.api.types.is_integer_dtype(df[c]) for c in cols}
    for i in range(len(df)):
        cells = []
        for c in cols:
            v = df[c].iloc[i]
            if isinstance(v, str):
                cells.append(v)
            elif pd.isna(v):
                cells.append("")
            elif isint[c]:
                cells.append(f"{int(v)}")
            else:
                cells.append(f"{v:.{nd}f}")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------- data
oof = pd.read_csv(TAB / "oof_predictions_lfo.csv", dtype={"fips": str})
oof["fips"] = oof["fips"].str.zfill(5)
wide = oof.pivot_table(index=["fips", "county", "year", "disease", "group", "up"], columns="model", values="p").reset_index()
models = [m for m in ["A", "B", "C", "D"] if m in wide]
counties = sorted(wide["fips"].unique())
cidx = {f: i for i, f in enumerate(counties)}
wide["ci"] = wide["fips"].map(cidx)
NC = len(counties)


def cmpmat(a, b):
    return (a[:, None] > b[None, :]).astype(float) + 0.5 * (a[:, None] == b[None, :])


cells = []
for (yr, dis), g in wide.groupby(["year", "disease"]):
    y = g["up"].values
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    if len(pos) == 0 or len(neg) == 0:
        continue
    cells.append(dict(year=yr, disease=dis, group=g["group"].iloc[0], cpos=g["ci"].values[pos], cneg=g["ci"].values[neg],
                      S={m: cmpmat(g[m].values[pos], g[m].values[neg]) for m in models}))
print(f"{len(cells)} scored year x disease cells, {NC} counties, {int(wide['up'].sum())} events")


def strat_auc(w, model, sel=None):
    num = den = 0.0
    for c in cells:
        if sel is not None and not sel(c):
            continue
        wp, wn = w[c["cpos"]], w[c["cneg"]]
        W = wp.sum() * wn.sum()
        if W > 0:
            num += wp @ c["S"][model] @ wn
            den += W
    return num / den if den > 0 else np.nan


ones = np.ones(NC)
point = {m: strat_auc(ones, m) for m in models}
print("point AUC (within year x disease):", {m: round(v, 4) for m, v in point.items()})

# ------------------------------------------------------------------ 3. specification curve
spec = []
labels = [("Stage 1 headline", "05_results"), ("Stage 2 exploratory", "05_results_stage2"),
          ("Stage 3 exploratory", "05_results_stage3"),
          ("First pass, confounded", "05_results_origoutcome_run")]
for lab, folder in labels:
    f = ROOT / folder / "tables" / "model_delta_auc_lfo.csv"
    if f.exists():
        d = pd.read_csv(f)
        for m in ["B", "C", "D"]:
            r = d[(d.scope == "all") & (d.model == m)]
            if len(r):
                spec.append(dict(spec=f"{lab}, model {m}", delta=float(r.delta_auc.iloc[0]), lo=float(r.lo.iloc[0]), hi=float(r.hi.iloc[0])))
for tau in ("070", "080", "090"):
    f = TAB / f"confound_check_n6_t{tau}.csv"
    if f.exists():
        d = pd.read_csv(f); r = d[d.spec == "B_dev"]
        if len(r):
            spec.append(dict(spec=f"Stand-in tau 0.{tau[1:]}, mortality dev.", delta=float(r.delta_vs_A.iloc[0]), lo=np.nan, hi=np.nan))
sp = pd.DataFrame(spec)
sp.to_csv(OUT_T / "adv_supp_specification_curve.csv", index=False)
if len(sp):
    fig, ax = plt.subplots(figsize=(8.5, max(3.2, 0.34 * len(sp) + 1.4)))
    ax.axvspan(-0.02, 0.02, color="#d8ecd8", label="practical equivalence (+/-0.02)")
    y = np.arange(len(sp))[::-1]
    for yi, (_, r) in zip(y, sp.iterrows()):
        if not np.isnan(r.lo):
            ax.plot([r.lo, r.hi], [yi, yi], color="#888", lw=1.5)
        ax.plot(r.delta, yi, "o", color="#1f4e79" if "confounded" not in r.spec else "#b03030", ms=5)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(list(sp.spec), fontsize=8)
    ax.set_xlabel("Gain in AUC over model A"); ax.set_title("Specification curve: gain in AUC over model A", fontsize=10)
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.2)); fig.tight_layout(); fig.savefig(OUT_F / "specification_curve.png", dpi=150); plt.close(fig)
    MD.append("## 1. Specification curve (figure: `05_results/figures_report/specification_curve.png`)\n")
    MD.append(md_table(sp))
    MD.append("Folders that do not exist on your machine are skipped. The red first-pass rows are the confounded run, shown only to compare with the earlier apparent gain.\n")

# ------------------------------------------------------------------ 4. performance by county-size quartile
mt = pd.read_csv(ROOT / "02_data" / "processed" / "model_table_local.csv", dtype={"fips": str})
mt["fips"] = mt["fips"].str.zfill(5)
pop = mt.drop_duplicates("fips").set_index("fips")["pop_log"]
wide["pop_log"] = wide["fips"].map(pop)
wide["pq"] = pd.qcut(wide["pop_log"].rank(method="first"), 4, labels=["Q1 smallest", "Q2", "Q3", "Q4 largest"])
rows = []
for q, g in wide.groupby("pq", observed=True):
    cset = set(g["fips"])
    sel = lambda c, cs=cset: True
    wq = np.array([1.0 if f in cset else 0.0 for f in counties])
    rows.append(dict(quartile=str(q), rows=len(g), events=int(g.up.sum()), event_rate=g.up.mean(), mean_pred_A=g["A"].mean(),
                     obs_over_pred=g.up.mean() / g["A"].mean(), brier_A=((g["A"] - g.up) ** 2).mean(),
                     auc_A=strat_auc(wq, "A"), auc_B=strat_auc(wq, "B")))
pq = pd.DataFrame(rows)
pq.to_csv(OUT_T / "adv_supp_performance_by_county_size.csv", index=False)
MD.append("## 2. Performance by county-size quartile (model A and B, 2017-2020 test years)\n")
MD.append(md_table(pq))
MD.append("Events, predicted risk and discrimination differ strongly by county size. Part of this is detectability of the "
          "outcome (section 4), not only epidemiology.\n")

# ------------------------------------------------------------------ 5. calibration and decision curve
y = wide["up"].values
cal_rows = []
for m in ["A", "B"]:
    p = np.clip(wide[m].values, 1e-6, 1 - 1e-6)
    lg = np.log(p / (1 - p)).reshape(-1, 1)
    lr = LogisticRegression(C=1e6, max_iter=1000).fit(lg, y)
    cal_rows.append(dict(model=m, calibration_slope=float(lr.coef_[0, 0]), calibration_intercept=float(lr.intercept_[0]),
                         brier=((p - y) ** 2).mean(), brier_skill_vs_prevalence=1 - ((p - y) ** 2).mean() / (y.mean() * (1 - y.mean()))))
cal = pd.DataFrame(cal_rows)
cal.to_csv(OUT_T / "adv_supp_calibration_summary.csv", index=False)
MD.append("## 3. Calibration summary\n")
MD.append(md_table(cal))
MD.append("A slope near 1 and intercept near 0 mean good calibration; a Brier skill near 0 means the model barely beats "
          "always predicting the average rate.\n")
# ------------------------------------------------------------------ 6. precision diagnostic
tr = pd.read_csv(ROOT / "02_data" / "processed" / "transitions.csv", dtype={"fips": str})
tr["fips"] = tr["fips"].str.zfill(5)
nxt = tr[["fips", "disease", "year", "slope_sd"]].copy(); nxt["year"] -= 1
w2 = wide.merge(nxt.rename(columns={"slope_sd": "sd_next"}), on=["fips", "disease", "year"], how="left")
w2 = w2[w2.sd_next.notna()].copy()
w2["sdt"] = pd.qcut(w2["sd_next"], 3, labels=["low uncertainty", "mid", "high uncertainty"])
rho = spearmanr(w2["pop_log"], w2["sd_next"]).correlation
tab = w2.groupby(["sdt", "pq"], observed=True).agg(rows=("up", "size"), events=("up", "sum"), event_rate=("up", "mean")).reset_index()
tab["sdt"] = tab["sdt"].astype(str); tab["pq"] = tab["pq"].astype(str)
tab.to_csv(OUT_T / "adv_supp_precision_diagnostic.csv", index=False)
MD.append("## 4. Precision diagnostic (not a predictor: it uses the outcome year's posterior uncertainty)\n")
MD.append(f"Spearman correlation between county population and the posterior uncertainty of the trend: {rho:.2f}.\n")
MD.append(md_table(tab))
MD.append("If event rates fall mainly with uncertainty and stay similar across county-size quartiles inside each uncertainty "
          "band, the population effect is largely a detectability effect.\n")

(ROOT / "00_docs" / "21_supplementary_results.md").write_text(
    "# 21_supplementary_results.md - auto-generated by 04_scripts/25_supplementary_diagnostics.py (do not edit by hand)\n\n"
    "Built only on existing results (no refits). Stage 1 out-of-fold predictions; exploratory stage files are used only in the specification curve.\n\n"
    + "\n".join(MD), encoding="utf-8")
print("Wrote 00_docs/21_supplementary_results.md, tables/adv_supp_*.csv and figures_report/specification_curve.png")
