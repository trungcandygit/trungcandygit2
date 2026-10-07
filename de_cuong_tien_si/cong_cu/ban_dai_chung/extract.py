"""Trích các đoạn của bản đại chúng thành danh sách có mã để biên tập.

Mỗi đoạn: id, loại (H0/H1/H2/P/L/T/M/TOC/C), chữ (đậm đánh dấu **...**).
Chạy: python3 extract.py in/goc.docx work/paras.json
"""
import html
import json
import re
import sys
import zipfile

src, out = sys.argv[1:3]
d = zipfile.ZipFile(src).read("word/document.xml").decode()
body = d[d.index("<w:body>"):]

# đánh dấu đoạn nằm trong bảng
tbl_spans = [(m.start(), m.end()) for m in re.finditer(r"<w:tbl>.*?</w:tbl>", body, re.S)]


def in_table(pos):
    return any(a <= pos < b for a, b in tbl_spans)


def text_of(p):
    out = []
    for r in re.findall(r"<w:r[ >].*?</w:r>|<m:oMath.*?</m:oMath>", p, re.S):
        if r.startswith("<m:oMath"):
            out.append("[[CÔNG THỨC]]")
            continue
        t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", r))
        t = html.unescape(t)
        if not t:
            continue
        bold = re.search(r"<w:b/>|<w:b w:val=\"(1|true)\"/>", r) is not None
        sub = "subscript" in r
        sup = "superscript" in r
        if sub:
            t = "_{" + t + "}"
        elif sup:
            t = "^{" + t + "}"
        out.append(f"**{t}**" if bold and t.strip() else t)
    s = "".join(out)
    return s.replace("****", "")


paras = []
for m in re.finditer(r"<w:p[ >].*?</w:p>", body, re.S):
    p = m.group(0)
    lvl = re.search(r'<w:outlineLvl w:val="(\d)"', p)
    if in_table(m.start()):
        kind = "T"
    elif "<m:oMath" in p:
        kind = "M"
    elif lvl:
        kind = "H" + lvl.group(1)
    elif '<w:ind w:left="454"/>' in p or ('<w:sz w:val="22"/>' in p and len(paras) < 420 and "w:left=" in p):
        kind = "TOC"
    elif "<w:numPr>" in p or 'w:hanging=' in p:
        kind = "L"
    else:
        kind = "P"
    paras.append({"id": len(paras), "k": kind, "t": text_of(p)})

json.dump(paras, open(out, "w"), ensure_ascii=False, indent=0)
from collections import Counter
c = Counter(x["k"] for x in paras)
w = Counter()
for x in paras:
    w[x["k"]] += len(x["t"].split())
print(c, w, sum(w.values()))
