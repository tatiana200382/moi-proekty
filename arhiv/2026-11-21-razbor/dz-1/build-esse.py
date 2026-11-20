"""Собирает эссе в Word: esse.docx. Источник — esse.md (без раздела «Пояснение»)."""
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn

src = open("esse.md", encoding="utf-8").read().split("## Пояснение")[0]
lines = [l.strip() for l in src.splitlines() if l.strip()]
title = lines[0].lstrip("# ").strip()
paras = lines[1:]

doc = Document()
for s in doc.sections:
    s.top_margin = Cm(2)
    s.bottom_margin = Cm(2)
    s.left_margin = Cm(2.5)
    s.right_margin = Cm(2.5)
normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(12.5)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
normal.paragraph_format.first_line_indent = Cm(1.25)
normal.paragraph_format.line_spacing = 1.3
normal.paragraph_format.space_after = Pt(4)

doc.add_heading(title, level=0)
for p in paras:
    doc.add_paragraph(p)

doc.save("esse.docx")
print("saved esse.docx", len(paras), "paragraphs")
