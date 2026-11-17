import pandas as pd
e = pd.read_csv(r"02_data\processed\transitions_ext_hiv.csv")
cols = ["upcross_0.80", "upcross_local_0.80"]
print("HIV  rate:", e[cols].mean().round(3).to_dict(), "events:", e[cols].sum().to_dict())
print("old 16 rate:", t[cols].mean().round(3).to_dict(), "events:", t[cols].sum().to_dict())
print(t.groupby("disease")["upcross_local_0.80"].agg(["mean", "sum"]).round(3).to_string())
