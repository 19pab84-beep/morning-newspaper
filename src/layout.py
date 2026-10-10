"""Black-and-white two-column newspaper; ReportLab; GPL-2.0-or-later."""
from __future__ import annotations

import html
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,
                                PageTemplate, Paragraph, Spacer)

W, H = A4
MARGIN = 39
GUTTER = 20
COL = (W - 2 * MARGIN - GUTTER) / 2
BLACK = colors.HexColor('#181818')
GRAY = colors.HexColor('#5a5a5a')
FONTS = {
    'Serif': '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    'SerifBold': '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
    'Sans': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    'SansBold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
}


def register_fonts():
    for name, file in FONTS.items():
        pdfmetrics.registerFont(TTFont(name, file))


class Rule(Flowable):
    def __init__(self, height=7):
        super().__init__()
        self.height = height
    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.height
    def draw(self):
        self.canv.setStrokeColor(colors.HexColor('#b0b0b0'))
        self.canv.setLineWidth(.45)
        self.canv.line(0, self.height / 2, self.width, self.height / 2)


def styles():
    return {
        'section': ParagraphStyle('section', fontName='SansBold', fontSize=9.1,
                                  leading=13, spaceBefore=12, spaceAfter=9, textColor=BLACK),
        'title': ParagraphStyle('title', fontName='SerifBold', fontSize=12.2,
                                leading=16, spaceAfter=5, textColor=BLACK),
        'body': ParagraphStyle('body', fontName='Serif', fontSize=9.15,
                               leading=13.5, alignment=TA_JUSTIFY,
                               spaceAfter=8, textColor=BLACK, splitLongWords=1),
        'source': ParagraphStyle('source', fontName='Sans', fontSize=7.1,
                                 leading=10.0, textColor=GRAY, spaceAfter=7,
                                 wordWrap='CJK'),
        'notice': ParagraphStyle('notice', fontName='Sans', fontSize=8.2,
                                 leading=12, textColor=GRAY, spaceAfter=10),
    }


def escape(text):
    return html.escape(str(text), quote=True)


def page_decoration(canvas, doc, issue_date: str, title: str, *, demo=False, ai=False):
    canvas.saveState()
    canvas.setStrokeColor(BLACK)
    canvas.setFillColor(BLACK)
    canvas.setFont('SansBold', 8)
    canvas.drawString(MARGIN, H - 39, 'WYDANIE CODZIENNE  /  POLSKA')
    canvas.setFont('Sans', 7.8)
    canvas.drawRightString(W - MARGIN, H - 39, issue_date)
    canvas.setLineWidth(.55)
    canvas.line(MARGIN, H-45, W-MARGIN, H-45)
    canvas.setFont('SerifBold', 25)
    canvas.drawCentredString(W/2, H - 78, title)
    canvas.setFont('Sans', 7.5)
    subtitle = 'WYDAJEMY CODZIENNIE  •  DO PORANNEJ KAWY'
    if demo:
        subtitle = 'WYDANIE DEMONSTRACYJNE • TREŚCI WYMYŚLONE • NIE SĄ TO WIADOMOŚCI'
    elif not ai:
        subtitle = 'SKRÓTY ZE ŹRÓDEŁ RSS  •  BEZ REDAKCJI AI'
    canvas.drawCentredString(W/2, H - 92, subtitle)
    canvas.setLineWidth(1.6)
    canvas.line(MARGIN, H - 102, W - MARGIN, H - 102)
    canvas.setLineWidth(.45)
    canvas.line(MARGIN, 49, W - MARGIN, 49)
    canvas.setFont('Sans', 7.3)
    canvas.drawString(MARGIN, 35, 'PORANNA PRASA  •  ŹRÓDŁA POD KAŻDYM MATERIAŁEM')
    canvas.drawRightString(W - MARGIN, 35, f'{doc.page}')
    canvas.restoreState()


def create_pdf(stories: list[dict], dest: Path, *, issue_date: str,
               title='PORANNA PRASA', demo=False, ai=False) -> int:
    """Return rendered page count; uses ReportLab onPage callbacks."""
    register_fonts()
    st = styles()
    dest.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(dest), pagesize=A4, leftMargin=MARGIN,
                          rightMargin=MARGIN, topMargin=115, bottomMargin=58,
                          pageCompression=1, title=f'{title} - {issue_date}',
                          author='Poranna Prasa')
    left = Frame(MARGIN, 56, COL, H - 170, leftPadding=0, rightPadding=0,
                 topPadding=0, bottomPadding=0, showBoundary=0)
    right = Frame(MARGIN+COL+GUTTER, 56, COL, H - 170,
                  leftPadding=0, rightPadding=0, topPadding=0,
                  bottomPadding=0, showBoundary=0)
    counter = {'pages': 0}
    def draw_page(c, d):
        counter['pages'] += 1
        page_decoration(c,d,issue_date,title,demo=demo,ai=ai)
    doc.addPageTemplates(PageTemplate(id='gazeta', frames=[left, right], onPage=draw_page))
    groups = defaultdict(list)
    for story in stories:
        groups[story['section']].append(story)
    flowables = []
    if demo:
        flowables.append(Paragraph('<b>TEST KOMPATYBILNOŚCI.</b> Wszystkie opisane poniżej historie są przykładowymi, fikcyjnymi materiałami. Nie przedstawiają rzeczywistych wydarzeń.', st['notice']))
    sections = list(groups.items())
    for section, items in sections:
        flowables.append(KeepTogether([Paragraph(escape(section), st['section']), Rule(6)]))
        for item in items:
            source = escape(item.get('source', 'Źródło'))
            published = item.get('published', '')[:10]
            if item.get('link', '').startswith(('http://','https://')):
                href = html.escape(item['link'], quote=True)
                source = f'<link href="{href}" color="#555555">{source}</link>'
            block = [Paragraph(escape(item['headline']), st['title']),
                     Paragraph(escape(item['body']), st['body']),
                     Paragraph(f'Źródło: {source}  •  {published}', st['source']), Rule()]
            flowables.append(KeepTogether(block))
    class CounterDoc(BaseDocTemplate):
        pass
    doc.build(flowables)
    return counter['pages']
