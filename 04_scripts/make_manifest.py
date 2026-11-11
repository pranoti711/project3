"""
make_manifest.py - SHA-256 fingerprint of the key project files, so anyone can check they are unchanged.
Run from project3:  python tools/make_manifest.py      -> 00_docs/manifest.csv
Files listed: scripts, config, documents, model tables, stage result tables (not raw data).
"""
import csv
import hashlib
from pathlib import Path

root = Path.cwd()
patterns = ["04_scripts/*.py", "04_scripts/*.R", "03_config/*", "00_docs/*.md", "02_data/processed/model_table*.csv",
            "02_data/processed/transitions.csv", "05_results/tables/*.csv", "05_results_stage2/tables/*.csv",
            "05_results_stage3/tables/*.csv", "run_from_07.py", "requirements.txt"]
rows = []
for pat in patterns:
    for f in sorted(root.glob(pat)):
        if f.is_file():
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            rows.append((str(f.relative_to(root)).replace("\\", "/"), f.stat().st_size, h))
out = root / "00_docs" / "manifest.csv"
with out.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["file", "bytes", "sha256"]); w.writerows(rows)
print(f"Wrote {out} ({len(rows)} files)")
