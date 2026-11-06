"""12_multiplicity.py - Holm correction across the group placebo tests, plus a lead-time summary.
Reads  05_results/tables/placebo_group_tests.csv, leadtime_summary.csv
Writes 05_results/tables/placebo_group_tests_holm.csv
Run after 11_placebos_surrogates.py:  python 04_scripts/12_multiplicity.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

T = Path(__file__).resolve().parents[1] / "05_results" / "tables"


def holm(p):
    """Holm-Bonferroni adjusted p-values."""
    p = np.asarray(p, float)
    n = len(p)
    adj = np.empty(n)
    running = 0.0
    for k, i in enumerate(np.argsort(p)):
        running = max(running, (n - k) * p[i])
        adj[i] = min(1.0, running)
    return adj


g = pd.read_csv(T / "placebo_group_tests.csv")
g["n1_p_holm"] = holm(g["n1_p"])
g["n2_p_holm"] = holm(g["n2_p"])
g["supported"] = (
    (g["n1_p_holm"] < 0.05) & (g["n2_p_holm"] < 0.05)
    & (g["observed_delta_auc"] > g["n1_null_mean"])
    & (g["observed_delta_auc"] > g["n2_null_mean"])
)
g.to_csv(T / "placebo_group_tests_holm.csv", index=False)
print("=== Group placebo tests, Holm-corrected across groups ===")
print(g[["group", "observed_delta_auc", "n1_p", "n1_p_holm", "n2_p", "n2_p_holm", "supported"]]
      .round(4).to_string(index=False))
perms = int(g["perms"].iloc[0]) if "perms" in g else 0
print(f"\nPermutations used: {perms}. Smallest possible p is about {1 / (perms + 1):.4f}; "
      f"after Holm over {len(g)} groups the floor is {len(g) / (perms + 1):.4f}. Use >= 1000 permutations.")

lt = pd.read_csv(T / "leadtime_summary.csv")
print(f"\nLead-time tests: {len(lt)} | Holm-significant (p < 0.05): {int((lt['perm_p_holm'] < 0.05).sum())} "
      f"| smallest Holm p: {lt['perm_p_holm'].min():.3f}")
