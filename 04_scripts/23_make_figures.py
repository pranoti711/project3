"""
23_make_figures.py - report figures and county maps. (advanced evaluation layer)

Writes PNG files to 05_results/figures_report/. A figure is skipped (with a message) if its input table is missing.
  f1_three_stages_forest.png   pooled change in AUC (B, C, D vs A) for the three stages, with 95% intervals
  f2_auc_by_year.png           within-year AUC of A, B, C, D by test year
  f3_population_vs_mortality.png   AUC of the baseline without population, with population, and with mortality
  f4_calibration_model_A.png   predicted vs observed event rate (deciles), model A
  f5_per_disease_forest.png    per-disease change in AUC (B - A) with the random-effects pooled estimate
  f6_power_curve.png           power to detect a true AUC gain, with the minimum detectable effect
  f7_decision_curve.png        net benefit of the models against alarm-for-all and never-alarm
  f8_county_map.png            observed events and model A mean predicted risk by county (needs pyshp: pip install pyshp)
Run : python 04_scripts/23_make_figures.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adv_common import find_root, load_oof, wide_preds  # noqa: E402

root = find_root()
tab = root / "05_results" / "tables"
out = root / "05_results" / "figures_report"
out.mkdir(parents=True, exist_ok=True)
COL = {"A": "#444444", "B": "#d55e00", "C": "#0072b2", "D": "#009e73"}


def read(path):
    p = Path(path)
    if not p.exists():
        print(f"  (skipped, missing {p.relative_to(root)})")
        return None
    return pd.read_csv(p)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(out / name, dpi=160)
    plt.close(fig)
    print("  wrote", name)


# f1 - three stages
rows = []
for stage, folder in [("Stage 1: mortality", "05_results"), ("Stage 2: neighbours + traits", "05_results_stage2"),
                      ("Stage 3: cross-disease", "05_results_stage3")]:
    d = read(root / folder / "tables" / "model_delta_auc_lfo.csv")
    if d is None:
        continue
    d = d[d["scope"] == "all"]
    for _, r in d.iterrows():
        rows.append((stage, r["model"], r["delta_auc"], r["lo"], r["hi"]))
if rows:
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    y = 0
    ticks, labels = [], []
    for stage in dict.fromkeys(r[0] for r in rows):
        for st, m, dlt, lo, hi in [r for r in rows if r[0] == stage]:
            ax.errorbar(dlt, y, xerr=[[dlt - lo], [hi - dlt]], fmt="o", color=COL[m], capsize=3)
            ticks.append(y); labels.append(f"{stage} - {m}")
            y -= 1
        y -= 0.5
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Change in within-year AUC versus model A (95% county-cluster bootstrap)")
    ax.set_title("No stage improves on the baseline")
    save(fig, "f1_three_stages_forest.png")

# f2 - AUC by year
sc = read(tab / "model_scores_lfo.csv")
if sc is not None:
    s = sc[sc["scope"].astype(str).str.startswith("year_")].copy()
    s["year"] = s["scope"].str[5:].astype(int)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for m, g in s.groupby("model"):
        ax.plot(g["year"], g["auc"], marker="o", color=COL.get(m), label=f"model {m}")
    ax.axhline(0.5, color="grey", ls="--", lw=0.8)
    ax.set_xticks(sorted(s["year"].unique())); ax.set_ylabel("Within-year AUC"); ax.set_xlabel("Test year")
    ax.set_title("Out-of-sample AUC by test year"); ax.legend()
    save(fig, "f2_auc_by_year.png")

# f3 - population vs mortality
cc = read(tab / "confound_check_n6_t080.csv")
if cc is not None:
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.bar(cc["spec"], cc["strat_auc"], color=["#999999", "#444444", "#d55e00", "#e69f00", "#f0e442"][: len(cc)])
    ax.set_ylim(0.45, max(cc["strat_auc"]) + 0.04)
    for i, v in enumerate(cc["strat_auc"]):
        ax.text(i, v + 0.004, f"{v:.3f}", ha="center", fontsize=8)
    ax.axhline(0.5, color="grey", ls="--", lw=0.8)
    ax.set_ylabel("Within-year AUC (fast stand-in model)")
    ax.set_title("County size explains the gain; mortality adds nothing on top")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    save(fig, "f3_population_vs_mortality.png")

# oof based
try:
    o = load_oof(root)
    df, preds = wide_preds(o)
except SystemExit as e:
    print(" ", e); df = preds = None

# f4 - calibration
if preds is not None:
    p = preds["A"]; y = df["up"].values
    q = pd.qcut(p, 10, duplicates="drop")
    g = pd.DataFrame({"p": p, "y": y, "q": q}).groupby("q", observed=True).agg(p=("p", "mean"), y=("y", "mean"), n=("y", "size"))
    fig, ax = plt.subplots(figsize=(5, 5))
    m = max(g["p"].max(), g["y"].max()) * 1.1
    ax.plot([0, m], [0, m], color="grey", ls="--")
    ax.plot(g["p"], g["y"], "o-", color=COL["A"])
    ax.set_xlabel("Mean predicted probability (decile)"); ax.set_ylabel("Observed event rate")
    ax.set_title("Calibration of model A (2017-2020)")
    save(fig, "f4_calibration_model_A.png")

# f5 - per-disease forest
pdl = read(tab / "adv_per_disease_delta.csv"); meta = read(tab / "adv_meta_analysis.csv")
if pdl is not None:
    pdl = pdl.sort_values("delta").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.errorbar(pdl["delta"], range(len(pdl)), xerr=1.96 * pdl["se"], fmt="o", color=COL["B"], capsize=2)
    ax.set_yticks(range(len(pdl))); ax.set_yticklabels([f"{d[:30]} ({e})" for d, e in zip(pdl["disease"], pdl["events"])], fontsize=7)
    ax.axvline(0, color="black", lw=0.8)
    if meta is not None:
        r = meta.iloc[0]
        ax.axvspan(r["lo"], r["hi"], color="grey", alpha=0.25, label=f"pooled {r['pooled']:+.3f} (I2 = {r['I2']:.0f}%)")
        ax.legend(loc="lower right", fontsize=8)
    ax.set_xlabel("Change in within-year AUC, B - A (approx. 95% interval); events in brackets")
    ax.set_title("Per-disease effect of mortality")
    save(fig, "f5_per_disease_forest.png")

# f6 - power
pw = read(tab / "adv_power_curve.csv"); mde = read(tab / "adv_mde.csv")
if pw is not None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(pw["true_delta"], pw["power"], color=COL["B"])
    ax.axhline(0.8, color="grey", ls="--", lw=0.8)
    if mde is not None:
        x = mde["mde_80pct_power"].iloc[0]
        ax.axvline(x, color="grey", ls=":", lw=0.8); ax.text(x + 0.002, 0.1, f"MDE {x:.3f}", fontsize=8)
    ax.set_xlabel("True gain in AUC"); ax.set_ylabel("Power"); ax.set_title("What gain could this study detect?")
    save(fig, "f6_power_curve.png")

# f7 - decision curve
dc = read(tab / "adv_decision_curve.csv")
if dc is not None:
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for m in ["A", "B", "C", "D"]:
        g = dc[dc["model"] == m]
        if len(g):
            ax.plot(g["pt"], g["net_benefit"], color=COL[m], label=f"model {m}")
    g = dc[dc["model"] == "treat_all"]; ax.plot(g["pt"], g["net_benefit"], color="grey", ls="--", label="alarm for all")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_ylim(-0.005, 0.02); ax.set_xlabel("Alarm threshold (probability)"); ax.set_ylabel("Net benefit")
    ax.set_title("Decision curve"); ax.legend(fontsize=8)
    save(fig, "f7_decision_curve.png")

# f8 - county maps (optional)
try:
    import shapefile  # pyshp
    shp = root / "02_data" / "interim" / "geography" / "cb_2025_us_county_500k.shp"
    if shp.exists() and df is not None:
        from matplotlib.collections import PolyCollection
        rd = shapefile.Reader(str(shp))
        names = [f[0] for f in rd.fields[1:]]
        ist = names.index("STATEFP"); igeo = names.index("GEOID")
        polys, geoids = [], []
        for sr in rd.shapeRecords():
            if sr.record[ist] != "06":
                continue
            pts = sr.shape.points; parts = list(sr.shape.parts) + [len(pts)]
            for a, b in zip(parts[:-1], parts[1:]):
                polys.append(pts[a:b]); geoids.append(sr.record[igeo])
        ev = df.groupby("fips").agg(events=("up", "sum"), n=("up", "size"))
        ev["rate"] = ev["events"] / ev["n"] * 1000
        ev["pA"] = pd.Series(preds["A"], index=df.index).groupby(df["fips"]).mean() * 1000
        fig, axes = plt.subplots(1, 2, figsize=(10, 6))
        for ax, col, title in [(axes[0], "rate", "Observed events per 1000 county-disease-years"),
                               (axes[1], "pA", "Model A mean predicted risk per 1000")]:
            vals = np.array([ev[col].get(g, np.nan) for g in geoids])
            pc = PolyCollection(polys, array=vals, cmap="viridis", edgecolors="white", linewidths=0.3)
            ax.add_collection(pc); ax.autoscale_view(); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=9)
            fig.colorbar(pc, ax=ax, shrink=0.6)
        save(fig, "f8_county_map.png")
    else:
        print("  (map skipped: shapefile or predictions missing)")
except ImportError:
    print("  (map skipped: pip install pyshp)")
print("Figures in", out)
