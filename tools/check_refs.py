from docx import Document
d = Document(r"06_paper\manuscript_draft.docx")
ps = [p.text.strip() for p in d.paragraphs if p.text.strip()]
idx = [i for i,t in enumerate(ps) if t.lower().startswith("references")][-1]
refs = ps[idx+1:]
print(len(refs), "entries after the References heading")
for r in refs: print("-", r[:110])
