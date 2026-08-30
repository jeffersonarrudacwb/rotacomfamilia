# -*- coding: utf-8 -*-
"""Midia kit em PDF, no mesmo tema dos ebooks e das propostas.

    python mediakit/build_mediakit.py

O anterior era um arquivo de 14 MB montado fora do projeto. Alem do peso, ele
tinha ficado para tras: telefone e e-mail antigos, texto repetido duas vezes na
mesma pagina e "2.9 mi horas de visualizacao" onde o certo e 2.9 mil. Numero
inflado em midia kit e o tipo de coisa que a marca confere.

Agora o conteudo mora no mediakit.json ao lado. Numero errado se corrige em uma
linha e o PDF sai de novo, igual. Cores, fontes, Callout e StatStrip vem de
ebooks/framework.py, o mesmo modulo que monta os ebooks e as propostas de
assessoria, entao os documentos chegam na marca com a mesma cara.
"""
import hashlib
import io
import json
import math
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, 'ebooks'))

from PIL import Image as PILImage, ImageOps  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak, Table,
    TableStyle, NextPageTemplate, Image, Flowable, KeepTogether,
)
from reportlab.lib.units import cm  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.enums import TA_CENTER  # noqa: E402
from reportlab.lib.utils import simpleSplit  # noqa: E402

from framework import (  # noqa: E402
    C, PAGE, MARGIN, SANS, SANS_BOLD, SANS_OBL, SERIF, SERIF_IT, styles,
    Divider, Callout, StatStrip,
)

FOTOS = os.path.join(RAIZ, 'fotos')
CACHE = os.path.join(AQUI, '.cache-img')
UTIL = PAGE[0] - 2 * MARGIN
DPI = 200


# --------------------------------------------------------------------------
# Fotos
# --------------------------------------------------------------------------
def recorte(rel, larg_pt, alt_pt, foco=0.5, fundir=0.0):
    """Foto cortada no formato exato do espaco e reduzida para 200 DPI.

    O ReportLab embute o arquivo inteiro e so escala na hora de desenhar, entao
    entregar o original da camera coloca 4000 px dentro do PDF para aparecer com
    4 cm de largura. Foi assim que o ebook de roteiros chegou a 11 MB.

    'foco' e a altura do corte quando a foto e mais alta que o espaco: 0.5 corta
    pelo meio, valores menores sobem. Serve para foto em que o miolo e ceu ou
    agua e o assunto esta em cima.

    'fundir' e a fracao da altura em que o pe da foto se dissolve na cor do
    fundo. A primeira versao fazia essa passagem no PDF, com fatias
    transparentes desenhadas no canvas, e a emenda aparecia: fatias vizinhas se
    sobrepoem, a opacidade soma e cada emenda virava um risco horizontal mais
    escuro na capa. Aqui a mistura acontece no pixel, antes de o arquivo entrar
    no PDF, e nao sobra transparencia nenhuma para o leitor interpretar.
    """
    origem = os.path.join(FOTOS, rel)
    px_l = int(math.ceil(larg_pt / 72.0 * DPI))
    px_a = int(math.ceil(alt_pt / 72.0 * DPI))
    assinatura = '%s|%d|%d|%d|%.2f|%.2f' % (os.path.abspath(origem),
                                            int(os.path.getmtime(origem)),
                                            px_l, px_a, foco, fundir)
    chave = hashlib.md5(assinatura.encode('utf-8')).hexdigest()[:16]
    destino = os.path.join(CACHE, chave + '.jpg')
    if os.path.exists(destino):
        return destino
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)

    im = PILImage.open(origem)
    try:
        im = ImageOps.exif_transpose(im)
    except Exception:
        pass
    if im.mode != 'RGB':
        im = im.convert('RGB')

    alvo = px_l / float(px_a)
    if im.width / float(im.height) > alvo:      # larga demais: corta os lados
        nova = int(round(im.height * alvo))
        e = int((im.width - nova) * 0.5)
        im = im.crop((e, 0, e + nova, im.height))
    else:                                        # alta demais: corta em cima
        nova = int(round(im.width / alvo))
        t = int((im.height - nova) * foco)
        im = im.crop((0, t, im.width, t + nova))

    im = im.resize((px_l, px_a), PILImage.LANCZOS)
    if fundir > 0:
        im = PILImage.composite(
            PILImage.new('RGB', im.size, cor_rgb(C['deep'])), im,
            rampa(im.size, fundir))
    # sem exif: nao vai GPS nem numero de serie da camera para dentro do PDF
    im.save(destino, 'JPEG', quality=82, optimize=True, progressive=True)
    return destino


def cor_rgb(cor):
    return (int(round(cor.red * 255)), int(round(cor.green * 255)),
            int(round(cor.blue * 255)))


def rampa(tamanho, fracao, curva=1.6):
    """Mascara vertical: transparente em cima, opaca no pe da foto."""
    larg, alt = tamanho
    coluna = PILImage.new('L', (1, alt), 0)
    px = coluna.load()
    inicio = int(alt * (1.0 - fracao))
    for y in range(inicio, alt):
        t = (y - inicio) / float(max(1, alt - 1 - inicio))
        px[0, y] = int(round(255 * (t ** curva)))
    return coluna.resize((larg, alt))


def foto(rel, larg, alt, foco=0.5):
    return Image(recorte(rel, larg, alt, foco), width=larg, height=alt)


# --------------------------------------------------------------------------
# Desenho das paginas
# --------------------------------------------------------------------------
def rota_marca(c, w, base, cor, altura, opacidade):
    """Arco pontilhado com um ponto em cada ponta, em marca d'agua.

    As propostas usam a silhueta de Nova York no rodape porque sao de uma
    viagem para Nova York. O midia kit nao e sobre uma cidade: e sobre viajar.
    Entao aqui a marca e a rota tracejada da propria logo, que serve para
    qualquer destino.
    """
    c.saveState()
    try:
        c.setStrokeAlpha(opacidade)
        c.setFillAlpha(opacidade)
    except AttributeError:
        pass
    c.setStrokeColor(cor)
    c.setFillColor(cor)
    c.setLineWidth(1.1)
    c.setDash(3, 4)
    x0, x1 = MARGIN, w - MARGIN
    p = c.beginPath()
    for i in range(61):
        t = i / 60.0
        x = x0 + (x1 - x0) * t
        y = base + altura * math.sin(math.pi * t)
        p.moveTo(x, y) if i == 0 else p.lineTo(x, y)
    c.drawPath(p, fill=0, stroke=1)
    c.setDash()
    for x in (x0, x1):
        c.circle(x, base, 1.9, fill=1, stroke=0)
    c.restoreState()


def fundo_capa(canvas, doc):
    w, h = PAGE
    canvas.saveState()
    canvas.setFillColor(C['deep'])
    canvas.rect(0, 0, w, h, fill=1, stroke=0)

    # faixa dourada no topo, a mesma das propostas
    canvas.setFillColor(C['gold'])
    canvas.rect(0, h - 0.28 * cm, w, 0.28 * cm, fill=1, stroke=0)

    # a foto sangra de borda a borda e o pe dela ja vem dissolvido no fundo
    alt = h * 0.47
    y = h - 0.28 * cm - alt
    canvas.drawImage(recorte(doc.capa_foto, w, alt, foco=doc.capa_foco,
                             fundir=0.58),
                     0, y, width=w, height=alt, mask='auto')

    canvas.setFillColor(C['gold'])
    canvas.setFont(SANS_BOLD, 8)
    canvas.drawString(MARGIN, 1.35 * cm, doc.capa_pe_esq)
    canvas.setFillColor(C['sand'])
    canvas.setFont(SANS, 8)
    canvas.drawRightString(w - MARGIN, 1.35 * cm, doc.capa_pe_dir)
    canvas.setStrokeColor(C['gold'])
    canvas.setLineWidth(0.5)
    try:
        canvas.setStrokeAlpha(0.45)
    except AttributeError:
        pass
    canvas.line(MARGIN, 1.05 * cm, w - MARGIN, 1.05 * cm)
    canvas.restoreState()


def fundo_conteudo(canvas, doc):
    w, h = PAGE
    canvas.saveState()
    canvas.setFillColor(C['cream'])
    canvas.rect(0, 0, w, h, fill=1, stroke=0)

    canvas.setFillColor(C['deep'])
    canvas.rect(0, h - 0.85 * cm, w, 0.85 * cm, fill=1, stroke=0)
    canvas.setFillColor(C['gold'])
    canvas.rect(0, h - 0.92 * cm, w, 0.07 * cm, fill=1, stroke=0)
    canvas.setFillColor(C['cream'])
    canvas.setFont(SANS_BOLD, 8.5)
    canvas.drawString(MARGIN, h - 0.55 * cm, 'ROTA COM FAMÍLIA')
    canvas.setFillColor(C['sand'])
    canvas.setFont(SANS, 8)
    canvas.drawRightString(w - MARGIN, h - 0.55 * cm, doc.ebook_title)

    rota_marca(canvas, w, 1.02 * cm, C['gold_d'], 0.95 * cm, 0.15)

    canvas.setFillColor(C['deep'])
    canvas.rect(0, 0, w, 0.7 * cm, fill=1, stroke=0)
    canvas.setFillColor(C['gold'])
    canvas.rect(0, 0.7 * cm, w, 0.05 * cm, fill=1, stroke=0)
    canvas.setFillColor(C['cream'])
    canvas.setFont(SANS, 8)
    canvas.drawString(MARGIN, 0.25 * cm, 'rotacomfamilia.com.br')
    canvas.setFillColor(C['gold'])
    canvas.drawCentredString(w / 2, 0.25 * cm, '·  ·  ·')
    canvas.setFillColor(C['cream'])
    canvas.drawRightString(w - MARGIN, 0.25 * cm, 'p. %02d' % (doc.page - 1))
    canvas.restoreState()


def fundo_contato(canvas, doc):
    """Ultima pagina: escura como a capa, para fechar o documento no mesmo tom."""
    w, h = PAGE
    canvas.saveState()
    canvas.setFillColor(C['deep'])
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setFillColor(C['gold'])
    canvas.rect(0, h - 0.28 * cm, w, 0.28 * cm, fill=1, stroke=0)
    rota_marca(canvas, w, 2.6 * cm, C['gold'], 1.4 * cm, 0.28)
    canvas.setFillColor(C['fern'])
    canvas.setFont(SANS, 8)
    canvas.drawCentredString(w / 2, 1.15 * cm, 'rotacomfamilia.com.br')
    canvas.restoreState()


class MidiaKit(BaseDocTemplate):
    def __init__(self, arquivo, titulo, capa):
        BaseDocTemplate.__init__(
            self, arquivo, pagesize=PAGE,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=1.5 * cm, bottomMargin=1.2 * cm,
            title=titulo, author='Rota com Família', creator='Rota com Família',
            subject='Mídia kit · parcerias com marcas')
        self.ebook_title = titulo
        self.capa_foto = capa['foto']
        self.capa_foco = capa.get('foco', 0.5)
        self.capa_pe_esq = capa['pe_esquerda']
        self.capa_pe_dir = capa['pe_direita']

        # A capa comeca abaixo da foto: topPadding empurra o texto para a metade
        # escura da pagina.
        f_capa = Frame(0, 0, PAGE[0], PAGE[1], leftPadding=2.4 * cm,
                       rightPadding=2.4 * cm, topPadding=PAGE[1] * 0.505,
                       bottomPadding=2.2 * cm, id='capa')
        f_corpo = Frame(MARGIN, 1.15 * cm, UTIL, PAGE[1] - 2.35 * cm,
                        leftPadding=0, rightPadding=0, topPadding=0.4 * cm,
                        bottomPadding=0, id='corpo')
        # o topPadding grande e o que centra o bloco de contato na folha: o
        # conteudo tem cerca de 14 cm num quadro de 22, e encostado no topo a
        # pagina ficava com um vazio de meia folha embaixo
        f_contato = Frame(MARGIN, 2.2 * cm, UTIL, PAGE[1] - 5.2 * cm,
                          leftPadding=0.8 * cm, rightPadding=0.8 * cm,
                          topPadding=3.6 * cm, bottomPadding=0, id='contato')
        self.addPageTemplates([
            PageTemplate(id='Capa', frames=[f_capa], onPage=fundo_capa),
            PageTemplate(id='Corpo', frames=[f_corpo], onPage=fundo_conteudo),
            PageTemplate(id='Contato', frames=[f_contato], onPage=fundo_contato),
        ])


# --------------------------------------------------------------------------
# Pecas
# --------------------------------------------------------------------------
def estilos():
    return {
        'capa_selo': ParagraphStyle('cs', fontName=SANS_BOLD, fontSize=9,
                                    leading=13, textColor=C['gold'],
                                    spaceAfter=12),
        'capa_titulo': ParagraphStyle('ct', fontName=SERIF, fontSize=42,
                                      leading=46, textColor=C['cream'],
                                      spaceAfter=8),
        'capa_sub': ParagraphStyle('cu', fontName=SANS, fontSize=12,
                                   leading=18, textColor=C['sand']),
        'ct_titulo': ParagraphStyle('kt', fontName=SERIF, fontSize=26,
                                    leading=32, textColor=C['cream'],
                                    alignment=TA_CENTER),
        'ct_frase': ParagraphStyle('kf', fontName=SERIF_IT, fontSize=14,
                                   leading=21, textColor=C['gold'],
                                   alignment=TA_CENTER),
        'ct_texto': ParagraphStyle('kx', fontName=SANS, fontSize=10.5,
                                   leading=16, textColor=C['sand'],
                                   alignment=TA_CENTER),
        'ct_rot': ParagraphStyle('kr', fontName=SANS_BOLD, fontSize=8,
                                 leading=11, textColor=C['fern'],
                                 alignment=TA_CENTER),
        'ct_val': ParagraphStyle('kv', fontName=SANS_BOLD, fontSize=11.5,
                                 leading=15, textColor=C['cream'],
                                 alignment=TA_CENTER),
        'legenda': ParagraphStyle('lg', fontName=SANS_BOLD, fontSize=7.6,
                                  leading=9.6, textColor=C['deep'],
                                  alignment=TA_CENTER),
        'pais': ParagraphStyle('ps', fontName=SANS, fontSize=6.8, leading=8.6,
                               textColor=C['muted'], alignment=TA_CENTER),
    }


class Etiquetas(Flowable):
    """Fichas do publico-alvo, quebrando linha sozinhas.

    Desenhadas no canvas, e nao como tabela, porque a quantidade muda com o
    JSON e uma tabela de coluna fixa deixaria buraco quando sobrasse um item.
    """
    def __init__(self, itens, tamanho=8.6):
        Flowable.__init__(self)
        self.itens = itens
        self.tam = tamanho

    def _linhas(self, aw):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        linhas, atual, larg = [], [], 0.0
        for t in self.itens:
            w = stringWidth(t, SANS_BOLD, self.tam) + 0.72 * cm
            if atual and larg + w > aw:
                linhas.append(atual)
                atual, larg = [], 0.0
            atual.append((t, w))
            larg += w + 0.22 * cm
        if atual:
            linhas.append(atual)
        return linhas

    def wrap(self, aw, ah):
        self._aw = aw
        self._ls = self._linhas(aw)
        self._h = len(self._ls) * 0.78 * cm
        return aw, self._h

    def draw(self):
        c = self.canv
        y = self._h - 0.56 * cm
        for linha in self._ls:
            x = 0
            for texto, w in linha:
                c.setFillColor(C['sand'])
                c.setStrokeColor(C['border'])
                c.setLineWidth(0.5)
                c.roundRect(x, y, w, 0.56 * cm, 0.28 * cm, fill=1, stroke=1)
                c.setFillColor(C['gold_d'])
                c.circle(x + 0.3 * cm, y + 0.28 * cm, 0.07 * cm, fill=1, stroke=0)
                c.setFillColor(C['deep'])
                c.setFont(SANS_BOLD, self.tam)
                c.drawString(x + 0.5 * cm, y + 0.19 * cm, texto)
                x += w + 0.22 * cm
            y -= 0.78 * cm


class Trilha(Flowable):
    """Linha do tempo do processo: bolinhas numeradas ligadas por tracejado.

    Usa a mesma rota tracejada do rodape, agora como conteudo: cada parada e
    uma etapa da parceria. Serve para a marca ver, sem precisar perguntar, o
    que acontece entre o briefing e o relatorio.
    """
    def __init__(self, etapas):
        Flowable.__init__(self)
        self.etapas = etapas

    def wrap(self, aw, ah):
        self._aw = aw
        col = aw / float(len(self.etapas))
        self._tit, self._txt = [], []
        for e in self.etapas:
            self._tit.append(simpleSplit(e['titulo'], SANS_BOLD, 8.2, col - 0.3 * cm))
            self._txt.append(simpleSplit(e['texto'], SANS, 7.4, col - 0.3 * cm))
        linhas = max(len(a) + len(b) for a, b in zip(self._tit, self._txt))
        self._h = 1.5 * cm + linhas * 0.34 * cm
        return aw, self._h

    def draw(self):
        c = self.canv
        n = len(self.etapas)
        col = self._aw / float(n)
        y = self._h - 0.42 * cm            # altura da linha das bolinhas
        r = 0.3 * cm

        c.saveState()
        c.setStrokeColor(C['gold'])
        c.setLineWidth(1.0)
        c.setDash(2.5, 3)
        for i in range(n - 1):
            c.line(col * (i + 0.5) + r + 2, y, col * (i + 1.5) - r - 2, y)
        c.setDash()

        for i, etapa in enumerate(self.etapas):
            x = col * (i + 0.5)
            c.setFillColor(C['gold'])
            c.circle(x, y, r, fill=1, stroke=0)
            c.setFillColor(C['deep'])
            c.setFont(SANS_BOLD, 8)
            c.drawCentredString(x, y - 2.9, '%d' % (i + 1))

            ty = y - r - 0.36 * cm
            c.setFillColor(C['deep'])
            c.setFont(SANS_BOLD, 8.2)
            for linha in self._tit[i]:
                c.drawCentredString(x, ty, linha)
                ty -= 0.34 * cm
            c.setFillColor(C['muted'])
            c.setFont(SANS, 7.4)
            for linha in self._txt[i]:
                c.drawCentredString(x, ty, linha)
                ty -= 0.34 * cm
        c.restoreState()


def cartoes(itens, colunas=2, gap=0.5 * cm):
    """Grade de cases do portfolio.

    O conteudo entra como lista de flowables dentro da celula, e nao como uma
    tabela aninhada: assim o fundo areia preenche a celula inteira e os cartoes
    da mesma linha terminam na mesma altura, mesmo com textos de tamanhos
    diferentes.
    """
    larg = (UTIL - gap * (colunas - 1)) / colunas
    cel_st = {
        'topo': ParagraphStyle('a', fontName=SANS_BOLD, fontSize=7.4,
                               leading=10, textColor=C['gold_d']),
        'tit': ParagraphStyle('b', fontName=SANS_BOLD, fontSize=9.8,
                              leading=12.6, textColor=C['deep']),
        'txt': ParagraphStyle('c', fontName=SANS, fontSize=8.4,
                              leading=11.4, textColor=C['text']),
        'tag': ParagraphStyle('d', fontName=SANS_OBL, fontSize=7.8,
                              leading=10, textColor=C['muted']),
    }

    def conteudo(it):
        return [
            Paragraph('%s &nbsp;·&nbsp; %s' % (it['plataforma'].upper(),
                                               it['metrica']), cel_st['topo']),
            Spacer(1, 0.12 * cm),
            Paragraph(it['titulo'], cel_st['tit']),
            Spacer(1, 0.1 * cm),
            Paragraph(it['texto'], cel_st['txt']),
            Spacer(1, 0.14 * cm),
            Paragraph(it['tag'], cel_st['tag']),
        ]

    linhas, larguras, estilo = [], [], []
    for c_ in range(colunas):
        larguras.append(larg)
        if c_ < colunas - 1:
            larguras.append(gap)

    grupos = [itens[i:i + colunas] for i in range(0, len(itens), colunas)]
    alturas = []
    for g, grupo in enumerate(grupos):
        if g:
            linhas.append([''] * len(larguras))
            alturas.append(0.42 * cm)
        linha = []
        for i in range(colunas):
            linha.append(conteudo(grupo[i]) if i < len(grupo) else '')
            if i < colunas - 1:
                linha.append('')
        linhas.append(linha)
        alturas.append(None)

    t = Table(linhas, colWidths=larguras, rowHeights=alturas)
    estilo = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]
    r = 0
    for g, grupo in enumerate(grupos):
        if g:
            r += 1
        for i in range(len(grupo)):
            col = i * 2
            estilo += [
                ('BACKGROUND', (col, r), (col, r), C['sand']),
                ('LINEBEFORE', (col, r), (col, r), 2.0, C['gold']),
                ('LEFTPADDING', (col, r), (col, r), 0.42 * cm),
                ('RIGHTPADDING', (col, r), (col, r), 0.38 * cm),
                ('TOPPADDING', (col, r), (col, r), 0.34 * cm),
                ('BOTTOMPADDING', (col, r), (col, r), 0.34 * cm),
            ]
        r += 1
    t.setStyle(TableStyle(estilo))
    return t


def mosaico(destinos, colunas=4, gap=0.28 * cm):
    """Fotos dos destinos, quadradas, com legenda embaixo."""
    E = estilos()
    lado = (UTIL - gap * (colunas - 1)) / colunas
    larguras = []
    for c_ in range(colunas):
        larguras.append(lado)
        if c_ < colunas - 1:
            larguras.append(gap)

    linhas, alturas = [], []
    grupos = [destinos[i:i + colunas] for i in range(0, len(destinos), colunas)]
    for g, grupo in enumerate(grupos):
        if g:
            linhas.append([''] * len(larguras))
            alturas.append(0.34 * cm)
        fila_img, fila_txt = [], []
        for i in range(colunas):
            if i < len(grupo):
                d = grupo[i]
                fila_img.append(foto(d['foto'], lado, lado, d.get('foco', 0.5)))
                fila_txt.append([Paragraph(d['cidade'], E['legenda']),
                                 Paragraph(d['pais'], E['pais'])])
            else:
                fila_img.append('')
                fila_txt.append('')
            if i < colunas - 1:
                fila_img.append('')
                fila_txt.append('')
        linhas.append(fila_img)
        alturas.append(lado)
        linhas.append(fila_txt)
        alturas.append(None)

    t = Table(linhas, colWidths=larguras, rowHeights=alturas)
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.1 * cm),
    ]))
    return t


def formatos(itens, S):
    """Os formatos de parceria: numero dourado, titulo e explicacao."""
    saida = []
    for i, it in enumerate(itens, 1):
        n = Paragraph('<font color="#D4A437">%02d</font>' % i,
                      ParagraphStyle('n', fontName=SERIF, fontSize=21,
                                     leading=23))
        corpo = [Paragraph('<b>%s</b>' % it['titulo'], S['h2']),
                 Paragraph(it['texto'], S['body'])]
        t = Table([[n, corpo]], colWidths=[1.4 * cm, UTIL - 1.4 * cm])
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0.3 * cm),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.3 * cm),
        ]))
        saida.append(KeepTogether(t))
    return saida


def canais(itens, E):
    """Contatos da ultima pagina: rotulo pequeno em cima, valor em destaque.

    Um por linha, e nao tres lado a lado. Lado a lado nao cabe: o e-mail
    sozinho ocupa quase metade da largura util e quebrava no meio da palavra,
    virando "contato@rotacomfamilia.com." e "br" na linha de baixo. Endereco
    cortado e o tipo de detalhe que faz a marca desistir de escrever.
    """
    linhas, estilo = [], [
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]
    for i, item in enumerate(itens):
        r = len(linhas)
        linhas.append([Paragraph(item['rotulo'].upper(), E['ct_rot'])])
        linhas.append([Paragraph(item['valor'], E['ct_val'])])
        estilo += [
            ('TOPPADDING', (0, r), (0, r), 0.36 * cm if i else 0),
            ('BOTTOMPADDING', (0, r), (0, r), 0.08 * cm),
            ('TOPPADDING', (0, r + 1), (0, r + 1), 0),
            ('BOTTOMPADDING', (0, r + 1), (0, r + 1), 0),
        ]
    t = Table(linhas, colWidths=[UTIL - 1.6 * cm])
    t.setStyle(TableStyle(estilo))
    return t


# --------------------------------------------------------------------------
# Montagem
# --------------------------------------------------------------------------
def montar(d):
    S = styles()
    E = estilos()
    st = []

    # ------------------------------------------------------------ 1. capa
    st.append(Image(os.path.join(FOTOS, d['logo']), width=2.5 * cm,
                    height=2.5 * cm, mask='auto'))
    st.append(Spacer(1, 0.5 * cm))
    st.append(Paragraph(d['capa']['selo'].upper(), E['capa_selo']))
    st.append(Paragraph(d['capa']['titulo'], E['capa_titulo']))
    st.append(Paragraph(d['capa']['subtitulo'], E['capa_sub']))

    # -------------------------------------------------------- 2. sobre nos
    # Sem o NextPageTemplate a capa vale para o documento inteiro e as paginas
    # seguintes saem com texto escuro sobre fundo escuro.
    st.append(NextPageTemplate('Corpo'))
    st.append(PageBreak())
    st.append(Paragraph('SOBRE NÓS', S['eyebrow']))
    st.append(Paragraph(d['sobre']['titulo'], S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm))

    texto = []
    for p in d['sobre']['paragrafos']:
        texto.append(Paragraph(p, S['body']))
    larg_foto = 5.4 * cm
    t = Table([[texto, foto(d['sobre']['foto'], larg_foto, 7.2 * cm,
                            d['sobre'].get('foco', 0.5))]],
              colWidths=[UTIL - larg_foto - 0.5 * cm, larg_foto + 0.5 * cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 0.5 * cm),
        ('RIGHTPADDING', (1, 0), (1, 0), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    st.append(t)

    st.append(Spacer(1, 0.45 * cm))
    st.append(Divider(width_pct=1.0, gap_before=0, gap_after=0.25 * cm))
    st.append(StatStrip([(x['numero'], x['rotulo']) for x in d['numeros']]))
    st.append(Divider(width_pct=1.0, gap_before=0, gap_after=0.28 * cm))
    st.append(Paragraph('<i>%s</i>' % d['numeros_nota'], S['small']))

    # ------------------------------------------- 3. publico, na mesma pagina
    # Publico tinha pagina propria e as duas terminavam na metade da folha.
    # Juntas cabem, e o assunto e o mesmo: quem somos e quem esta do outro lado.
    st.append(Spacer(1, 0.5 * cm))
    st.append(Paragraph(d['publico']['titulo'], S['h2']))
    for p in d['publico']['paragrafos']:
        st.append(Paragraph(p, S['body']))
    st.append(Spacer(1, 0.15 * cm))
    st.append(Etiquetas(d['publico']['etiquetas'] + d['publico']['regioes']))
    st.append(Spacer(1, 0.25 * cm))
    st.append(Callout(d['publico']['caixa_titulo'], d['publico']['caixa_texto'],
                      kind='note'))

    # -------------------------------------------------------- 4. portfolio
    st.append(PageBreak())
    st.append(Paragraph('PORTFÓLIO', S['eyebrow']))
    st.append(Paragraph(d['portfolio']['titulo'], S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm))
    st.append(Paragraph(d['portfolio']['texto'], S['body']))
    st.append(Spacer(1, 0.4 * cm))
    st.append(cartoes(d['portfolio']['cases']))
    st.append(Spacer(1, 0.45 * cm))
    st.append(Callout(d['portfolio']['caixa_titulo'],
                      d['portfolio']['caixa_texto'], kind='tip'))

    # -------------------------------------------------------- 5. destinos
    st.append(PageBreak())
    st.append(Paragraph('ACERVO', S['eyebrow']))
    st.append(Paragraph(d['destinos']['titulo'], S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm))
    st.append(Paragraph(d['destinos']['texto'], S['body']))
    st.append(Spacer(1, 0.35 * cm))
    st.append(mosaico(d['destinos']['fotos']))
    st.append(Spacer(1, 0.3 * cm))
    st.append(Divider(width_pct=1.0, gap_before=0, gap_after=0.25 * cm))
    st.append(StatStrip([(x['numero'], x['rotulo'])
                         for x in d['destinos']['resumo']]))
    st.append(Divider(width_pct=1.0, gap_before=0, gap_after=0.3 * cm))
    st.append(Paragraph('<b>Lista completa.</b> %s' % d['destinos']['lista'],
                        S['body']))

    # -------------------------------------------------------- 6. parcerias
    st.append(PageBreak())
    st.append(Paragraph('PROPOSTA DE PARCERIA', S['eyebrow']))
    st.append(Paragraph(d['parceria']['titulo'], S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm))
    st.append(Paragraph(d['parceria']['texto'], S['body']))
    st.append(Spacer(1, 0.35 * cm))
    st.extend(formatos(d['parceria']['formatos'], S))
    st.append(Spacer(1, 0.25 * cm))
    st.append(Paragraph('Como funciona, do primeiro contato ao relatório',
                        S['h3']))
    st.append(Spacer(1, 0.35 * cm))
    st.append(Trilha(d['parceria']['etapas']))
    st.append(Spacer(1, 0.45 * cm))
    st.append(Callout(d['parceria']['caixa_titulo'],
                      d['parceria']['caixa_texto'], kind='tip'))

    # --------------------------------------------------------- 7. contato
    st.append(NextPageTemplate('Contato'))
    st.append(PageBreak())
    st.append(Image(os.path.join(FOTOS, d['logo']), width=2.8 * cm,
                    height=2.8 * cm, mask='auto'))
    st.append(Spacer(1, 0.7 * cm))
    st.append(Paragraph('“%s”' % d['contato']['frase'], E['ct_frase']))
    st.append(Spacer(1, 0.7 * cm))
    st.append(Paragraph(d['contato']['titulo'], E['ct_titulo']))
    st.append(Spacer(1, 0.35 * cm))
    st.append(Paragraph(d['contato']['texto'], E['ct_texto']))
    st.append(Spacer(1, 0.85 * cm))
    st.append(canais(d['contato']['canais'], E))
    st.append(Spacer(1, 0.85 * cm))
    st.append(Divider(width_pct=0.3, gap_before=0, gap_after=0.5 * cm))
    st.append(Paragraph(d['contato']['redes'], E['ct_texto']))
    return st


def em_aberto(no, chave=''):
    """Procura marcadores [[...]] so dentro de texto.

    Serializar o dicionario e procurar '[[' acusa sempre, porque lista dentro de
    lista ja escreve '[[' no proprio JSON. Chaves com _ na frente sao notas para
    nos e nao vao para o PDF.
    """
    achados = []
    if isinstance(no, dict):
        for k, v in no.items():
            if not str(k).startswith('_'):
                achados += em_aberto(v, k)
    elif isinstance(no, list):
        for v in no:
            achados += em_aberto(v, chave)
    elif isinstance(no, str) and '[[' in no:
        achados.append('%s: %s' % (chave, no))
    return achados


def main():
    caminho = os.path.join(AQUI, 'mediakit.json')
    d = json.load(io.open(caminho, encoding='utf-8'))

    saida = os.path.join(AQUI, d['arquivo'])
    doc = MidiaKit(saida, d['titulo_doc'], d['capa'])
    doc.build(montar(d))

    tam = os.path.getsize(saida) / 1024.0
    print('OK: %s  (%.0f KB)' % (saida, tam))

    faltando = em_aberto(d)
    if faltando:
        print('ATENCAO: %d campo(s) em aberto:' % len(faltando))
        for t in faltando[:8]:
            print('  %s' % t[:80])
    return 0


if __name__ == '__main__':
    sys.exit(main())
