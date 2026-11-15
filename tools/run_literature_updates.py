"""
run_literature_updates.py - applies the three literature patches in the right order and stops at the first problem.
Run from the project3 folder:  python tools/run_literature_updates.py
"""
import py_compile
import subprocess
import sys
from pathlib import Path

tools = Path.cwd() / "tools"
scripts = ["patch_verified_papers.py", "patch_gonsalves2023.py", "patch_bauer2023.py"]
for s in scripts:
    p = tools / s
    if not p.exists():
        sys.exit(f"Missing {p}. Nothing run.")
    try:
        py_compile.compile(str(p), doraise=True)
    except py_compile.PyCompileError as e:
        sys.exit(f"Syntax error in {s}: {e}. Nothing run.")
for s in scripts:
    print(f"=== {s} ===")
    r = subprocess.run([sys.executable, str(tools / s)], capture_output=True, text=True)
    print((r.stdout + r.stderr).strip())
    if r.returncode != 0:
        sys.exit(f"{s} stopped with an error. Later patches were not run.")
print("All literature patches finished.")
