"""In một chương với [M] đánh dấu đúng từng công thức: python3 view.py START END"""
import json, re, sys, zipfile
P = json.load(open("work/paras.json"))
d = zipfile.ZipFile("in/goc.docx").read("word/document.xml").decode()
body = d[d.index("<w:body>"):]
sp = [m.group(0) for m in re.finditer(r"<w:p[ >].*?</w:p>", body, re.S)]
a, b = int(sys.argv[1]), int(sys.argv[2])
for i in range(a, b):
    if "oMath" in sp[i]:
        t = re.sub(r"<m:oMathPara\b.*?</m:oMathPara>|<m:oMath\b.*?</m:oMath>",
                   lambda m: "[M:" + re.sub(r"<[^>]+>", "", m.group(0)) + "]", sp[i], flags=re.S)
        t = re.sub(r"<w:pPr>.*?</w:pPr>", "", t, flags=re.S)
        t = re.sub(r"<[^>]+>", "", t)
    else:
        t = P[i]["t"]
    print(f"[{i}|{P[i]['k']}] {t}")
