"""Kiểm tra số [[CÔNG THỨC]] trong các tệp sửa khớp số công thức thật trong XML gốc."""
import glob, re, zipfile, sys
d = zipfile.ZipFile("in/goc.docx").read("word/document.xml").decode()
body = d[d.index("<w:body>"):]
sp = [m.group(0) for m in re.finditer(r"<w:p[ >].*?</w:p>", body, re.S)]
ed = {}
for f in sorted(glob.glob("work/ed*.txt")):
    cur = None
    for line in open(f, encoding="utf-8").read().split("\n"):
        m = re.match(r"^@@ (\d+)( DEL)?\s*$", line)
        if m:
            cur = int(m.group(1)); ed[cur] = None if m.group(2) else ""
            if m.group(2): cur = None
            continue
        if cur is not None and line.strip(): ed[cur] += " " + line
bad = 0
for i, e in sorted(ed.items()):
    n = len(re.findall(r"<m:oMathPara\b.*?</m:oMathPara>|<m:oMath\b.*?</m:oMath>", sp[i], re.S))
    if e is None:
        if n: print("XÓA đoạn có công thức", i, n)
        continue
    if e.count("[[CÔNG THỨC]]") != n:
        bad += 1
        t = re.sub(r"<m:oMath\b.*?</m:oMath>", "[M]", sp[i], flags=re.S)
        print("LỆCH", i, e.count("[[CÔNG THỨC]]"), n, re.sub(r"<[^>]+>", "", t)[:300])
print("lệch:", bad)
