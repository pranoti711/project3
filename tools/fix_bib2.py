import re
from pathlib import Path

p = Path("06_paper/references.bib")
s = p.read_text(encoding="utf-8")
s = s.split("% ---- Candidates")[0].rstrip() + "\n\n"          # drop unverified candidates block
s = s[re.search(r"(?m)^@", s).start():]                        # drop starter comment at the top

s += r"""@article{gezer2024,
  author  = {Gezer, Fatih and Howard, Kerry A. and Litwin, Alain H. and Martin, Natasha K. and Rennert, Lior},
  title   = {Identification of factors associated with opioid-related and hepatitis {C} virus-related hospitalisations at the {ZIP} code area level in the {USA}: an ecological and modelling study},
  journal = {The Lancet Public Health},
  year    = {2024},
  volume  = {9},
  number  = {6},
  pages   = {e354--e364},
  doi     = {10.1016/S2468-2667(24)00076-8}
}

@article{sumetsky2019,
  author  = {Sumetsky, N. and Mair, C. and Burke, J. G.},
  title   = {Opioid-related diagnoses and {HIV}, {HCV} and mental disorders: using {Pennsylvania} hospitalisation data to assess community-level relationships over space and time},
  journal = {Journal of Epidemiology and Community Health},
  year    = {2019},
  volume  = {73},
  pages   = {935},
  doi     = {10.1136/jech-2019-212551},
  note    = {TODO: confirm full first names and end page on PubMed}
}

@article{marks2021lph,
  author  = {Marks, C. and others},
  title   = {Identifying counties at risk of high overdose mortality burden during the emerging fentanyl epidemic in the {USA}: a predictive statistical modelling study},
  journal = {The Lancet Public Health},
  year    = {2021},
  volume  = {6},
  pages   = {e720},
  doi     = {10.1016/S2468-2667(21)00080-3},
  note    = {TODO: full author list and end page}
}

@article{bauer2023,
  author  = {Bauer, C. and others},
  title   = {Small area forecasting of opioid-related mortality: {Bayesian} spatiotemporal dynamic modeling approach},
  journal = {JMIR Public Health and Surveillance},
  year    = {2023},
  volume  = {9},
  pages   = {e41450},
  doi     = {10.2196/41450},
  note    = {TODO: full author list}
}
"""
p.write_text(s, encoding="utf-8")
print("bib entries now:", len(re.findall(r"(?m)^@", s)))
