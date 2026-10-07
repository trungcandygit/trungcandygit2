import re
s = open("body.tex", encoding="utf-8").read()
# tiêu đề: bỏ hypertarget, texorpdfstring, \textbf
s = re.sub(r"\\hypertarget\{[^}]*\}\{%\n(\\(?:chapter|section|subsection)\{.*?\})\\label\{[^}]*\}\}", r"\1", s)
s = re.sub(r"\\(chapter|section|subsection)\{\\texorpdfstring\{\\textbf\{(.*?)\}\}\{.*?\}\}", r"\\\1{\2}", s)
# bảng một cột -> khung tcolorbox
def box(m):
    inner = m.group(1).strip()
    inner = re.sub(r"\s*\\\\\s*$", "", inner)
    return "\\begin{tcolorbox}[breakable]\n" + inner + "\n\\end{tcolorbox}"
s = re.sub(r"\\begin\{longtable\}\[\]\{@\{\}\n  >\{\\raggedright\\arraybackslash\}p\{\(\\columnwidth - 0\\tabcolsep\) \* \\real\{1\.0000\}\}@\{\}\}\n\\toprule\\noalign\{\}\n\\endhead\n\\bottomrule\\noalign\{\}\n\\endlastfoot\n(.*?)\\end\{longtable\}", box, s, flags=re.S)
# câu hỏi tự kiểm tra
s = re.sub(r"\\begin\{quote\}\n(.*?)\n\\end\{quote\}", r"{\\itshape \1\\par}", s, flags=re.S)
# bảng nhiều cột: chữ nhỏ hơn một chút
s = s.replace("\\begin{longtable}", "{\\small\\begin{longtable}").replace("\\end{longtable}", "\\end{longtable}}")
s = re.sub(r"\"([^\"\n]*)\"", "\u201c\\1\u201d", s)
s = re.sub(r"(\\chapter\{[^\n]*)", lambda m: m.group(1).replace("β", "beta"), s)
for a, b in (("β", r"\texorpdfstring{$\beta$}{beta}"), ("μ", r"$\mu$"), ("ρ", r"$\rho$")):
    s = s.replace(a, b)
open("body2.tex", "w", encoding="utf-8").write(s)
print(s.count("tcolorbox}[breakable]"), s.count("longtable}"), s.count("\\chapter{"))
