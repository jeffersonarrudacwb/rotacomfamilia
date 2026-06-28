"""
Rota com Família — Ebook framework
Brand-aligned PDF builder using reportlab.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image,
    PageBreak, Table, TableStyle, NextPageTemplate, Flowable
)
from reportlab.lib.utils import simpleSplit
from PIL import Image as PILImage

# ---------------- PATHS ----------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PHOTOS_DIR = ROOT
PDF_DIR = os.path.join(HERE, 'pdf')
os.makedirs(PDF_DIR, exist_ok=True)

# ---------------- BRAND COLORS ----------------
C = {
    'deep':   HexColor('#14150D'),  # olive black
    'navy':   HexColor('#1F2014'),
    'olive':  HexColor('#2A2B19'),
    'gold':   HexColor('#D4A437'),  # mustard accent
    'gold_d': HexColor('#A8821F'),
    'sunset': HexColor('#C8732E'),
    'cream':  HexColor('#FAF1DA'),
    'sand':   HexColor('#F4E4C1'),
    'fern':   HexColor('#A9B47E'),
    'text':   HexColor('#252215'),
    'muted':  HexColor('#6E6B5E'),
    'border': HexColor('#E5DCC0'),
}

PAGE = A4
MARGIN = 2.2 * cm

# ---------------- FONTS ----------------
# Use built-in PDF fonts (Times for serif headings, Helvetica for body)
SERIF      = 'Times-Bold'
SERIF_REG  = 'Times-Roman'
SERIF_IT   = 'Times-Italic'
SANS       = 'Helvetica'
SANS_BOLD  = 'Helvetica-Bold'
SANS_OBL   = 'Helvetica-Oblique'
MONO       = 'Courier'
MONO_BOLD  = 'Courier-Bold'


# ---------------- STYLES ----------------
def styles():
    return {
        'h1': ParagraphStyle('h1', fontName=SERIF, fontSize=26, leading=32,
                              textColor=C['deep'], spaceAfter=10, spaceBefore=6),
        'h2': ParagraphStyle('h2', fontName=SERIF, fontSize=18, leading=24,
                              textColor=C['deep'], spaceBefore=14, spaceAfter=6),
        'h3': ParagraphStyle('h3', fontName=SANS_BOLD, fontSize=11.5, leading=15,
                              textColor=C['sunset'], spaceBefore=10, spaceAfter=3),
        'body': ParagraphStyle('body', fontName=SANS, fontSize=10.5, leading=15.5,
                                textColor=C['text'], alignment=TA_JUSTIFY, spaceAfter=8),
        'lead': ParagraphStyle('lead', fontName=SANS, fontSize=12, leading=18,
                                textColor=C['text'], spaceAfter=10),
        'eyebrow': ParagraphStyle('eyebrow', fontName=SANS_BOLD, fontSize=8.5, leading=12,
                                   textColor=C['gold_d'], spaceAfter=2),
        'bullet': ParagraphStyle('bullet', fontName=SANS, fontSize=10.5, leading=15,
                                  textColor=C['text'], leftIndent=16, bulletIndent=2, spaceAfter=4),
        'caption': ParagraphStyle('cap', fontName=SANS_OBL, fontSize=8.5, leading=11,
                                   textColor=C['muted'], alignment=TA_CENTER,
                                   spaceBefore=3, spaceAfter=12),
        'small': ParagraphStyle('sm', fontName=SANS, fontSize=9, leading=12, textColor=C['muted']),
        # Cover
        'cover_eyebrow': ParagraphStyle('ce', fontName=SANS_BOLD, fontSize=10, leading=14,
                                         textColor=C['gold'], alignment=TA_CENTER),
        'cover_title': ParagraphStyle('ct', fontName=SERIF, fontSize=40, leading=46,
                                       textColor=white, alignment=TA_CENTER, spaceAfter=8),
        'cover_sub': ParagraphStyle('cs', fontName=SANS, fontSize=13, leading=19,
                                     textColor=HexColor('#E5DCC0'), alignment=TA_CENTER, spaceAfter=12),
        'cover_year': ParagraphStyle('cy', fontName=SERIF, fontSize=86, leading=92,
                                      textColor=C['gold'], alignment=TA_CENTER),
        'cover_author': ParagraphStyle('ca', fontName=SANS, fontSize=10, leading=14,
                                        textColor=HexColor('#A9B47E'), alignment=TA_CENTER),
        # TOC
        'toc_item': ParagraphStyle('toc', fontName=SANS, fontSize=11, leading=18,
                                    textColor=C['text']),
        # Quote / pull-quote
        'quote': ParagraphStyle('q', fontName=SERIF_IT, fontSize=14, leading=20,
                                 textColor=C['gold_d'], leftIndent=20, rightIndent=20,
                                 spaceBefore=12, spaceAfter=12, alignment=TA_LEFT),
    }


# ---------------- PAGE BACKGROUNDS ----------------
def draw_cover_bg(canvas, doc):
    canvas.saveState()
    w, h = PAGE
    canvas.setFillColor(C['deep'])
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    # subtle olive overlay
    canvas.setFillColor(C['olive'])
    canvas.setFillAlpha(0.4)
    canvas.circle(w * 0.78, h * 0.82, 9*cm, fill=1, stroke=0)
    canvas.setFillAlpha(1)
    # gold double-border frame
    canvas.setStrokeColor(C['gold'])
    canvas.setLineWidth(1.4)
    canvas.rect(1.2*cm, 1.2*cm, w - 2.4*cm, h - 2.4*cm, fill=0, stroke=1)
    canvas.setLineWidth(0.4)
    canvas.rect(1.5*cm, 1.5*cm, w - 3*cm, h - 3*cm, fill=0, stroke=1)
    # brand mark top
    canvas.setFillColor(C['gold'])
    canvas.setFont(SERIF, 14)
    canvas.drawCentredString(w/2, h - 2.4*cm, 'ROTA COM FAMÍLIA')
    canvas.setStrokeColor(C['gold'])
    canvas.setLineWidth(0.5)
    canvas.line(w/2 - 3*cm, h - 2.8*cm, w/2 + 3*cm, h - 2.8*cm)
    # compass-ish ornament bottom
    canvas.setFillColor(C['gold'])
    canvas.setFont(SERIF, 12)
    canvas.drawCentredString(w/2, 1.9*cm, '•  •  •')
    canvas.restoreState()


def draw_content_bg(canvas, doc):
    canvas.saveState()
    w, h = PAGE
    canvas.setFillColor(C['cream'])
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    # Top bar (dark olive + gold strip)
    canvas.setFillColor(C['deep'])
    canvas.rect(0, h - 0.85*cm, w, 0.85*cm, fill=1, stroke=0)
    canvas.setFillColor(C['gold'])
    canvas.rect(0, h - 0.92*cm, w, 0.07*cm, fill=1, stroke=0)
    # header text
    canvas.setFillColor(C['cream'])
    canvas.setFont(SANS_BOLD, 8.5)
    canvas.drawString(MARGIN, h - 0.55*cm, 'ROTA COM FAMÍLIA')
    canvas.setFillColor(HexColor('#E5DCC0'))
    canvas.setFont(SANS, 8)
    canvas.drawRightString(w - MARGIN, h - 0.55*cm, doc.ebook_title)
    # Footer
    canvas.setFillColor(C['deep'])
    canvas.rect(0, 0, w, 0.7*cm, fill=1, stroke=0)
    canvas.setFillColor(C['gold'])
    canvas.rect(0, 0.7*cm, w, 0.05*cm, fill=1, stroke=0)
    canvas.setFillColor(C['cream'])
    canvas.setFont(SANS, 8)
    canvas.drawString(MARGIN, 0.25*cm, 'rotacomfamilia.com')
    canvas.setFillColor(C['gold'])
    canvas.drawCentredString(w/2, 0.25*cm, '·  ·  ·')
    canvas.setFillColor(C['cream'])
    pno = doc.page - 1  # offset cover
    canvas.drawRightString(w - MARGIN, 0.25*cm, f'p. {pno:02d}')
    canvas.restoreState()


# ---------------- CUSTOM FLOWABLES ----------------
class Divider(Flowable):
    def __init__(self, width_pct=0.3, color=None, gap_before=0.3*cm, gap_after=0.3*cm):
        Flowable.__init__(self)
        self.width_pct = width_pct
        self.color = color or C['gold']
        self.gap_before = gap_before
        self.gap_after = gap_after
    def wrap(self, aw, ah):
        self._aw = aw
        self._h = self.gap_before + 0.05*cm + self.gap_after
        return aw, self._h
    def draw(self):
        x_start = (self._aw - self._aw * self.width_pct) / 2
        x_end = x_start + self._aw * self.width_pct
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(1.2)
        self.canv.line(x_start, self.gap_after, x_end, self.gap_after)


class Callout(Flowable):
    """Tip-box with gold accent, sand background."""
    def __init__(self, title, body, kind='tip'):
        Flowable.__init__(self)
        self.title = title
        self.body = body
        self.kind = kind
    def wrap(self, aw, ah):
        self._aw = aw
        tw = aw - 1.5*cm
        self._t_lines = simpleSplit(self.title, SANS_BOLD, 10, tw)
        self._b_lines = simpleSplit(self.body, SANS, 9.5, tw)
        self._h = (0.5*cm + len(self._t_lines)*0.42*cm + 0.15*cm
                   + len(self._b_lines)*0.42*cm + 0.5*cm)
        return aw, self._h
    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(C['sand'])
        c.roundRect(0, 0, self._aw, self._h, 0.2*cm, fill=1, stroke=0)
        c.setFillColor(C['gold'])
        c.rect(0, 0, 0.18*cm, self._h, fill=1, stroke=0)
        # icon label
        icon = {'tip': '✦ DICA', 'warn': '!  ATENÇÃO', 'note': '◆ NOTA'}.get(self.kind, '✦ DICA')
        c.setFillColor(C['gold_d'])
        c.setFont(SANS_BOLD, 8)
        c.drawString(0.6*cm, self._h - 0.45*cm, icon)
        # title
        c.setFillColor(C['deep'])
        c.setFont(SANS_BOLD, 10)
        y = self._h - 0.85*cm
        for line in self._t_lines:
            c.drawString(0.6*cm, y, line)
            y -= 0.42*cm
        # body
        c.setFillColor(C['text'])
        c.setFont(SANS, 9.5)
        y -= 0.05*cm
        for line in self._b_lines:
            c.drawString(0.6*cm, y, line)
            y -= 0.42*cm
        c.restoreState()


class StatStrip(Flowable):
    """Horizontal strip of numbers."""
    def __init__(self, items):
        # items: [(number, label), ...]
        Flowable.__init__(self)
        self.items = items
    def wrap(self, aw, ah):
        self._aw = aw
        self._h = 2.6*cm
        return aw, self._h
    def draw(self):
        c = self.canv
        n = len(self.items)
        col_w = self._aw / n
        for i, (num, lbl) in enumerate(self.items):
            x = i * col_w
            # number
            c.setFillColor(C['sunset'])
            c.setFont(SERIF, 22)
            c.drawCentredString(x + col_w/2, self._h - 1.1*cm, num)
            # label
            c.setFillColor(C['muted'])
            c.setFont(SANS, 8.5)
            lines = simpleSplit(lbl, SANS, 8.5, col_w - 0.4*cm)
            y = self._h - 1.7*cm
            for line in lines:
                c.drawCentredString(x + col_w/2, y, line)
                y -= 0.32*cm
            # divider
            if i < n - 1:
                c.setStrokeColor(C['border'])
                c.setLineWidth(0.5)
                c.line(x + col_w, 0.4*cm, x + col_w, self._h - 0.4*cm)


# ---------------- DOC TEMPLATE ----------------
class EbookDoc(BaseDocTemplate):
    def __init__(self, filename, title):
        BaseDocTemplate.__init__(
            self, filename, pagesize=PAGE,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=1.5*cm, bottomMargin=1.2*cm,
            title=title, author='Rota com Família — Antunes Arruda',
            creator='Rota com Família'
        )
        self.ebook_title = title
        cover_frame = Frame(0, 0, PAGE[0], PAGE[1],
                             leftPadding=2.5*cm, rightPadding=2.5*cm,
                             topPadding=2.5*cm, bottomPadding=2.5*cm, id='cover')
        content_frame = Frame(MARGIN, 1.1*cm, PAGE[0] - 2*MARGIN, PAGE[1] - 2.3*cm,
                               leftPadding=0, rightPadding=0,
                               topPadding=0.4*cm, bottomPadding=0, id='content')
        self.addPageTemplates([
            PageTemplate(id='Cover', frames=[cover_frame], onPage=draw_cover_bg),
            PageTemplate(id='Content', frames=[content_frame], onPage=draw_content_bg),
        ])


# ---------------- HELPERS ----------------
def cover_block(title, subtitle=None, badge='UM EBOOK ROTA COM FAMÍLIA', year=None):
    s = styles()
    items = [Spacer(1, 5.5*cm),
             Paragraph(badge, s['cover_eyebrow']),
             Spacer(1, 0.6*cm),
             Paragraph(title, s['cover_title'])]
    if subtitle:
        items += [Spacer(1, 0.2*cm), Paragraph(subtitle, s['cover_sub'])]
    if year:
        items += [Spacer(1, 1.2*cm), Paragraph(year, s['cover_year'])]
    items += [Spacer(1, 2.0*cm),
              Paragraph('Jefferson · Kharol · Derek<br/>Antunes Arruda', s['cover_author'])]
    return items


def photo(name, max_w=None, max_h=10*cm):
    path = os.path.join(PHOTOS_DIR, name)
    pil = PILImage.open(path)
    iw, ih = pil.size
    aspect = iw / ih
    if max_w is None:
        max_w = PAGE[0] - 2 * MARGIN
    w = max_w
    h = w / aspect
    if h > max_h:
        h = max_h
        w = h * aspect
    return Image(path, width=w, height=h)


def caption(text):
    return Paragraph(text, styles()['caption'])


def bullet_list(items):
    s = styles()['bullet']
    return [Paragraph(f'<font color="#D4A437">■</font>  {item}', s) for item in items]


def to_content():
    return [NextPageTemplate('Content'), PageBreak()]


def to_cover():
    return [NextPageTemplate('Cover'), PageBreak()]


def two_col_photo_row(photo_a, photo_b, gap=0.4*cm, h=6.5*cm):
    """Side-by-side two photos."""
    avail = PAGE[0] - 2*MARGIN
    each_w = (avail - gap) / 2
    def fit(name):
        path = os.path.join(PHOTOS_DIR, name)
        pil = PILImage.open(path)
        iw, ih = pil.size
        aspect = iw / ih
        w = each_w
        ph = w / aspect
        if ph > h:
            ph = h
            w = ph * aspect
        return Image(path, width=w, height=ph)
    t = Table([[fit(photo_a), fit(photo_b)]], colWidths=[each_w, each_w])
    t.setStyle(TableStyle([
        ('LEFTPADDING',(0,0),(-1,-1),0),
        ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),0),
        ('BOTTOMPADDING',(0,0),(-1,-1),0),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    return t


def data_table(rows, header=True, col_widths=None):
    """Branded table with cream/olive scheme."""
    if col_widths is None:
        col_widths = [PAGE[0] - 2*MARGIN] * 0  # auto
    t = Table(rows, colWidths=col_widths if col_widths else None)
    style = [
        ('FONTNAME',(0,0),(-1,-1), SANS),
        ('FONTSIZE',(0,0),(-1,-1), 9.5),
        ('TEXTCOLOR',(0,0),(-1,-1), C['text']),
        ('GRID',(0,0),(-1,-1), 0.4, C['border']),
        ('LEFTPADDING',(0,0),(-1,-1), 0.3*cm),
        ('RIGHTPADDING',(0,0),(-1,-1), 0.3*cm),
        ('TOPPADDING',(0,0),(-1,-1), 0.18*cm),
        ('BOTTOMPADDING',(0,0),(-1,-1), 0.18*cm),
        ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
    ]
    if header:
        style += [
            ('BACKGROUND',(0,0),(-1,0), C['deep']),
            ('TEXTCOLOR',(0,0),(-1,0), C['cream']),
            ('FONTNAME',(0,0),(-1,0), SANS_BOLD),
            ('FONTSIZE',(0,0),(-1,0), 9.5),
            ('ROWBACKGROUNDS',(0,1),(-1,-1), [C['cream'], C['sand']]),
        ]
    else:
        style += [('ROWBACKGROUNDS',(0,0),(-1,-1), [C['cream'], C['sand']])]
    t.setStyle(TableStyle(style))
    return t


def section_opener(eyebrow, title, lead=None):
    """Big section opener: gold eyebrow + serif title + lead paragraph."""
    s = styles()
    out = [
        Spacer(1, 0.3*cm),
        Paragraph(eyebrow.upper(), s['eyebrow']),
        Paragraph(title, s['h1']),
        Divider(width_pct=0.18, gap_before=0.2*cm, gap_after=0.2*cm),
    ]
    if lead:
        out.append(Spacer(1, 0.1*cm))
        out.append(Paragraph(lead, s['lead']))
    out.append(Spacer(1, 0.3*cm))
    return out


def toc(entries):
    """Table of contents — list of (title, page) tuples."""
    s = styles()
    rows = []
    for i, (t, p) in enumerate(entries):
        num = f'{i+1:02d}'
        rows.append([
            Paragraph(f'<font color="#D4A437"><b>{num}</b></font>', s['toc_item']),
            Paragraph(t, s['toc_item']),
            Paragraph(f'<font color="#6E6B5E">p. {p}</font>', s['toc_item']),
        ])
    table = Table(rows, colWidths=[1.2*cm, 12.5*cm, 2*cm])
    table.setStyle(TableStyle([
        ('LEFTPADDING',(0,0),(-1,-1), 0.1*cm),
        ('RIGHTPADDING',(0,0),(-1,-1), 0.1*cm),
        ('TOPPADDING',(0,0),(-1,-1), 0.18*cm),
        ('BOTTOMPADDING',(0,0),(-1,-1), 0.18*cm),
        ('VALIGN',(0,0),(-1,-1), 'TOP'),
        ('LINEBELOW',(0,0),(-1,-2), 0.3, C['border']),
    ]))
    return table


def back_cover_block(blurb):
    """Big closing block with CTA-like styling."""
    s = styles()
    return [
        Spacer(1, 1.5*cm),
        Paragraph('OBRIGADO POR LER ATÉ AQUI.', s['eyebrow']),
        Spacer(1, 0.3*cm),
        Paragraph(blurb, s['lead']),
        Spacer(1, 0.6*cm),
        Divider(width_pct=0.3),
        Spacer(1, 0.4*cm),
        Paragraph(
            '<b>rotacomfamilia.com</b>  ·  @rotacomfamilia  ·  YouTube · Instagram · TikTok',
            s['small']
        ),
        Paragraph(
            'Quer assessoria pra emitir sua próxima viagem? <b>contato@rotacomfamilia.com</b>',
            s['small']
        ),
    ]
