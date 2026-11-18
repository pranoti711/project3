import re
import pandas as pd
from pathlib import Path

d = pd.read_csv("02_data/processed/model_table.csv")
ycol = [c for c in d.columns if "year" in c.lower()][0]
t = d[d[ycol].between(2017, 2020)]
print("scored-year rows:", len(t), "(expected about 3712 if the year column is the target year)")
cols = ["allcause_dev", "drug_od_dev", "suicide_dev", "homicide_dev"]
a, dr, su, ho = [round(100 * t[c].isna().mean()) for c in cols]
print("all-cause %d%%, drug %d%%, suicide %d%%, homicide %d%%" % (a, dr, su, ho))

p = Path("00_docs/27_discussion_draft.md")
s = p.read_text(encoding="utf-8")

s, n1 = re.subn(r"\(43% of drug-overdose and suicide rows and 66% of homicide rows\s+missing\)",
                f"(missing in {dr}% of drug-overdose, {su}% of suicide and {ho}% of homicide rows)", s)
s, n2 = re.subn(r"missing in many\s*county-years because of small-count suppression, from under 20% for all-cause\s+mortality to about two-thirds or more for homicide",
                f"missing in {a}% (all-cause), {dr}% (drug overdose), {su}% (suicide) and {ho}% (homicide) of "
                "scored county-disease-years because of small-count suppression", s)
print("point 2 replaced:", n1, "| limitations replaced:", n2)
p.write_text(s, encoding="utf-8")
