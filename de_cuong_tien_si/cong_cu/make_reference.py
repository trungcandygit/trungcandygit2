"""Tạo reference.docx cho pandoc theo khuôn trình bày của bản M7.

A4, Times New Roman 13, giãn dòng 1,5, thụt 1 cm, căn đều; theme Office lấy từ M7.
Chạy: python3 make_reference.py <ref_default_unzipped> <m7_unzipped> <out.docx>
"""
import shutil
import sys
import zipfile
from pathlib import Path

src, m7, out = map(Path, sys.argv[1:4])
work = out.with_suffix(".d")
if work.exists():
    shutil.rmtree(work)
shutil.copytree(src, work)
shutil.copy(m7 / "word/theme/theme1.xml", work / "word/theme/theme1.xml")

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
FONT = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman"/>'


def pstyle(sid, name, ppr="", rpr="", based="Normal", nxt=None, extra=""):
    nxt = f'<w:next w:val="{nxt}"/>' if nxt else ""
    b = f'<w:basedOn w:val="{based}"/>' if based else ""
    return (f'<w:style w:type="paragraph" w:customStyle="1" w:styleId="{sid}"><w:name w:val="{name}"/>'
            f'{b}{nxt}<w:qFormat/>{extra}<w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')


def builtin(sid, name, ppr="", rpr="", based="Normal", nxt=None, extra=""):
    return pstyle(sid, name, ppr, rpr, based, nxt, extra).replace(' w:customStyle="1"', "")


BODY_P = '<w:spacing w:before="0" w:after="60" w:line="360" w:lineRule="auto"/><w:ind w:firstLine="567"/><w:jc w:val="both"/>'
NOIND = '<w:spacing w:before="0" w:after="60" w:line="360" w:lineRule="auto"/><w:ind w:firstLine="0"/>'

styles = [
    f'<w:docDefaults><w:rPrDefault><w:rPr>{FONT}<w:sz w:val="26"/><w:szCs w:val="26"/>'
    '<w:lang w:val="vi-VN" w:eastAsia="en-US" w:bidi="ar-SA"/></w:rPr></w:rPrDefault>'
    '<w:pPrDefault><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>',
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>',
    '<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont"><w:name w:val="Default Paragraph Font"/><w:uiPriority w:val="1"/><w:semiHidden/></w:style>',
    '<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/><w:semiHidden/><w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>',
    builtin("BodyText", "Body Text", BODY_P),
    builtin("FirstParagraph", "First Paragraph", BODY_P, based="BodyText", nxt="BodyText"),
    pstyle("Compact", "Compact", '<w:spacing w:before="20" w:after="20" w:line="264" w:lineRule="auto"/><w:ind w:firstLine="0"/><w:jc w:val="left"/>',
           '<w:sz w:val="23"/><w:szCs w:val="23"/>', based="BodyText"),
    builtin("Title", "Title", '<w:jc w:val="center"/>', '<w:b/><w:sz w:val="28"/>', nxt="BodyText"),
    builtin("Heading1", "heading 1",
            '<w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="120" w:line="360" w:lineRule="auto"/><w:outlineLvl w:val="0"/>',
            '<w:b/><w:bCs/><w:color w:val="000000"/><w:sz w:val="26"/><w:szCs w:val="26"/>', nxt="BodyText"),
    builtin("Heading2", "heading 2",
            '<w:keepNext/><w:keepLines/><w:spacing w:before="180" w:after="60" w:line="360" w:lineRule="auto"/><w:outlineLvl w:val="1"/>',
            '<w:b/><w:bCs/><w:color w:val="000000"/><w:sz w:val="26"/><w:szCs w:val="26"/>', nxt="BodyText"),
    builtin("Heading3", "heading 3",
            '<w:keepNext/><w:keepLines/><w:spacing w:before="120" w:after="60" w:line="360" w:lineRule="auto"/><w:outlineLvl w:val="2"/>',
            '<w:b/><w:bCs/><w:i/><w:iCs/><w:color w:val="000000"/><w:sz w:val="26"/><w:szCs w:val="26"/>', nxt="BodyText"),
    pstyle("TableCaption", "TableCaption",
           '<w:keepNext/><w:spacing w:before="120" w:after="60" w:line="312" w:lineRule="auto"/><w:ind w:firstLine="0"/><w:jc w:val="center"/>',
           '<w:b/><w:bCs/>'),
    pstyle("FigureCaption", "FigureCaption",
           '<w:keepNext/><w:spacing w:before="60" w:after="0" w:line="312" w:lineRule="auto"/><w:ind w:firstLine="0"/><w:jc w:val="center"/>',
           '<w:b/><w:bCs/>'),
    pstyle("SourceNote", "SourceNote",
           '<w:spacing w:before="40" w:after="120" w:line="276" w:lineRule="auto"/><w:ind w:firstLine="0"/><w:jc w:val="right"/>',
           '<w:i/><w:iCs/><w:sz w:val="24"/><w:szCs w:val="24"/>'),
    pstyle("Equation", "Equation", '<w:tabs><w:tab w:val="center" w:pos="4394"/><w:tab w:val="right" w:pos="8778"/></w:tabs><w:spacing w:before="60" w:after="60" w:line="276" w:lineRule="auto"/><w:ind w:firstLine="0"/><w:jc w:val="left"/>'),
    pstyle("FigureBox", "FigureBox", '<w:keepNext/><w:spacing w:before="120" w:after="60"/><w:ind w:firstLine="0"/><w:jc w:val="center"/>'),
    pstyle("CoverLine", "CoverLine", NOIND + '<w:jc w:val="both"/>'),
    pstyle("Reference", "Reference",
           '<w:spacing w:before="0" w:after="80" w:line="312" w:lineRule="auto"/><w:ind w:left="567" w:hanging="567"/><w:jc w:val="both"/>'),
    pstyle("ListHeading", "ListHeading",
           '<w:keepNext/><w:spacing w:before="240" w:after="120"/><w:ind w:firstLine="0"/><w:jc w:val="center"/>',
           '<w:b/><w:bCs/>'),
    builtin("TOC1", "toc 1", '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="8778"/></w:tabs><w:spacing w:before="40" w:after="0" w:line="276" w:lineRule="auto"/><w:ind w:firstLine="0"/>', '<w:b/>'),
    builtin("TOC2", "toc 2", '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="8778"/></w:tabs><w:spacing w:before="0" w:after="0" w:line="276" w:lineRule="auto"/><w:ind w:left="284" w:firstLine="0"/>'),
    builtin("TOC3", "toc 3", '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="8778"/></w:tabs><w:spacing w:before="0" w:after="0" w:line="276" w:lineRule="auto"/><w:ind w:left="567" w:firstLine="0"/>', '<w:i/>'),
    builtin("TableofFigures", "table of figures", '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="8778"/></w:tabs><w:spacing w:before="0" w:after="40" w:line="300" w:lineRule="auto"/><w:ind w:left="1134" w:hanging="1134"/>'),
    builtin("TOCHeading", "TOC Heading", '<w:keepNext/><w:spacing w:before="240" w:after="120"/><w:jc w:val="center"/>', '<w:b/><w:bCs/>', based="Normal"),
    builtin("FootnoteText", "footnote text", '<w:spacing w:after="0"/>', '<w:sz w:val="20"/>'),
    builtin("Footer", "footer", '<w:tabs><w:tab w:val="center" w:pos="4680"/><w:tab w:val="right" w:pos="9360"/></w:tabs><w:jc w:val="center"/>'),
    builtin("Caption", "caption", '<w:jc w:val="center"/>', '<w:b/>'),
    pstyle("ImageCaption", "Image Caption", '<w:jc w:val="center"/>', '<w:b/>'),
    pstyle("Figure", "Figure", '<w:jc w:val="center"/>'),
    pstyle("CaptionedFigure", "Captioned Figure", '<w:keepNext/><w:jc w:val="center"/>'),
    '<w:style w:type="character" w:customStyle="1" w:styleId="BodyTextChar"><w:name w:val="Body Text Char"/><w:basedOn w:val="DefaultParagraphFont"/></w:style>',
    '<w:style w:type="character" w:customStyle="1" w:styleId="VerbatimChar"><w:name w:val="Verbatim Char"/><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="22"/></w:rPr></w:style>',
    '<w:style w:type="character" w:customStyle="1" w:styleId="SectionNumber"><w:name w:val="Section Number"/></w:style>',
    '<w:style w:type="character" w:styleId="FootnoteReference"><w:name w:val="footnote reference"/><w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style>',
    '<w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/><w:rPr><w:color w:val="000000"/></w:rPr></w:style>',
    '<w:style w:type="table" w:customStyle="1" w:styleId="Table"><w:name w:val="Table"/><w:basedOn w:val="TableNormal"/><w:tblPr>'
    '<w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tblBorders>'
    '<w:tblCellMar><w:top w:w="28" w:type="dxa"/><w:left w:w="85" w:type="dxa"/><w:bottom w:w="28" w:type="dxa"/><w:right w:w="85" w:type="dxa"/></w:tblCellMar></w:tblPr>'
    '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/><w:bCs/></w:rPr></w:tblStylePr></w:style>',
]

xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
       f'<w:styles {W}>' + "".join(styles) + "</w:styles>")
(work / "word/styles.xml").write_text(xml, encoding="utf-8")

if out.exists():
    out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(work.rglob("*")):
        if p.is_file():
            z.write(p, p.relative_to(work).as_posix())
print("wrote", out)
