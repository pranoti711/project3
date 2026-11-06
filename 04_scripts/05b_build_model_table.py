"""Build leakage-safe inputs for the ABCD leave-future-out models.

CHANGED (v2): adds lagged WITHIN-COUNTY mortality deviations (allcause_dev, drug_od_dev,
suicide_dev, homicide_dev). Each is the county's mortality rate in year t-1 minus its own mean
over years t-6..t-2 (needs >= 3 of those years). Using the deviation instead of the level removes
the between-county level (which mostly tracks county size) and keeps only 'is mortality rising in
this county compared with its own past'. Year t-1 is also what would be published in time.
The raw level columns are kept (07_leadtime.R reads them).
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "02_data" / "processed"
PANEL_PATH = PROCESSED / "analysis_long.csv"
AQI_PATH = ROOT / "02_data" / "raw" / "environment" / "epa_annual_aqi_by_county_ca_1990_2024.csv"
DROUGHT_PATH = ROOT / "02_data" / "raw" / "environment" / "drought" / "usdm_ca_county_weekly_2000_2024.csv"

MORTALITY_COLUMNS = {
    "mort_all_cause_rate": "allcause_rate",
    "mort_drug_od_rate": "drug_od_rate",
    "mort_suicide_rate": "suicide_rate",
    "mort_homicide_rate": "homicide_rate",
}


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def load_environment_context(panel: pd.DataFrame) -> pd.DataFrame:
    keys = ["fips", "year"]
    county_map = panel[["fips", "county"]].drop_duplicates()
    if county_map["county"].duplicated().any():
        raise ValueError("County names do not map uniquely to FIPS codes.")

    aqi = pd.read_csv(AQI_PATH)
    aqi = aqi[aqi["State"].eq("California")].copy()
    aqi["year"] = pd.to_numeric(aqi["Year"], errors="raise").astype(int)
    aqi = aqi.merge(county_map, left_on="County", right_on="county", how="inner", validate="many_to_one")
    aqi_context = aqi.rename(columns={"Median AQI": "aqi_median"})[keys + ["aqi_median"]]
    if aqi_context.duplicated(keys).any():
        raise ValueError("The annual AQI file has duplicate California county-year rows.")

    drought = pd.read_csv(DROUGHT_PATH, dtype={"FIPS": "string"})
    drought["fips"] = drought["FIPS"].str.zfill(5)
    drought["year"] = pd.to_datetime(drought["ValidStart"], errors="raise").dt.year
    category_columns = ["D0", "D1", "D2", "D3", "D4"]
    drought["drought_dsci"] = sum(
        drought[column].mul(weight) for weight, column in enumerate(category_columns, start=1)
    )
    drought_context = (
        drought.groupby(keys, as_index=False)["drought_dsci"]
        .mean()
    )
    context = aqi_context.merge(drought_context, on=keys, how="outer", validate="one_to_one")
    context["year"] = context["year"].astype(int)
    return context


def mortality_deviation(panel: pd.DataFrame) -> pd.DataFrame:
    """Lagged within-county deviation: rate(t-1) - mean(rate(t-6..t-2)), needs >= 3 prior years."""
    cols = list(MORTALITY_COLUMNS)
    mt = panel[["fips", "year", *cols]].drop_duplicates(["fips", "year"])
    years = range(int(mt["year"].min()), int(mt["year"].max()) + 1)
    grid = pd.MultiIndex.from_product([mt["fips"].unique(), years], names=["fips", "year"])
    mt = mt.set_index(["fips", "year"]).reindex(grid).sort_index()
    out = pd.DataFrame(index=mt.index)
    for col, short in MORTALITY_COLUMNS.items():
        g = mt[col].groupby(level="fips")
        lag1 = g.shift(1)
        trail = pd.concat([g.shift(k) for k in range(2, 7)], axis=1)
        mu = trail.mean(axis=1, skipna=True)
        n = trail.notna().sum(axis=1)
        out[short.replace("_rate", "_dev")] = (lag1 - mu).where(n >= 3)
    return out.reset_index()


def build_model_table(transitions_path: Path, output_path: Path, outcome: str = "upcross_0.80") -> int:
    panel = pd.read_csv(PANEL_PATH, dtype={"fips": "string"})
    transitions = pd.read_csv(transitions_path, dtype={"fips": "string"})

    panel_required = {
        "fips", "county", "year", "disease", "group", "cases",
        "population_cdph", *MORTALITY_COLUMNS,
    }
    transition_required = {"fips", "year", "disease", "group", outcome}
    if missing := panel_required.difference(panel.columns):
        raise ValueError(f"analysis_long.csv is missing columns: {', '.join(sorted(missing))}")
    if missing := transition_required.difference(transitions.columns):
        raise ValueError(f"{transitions_path.name} is missing columns: {', '.join(sorted(missing))}")

    keys = ["fips", "year", "disease"]
    panel["fips"] = panel["fips"].str.zfill(5)
    transitions["fips"] = transitions["fips"].str.zfill(5)
    if panel.duplicated(keys).any():
        raise ValueError("analysis_long.csv contains duplicate county-year-disease rows.")
    if transitions.duplicated(keys).any():
        raise ValueError(f"{transitions_path.name} contains duplicate county-year-disease rows.")

    panel["year"] = pd.to_numeric(panel["year"], errors="raise").astype(int)
    transitions["year"] = pd.to_numeric(transitions["year"], errors="raise").astype(int)
    for column in ["cases", "population_cdph", *MORTALITY_COLUMNS]:
        panel[column] = pd.to_numeric(panel[column], errors="coerce")

    panel["case_rate"] = panel["cases"].div(panel["population_cdph"]).mul(100_000)
    panel = panel.sort_values(keys).copy()
    groups = panel.groupby(["fips", "disease"], sort=False)
    panel["lag_rate"] = groups["case_rate"].shift(0)
    prior_rate = groups["case_rate"].shift(1)
    prior_year = groups["year"].shift(1)
    panel["trend_slope"] = panel["case_rate"] - prior_rate.where(panel["year"].sub(prior_year).eq(1))
    panel["pop_log"] = np.log(panel["population_cdph"].where(panel["population_cdph"] > 0))
    physician_count = pd.to_numeric(panel["ahrf_md_nf_prim_care_pc_excl_rsdnt"], errors="coerce")
    panel["physicians_per_100k"] = physician_count.div(panel["population_cdph"]).mul(100_000)
    panel = panel.merge(load_environment_context(panel), on=keys[:2], how="left", validate="many_to_one")
    panel = panel.merge(mortality_deviation(panel), on=keys[:2], how="left", validate="many_to_one")

    events = transitions[["fips", "year", "disease", "group", outcome]].copy()
    events[outcome] = pd.to_numeric(events[outcome], errors="coerce")
    if not events[outcome].dropna().isin([0, 1]).all():
        raise ValueError("Transition outcome values must be 0, 1, or missing.")

    targets = events.dropna(subset=[outcome]).copy()
    targets["year"] -= 1
    targets = targets.rename(columns={outcome: "up"})

    previous = events[["fips", "year", "disease", outcome]].rename(
        columns={outcome: "prev_up"}
    )
    model = panel.merge(targets, on=keys, how="inner", suffixes=("", "_transition"), validate="one_to_one")
    model = model.merge(previous, on=keys, how="left", validate="one_to_one")

    if "group_transition" in model:
        mismatch = model["group"].ne(model["group_transition"])
        if mismatch.any():
            raise ValueError("Disease group differs between panel and transition output.")
        model = model.drop(columns="group_transition")

    model = model.rename(columns=MORTALITY_COLUMNS)
    columns = [
        "county", "fips", "year", "disease", "group", "up",
        "lag_rate", "trend_slope", "prev_up",
        "allcause_rate", "drug_od_rate", "suicide_rate", "homicide_rate",
        "allcause_dev", "drug_od_dev", "suicide_dev", "homicide_dev",
        "aqi_median", "drought_dsci", "physicians_per_100k", "pop_log",
    ]
    model = model[columns].sort_values(["disease", "fips", "year"])
    if model.empty:
        raise ValueError("No rows have both panel data and known transition outcomes.")
    if not model["up"].isin([0, 1]).all():
        raise ValueError("The generated outcome contains values other than 0 or 1.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.to_csv(output_path, index=False)
    print(
        f"Wrote {len(model):,} rows for {model['disease'].nunique()} diseases "
        f"and {model['fips'].nunique()} counties to {output_path}"
    )
    print(
        "Outcome is the next-year upcross; lag_rate and trend_slope use "
        "observed disease cases through the prediction year."
    )
    return len(model)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transitions", default="02_data/processed/transitions.csv")
    parser.add_argument("--output", default="02_data/processed/model_table.csv")
    parser.add_argument("--outcome", default="upcross_0.80",
                        help="outcome column in transitions.csv, e.g. upcross_local_0.80")
    args = parser.parse_args()

    transitions_path = project_path(args.transitions)
    output_path = project_path(args.output)
    if not PANEL_PATH.is_file():
        raise SystemExit(f"Required analysis panel is missing: {PANEL_PATH}")
    if not transitions_path.is_file():
        raise SystemExit(
            f"Required transition output is missing: {transitions_path}. "
            "Run 05_transitions.R first."
        )
    build_model_table(transitions_path, output_path, args.outcome)


if __name__ == "__main__":
    main()
