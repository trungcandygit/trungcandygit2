import json, re, subprocess, glob, unicodedata
P = json.load(open("work/paras.json"))
ed = {}
for f in sorted(glob.glob("work/ed*.txt")):
    cur = None
    for line in open(f).read().split("\n"):
        m = re.match(r"^@@ (\d+)( DEL)?\s*$", line)
        if m:
            cur = int(m.group(1)); ed[cur] = None if m.group(2) else ""
            if m.group(2): cur = None
            continue
        if cur is not None and line.strip(): ed[cur] = (ed[cur] + " " + line.strip()).strip()
heads = []
for p in P:
    if p["k"] == "H0" and p["id"] >= 312 and not (3891 <= p["id"] <= 3894):
        h = (ed.get(p["id"]) or p["t"]).replace("**", "")
        heads.append((h, p["id"] in ed))
# old unedited headings get section renumbering like apply.py
import importlib.util
src = open("apply.py").read()
ns = {"re": re}
exec(src[src.index("SEC = {"):src.index("def fix_old")], ns)
def ren(h):
    for a, b in ns["TERMS"]:
        h = re.sub(a, ns["sec"], h) if b is None else re.sub(a, b, h)
    return h
heads = [(h if e else ren(h)).replace("Lí ", "Lý ").replace(" lí ", " lý ") for h, e in heads]
n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", "work/out.pdf"], capture_output=True, text=True).stdout).group(1))
norm = lambda s: re.sub(r"\s+", "", unicodedata.normalize("NFC", s)).lower()
pages = [norm(subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "work/out.pdf", "-"], capture_output=True, text=True).stdout) for i in range(1, n + 1)]
out = []
lk = norm(heads[-1])[:40]
start = max([i for i in range(min(8, n)) if lk in pages[i]] or [-1]) + 1
for h in heads:
    key = norm(h)[:40]
    pg = next((i for i in range(start, n) if key in pages[i]), None)
    if pg is None: print("MISS", h); continue
    start = pg
    out.append([h, pg + 1])
json.dump(out, open("work/toc.json", "w"), ensure_ascii=False)
print(len(heads), len(out), out[:3], out[-2:])
