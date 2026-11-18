import re
from pathlib import Path

p = Path("00_docs/10_results_writeup.md")
t = p.read_text(encoding="utf-8-sig")
R = [
 (r"\(`upcross_local_0\.80`\)", "(local up-crossing definition, threshold 0.80)"),
 (r"`review_travel`\s+group", "travel-associated group"),
 (r"Pre-specified\s+in\s+`13_stage2_plan\.md`\s+\(stage\s+1\s+frozen\s+at\s+commit\s+bbc9ebe\)\.",
  "Pre-specified in a written plan committed before the run (repository tag stage2-plan-frozen; stage 1 frozen at tag stage1-freeze)."),
 (r"Pre-specified\s+in\s+`17_stage3_plan\.md`\s+\(committed\s+as\s+ee54e5f\s+before\s+the\s+run\)\.",
  "Pre-specified in a written plan committed before the run (repository tag stage3-plan-frozen)."),
 (r"\(git\s+commit\s+a1b6688,\s+tag\s+hiv-ext\)", "(repository tag hiv-ext)"),
 (r"\bsection\s+11\b", "the advanced evaluation layer"),
 (r"\bsection\s+12\b", "the second advanced layer"),
]
for pat, rep in R:
    t, n = re.subn(pat, rep, t)
    print(n, "x", pat[:55])
t, n = re.subn(r"`([^`\n]+)`", r"\1", t)          # remaining backticked names become plain text
print(n, "x backticks removed")
p.write_text(t, encoding="utf-8")

a = Path("00_docs/26_abstract_draft.md")
s = a.read_text(encoding="utf-8-sig")
s, n = re.subn(r"Stage 1 was pre-specified;", "Stage 1 was pre-specified (protocol frozen at git tag stage1-freeze);", s)
print(n, "x abstract pre-specified pointer")
a.write_text(s, encoding="utf-8")

b = Path("tools/build_manuscript2.py")
c = b.read_text(encoding="utf-8")
c, n1 = re.subn(r'TAG = "[^"]+"', 'TAG = "final-draft-v16"', c, count=1)
c, n2 = re.subn(re.escape(r'+ TAG + ").\n\n"'),
                lambda m: r'+ TAG + "). File names mentioned in the text (for example 13_stage2_plan.md) refer to documents in this repository.\n\n"', c, count=1)
print(n1, "x TAG updated;", n2, "x availability sentence")
b.write_text(c, encoding="utf-8")
