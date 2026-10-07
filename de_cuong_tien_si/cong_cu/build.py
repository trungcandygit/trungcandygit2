"""Dựng đề cương .docx: pandoc + hậu xử lý OOXML.

- Bìa theo mẫu DEM D2.2026 (logo, tên đề tài, thông tin thí sinh).
- Mục lục, danh mục bảng, danh mục hình là trường TOC của Word; kết quả tĩnh lấy
  từ số trang của bản render (tệp pages.json) để mở ra đã có số trang.
- Hình 1, 2 là nhóm Shape gốc của Word, style mặc định (theme accent1).
- Hình 3 là SmartArt thật (Vertical Block List, quick style simple1, màu accent1_2).

Chạy: python3 build.py <thư mục work> <out.docx> [pages.json]
"""
import html
import json
import re
import shutil
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path

WORK = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
PAGES = json.loads(Path(sys.argv[3]).read_text()) if len(sys.argv) > 3 and Path(sys.argv[3]).exists() else {}
LOGO = WORK.parent / "in/media_M7/media/image1.png"

CM = 360000  # EMU / cm


def esc(s):
    return html.escape(s, quote=False)


# --------------------------------------------------------------------------- pandoc
md = (WORK / "de_cuong.md").read_text(encoding="utf-8")
md = md.replace("REFS_EN", (WORK / "refs_en.md").read_text(encoding="utf-8"))
(WORK / "_full.md").write_text(md, encoding="utf-8")
raw = WORK / "_raw.docx"
subprocess.run(["pandoc", str(WORK / "_full.md"), "-f", "markdown+subscript+superscript",
                "-o", str(raw), "--reference-doc", str(WORK / "reference.docx")], check=True)

tmp = WORK / "_docx"
if tmp.exists():
    shutil.rmtree(tmp)
with zipfile.ZipFile(raw) as z:
    z.extractall(tmp)
doc = (tmp / "word/document.xml").read_text(encoding="utf-8")
rels = (tmp / "word/_rels/document.xml.rels").read_text(encoding="utf-8")
ctypes = (tmp / "[Content_Types].xml").read_text(encoding="utf-8")

NS = {
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "dgm": "http://schemas.openxmlformats.org/drawingml/2006/diagram",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
}
root_m = re.search(r"<w:document[^>]*>", doc)
root = root_m.group(0)
add = "".join(f' xmlns:{k}="{v}"' for k, v in NS.items() if f"xmlns:{k}=" not in root)
new_root = root[:-1] + add
if "mc:Ignorable" not in new_root:
    new_root += ' mc:Ignorable="w14 wp14"'
doc = doc.replace(root, new_root + ">", 1)

_rid = [100]


def new_rel(rtype, target):
    global rels
    _rid[0] += 1
    rid = f"rIdX{_rid[0]}"
    rels = rels.replace("</Relationships>",
                        f'<Relationship Id="{rid}" Type="{rtype}" Target="{target}"/></Relationships>')
    return rid


def add_ctype(part, ctype):
    global ctypes
    ctypes = ctypes.replace("</Types>", f'<Override PartName="{part}" ContentType="{ctype}"/></Types>')


def para_containing(token):
    m = re.search(r"<w:p>(?:(?!<w:p>).)*?" + re.escape(token) + r".*?</w:p>", doc, re.S)
    if not m:
        m = re.search(r"<w:p [^>]*>(?:(?!<w:p[ >]).)*?" + re.escape(token) + r".*?</w:p>", doc, re.S)
    assert m, token
    return m.group(0)


def replace_para(token, new_xml):
    global doc
    doc = doc.replace(para_containing(token), new_xml, 1)


# --------------------------------------------------------------------------- helpers
def run(text, b=False, i=False, sz=None, sub=False, color=None, caps=False):
    rpr = ""
    if b:
        rpr += "<w:b/><w:bCs/>"
    if i:
        rpr += "<w:i/><w:iCs/>"
    if caps:
        rpr += "<w:caps/>"
    if color:
        rpr += f'<w:color w:val="{color}"/>'
    if sz:
        rpr += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    if sub:
        rpr += '<w:vertAlign w:val="subscript"/>'
    return f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


def rich(text, **kw):
    """'H_1' -> H với chỉ số dưới 1; '_x' dạng ký hiệu ngắn."""
    out = []
    for part in re.split(r"(_\{[^}]*\}|_[A-Za-z0-9])", text):
        if not part:
            continue
        if part.startswith("_"):
            out.append(run(part[1:].strip("{}"), sub=True, **kw))
        else:
            out.append(run(part, **kw))
    return "".join(out)


def p(content, jc="center", style=None, before=0, after=0, line=240, ind0=True, keep=False):
    ps = f'<w:pStyle w:val="{style}"/>' if style else ""
    k = "<w:keepNext/>" if keep else ""
    ind = '<w:ind w:firstLine="0"/>' if ind0 else ""
    return (f'<w:p><w:pPr>{ps}{k}<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="auto"/>'
            f'{ind}<w:jc w:val="{jc}"/></w:pPr>{content}</w:p>')


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


_docpr = [500]


def docpr_id():
    _docpr[0] += 1
    return _docpr[0]


# --------------------------------------------------------------------------- Word shapes
DEFAULT_STYLE = ('<wps:style><a:lnRef idx="2"><a:schemeClr val="{c}"><a:shade val="50000"/></a:schemeClr></a:lnRef>'
                 '<a:fillRef idx="1"><a:schemeClr val="{c}"/></a:fillRef><a:effectRef idx="0"><a:schemeClr val="{c}"/></a:effectRef>'
                 '<a:fontRef idx="minor"><a:schemeClr val="lt1"/></a:fontRef></wps:style>')
LINE_STYLE = ('<wps:style><a:lnRef idx="1"><a:schemeClr val="accent1"/></a:lnRef><a:fillRef idx="0"><a:schemeClr val="accent1"/></a:fillRef>'
              '<a:effectRef idx="0"><a:schemeClr val="accent1"/></a:effectRef><a:fontRef idx="minor"><a:schemeClr val="tx1"/></a:fontRef></wps:style>')


def txbx_paras(lines, color=None, sz=22):
    """lines: list of (text, bold)."""
    out = []
    for t, bold in lines:
        out.append(f'<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
                   f'<w:ind w:firstLine="0"/><w:jc w:val="center"/></w:pPr>{rich(t, b=bold, sz=sz, color=color)}</w:p>')
    return "".join(out)


class Group:
    def __init__(self, w_cm, h_cm):
        self.w, self.h = int(w_cm * CM), int(h_cm * CM)
        self.items = []
        self.n = 0

    def _id(self):
        self.n += 1
        return self.n

    def box(self, x, y, w, h, lines, prst="rect", scheme="accent1", sz=22, default_style=True):
        x, y, w, h = (int(v * CM) for v in (x, y, w, h))
        sid = self._id()
        if default_style:
            sppr = f'<a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>'
            style = DEFAULT_STYLE.format(c=scheme)
            body = txbx_paras(lines, color="000000" if scheme == "accent2" else "FFFFFF", sz=sz)
        else:  # nhãn chữ: không nền, không viền (hộp văn bản trong suốt)
            sppr = f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln>'
            style = ""
            body = txbx_paras(lines, sz=sz)
        self.items.append(
            f'<wps:wsp><wps:cNvPr id="{sid}" name="Shape {sid}"/><wps:cNvSpPr/>'
            f'<wps:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>{sppr}</wps:spPr>'
            f'{style}<wps:txbx><w:txbxContent>{body}</w:txbxContent></wps:txbx>'
            f'<wps:bodyPr rot="0" vert="horz" wrap="square" lIns="54000" tIns="36000" rIns="54000" bIns="36000" anchor="ctr" anchorCtr="0"><a:noAutofit/></wps:bodyPr></wps:wsp>')

    def arrow(self, x1, y1, x2, y2, dash=False, head=True):
        flipH = x2 < x1
        flipV = y2 < y1
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)
        x, y, w, h = (int(v * CM) for v in (x, y, w, h))
        sid = self._id()
        flips = (' flipH="1"' if flipH else "") + (' flipV="1"' if flipV else "")
        d = '<a:prstDash val="dash"/>' if dash else ""
        tail = '<a:tailEnd type="triangle"/>' if head else ""
        self.items.append(
            f'<wps:wsp><wps:cNvPr id="{sid}" name="Connector {sid}"/><wps:cNvCnPr/>'
            f'<wps:spPr><a:xfrm{flips}><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'<a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom><a:ln w="12700">{d}{tail}</a:ln></wps:spPr>'
            f'{LINE_STYLE}<wps:bodyPr/></wps:wsp>')

    def xml(self, name):
        did = docpr_id()
        inner = "".join(self.items)
        return (f'<w:r><mc:AlternateContent><mc:Choice Requires="wpg"><w:drawing>'
                f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{self.w}" cy="{self.h}"/>'
                f'<wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="{did}" name="{esc(name)}"/><wp:cNvGraphicFramePr/>'
                f'<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup">'
                f'<wpg:wgp><wpg:cNvGrpSpPr/><wpg:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{self.w}" cy="{self.h}"/>'
                f'<a:chOff x="0" y="0"/><a:chExt cx="{self.w}" cy="{self.h}"/></a:xfrm></wpg:grpSpPr>{inner}</wpg:wgp>'
                f'</a:graphicData></a:graphic></wp:inline></w:drawing></mc:Choice>'
                f'<mc:Fallback><w:t>[{esc(name)}]</w:t></mc:Fallback></mc:AlternateContent></w:r>')


def figure_framework():
    g = Group(15.4, 8.4)
    bw, bh, y0 = 4.4, 3.3, 0.0
    xs = (0.0, 5.5, 11.0)
    g.box(xs[0], y0, bw, bh, [("Chế độ thị trường", True), ("Chế độ bình thường", False),
                              ("Chế độ căng thẳng", False), ("(biến S_t)", False)])
    g.box(xs[1], y0, bw, bh, [("Rủi ro lựa chọn mô hình", True), ("Mức hối tiếc R_t", False),
                              ("Độ phân tán D_t", False), ("Tập tin cậy mô hình", False)])
    g.box(xs[2], y0, bw, bh, [("Kết quả danh mục", True), ("Lợi suất tương đương chắc chắn", False),
                              ("Độ sụt giảm tối đa", False), ("Thiệt hại kỳ vọng, vòng quay", False)])
    yc = y0 + bh / 2
    m1 = (xs[0] + bw + xs[1]) / 2
    m2 = (xs[1] + bw + xs[2]) / 2
    g.arrow(xs[0] + bw, yc, xs[1], yc)
    g.arrow(xs[1] + bw, yc, xs[2], yc, dash=True)
    by, bh2, bw2 = 5.0, 3.3, 5.2
    g.box(m1 - bw2 / 2, by, bw2, bh2, [("Biến kênh", True), ("Biến động thực hiện (kiểm soát)", False),
                                      ("Phi thanh khoản, tương quan đuôi", False), ("Phân tán chéo (thăm dò)", False)])
    g.box(m2 - bw2 / 2, by, bw2, bh2, [("Cơ chế giảm thiểu", True), ("Kết hợp mô hình", False),
                                      ("Danh mục vững chắc", False), ("Quy tắc theo chế độ", False)])
    g.arrow(m1, by, m1, yc)
    g.arrow(m2, by, m2, yc)
    g.box(m1 - 0.6, yc - 0.85, 1.2, 0.6, [("H_1", True)], default_style=False, sz=22)
    g.box(m1 + 0.05, 3.7, 1.9, 0.6, [("H_2, H_4", True)], default_style=False, sz=22)
    g.box(m2 + 0.05, 3.7, 1.2, 0.6, [("H_3", True)], default_style=False, sz=22)
    return g.xml("Hình 1. Khung phân tích")


def figure_windows():
    g = Group(15.4, 6.2)
    left, est, ev, rh, gap = 2.4, 7.0, 1.75, 0.95, 0.35
    rows = 3
    for k in range(rows):
        y = k * (rh + gap)
        x = left + k * ev
        g.box(0, y, left - 0.15, rh, [(f"Cửa sổ {k + 1}", False)], default_style=False, sz=20)
        g.box(x, y, est, rh, [("Ước lượng: 104 tuần", False)], sz=20)
        g.box(x + est, y, ev, rh, [("Đánh giá:", False), ("6 tháng", False)], scheme="accent2", sz=16)
    ty = rows * (rh + gap) + 0.15
    g.arrow(left, ty, 15.3, ty)
    g.box(13.3, ty + 0.05, 2.0, 0.5, [("thời gian", False)], default_style=False, sz=18)
    for k in range(rows):
        x = left + est + k * ev
        g.arrow(x, ty + 0.7, x, ty + 0.05)
    g.box(left + 0.5, ty + 0.75, 11.0, 1.25,
          [("Đầu mỗi cửa sổ đánh giá: chọn trước mô hình c có lợi suất tương đương", False),
           ("chắc chắn cao nhất trong 36 tháng trước; mức hối tiếc R_t tính trên cửa sổ đó", False)], default_style=False, sz=19)
    return g.xml("Hình 2. Thiết kế cửa sổ")


# --------------------------------------------------------------------------- SmartArt
def guid():
    return "{" + str(uuid.uuid4()).upper() + "}"


def smartart_vlist5(items):
    """items: [(tiêu đề cấp 1, [các dòng cấp 2])] -> data model đầy đủ (gồm điểm trình bày)."""
    LO = "urn:microsoft.com/office/officeart/2005/8/layout/vList5"
    pts, cxns = [], []
    docid = guid()
    pts.append(f'<dgm:pt modelId="{docid}" type="doc"><dgm:prSet loTypeId="{LO}" loCatId="list" '
               'qsTypeId="urn:microsoft.com/office/officeart/2005/8/quickstyle/simple1" qsCatId="simple" '
               'csTypeId="urn:microsoft.com/office/officeart/2005/8/colors/accent1_2" csCatId="accent1" phldr="0"/>'
               '<dgm:spPr/><dgm:t><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="vi-VN"/></a:p></dgm:t></dgm:pt>')

    def text_pt(mid, txt):
        return (f'<dgm:pt modelId="{mid}"><dgm:prSet phldrT="[Text]"/><dgm:spPr/><dgm:t><a:bodyPr/><a:lstStyle/>'
                f'<a:p><a:r><a:rPr lang="vi-VN"/><a:t>{esc(txt)}</a:t></a:r></a:p></dgm:t></dgm:pt>')

    def trans(parent, child, srcord):
        cx, pt_, st = guid(), guid(), guid()
        pts.append(f'<dgm:pt modelId="{pt_}" type="parTrans" cxnId="{cx}"><dgm:prSet/><dgm:spPr/>'
                   '<dgm:t><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="vi-VN"/></a:p></dgm:t></dgm:pt>')
        pts.append(f'<dgm:pt modelId="{st}" type="sibTrans" cxnId="{cx}"><dgm:prSet/><dgm:spPr/>'
                   '<dgm:t><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="vi-VN"/></a:p></dgm:t></dgm:pt>')
        cxns.append(f'<dgm:cxn modelId="{cx}" srcId="{parent}" destId="{child}" srcOrd="{srcord}" destOrd="0" '
                    f'parTransId="{pt_}" sibTransId="{st}"/>')
        return st

    nodes = []
    for i, (title, children) in enumerate(items):
        nid = guid()
        pts.append(text_pt(nid, title))
        sib = trans(docid, nid, i)
        kids = []
        for j, c in enumerate(children):
            cid = guid()
            pts.append(text_pt(cid, c))
            trans(nid, cid, j)
            kids.append(cid)
        nodes.append((nid, sib, kids))

    n = len(nodes)
    nk = sum(1 for _, _, k in nodes if k)
    name0 = guid()
    pts.append(f'<dgm:pt modelId="{name0}" type="pres"><dgm:prSet presAssocID="{docid}" presName="Name0" presStyleCnt="0">'
               '<dgm:presLayoutVars><dgm:dir/><dgm:animLvl val="lvl"/><dgm:resizeHandles val="exact"/></dgm:presLayoutVars>'
               '</dgm:prSet><dgm:spPr/></dgm:pt>')

    def presof(src, dst, so=0, do=0):
        cxns.append(f'<dgm:cxn modelId="{guid()}" type="presOf" srcId="{src}" destId="{dst}" srcOrd="{so}" destOrd="{do}" presId="{LO}"/>')

    def presparof(src, dst, so):
        cxns.append(f'<dgm:cxn modelId="{guid()}" type="presParOf" srcId="{src}" destId="{dst}" srcOrd="{so}" destOrd="0" presId="{LO}"/>')

    presof(docid, name0)
    order = 0
    kidx = 0
    for i, (nid, sib, kids) in enumerate(nodes):
        lin, par = guid(), guid()
        pts.append(f'<dgm:pt modelId="{lin}" type="pres"><dgm:prSet presAssocID="{nid}" presName="linNode" presStyleCnt="0"/><dgm:spPr/></dgm:pt>')
        pts.append(f'<dgm:pt modelId="{par}" type="pres"><dgm:prSet presAssocID="{nid}" presName="parentText" presStyleLbl="node1" '
                   f'presStyleIdx="{i}" presStyleCnt="{n}"><dgm:presLayoutVars><dgm:chMax val="1"/><dgm:bulletEnabled val="1"/>'
                   '</dgm:presLayoutVars></dgm:prSet><dgm:spPr/></dgm:pt>')
        presparof(name0, lin, order); order += 1
        presparof(lin, par, 0)
        presof(nid, par)
        if kids:
            des = guid()
            pts.append(f'<dgm:pt modelId="{des}" type="pres"><dgm:prSet presAssocID="{nid}" presName="descendantText" '
                       f'presStyleLbl="alignAccFollowNode1" presStyleIdx="{kidx}" presStyleCnt="{nk}"><dgm:presLayoutVars>'
                       '<dgm:bulletEnabled val="1"/></dgm:presLayoutVars></dgm:prSet><dgm:spPr/></dgm:pt>')
            kidx += 1
            presparof(lin, des, 1)
            for j, c in enumerate(kids):
                presof(c, des, 0, j)
        if i < n - 1:
            sp = guid()
            pts.append(f'<dgm:pt modelId="{sp}" type="pres"><dgm:prSet presAssocID="{sib}" presName="sp" presStyleCnt="0"/><dgm:spPr/></dgm:pt>')
            presparof(name0, sp, order); order += 1

    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<dgm:dataModel xmlns:dgm="{NS["dgm"]}" xmlns:a="{NS["a"]}"><dgm:ptLst>{"".join(pts)}</dgm:ptLst>'
            f'<dgm:cxnLst>{"".join(cxns)}</dgm:cxnLst><dgm:bg/><dgm:whole/></dgm:dataModel>')


def figure_process_smartart():
    items = [
        ("Bước 1. Dữ liệu", ["Giá điều chỉnh, khối lượng, lãi suất phi rủi ro",
                             "Rổ 30 cổ phiếu xác định tại từng ngày tái cân bằng"]),
        ("Bước 2. Chế độ thị trường", ["Mô hình chuyển chế độ Markov, cửa sổ mở rộng",
                                       "Xác suất lọc của chế độ căng thẳng tại ngày t"]),
        ("Bước 3. Tập bảy mô hình", ["Đăng ký trước: cửa sổ, siêu tham số, ngưỡng, quy tắc kết luận",
                                     "Ước lượng M1 đến M7, tái cân bằng hằng tháng"]),
        ("Bước 4. Đo lường và kiểm định", ["Mức hối tiếc, độ phân tán, tập tin cậy mô hình",
                                           "Hồi quy, phân phối rỗng bootstrap: H1, H2, H4"]),
        ("Bước 5. Cơ chế giảm thiểu", ["Kết hợp mô hình, danh mục vững chắc, quy tắc chế độ",
                                       "So sánh sau chi phí giao dịch: H3"]),
    ]
    dgm_dir = tmp / "word/diagrams"
    dgm_dir.mkdir(exist_ok=True)
    (dgm_dir / "data1.xml").write_text(smartart_vlist5(items), encoding="utf-8")
    for nm in ("layout1", "quickStyle1", "colors1"):
        shutil.copy(WORK / "smartart" / f"{nm}.xml", dgm_dir / f"{nm}.xml")
    base = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
    dm = new_rel(base + "diagramData", "diagrams/data1.xml")
    lo = new_rel(base + "diagramLayout", "diagrams/layout1.xml")
    qs = new_rel(base + "diagramQuickStyle", "diagrams/quickStyle1.xml")
    cs = new_rel(base + "diagramColors", "diagrams/colors1.xml")
    ct = "application/vnd.openxmlformats-officedocument.drawingml."
    add_ctype("/word/diagrams/data1.xml", ct + "diagramData+xml")
    add_ctype("/word/diagrams/layout1.xml", ct + "diagramLayout+xml")
    add_ctype("/word/diagrams/quickStyle1.xml", ct + "diagramStyle+xml")
    add_ctype("/word/diagrams/colors1.xml", ct + "diagramColors+xml")
    did = docpr_id()
    return (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{int(15.4 * CM)}" cy="{int(10.0 * CM)}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
            f'<wp:docPr id="{did}" name="Hình 3. Quy trình (SmartArt)"/><wp:cNvGraphicFramePr/>'
            f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/diagram">'
            f'<dgm:relIds r:dm="{dm}" r:lo="{lo}" r:qs="{qs}" r:cs="{cs}"/></a:graphicData></a:graphic>'
            f'</wp:inline></w:drawing></w:r>')




def fix_equations(d):
    def repl(m):
        para = m.group(0)
        para = re.sub(r"<m:oMathPara>(?:<m:oMathParaPr>.*?</m:oMathParaPr>)?(.*?)</m:oMathPara>", r"\1", para, flags=re.S)
        para = re.sub(r"(<w:pPr>.*?</w:pPr>)", r'\1<w:r><w:tab/></w:r>', para, count=1, flags=re.S)
        para = re.sub(r'<w:r>(?:(?!<w:r>).)*?EQNUM\((\d+)\)</w:t></w:r>', r'<w:r><w:tab/><w:t>(\1)</w:t></w:r>', para, flags=re.S)
        return para
    return re.sub(r'<w:p>(?:(?!<w:p>).)*?<w:pStyle w:val="Equation" ?/>.*?</w:p>', repl, d, flags=re.S)


doc = fix_equations(doc)


def fix_tables(d):
    def tbl(m):
        t = m.group(0)
        first = [True]

        def tr(mm):
            props = "<w:cantSplit/>" + ("<w:tblHeader/>" if first[0] else "")
            first[0] = False
            return "<w:tr><w:trPr>" + props + "</w:trPr>"
        t = re.sub(r"<w:tr>(?:<w:trPr>.*?</w:trPr>)?", tr, t, flags=re.S)
        return t
    return re.sub(r"<w:tbl>.*?</w:tbl>", tbl, d, flags=re.S)


doc = fix_tables(doc)


def fix_schema(d):
    d = re.sub(r"<w:sectPr ?/>", "", d)
    d = re.sub(r'(<w:tblPr>.*?)<w:jc w:val="[^"]*" ?/>(.*?</w:tblPr>)', r"\1\2", d, flags=re.S)
    d = re.sub(r'<m:endChr ([^>]*)/><m:sepChr ([^>]*)/>', r'<m:sepChr \2/><m:endChr \1/>', d)
    return d


doc = fix_schema(doc)
FIG_P = '<w:p><w:pPr><w:pStyle w:val="FigureBox"/></w:pPr>{}</w:p>'
replace_para("FIGURE_1", FIG_P.format(figure_framework()))
replace_para("FIGURE_2", FIG_P.format(figure_windows()))
replace_para("FIGURE_3", FIG_P.format(figure_process_smartart()))

# --------------------------------------------------------------------------- bìa
shutil.copy(LOGO, tmp / "word/media_logo.png")
logo_rid = new_rel("http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", "media_logo.png")
if 'Extension="png"' not in ctypes:
    ctypes = ctypes.replace("</Types>", '<Default Extension="png" ContentType="image/png"/></Types>')
lw = int(3.2 * CM)
lh = int(lw * 9.58 / 6.40)  # tỉ lệ ảnh gốc 6.40 x 9.58 in? (giữ theo tỉ lệ thực bên dưới)
from struct import unpack
with open(LOGO, "rb") as f:
    f.read(16)
    pw, ph = unpack(">II", f.read(8))
lh = int(lw * ph / pw)
logo = (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{lw}" cy="{lh}"/>'
        f'<wp:docPr id="{docpr_id()}" name="Logo VNU-IS"/><wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>'
        f'<pic:nvPicPr><pic:cNvPr id="0" name="logo.png"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{logo_rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{lw}" cy="{lh}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        f'</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')

TITLE = "RỦI RO LỰA CHỌN MÔ HÌNH TRONG QUẢN TRỊ DANH MỤC ĐẦU TƯ THEO CHẾ ĐỘ THỊ TRƯỜNG: BẰNG CHỨNG TỪ THỊ TRƯỜNG CHỨNG KHOÁN VIỆT NAM"
cover = "".join([
    p(run("ĐẠI HỌC QUỐC GIA HÀ NỘI", sz=26), after=0),
    p(run("TRƯỜNG QUỐC TẾ", b=True, sz=26), after=240),
    p(logo, after=480),
    p(run("Tên đề cương nghiên cứu:", sz=26), after=120),
    p(run(TITLE, b=True, sz=28), after=480, line=300),
    p(run("ĐỀ CƯƠNG NGHIÊN CỨU", b=True, sz=32), after=360),
    p(run("Chuyên ngành: Kinh tế và Quản lý", sz=26)),
    p(run("Mã số: 9310116.01QTD", sz=26), after=360),
    p(run("Họ và tên thí sinh: ", sz=26) + run("NGUYỄN VĂN TRUNG", b=True, sz=26), after=120),
    p(run("Cơ quan công tác: ……………………………………", sz=26), after=360),
    p(run("Người hướng dẫn khoa học (dự kiến):", sz=26), after=60),
    p(run("- ……………………………………", sz=26)),
    p(run("- ……………………………………", sz=26), after=1200),
    p(run("HÀ NỘI – 2026", b=True, sz=26)),
])

# --------------------------------------------------------------------------- mục lục & danh mục
def plain(xml):
    t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml))
    return html.unescape(t)


headings = []
for m in re.finditer(r'<w:p>(?:(?!<w:p>).)*?<w:pStyle w:val="(Heading[123]|TableCaption|FigureCaption)" ?/>.*?</w:p>', doc, re.S):
    headings.append((m.group(1), plain(m.group(0)).strip()))

_bm = [0]


def toc_block(title, instr, entries):
    """entries: list of (level, text, style). Kết quả tĩnh, Word sẽ cập nhật."""
    out = [p(run(title, b=True, sz=26), before=0, after=240, jc="center")]
    first = True
    for lvl, text, style in entries:
        pg = PAGES.get(text, "")
        fld_begin = ""
        if first:
            fld_begin = (f'<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> {instr} </w:instrText></w:r>'
                         '<w:r><w:fldChar w:fldCharType="separate"/></w:r>')
            first = False
        out.append(f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>{fld_begin}'
                   f'{run(text)}<w:r><w:tab/></w:r>{run(str(pg))}</w:p>')
    out.append('<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="120" w:lineRule="auto"/></w:pPr><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')
    return "".join(out)


toc_entries = [(int(k[-1]), t, f"TOC{k[-1]}") for k, t in headings if k.startswith("Heading")]
tab_entries = [(1, t, "TableofFigures") for k, t in headings if k == "TableCaption"]
fig_entries = [(1, t, "TableofFigures") for k, t in headings if k == "FigureCaption"]

toc = toc_block("MỤC LỤC", 'TOC \\o "1-3" \\h \\z \\u', toc_entries)
lot = (toc_block("DANH MỤC BẢNG", 'TOC \\h \\z \\t "Table Caption,1"', tab_entries)
       + toc_block("DANH MỤC HÌNH", 'TOC \\h \\z \\t "Figure Caption,1"', fig_entries))

ABBR = [
    ("ABC-MCMC", "Tính toán Bayes xấp xỉ kết hợp Monte Carlo chuỗi Markov (Approximate Bayesian Computation - Markov Chain Monte Carlo)"),
    ("ARIMA", "Mô hình tự hồi quy trung bình trượt tích hợp (Autoregressive Integrated Moving Average)"),
    ("BMA", "Trung bình hóa mô hình Bayes (Bayesian Model Averaging)"),
    ("CAPM", "Mô hình định giá tài sản vốn (Capital Asset Pricing Model)"),
    ("CEQ", "Mức thỏa dụng tương đương chắc chắn (Certainty-Equivalent Return)"),
    ("CPI", "Chỉ số giá tiêu dùng (Consumer Price Index)"),
    ("ES", "Giá trị thiệt hại kỳ vọng (Expected Shortfall)"),
    ("HAC", "Sai số chuẩn bền với phương sai thay đổi và tự tương quan (Heteroskedasticity and Autocorrelation Consistent)"),
    ("HOSE", "Sở Giao dịch Chứng khoán Thành phố Hồ Chí Minh"),
    ("ILLIQ", "Độ phi thanh khoản của Amihud (Amihud Illiquidity)"),
    ("IMF", "Quỹ Tiền tệ Quốc tế (International Monetary Fund)"),
    ("MCS", "Tập tin cậy mô hình (Model Confidence Set)"),
    ("OSF", "Open Science Framework"),
    ("VIF", "Hệ số phóng đại phương sai (Variance Inflation Factor)"),
]


def abbr_table():
    rows = []
    for i, (a, b) in enumerate([("Chữ viết tắt", "Nghĩa đầy đủ")] + ABBR):
        bold = i == 0
        cells = ""
        for txt, wdt in ((a, 2000), (b, 6778)):
            cells += (f'<w:tc><w:tcPr><w:tcW w:w="{wdt}" w:type="dxa"/></w:tcPr><w:p><w:pPr><w:pStyle w:val="Compact"/></w:pPr>'
                      f'{run(txt, b=bold)}</w:p></w:tc>')
        rows.append(f"<w:tr>{cells}</w:tr>")
    return (p(run("DANH MỤC CHỮ VIẾT TẮT", b=True, sz=26), after=240) +
            '<w:tbl><w:tblPr><w:tblStyle w:val="Table"/><w:tblW w:w="8778" w:type="dxa"/>'
            '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
            '<w:tblGrid><w:gridCol w:w="2000"/><w:gridCol w:w="6778"/></w:tblGrid>' + "".join(rows) + "</w:tbl>")


# --------------------------------------------------------------------------- phân đoạn & số trang
footer_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              f'<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:pStyle w:val="Footer"/><w:jc w:val="center"/></w:pPr>'
              '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
              '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')
empty_footer = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:pStyle w:val="Footer"/></w:pPr></w:p></w:ftr>')
(tmp / "word/footer1.xml").write_text(footer_xml, encoding="utf-8")
(tmp / "word/footer0.xml").write_text(empty_footer, encoding="utf-8")
FT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
f1 = new_rel(FT, "footer1.xml")
f0 = new_rel(FT, "footer0.xml")
add_ctype("/word/footer1.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml")
add_ctype("/word/footer0.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml")

PG = ('<w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1984" '
      'w:header="567" w:footer="567" w:gutter="0"/><w:cols w:space="720"/><w:docGrid w:linePitch="360"/>')


def sect(footer_rid, fmt=None, start=None, last=False):
    num = ""
    if fmt or start:
        num = "<w:pgNumType" + (f' w:fmt="{fmt}"' if fmt else "") + (f' w:start="{start}"' if start else "") + "/>"
    s = f'<w:sectPr><w:footerReference w:type="default" r:id="{footer_rid}"/>{PG[:PG.index("<w:cols")]}{num}{PG[PG.index("<w:cols"):]}</w:sectPr>'
    if last:
        return s
    return f"<w:p><w:pPr>{s}</w:pPr></w:p>"


# đoạn mở đầu (mục 1-3) đứng trước TOC_PLACEHOLDER trong pandoc output
body_m = re.search(r"<w:body>(.*)</w:body>", doc, re.S)
body = body_m.group(1)
body = re.sub(r"<w:sectPr.*?</w:sectPr>\s*$", "", body, flags=re.S)
toc_para = para_containing("TOC_PLACEHOLDER")
i = body.index(toc_para)
front_items = body[:i]
rest = body[i:]
lot = lot.replace("<w:pPr>", "<w:pPr><w:pageBreakBefore/>", 1)
rest = rest.replace(toc_para, toc, 1)
rest = rest.replace(para_containing("LOT_PLACEHOLDER"), lot, 1)

lot_end = rest.index(lot) + len(lot)
front2 = rest[:lot_end]
main = rest[lot_end:]

sign = "".join([
    p("", after=240),
    p(run("Hà Nội, ngày 30 tháng 9 năm 2026", i=True), jc="right", after=60),
    p(run("NGƯỜI DỰ TUYỂN", b=True), jc="right", after=0),
    p(run("(Ký và ghi rõ họ tên)", i=True), jc="right", after=1200),
    p(run("Nguyễn Văn Trung", b=True), jc="right"),
])
main = main.replace(para_containing("SIGNATURE_PLACEHOLDER"), sign, 1)

new_body = (cover + sect(f0)
            + front_items + front2 + sect(f1, fmt="lowerRoman", start=1)
            + main + sect(f1, fmt="decimal", start=1, last=True))
doc = doc[:body_m.start(1)] + new_body + doc[body_m.end(1):]

# Đề mục 1-3 của form không phải heading: giữ nguyên. Cập nhật trường khi mở trong Word.
settings_old = (tmp / "word/settings.xml").read_text(encoding="utf-8")
fn = re.search(r"<w:footnotePr>.*?</w:footnotePr>", settings_old, re.S)
en = re.search(r"<w:endnotePr>.*?</w:endnotePr>", settings_old, re.S)
settings = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
            '<w:zoom w:percent="100"/><w:defaultTabStop w:val="720"/>'
            '<w:characterSpacingControl w:val="doNotCompress"/><w:updateFields w:val="true"/>'
            + (fn.group(0) if fn else "") + (en.group(0) if en else "") +
            '<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>'
            '<m:mathPr><m:mathFont m:val="Cambria Math"/><m:dispDef/></m:mathPr>'
            '<w:themeFontLang w:val="vi-VN"/>'
            '<w:clrSchemeMapping w:bg1="light1" w:t1="dark1" w:bg2="light2" w:t2="dark2" w:accent1="accent1" w:accent2="accent2" '
            'w:accent3="accent3" w:accent4="accent4" w:accent5="accent5" w:accent6="accent6" w:hyperlink="hyperlink" w:followedHyperlink="followedHyperlink"/>'
            '<w:decimalSymbol w:val=","/><w:listSeparator w:val=";"/></w:settings>')
numbering = (tmp / "word/numbering.xml").read_text(encoding="utf-8")
numbering = re.sub(r'<w:nsid w:val="([0-9A-Fa-f]{1,7})" ?/>', lambda m: f'<w:nsid w:val="{int(m.group(1), 16):08X}"/>', numbering)
(tmp / "word/numbering.xml").write_text(numbering, encoding="utf-8")
(tmp / "word/settings.xml").write_text(settings, encoding="utf-8")

(tmp / "word/document.xml").write_text(doc, encoding="utf-8")
(tmp / "word/_rels/document.xml.rels").write_text(rels, encoding="utf-8")
(tmp / "[Content_Types].xml").write_text(ctypes, encoding="utf-8")

if OUT.exists():
    OUT.unlink()
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(tmp / "[Content_Types].xml", "[Content_Types].xml")
    for f in sorted(tmp.rglob("*")):
        if f.is_file() and f.name != "[Content_Types].xml":
            z.write(f, f.relative_to(tmp).as_posix())
json.dump([t for _, t in headings], open(WORK / "_headings.json", "w"), ensure_ascii=False)
print("wrote", OUT, "headings:", len(headings))
