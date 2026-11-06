"""03_disease_groups.py - DRAFT disease-group assignment from the real CDPH disease list.
Writes 02_data/interim/disease_groups_draft.csv. NOTHING here is frozen: a second person must
review it, then copy it to disease_groups_frozen.csv (and register it) before any modelling.
Run from anywhere: python 04_scripts/03_disease_groups.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC, INTERIM = ROOT / "02_data/processed", ROOT / "02_data/interim"
INTERIM.mkdir(parents=True, exist_ok=True)

# (keyword, group, reason).  First match wins.  Groups follow Phase 0 Section 8.
RULES = [
    ("botulism, wound",   "drug_linked",   "wound botulism: injection-drug pathway (find a citation before registering)"),
    ("hepatitis c",       "drug_linked",   "documented injection-drug pathway (not in the 52-disease file)"),
    ("hepatitis b",       "drug_linked",   "documented injection-drug pathway (not in the 52-disease file)"),
    ("hepatitis a",       "ambiguous",     "California outbreaks tied to homelessness; analyse separately"),
    ("hiv",               "ambiguous",     "large sexual-transmission component"),
    ("syphilis",          "ambiguous",     "large sexual-transmission component"),
    ("coccidioidomycosis","environment",   "soil/dust and climate driven"),
    ("lyme", "environment", "tick-borne"), ("anaplasmosis", "environment", "tick-borne"),
    ("babesiosis", "environment", "tick-borne"), ("ehrlichiosis", "environment", "tick-borne"),
    ("spotted fever", "environment", "tick-borne"), ("relapsing fever", "environment", "tick-borne"),
    ("typhus", "environment", "flea/louse-borne"), ("plague", "environment", "rodent/flea, environment"),
    ("tularemia", "environment", "environment/vector"), ("hantavirus", "environment", "rodent exposure"),
    ("q fever", "environment", "animal/environment exposure"), ("legionellosis", "environment", "water systems/climate"),
    ("vibrio", "environment", "warm coastal water"), ("leptospirosis", "environment", "water/animal exposure"),
    ("chlamydia", "review_sti", "sexually transmitted; not in the Phase 0 plan - decide group before freezing"),
    ("gonorrhea", "review_sti", "sexually transmitted; not in the Phase 0 plan - decide group before freezing"),
    ("dengue", "review_travel", "mostly travel-associated in California; decide before freezing"),
    ("zika", "review_travel", "mostly travel-associated"), ("chikungunya", "review_travel", "mostly travel-associated"),
    ("malaria", "review_travel", "mostly travel-associated"), ("flavivirus", "review_travel", "undetermined species"),
    ("typhoid", "review_travel", "mostly travel-associated"), ("paratyphoid", "review_travel", "mostly travel-associated"),
    ("campylobacteriosis", "comparison", "foodborne; no plausible overdose pathway"),
    ("salmonellosis", "comparison", "foodborne"), ("shigellosis", "comparison", "enteric (check outbreak/reporting shifts)"),
    ("giardiasis", "comparison", "enteric"), ("cryptosporidiosis", "comparison", "enteric"),
    ("cyclosporiasis", "comparison", "foodborne"), ("listeriosis", "comparison", "foodborne"),
    ("shiga toxin", "comparison", "foodborne (STEC)"), ("hemolytic uremic", "comparison", "foodborne (STEC)"),
    ("yersiniosis", "comparison", "foodborne"),
]

d = pd.read_csv(PROC / "disease_ca_long_all_sex.csv", dtype=str, usecols=["Disease"])
out = []
for name in sorted(d.Disease.unique()):
    low = name.lower()
    g, why = next(((g, w) for k, g, w in RULES if k in low), ("unassigned", "rare or non-infectious; likely exclude on screening"))
    out.append({"disease": name, "group_draft": g, "reason": why, "status": "DRAFT - needs second-person review"})
out = pd.DataFrame(out)
out.to_csv(INTERIM / "disease_groups_draft.csv", index=False)
print(out.group_draft.value_counts().to_string())
need = [k for k in ["hepatitis a", "hepatitis b", "hepatitis c", "hiv", "syphilis"] if not out.disease.str.lower().str.contains(k).any()]
print("\nStill NOT in your disease files (needed for drug-linked / ambiguous groups):", need)
print("wrote", INTERIM / "disease_groups_draft.csv")
