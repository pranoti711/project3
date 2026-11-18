from docx import Document
d = Document(r"06_paper\manuscript_draft.docx")
for i in [32,47,52,55,57,59,65,76,90,98,102,108]:
    print(f"--- para {i}\n{d.paragraphs[i].text}\n")
