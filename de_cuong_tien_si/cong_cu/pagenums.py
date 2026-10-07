"""Lấy số trang của đề mục, bảng, hình từ bản PDF để điền vào mục lục tĩnh.
Chạy: python3 pagenums.py <pdf> <_headings.json> <pages.json>"""
import json, re, subprocess, sys
pdf, heads, out = sys.argv[1:4]
n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
norm = lambda t: re.sub(r"\s+", " ", t).strip()
pages = [norm(subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), pdf, "-"], capture_output=True, text=True).stdout) for i in range(1, n + 1)]
# trang thân bài bắt đầu ở trang có "4.1. Lý do chọn đề tài" dạng đề mục (sau mục lục)
body = next(i for i, p in enumerate(pages) if "4.1. Lý do chọn đề tài" in p and "Tổ chức đầu tư" in p)
res = {}
for h in json.load(open(heads)):
    key = norm(h)[:60]
    for i in range(body, n):
        flat = pages[i].replace(" ", "")
        if key.replace(" ", "") in flat:
            res[h] = i - body + 1
            break
    else:
        print("không thấy:", h)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=0)
print("body pdf page", body + 1, "entries", len(res))
