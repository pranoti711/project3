"""04_simulation.py - A1: short-series power simulation (stand-in test, BEFORE any real cross-domain result).
Question: with only 5 overlapping years of county mortality (2019-2023), how often would a lagged
mortality-transition predictor be detected if it truly leads disease transitions, and how often is a
false link reported when shared yearly shocks exist?
Design (matches Phase 0): 58 counties; T(i,d,t+1) predicted from mortality transitions at lags 0..L known by end of year t
(so more lags = fewer usable target years: with M mortality years, L=0 -> M targets, L=1 -> M-1, L=2 -> M-2).
Planted truth: disease transition probability depends on mortality transition at TRUE_LAG years before; shared year shocks hit both series.
Stand-in analysis: discrete-time logistic model, disease + year fixed effects, likelihood-ratio test of the mortality lags (alpha=0.05).
This is NOT the final method (RW2/BYM2 transitions + hierarchical hazard); rerun with the real engine when it exists.
Outputs: 05_results/simulation/power_table.csv and 00_docs/08_simulation_summary.md
"""
from pathlib import Path
import itertools, numpy as np, pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
RES, DOCS = ROOT / "05_results/simulation", ROOT / "00_docs"
RES.mkdir(parents=True, exist_ok=True); DOCS.mkdir(parents=True, exist_ok=True)

N_COUNTIES, M_YEARS = 58, 5           # mortality years 2019-2023
Q_MORT = 0.20                          # share of county-years with a mortality 'transition'
SHOCK = 1.0                            # sd of shared yearly shock (hits mortality and disease)
REPS, ALPHA, SEED = 100, 0.05, 20261022
GRID = dict(D=[3, 8], p0=[0.10, 0.20], beta=[0.0, 0.5, 1.0], true_lag=[0, 1], L=[0, 1, 2])
logit = lambda p: np.log(p / (1 - p)); expit = lambda x: 1 / (1 + np.exp(-x))

def simulate(rng, D, p0, beta, true_lag):
    u = rng.normal(0, SHOCK, M_YEARS + 1)                              # shared yearly shocks (years 0..M)
    mort = (rng.random((N_COUNTIES, M_YEARS + 1)) < expit(logit(Q_MORT) + u)).astype(int)
    dint = rng.normal(0, 0.5, D)                                       # disease intercepts
    rows = []
    for t in range(M_YEARS):                                           # t = predictor year; target year t+1
        for d in range(D):
            eta = logit(p0) + dint[d] + u[t + 1]
            lead_year = t + 1 - (true_lag + 1)                         # lag 0 = mortality at t drives t+1
            m_true = mort[:, lead_year] if lead_year >= 0 else np.zeros(N_COUNTIES)
            y = (rng.random(N_COUNTIES) < expit(eta + beta * m_true)).astype(int)
            rows.append(pd.DataFrame({"county": np.arange(N_COUNTIES), "d": d, "t": t, "y": y,
                                      **{f"m{k}": (mort[:, t - k] if t - k >= 0 else np.nan) for k in range(3)}}))
    return pd.concat(rows, ignore_index=True)

def design(df, cols, year_fe=True):
    X = pd.get_dummies(df.d, prefix="d", drop_first=False).astype(float)
    if year_fe: X = X.join(pd.get_dummies(df.t, prefix="t", drop_first=True).astype(float))
    return sm.add_constant(X.join(df[cols]).drop(columns=["d_0"]), has_constant="add")

def lrt(df, L, year_fe=True):
    use = df[df.t >= L].dropna(subset=[f"m{k}" for k in range(L + 1)])
    cols = [f"m{k}" for k in range(L + 1)]
    try:
        f0 = sm.GLM(use.y, design(use, [], year_fe), family=sm.families.Binomial()).fit()
        f1 = sm.GLM(use.y, design(use, cols, year_fe), family=sm.families.Binomial()).fit()
        stat = 2 * (f1.llf - f0.llf); return chi2.sf(max(stat, 0), L + 1), use.t.nunique()
    except Exception:
        return np.nan, use.t.nunique()

rng = np.random.default_rng(SEED)
out = []
for D, p0, beta, tl, L in itertools.product(*GRID.values()):
    ps, tg = [], None
    for _ in range(REPS):
        p, tg = lrt(simulate(rng, D, p0, beta, tl), L); ps.append(p)
    ps = np.array(ps, dtype=float)
    out.append(dict(diseases=D, event_prob=p0, log_odds_effect=beta, true_lead_years=tl + 1, lags_tested=L + 1,
                    target_years_usable=tg, rejection_rate=float(np.nanmean(ps < ALPHA))))
res = pd.DataFrame(out)

# shared-shock false positives: beta = 0, analysis WITHOUT year effects (L=0)
fp = []
for D in GRID["D"]:
    ps = np.array([lrt(simulate(rng, D, 0.10, 0.0, 0), 0, year_fe=False)[0] for _ in range(REPS)], dtype=float)
    fp.append(dict(diseases=D, test="no year effects, no true link", rejection_rate=float(np.nanmean(ps < ALPHA))))
fp = pd.DataFrame(fp)
res.round(3).to_csv(RES / "power_table.csv", index=False)

null = res[res.log_odds_effect == 0].rejection_rate.mean()
tab = res[res.log_odds_effect > 0].pivot_table(index=["true_lead_years", "diseases", "event_prob"],
                                               columns=["log_odds_effect", "lags_tested"], values="rejection_rate")
md = ["# Simulation summary (A1, stand-in logistic test)", "",
      f"58 counties, {M_YEARS} mortality years, {REPS} replicates per cell, alpha={ALPHA}. Shared yearly shocks sd={SHOCK}.", "",
      f"False-positive rate with year effects and NO true link (average over cells): {null:.3f} (nominal {ALPHA}).", "",
      "False-positive rate WITHOUT year effects and no true link:", fp.round(3).to_markdown(index=False), "",
      "Power (rejection rate) when a link is planted. Columns: effect on log-odds, then number of lags tested.",
      tab.round(2).to_markdown(), "",
      f"Reading: target years usable by number of lags tested = {res.groupby('lags_tested').target_years_usable.first().to_dict()}. Power is for this stand-in test only."]
(DOCS / "08_simulation_summary.md").write_text("\n".join(md), encoding="utf-8")
print("\n".join(md))
