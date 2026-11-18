from pathlib import Path
p = Path("tools/strengthen_novelty.py")
s = p.read_text(encoding="utf-8")
old = 'def get(url):\n    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:\n        return json.load(r)["message"]\n'
new = '''import time
def get(url):
    last = None
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.load(r)["message"]
        except Exception as e:
            last = e
            print("  retry", i + 1, "after", type(e).__name__)
            time.sleep(3 * (i + 1))
    raise SystemExit("Crossref not reachable: " + str(last))
'''
print("patched:", s.count(old))
p.write_text(s.replace(old, new), encoding="utf-8")
