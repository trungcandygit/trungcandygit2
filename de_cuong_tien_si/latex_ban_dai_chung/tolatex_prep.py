"""Chuẩn bị docx cho pandoc: gắn kiểu Heading theo outlineLvl, bỏ bìa và mục lục Word."""
import re, zipfile, sys
src, out = sys.argv[1:3]
z = zipfile.ZipFile(src)
d = z.read("word/document.xml").decode()
i = d.index("<w:body>") + len("<w:body>")
head, body = d[:i], d[i:]
end = body.index('w:fldCharType="end"')
body = body[body.index("</w:p>", end) + 6:]  # bỏ bìa + mục lục
def tag(m):
    p = m.group(0)
    lv = re.search(r'<w:outlineLvl w:val="(\d)"/>', p)
    if lv and "<w:pStyle" not in p:
        p = p.replace("<w:pPr>", f'<w:pPr><w:pStyle w:val="Heading{int(lv.group(1)) + 1}"/>', 1)
    return p
body = re.sub(r"<w:p[ >].*?</w:p>", tag, body, flags=re.S)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
    for it in z.infolist():
        data = z.read(it.filename)
        if it.filename == "word/document.xml":
            data = (head + body).encode()
        zo.writestr(it, data)
