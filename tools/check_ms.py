import re
from docx import Document
d = Document(r"06_paper\manuscript_draft.docx")
paras = [p.text for p in d.paragraphs]
bad = [r"first pass", r"\(hypothesis\)", r"\bsection\s*\d", r"\b\d{2}_\w+\.(md|csv|py|docx)\b",
       r"00_docs|02_data|05_results|tools[\\/]", r"\.(csv|py|md)\b", r"\bTODO\b|\bTBD\b|\bXXX\b", r"n\.d\."]
for i, t in enumerate(paras):
    for b in bad:
        if re.search(b, t, re.I):
            print(f"[{b}] para {i}: {t[:200]}")
print("tables:", len(d.tables))
for k, t in enumerate(d.tables):
    print(" table", k, "rows", len(t.rows), "cols", len(t.columns), "| first cell:", t.cell(0,0).text[:40])
