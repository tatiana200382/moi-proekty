"""Простй конвертер Markdown → DOCX для документов сдачи.

Использование: python3 md2docx.py input.md output.docx "Подзаголовок"
"""
import re
import sys
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def shade(cell, color="EDEDED"):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tc_pr.append(shd)


def widths_for(rows, total=17.0):
    cols = len(rows[0])
    lens = [0] * cols
    for r in rows:
        for i, v in enumerate(r):
            lens[i] = max(lens[i], min(len(v), 90))
    base = 2.0
    extra = max(total - base * cols, 0)
    s = sum(lens) or cols
    return [base + extra * l / s for l in lens]


def fix_layout(t, widths):
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    t._tbl.tblPr.append(layout)
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(w)
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))


def add_rich(p, text, size=None, italic=False):
    for part in re.split(r"(\*\*.+?\*\*)", text):
        if not part:
            continue
        bold = part.startswith("**") and part.endswith("**")
        r = p.add_run(part[2:-2] if bold else part)
        r.bold = bold
        if size:
            r.font.size = Pt(size)
        if italic:
            r.italic = True


def add_table(doc, block):
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in block]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    if not rows:
        return
    t = doc.add_table(rows=1, cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(rows[0]):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        shade(c)
    for row in rows[1:]:
        cells = t.add_row().cells
        for i, v in enumerate(row[: len(rows[0])]):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(v)
            r.font.size = Pt(8.5)
    fix_layout(t, widths_for(rows))


def main(src, out, subtitle=""):
    doc = Document()
    raw = open(src, encoding="utf-8").read()
    wide = any(line.count("|") - 1 >= 6 for line in raw.splitlines() if line.startswith("|"))
    for s in doc.sections:
        if wide:
            from docx.enum.section import WD_ORIENT
            s.orientation = WD_ORIENT.LANDSCAPE
            s.page_width, s.page_height = s.page_height, s.page_width
            s.top_margin = Cm(1.4)
            s.bottom_margin = Cm(1.4)
            s.left_margin = Cm(1.5)
            s.right_margin = Cm(1.5)
        else:
            s.top_margin = Cm(1.5)
            s.bottom_margin = Cm(1.5)
            s.left_margin = Cm(2)
            s.right_margin = Cm(2)
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")

    lines = raw.splitlines()
    i = 0
    first_heading = True
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            add_table(doc, block)
            continue
        if line.startswith("# "):
            doc.add_heading(line[2:].strip(), level=0)
            if subtitle:
                p = doc.add_paragraph()
                r = p.add_run(subtitle)
                r.italic = True
                r.font.size = Pt(10)
        elif line.startswith("### "):
            h = doc.add_heading(line[4:].strip(), level=2)
            h.paragraph_format.space_before = Pt(6)
        elif line.startswith("## "):
            h = doc.add_heading(line[3:].strip(), level=1)
            h.paragraph_format.space_before = Pt(9)
        elif line.startswith("> "):
            p = doc.add_paragraph()
            add_rich(p, line[2:].strip(), size=10, italic=True)
            p.paragraph_format.left_indent = Cm(0.8)
            p.paragraph_format.space_after = Pt(2)
        elif line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            add_rich(p, line[2:].strip(), size=10)
        elif re.match(r"^\d+\. ", line):
            p = doc.add_paragraph()
            m = re.match(r"^(\d+)\. ", line)
            p.paragraph_format.left_indent = Cm(0.8)
            p.paragraph_format.first_line_indent = Cm(-0.8)
            p.paragraph_format.space_after = Pt(2)
            add_rich(p, line, size=10)
        else:
            p = doc.add_paragraph()
            add_rich(p, line.strip(), size=10.5)
            p.paragraph_format.space_after = Pt(2)
        i += 1
    doc.save(out)
    print("saved", out)


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args[0], args[1], args[2] if len(args) > 2 else "")
