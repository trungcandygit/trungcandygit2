"""Bộ kiểm tra proofreading cho văn bản tiếng Việt.

Chuyển thể các nhóm kiểm tra của Academic-Writing-Check (passive, dups, weasel, abbr,
typography) và stop-slop (filler, em dash, câu khung đối lập), cộng thêm:
- tham chiếu trước (nhắc mục/bảng/hình/phương trình chưa xuất hiện);
- đối chiếu trích dẫn trong bài với danh mục tài liệu tham khảo;
- biến thể chính tả (kì/kỳ, lí/lý, hoá/hóa, khóan).
Chạy: python3 proofcheck.py de_cuong.md refs_en.md
"""
import re
import sys
from collections import Counter

md = open(sys.argv[1], encoding="utf-8").read()
refs = open(sys.argv[2], encoding="utf-8").read()
ref_vi = md[md.index("# 11."):]
body = md[:md.index("# 11.")]
issues = []


def report(cat, msg):
    issues.append((cat, msg))


lines = body.split("\n")


def ctx(m, s, w=40):
    a, b = max(0, m.start() - w), min(len(s), m.end() + w)
    return s[a:b].replace("\n", " ")


# 1. Trùng từ liền nhau (dups)
for m in re.finditer(r"\b(\w+) \1\b", body):
    if m.group(1).lower() not in {"từng"}:
        report("dups", ctx(m, body))

# 2. Weasel words / từ đệm cảm tính (weasel, stop-slop filler)
WEASEL = ["rất", "vô cùng", "hết sức", "cực kỳ", "khá", "đáng kể", "nhiều khả năng", "thực sự", "rõ ràng là",
          "không thể phủ nhận", "đóng vai trò then chốt", "then chốt", "vô cùng quan trọng", "cốt lõi",
          "toàn diện", "mang tính đột phá", "đột phá", "sâu sắc", "nổi bật", "hiển nhiên", "chắc chắn rằng",
          "có thể nói", "nhìn chung", "nói chung", "đáng chú ý", "cần lưu ý rằng", "điều quan trọng là",
          "trong bối cảnh hiện nay", "ngày càng", "cấp thiết", "mạnh mẽ"]
for w in WEASEL:
    for m in re.finditer(r"(?<!\w)" + re.escape(w) + r"(?!\w)", body, re.I):
        report("weasel", f"[{w}] " + ctx(m, body))

# 3. Bị động (passive): "được ... bởi", "bị"
for m in re.finditer(r"được[^.]{0,60}?\bbởi\b", body):
    report("passive", ctx(m, body))
cnt_duoc = len(re.findall(r"(?<!\w)được(?!\w)", body))
report("passive-stat", f"số lần 'được': {cnt_duoc}")

# 4. Typography: em dash, khoảng trắng trước dấu câu, dấu ngoặc
for m in re.finditer(r"—", body):
    report("typography", "em dash: " + ctx(m, body))
for m in re.finditer(r" [,.;:)]", body):
    report("typography", "khoảng trắng trước dấu: " + ctx(m, body, 20))
for m in re.finditer(r"\(\s|\s\)", body):
    report("typography", "khoảng trắng trong ngoặc: " + ctx(m, body, 20))
for m in re.finditer(r"\d{4}-\d{4}", body):
    report("typography", "khoảng năm dùng gạch nối thay vì gạch ngang: " + ctx(m, body, 20))
for m in re.finditer(r"\.\.", body):
    report("typography", "hai dấu chấm: " + ctx(m, body, 20))

# 5. Chính tả biến thể
VAR = {r"\bkì\b": "kỳ", r"\blí\b": "lý", r"quản lí": "quản lý", r"khóan": "khoán", r"\bhoá\b": "hóa",
       r"\btoà\b": "tòa", r"\bthuỷ\b": "thủy", r"\bquý\b(?= [IVX]+/)": None, r"\bmô hinh\b": "mô hình",
       r"\bchứng khoáng\b": "chứng khoán"}
for pat, fix in VAR.items():
    if fix is None:
        continue
    for m in re.finditer(pat, body):
        report("spelling", f"-> {fix}: " + ctx(m, body, 25))

# 6. Stop-slop: khung câu đối lập, mở đầu sáo rỗng, câu kết "punchy"
SLOP = [r"không phải là [^,.]{1,40}, mà là", r"không chỉ [^,.]{1,40} mà còn", r"Điều này cho thấy",
        r"Có thể thấy", r"Như vậy,", r"Tóm lại,", r"Nói cách khác,", r"Bên cạnh đó,", r"Ngoài ra,",
        r"Đặc biệt,", r"Hơn nữa,", r"Không những", r"đóng vai trò", r"góp phần", r"nhằm mục đích"]
for pat in SLOP:
    for m in re.finditer(pat, body):
        report("slop", f"[{pat}] " + ctx(m, body))

# 7. Viết tắt: định nghĩa lần đầu
ABBR_OK = {"ISSN", "DOI", "VN", "USD", "VND", "COVID", "SSRN", "OSF", "SR", "TT", "NHNN", "MDPI", "RePEc", "IDEAS",
           "VSTEP", "ASEAN", "FTSE", "LSEG", "ESG", "GRI", "TS", "PGS", "Q1", "Q2", "Q3", "VNU", "IS",
           "TOC", "LOT", "ABBR", "FIGURE", "EQNUM", "II", "III", "IV", "TT", "HĐ", "OECD", "JEBS", "AJEB",
           "FEJM", "FINR", "SFR", "ACCOP", "QTD"}
first = {}
for m in re.finditer(r"\b([A-Z][A-Z0-9\-]{1,}[A-Z0-9])\b", body):
    a = m.group(1)
    if a in ABBR_OK or re.fullmatch(r"[A-Z]\d*", a) or a.startswith("VN") or re.fullmatch(r"M\d|H\d|G\d|Q\d", a):
        continue
    first.setdefault(a, m.start())
for a, pos in sorted(first.items(), key=lambda x: x[1]):
    window = body[max(0, pos - 160):pos + len(a) + 2]
    if f"({a})" not in body[:pos + len(a) + 2] and f"({a}," not in body[:pos + len(a) + 2]:
        report("abbr", f"{a} chưa định nghĩa ở lần đầu: " + body[max(0, pos - 60):pos + 40].replace("\n", " "))

# 8. Tham chiếu trước: Bảng/Hình/mục/phương trình nhắc trước khi xuất hiện
def first_def(pattern):
    m = re.search(pattern, body)
    return m.start() if m else None


for kind, defpat in (("Bảng", r'custom-style="TableCaption"\}\n{0}\. '), ("Hình", r'custom-style="FigureCaption"\}\n{0}\. ')):
    for n in range(1, 10):
        d = first_def(defpat.replace("{0}", f"{kind} {n}"))
        if d is None:
            continue
        for m in re.finditer(rf"{kind} {n}\b", body[:d]):
            near = body[m.end():d]
            # cho phép câu dẫn ngay trước bảng/hình (cách < 600 ký tự, cùng mục)
            if len(near) > 700 or "\n#" in near:
                report("forward-ref", f"{kind} {n} được nhắc trước vị trí của nó: " + ctx(m, body))
for m in re.finditer(r"phương trình \((\d)\)", body):
    d = body.find(f"EQNUM({m.group(1)})")
    if d > m.start():
        report("forward-ref", "phương trình nhắc trước: " + ctx(m, body))
heads = [(m.start(), m.group(1)) for m in re.finditer(r"^#+ (\d+(?:\.\d+)*)\.", body, re.M)]
for m in re.finditer(r"(?:mục|Mục|chương|Chương) (\d+(?:\.\d+)*)", body):
    num = m.group(1)
    pos = next((p for p, h in heads if h == num), None)
    if pos is None:
        report("xref", f"không có mục {num}: " + ctx(m, body))
    elif pos > m.start():
        report("forward-ref", f"mục {num} nhắc trước: " + ctx(m, body))

# 9. Đối chiếu trích dẫn
reflist = re.findall(r'custom-style="Reference"\}\n(.*?)\n:::', refs + ref_vi, re.S)
keys = []
for r in reflist:
    m = re.match(r"(.+?)\s\((\d{4}[ab]?)\)", r)
    if not m:
        report("ref-format", r[:80]); continue
    authors, year = m.group(1), m.group(2)
    first_author = re.split(r",|\s", authors.strip())[0]
    if authors.startswith("Board of Governors"):
        first_author = "Board of Governors"
    if authors.startswith("International Monetary"):
        first_author = "IMF"
    if authors.startswith("Ngân hàng Nhà nước"):
        first_author = "Ngân hàng Nhà nước"
    if authors.startswith("Nguyễn Thanh Bình"):
        first_author = "Nguyễn"
    keys.append((first_author, year, r[:70]))
for fa, yr, r in keys:
    pat = re.escape(fa) + r"[^()]{0,80}?" + yr[:4]
    if fa == "Board of Governors":
        ok = re.search(r"Board of Governors of the Federal Reserve System, 2011", body) and (yr != "2026" or "2011; 2026" in body)
    elif fa == "IMF":
        ok = "IMF, 2023" in body
    else:
        ok = re.search(pat, body) or re.search(re.escape(fa) + r".{0,120}" + re.escape(yr), body, re.S)
    if not ok:
        report("cite", f"Tài liệu không được trích trong bài: {r}")
cites = set(re.findall(r"([A-ZĐ][\w\-éóá]+)(?: và cộng sự| và [A-ZĐ][\w\-éóá ]+?)?,? \(?(\d{4}[ab]?)\)?", body))
reftext = refs + ref_vi
for a, y in sorted(cites):
    if a in {"Bảng", "Hình", "Năm", "Quý", "Thông", "Giai", "Tập", "Cục", "Mục", "Giải", "Theo", "Ngày", "Phụ", "Trong", "Sau",
             "Từ", "Đề", "Khung", "Chỉ", "Nguồn", "Ở", "Với", "Tại", "Thí", "So", "Khi", "Kết", "Năm", "Bài", "Ước"}:
        continue
    if not re.search(re.escape(a) + r".{0,200}?\(" + re.escape(y) + r"\)", reftext, re.S):
        report("cite", f"Trích dẫn không có trong danh mục: {a} {y}")

cat = Counter(c for c, _ in issues)
for c, msg in issues:
    print(f"[{c}] {msg}")
print("\nTỔNG:", dict(cat))
