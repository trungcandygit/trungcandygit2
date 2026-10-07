"""Áp các chỉnh sửa (work/ed*.txt) vào document.xml của bản đại chúng, giữ định dạng gốc.

Định dạng tệp sửa:
    @@ <id>          dòng tiếp theo là chữ mới (có thể nhiều dòng; nối bằng dấu cách)
    @@ <id> DEL      xóa đoạn
Chữ mới: **đậm**, _{chỉ số dưới}, ^{chỉ số trên}.
Chạy: python3 apply.py in/goc.docx out.docx [--stats]
"""
import glob
import html
import json
import re
import sys
import zipfile

src, out = sys.argv[1:3]
STATS = "--stats" in sys.argv
P = json.load(open("work/paras.json"))

edits = {}
for f in sorted(glob.glob("work/ed*.txt")):
    cur = None
    for line in open(f, encoding="utf-8").read().split("\n"):
        m = re.match(r"^@@ (\d+)( DEL)?\s*$", line)
        if m:
            cur = int(m.group(1))
            edits[cur] = None if m.group(2) else ""
            if m.group(2):
                cur = None
            continue
        if cur is not None and line.strip():
            edits[cur] = (edits[cur] + " " + line.strip()).strip()


def words(s):
    return len(re.sub(r"\*\*|_\{|\^\{|\}|\[\[CÔNG THỨC\]\]", " ", s).split())


if STATS:
    h0 = [p["id"] for p in P if p["k"] == "H0"] + [len(P)]
    tot_o = tot_n = 0
    for i in range(len(h0) - 1):
        a, b = h0[i], h0[i + 1]
        o = sum(words(p["t"]) for p in P[a:b])
        n = 0
        for p in P[a:b]:
            if p["id"] in edits:
                n += 0 if edits[p["id"]] is None else words(edits[p["id"]])
            else:
                n += words(p["t"])
        tot_o += o
        tot_n += n
        print(f"{i:02d} {o:6d} -> {n:6d} ({(1 - n / max(o, 1)) * 100:5.1f}%) {P[a]['t'][:60]}")
    print(f"TOTAL {tot_o} -> {tot_n} ({(1 - tot_n / tot_o) * 100:.1f}%)")
    sys.exit(0)

z = zipfile.ZipFile(src)
doc = z.read("word/document.xml").decode()
bstart = doc.index("<w:body>")
head, body = doc[:bstart], doc[bstart:]
spans = [m.span() for m in re.finditer(r"<w:p[ >].*?</w:p>", body, re.S)]
assert len(spans) == len(P), (len(spans), len(P))


def esc(s):
    return html.escape(s, quote=False)


def build_runs(text, base_rpr, heading):
    if heading:
        text = text.replace("**", "")
    out = []
    for seg in re.split(r"(\*\*.*?\*\*)", text):
        if not seg:
            continue
        bold = seg.startswith("**") and seg.endswith("**") and len(seg) > 4
        if bold:
            seg = seg[2:-2]
        for part in re.split(r"(_\{[^}]*\}|\^\{[^}]*\})", seg):
            if not part:
                continue
            rpr = base_rpr
            if part.startswith("_{") or part.startswith("^{"):
                va = "subscript" if part[0] == "_" else "superscript"
                part = part[2:-1]
                rpr = rpr + f'<w:vertAlign w:val="{va}"/>'
            if bold:
                rpr = "<w:b/><w:bCs/>" + rpr
            out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{esc(part)}</w:t></w:r>')
    return "".join(out)


def clean_rpr(rpr):
    rpr = re.sub(r"<w:b/>|<w:bCs/>|<w:b w:val=\"[^\"]*\"/>|<w:bCs w:val=\"[^\"]*\"/>|<w:vertAlign[^>]*/>", "", rpr)
    return rpr


SEC = {"1.1": "4.1", "1.2": "4.1", "1.3": "4.3", "1.4": "4.4", "1.5": "4.5", "2.1": "4.1",
       "2.2": "4.2", "2.3": "4.2", "2.4": "4.3.2", "3.1.1": "4.3.3", "3.1.2": "4.3.4", "3.1": "4.3.9",
       "3.2": "4.3.5", "3.3": "4.3.6", "3.4": "4.3.7", "3.5": "4.3.8", "3.6": "4.3.10", "3.7": "4.3.10",
       "4": "4.4", "6": "7.4", "7": "8", "1": "1 và 4.1", "2": "4.2", "3": "4.3"}
GRP = {"2.2.1": 1, "2.2.2": 2, "2.2.3": 3, "2.2.4": 4, "2.2.5": 5, "2.2.6": 6}


def sec(m):
    w, n = m.group(1), m.group(2)
    if n in GRP:
        return f"{w} 4.2, nhóm ({GRP[n]})"
    return f"{w} {SEC.get(n, n)}"


TERMS = [(r"\s*\(C-\d+(?:,\s*C-\d+)*\)", ""), (r"\bRegret\b", "Mức hối tiếc"), (r"\bregret\b", "mức hối tiếc"),
         (r"\bCEQ\b", "lợi suất tương đương chắc chắn"), (r"\(MCS, Model Confidence Set\)", ""),
         (r"\bMCS\b", "tập tin cậy mô hình"), (r"\bILLIQ\b", "độ phi thanh khoản"), (r"\s*\(ES\)", ""),
         (r"\bES 95%", "giá trị thiệt hại kỳ vọng mức 95%"), (r"\bHAC\b", "sai số chuẩn bền vững"),
         (r"\bVIF\b", "hệ số phóng đại phương sai"), (r"\bBMA\b", "trung bình hóa mô hình Bayes"),
         (r"\bCAPM\b", "mô hình định giá tài sản vốn"), (r"\bABC-MCMC\b", "phương pháp tính toán Bayes xấp xỉ"),
         (r"đa prior", "với nhiều niềm tin tiên nghiệm"), (r"\s*\(prior\)", ""), (r"\bprior\b", "niềm tin tiên nghiệm"),
         (r"\bbacktest\b", "kiểm định ngược"), (r"\bQ([123])\b", r"Câu hỏi \1"), (r"\bG([1-4])\b", r"khoảng trống (\1)"),
         (r"\bIMF \(2023\)", "Quỹ Tiền tệ Quốc tế (International Monetary Fund, 2023)"), (r"Stress_t", "S_t"),
         (r"\b(mục|Mục) (\d+(?:\.\d+)*)(?![\d.]*\d)", None)]


def fix_old(p, late, gloss=False):
    def ft(m):
        t = m.group(2)
        for a, b in (TERMS[:1] + TERMS[-1:] if gloss else TERMS):
            t = re.sub(a, sec, t) if b is None else re.sub(a, b, t)
        if late:
            t = re.sub(r"\bBảng 4\b", "Bảng 5", t)
        return m.group(1) + t + m.group(3)
    return re.sub(r"(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)", ft, p)


TOCP = ('<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-1" \\h \\z \\u </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>Nhấn chuột phải, chọn Update Field để hiện mục lục.</w:t></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')
import os
TOCE = json.load(open("work/toc.json")) if os.path.exists("work/toc.json") else []
ent = "".join('<w:p><w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="8780"/></w:tabs><w:spacing w:after="60"/><w:ind w:left="0"/><w:jc w:val="left"/></w:pPr>'
              f'<w:r><w:t xml:space="preserve">{esc(h)}</w:t></w:r><w:r><w:tab/></w:r><w:r><w:t>{pg}</w:t></w:r></w:p>' for h, pg in TOCE)
TOCP = ('<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-1" \\h \\z \\u </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r></w:p>' + ent + '<w:p><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')
new_parts = []
last = 0
for i, (a, b) in enumerate(spans):
    new_parts.append(body[last:a])
    p = body[a:b]
    last = b
    if 6 <= i <= 311:
        if i == 6:
            new_parts.append(TOCP)
        continue
    if i >= 3891:  # bỏ thống kê độ dài và danh mục tài liệu tham khảo cho đỡ tốn trang
        continue
    if i not in edits:
        new_parts.append(fix_old(p, i >= 2771, 3417 <= i < 3891) if i >= 312 else p)
        continue
    e = edits[i]
    kind = P[i]["k"]
    if e is None:
        if kind == "T":
            # giữ một đoạn rỗng để ô bảng hợp lệ
            ppr = re.search(r"<w:pPr>.*?</w:pPr>", p, re.S)
            new_parts.append(f"<w:p>{ppr.group(0) if ppr else ''}</w:p>")
        continue
    maths = re.findall(r"<m:oMathPara\b.*?</m:oMathPara>|<m:oMath\b.*?</m:oMath>", p, re.S)
    if e.count("[[CÔNG THỨC]]") != len(maths):
        raise SystemExit(f"đoạn {i}: số [[CÔNG THỨC]] ({e.count('[[CÔNG THỨC]]')}) khác số công thức ({len(maths)})")
    m = re.match(r"(<w:p[^>]*>)", p)
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", p, re.S)
    rprs = re.findall(r"<w:r[ >](?:(?!</w:r>).)*?<w:rPr>(.*?)</w:rPr>", p, re.S)
    nonbold = [r for r in rprs if "<w:b/>" not in r]
    heading = kind.startswith("H")
    base = rprs[0] if heading and rprs else (nonbold[0] if nonbold else (rprs[0] if rprs else ""))
    if not heading:
        base = clean_rpr(base)
    pieces = e.split("[[CÔNG THỨC]]")
    runs = build_runs(pieces[0], base, heading)
    for k, mx in enumerate(maths):
        runs += mx + build_runs(pieces[k + 1], base, heading)
    new_parts.append(m.group(1) + (ppr.group(0) if ppr else "") + runs + "</w:p>")
new_parts.append(body[last:])
body = "".join(new_parts)

# chính tả thống nhất trong mọi nút chữ
SPELL = [(r"(?<![\wÀ-ỹ])lí(?![\wÀ-ỹ])", "lý"), (r"(?<![\wÀ-ỹ])Lí(?![\wÀ-ỹ])", "Lý"),
         (r"(?<![\wÀ-ỹ])kì(?![\wÀ-ỹ])", "kỳ"), (r"(?<![\wÀ-ỹ])Kì(?![\wÀ-ỹ])", "Kỳ"),
         (r"(?<![\wÀ-ỹ])kí(?![\wÀ-ỹ])", "ký"), (r"(?<![\wÀ-ỹ])Kí(?![\wÀ-ỹ])", "Ký"),
         (r"khóan", "khoán"), (r"Khóan", "Khoán")]


def fix_t(m):
    t = m.group(2)
    for a, b in SPELL:
        t = re.sub(a, b, t)
    return m.group(1) + t + m.group(3)


body = re.sub(r"(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)", fix_t, body)
# ký hiệu biến chế độ thống nhất với đề cương mới: Stress_t -> S_t trong công thức
body = re.sub(r"(<m:t(?: [^>]*)?>)Stress(</m:t>)", r"\1S\2", body)
# bỏ các hàng bảng không còn chữ và công thức
body = re.sub(r"<w:tr\b(?:(?!</w:tr>).)*</w:tr>", lambda m: "" if not re.sub(r"<[^>]+>", "", m.group(0)).strip() and "oMath" not in m.group(0) else m.group(0), body, flags=re.S)
open("work/_document.xml", "w", encoding="utf-8").write(head + body)

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
    for it in z.infolist():
        data = z.read(it.filename)
        if it.filename == "word/document.xml":
            data = (head + body).encode()
        zo.writestr(it, data)
print("wrote", out, "edits", len(edits))
