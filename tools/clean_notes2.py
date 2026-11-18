import re
from pathlib import Path
p = Path("00_docs/10_results_writeup.md")
t = p.read_text(encoding="utf-8-sig")
t, a = re.subn(r"\(section\s+5\)", "(see the section on why a first pass looked positive)", t)
t, b = re.subn(r"\s*\(an\s+abstract-level\s+report\)", "", t)
print(a, "x section 5;", b, "x abstract-level note")
p.write_text(t, encoding="utf-8")
