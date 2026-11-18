import re
from pathlib import Path

p = Path("06_paper/references.bib")
s = p.read_text(encoding="utf-8")

new = {
"richardson2004": r"""@article{richardson2004,
  author  = {Richardson, Sylvia and Thomson, Andrew and Best, Nicky and Elliott, Paul},
  title   = {Interpreting Posterior Relative Risk Estimates in Disease-Mapping Studies},
  journal = {Environmental Health Perspectives},
  year    = {2004},
  volume  = {112},
  number  = {9},
  pages   = {1016--1025},
  doi     = {10.1289/ehp.6740}
}""",
"lipsitch2010": r"""@article{lipsitch2010,
  author  = {Lipsitch, Marc and Tchetgen Tchetgen, Eric and Cohen, Ted},
  title   = {Negative Controls: A Tool for Detecting Confounding and Bias in Observational Studies},
  journal = {Epidemiology},
  year    = {2010},
  volume  = {21},
  number  = {3},
  pages   = {383--388},
  doi     = {10.1097/EDE.0b013e3181d61eeb}
}""",
"burkner2020": r"""@article{burkner2020,
  author  = {B{\"u}rkner, Paul-Christian and Gabry, Jonah and Vehtari, Aki},
  title   = {Approximate leave-future-out cross-validation for {Bayesian} time series models},
  journal = {Journal of Statistical Computation and Simulation},
  year    = {2020},
  volume  = {90},
  number  = {14},
  pages   = {2499--2523},
  doi     = {10.1080/00949655.2020.1783262}
}""",
}

for key, entry in new.items():
    s, n = re.subn(r"@article\{" + key + r",.*?\n\}", lambda m: entry, s, count=1, flags=re.S)
    print(key, "replaced:", n)

p.write_text(s, encoding="utf-8")
