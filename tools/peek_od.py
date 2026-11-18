import pandas as pd
f = r"02_data\raw\mortality\wonder_final\drug_od 2018-2024.xls"
try:
    df = pd.read_excel(f)
except Exception:
    df = pd.read_csv(f, sep="\t")
print(df.head(20).to_string())
