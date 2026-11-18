import pandas as pd
f = r"02_data\raw\mortality\wonder_final\drug_od 2018-2024.xls"
df = pd.read_excel(f)
df = df[df["Year"].notna()].copy()
df["Year"] = df["Year"].astype(int)
df["d"] = pd.to_numeric(df["Deaths"], errors="coerce")
ok = df.groupby("County")["d"].apply(lambda s: s.notna().all())
bal = df[df["County"].isin(ok[ok].index)]
t = bal.groupby("Year").agg(deaths=("d", "sum"), pop=("Population", "sum"))
t["rate_per_100k"] = t.deaths / t["pop"] * 1e5
t["change"] = t.rate_per_100k.diff()
print(ok.sum(), "of", len(ok), "counties report in all 7 years")
print(t.round(1))
