"""
26_maps_and_comovement.py - extra spatial figures (the advanced layer's 23_make_figures.py draws one county map; these add three) from existing results (no refits).

Needs : pip install pyshp matplotlib   (pyshp reads the county shapefile; geopandas is not needed)
Reads : 02_data/interim/geography/cb_*_us_county_500k.shp   (California = state code 06)
        05_results/tables/oof_predictions_lfo.csv
        02_data/processed/model_table_local.csv
Writes: 05_results/figures_report/map_events.png, map_predicted_risk.png, map_obs_minus_pred.png, disease_comovement.png
Run   : python 04_scripts/26_maps_and_comovement.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

try:
    import shapefile
except ImportError:
    raise SystemExit("Install the shapefile reader first:  pip install pyshp")


def find_root():
    p = Path.cwd().resolve()
    for q in [p, *p.parents]:
        if (q / "04_scripts").is_dir():
            return q
        if (q / "project3" / "04_scripts").is_dir():
            return q / "project3"
    raise SystemExit("Run from inside project3.")


ROOT = find_root()
OUT = ROOT / "05_results" / "figures_report"
OUT.mkdir(parents=True, exist_ok=True)
shp = sorted((ROOT / "02_data" / "interim" / "geography").glob("cb_*_us_county_500k.shp"))
if not shp:
    raise SystemExit("County shapefile not found in 02_data/interim/geography.")
rd = shapefile.Reader(str(shp[0]))
fields = [f[0] for f in rd.fields[1:]]
geoid_i = fields.index("GEOID")
polys = {}
for sr in rd.iterShapeRecords():
    gid = sr.record[geoid_i]
    if not str(gid).startswith("06"):
        continue
    pts = sr.shape.points
    parts = list(sr.shape.parts) + [len(pts)]
    polys[gid] = [Polygon(pts[parts[i]:parts[i + 1]], closed=True) for i in range(len(parts) - 1)]
print(f"{len(polys)} California counties in the shapefile")

oof = pd.read_csv(ROOT / "05_results" / "tables" / "oof_predictions_lfo.csv", dtype={"fips": str})
oof["fips"] = oof["fips"].str.zfill(5)
a = oof[oof["model"] == "A"]
agg = a.groupby("fips").agg(events=("up", "sum"), obs=("up", "mean"), pred=("p", "mean"), rows=("up", "size"))
agg["obs_minus_pred"] = agg["obs"] - agg["pred"]


def draw(col, title, fname, cmap="YlOrRd", center=False):
    fig, ax = plt.subplots(figsize=(5.2, 6.2))
    vals = agg[col]
    vmax = float(vals.abs().max()) if center else float(vals.max())
    vmin = -vmax if center else 0.0
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    cm = plt.get_cmap("RdBu_r" if center else cmap)
    for gid, plist in polys.items():
        v = vals.get(gid, np.nan)
        color = "#dddddd" if pd.isna(v) else cm(norm(v))
        ax.add_collection(PatchCollection(plist, facecolor=color, edgecolor="white", linewidth=0.3))
    ax.autoscale_view(); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=10)
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cm); fig.colorbar(sm, ax=ax, shrink=0.6)
    fig.tight_layout(); fig.savefig(OUT / fname, dpi=150); plt.close(fig)


draw("events", "Up-transition events per county\n(16 diseases, 2017-2020 test years)", "map_events.png")
draw("pred", "Mean predicted risk, model A\n(test years)", "map_predicted_risk.png")
draw("obs_minus_pred", "Observed minus predicted event rate\n(red = more events than predicted)", "map_obs_minus_pred.png", center=True)

# ---- cross-disease co-movement: correlation of county-year trend slopes between diseases
mt = pd.read_csv(ROOT / "02_data" / "processed" / "model_table_local.csv")
wd = mt.pivot_table(index=["fips", "year"], columns="disease", values="trend_slope")
order = (mt.drop_duplicates("disease").sort_values(["group", "disease"])["disease"]).tolist()
corr = wd[order].corr(method="spearman")
fig, ax = plt.subplots(figsize=(7.5, 6.5))
im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(order))); ax.set_xticklabels([d[:22] for d in order], rotation=90, fontsize=6)
ax.set_yticks(range(len(order))); ax.set_yticklabels([d[:22] for d in order], fontsize=6)
fig.colorbar(im, shrink=0.7); ax.set_title("Co-movement of disease trend slopes across county-years\n(ordered by disease group)", fontsize=9)
fig.tight_layout(); fig.savefig(OUT / "disease_comovement.png", dpi=150); plt.close(fig)
off = corr.values[~np.eye(len(order), dtype=bool)]
print(f"Mean off-diagonal co-movement: {np.nanmean(off):.2f} (range {np.nanmin(off):.2f} to {np.nanmax(off):.2f})")
print("Wrote 4 figures to", OUT)
