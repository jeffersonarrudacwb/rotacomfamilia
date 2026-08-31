# -*- coding: utf-8 -*-
"""Conferencia dos bilhetes antes de emitir, em uma pagina so.

    python propostas/build_conferencia.py boni

E o documento que o cliente deixa aberto na frente enquanto emite. Diferente
do roteiro, que conta a viagem, aqui so entra o que muda a emissao: numero do
voo, data, horario, milha, taxa e o que precisa ser conferido na hora.

Uma pagina, e sem capa de proposito. Capa em documento operacional custa uma
folha inteira para dizer o que o cabecalho ja diz, e obriga a rolar para achar
o numero do voo justamente quando a pessoa esta com a tela da Smiles aberta.

Cabecalho, rodape e silhueta vem da apresentacao, para os documentos do mesmo
cliente chegarem com a mesma cara.
"""
import io
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, 'ebooks'))
sys.path.insert(0, AQUI)

from reportlab.platypus import (  # noqa: E402
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether,
)
from reportlab.lib.units import cm  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.enums import (  # noqa: E402
    TA_RIGHT, TA_CENTER, TA_LEFT, TA_JUSTIFY,
)
from reportlab.lib.colors import HexColor  # noqa: E402

import skyline  # noqa: E402
from framework import (  # noqa: E402
    C, PAGE, MARGIN, SANS, SANS_BOLD, SANS_OBL, SERIF, Divider, Callout,
)

PDF_DIR = os.path.join(AQUI, 'pdf')
os.makedirs(PDF_DIR, exist_ok=True)

LARGURA_UTIL = PAGE[0] - 2 * MARGIN
ALINHA = {'e': TA_LEFT, 'c': TA_CENTER, 'd': TA_RIGHT}


# --------------------------------------------------------------------------
# Pagina
# --------------------------------------------------------------------------
def fundo(canvas, doc):
    """Mesmo topo e rodape dos outros documentos do Boni.

    A unica diferenca e o canto direito do rodape: nos documentos de varias
    paginas ele traz o numero da pagina, e aqui isso seria sempre 'p. 01'.
    No lugar entra de quem e o documento e de quando ele e, que e o que
    importa numa folha que vai ficar em cima da mesa junto com outras.
    """
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

    skyline.desenhar(canvas, w, base=0.75 * cm, cor=C['gold_d'],
                     altura=2.6 * cm, opacidade=0.13)

    canvas.setFillColor(C['deep'])
    canvas.rect(0, 0, w, 0.7 * cm, fill=1, stroke=0)
    canvas.setFillColor(C['gold'])
    canvas.rect(0, 0.7 * cm, w, 0.05 * cm, fill=1, stroke=0)
    canvas.setFillColor(C['cream'])
    canvas.setFont(SANS, 8)
    canvas.drawString(MARGIN, 0.25 * cm, 'rotacomfamilia.com.br')
    canvas.setFillColor(C['gold'])
    canvas.drawCentredString(w / 2, 0.25 * cm, '·  ·  ·')
    canvas.setFillColor(C['sand'])
    canvas.drawRightString(w - MARGIN, 0.25 * cm, doc.rodape_direita)
    canvas.restoreState()


class Conferencia(BaseDocTemplate):
    def __init__(self, filename, title, rodape_direita):
        BaseDocTemplate.__init__(
            self, filename, pagesize=PAGE,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=1.5 * cm, bottomMargin=1.2 * cm,
            title=title, author='Rota com Família', creator='Rota com Família')
        self.ebook_title = title
        self.rodape_direita = rodape_direita
        corpo = Frame(MARGIN, 1.15 * cm, PAGE[0] - 2 * MARGIN,
                      PAGE[1] - 2.35 * cm, leftPadding=0, rightPadding=0,
                      topPadding=0.4 * cm, bottomPadding=0, id='corpo')
        self.addPageTemplates([
            PageTemplate(id='Corpo', frames=[corpo], onPage=fundo),
        ])


# --------------------------------------------------------------------------
# Quadro
# --------------------------------------------------------------------------
def estilos_apertados():
    """Os estilos do framework, encolhidos para caber na pagina unica.

    O h1 de 26pt e o corpo de 10.5 sao do ebook, onde a pagina respira. Aqui
    o documento tem duas tabelas obrigatorias e uma folha so: com os tamanhos
    de la ele fecha em duas paginas, e a segunda entra com uma tabela orfa no
    topo. Encolher o titulo custa menos ao leitor do que virar a folha para
    achar a taxa enquanto emite.
    """
    return {
        'h1': ParagraphStyle('h1', fontName=SERIF, fontSize=20, leading=24,
                             textColor=C['deep'], spaceBefore=2, spaceAfter=5),
        'h2': ParagraphStyle('h2', fontName=SERIF, fontSize=13, leading=17,
                             textColor=C['deep'], spaceBefore=8, spaceAfter=2),
        'body': ParagraphStyle('body', fontName=SANS, fontSize=9.6,
                               leading=13.2, textColor=C['text'],
                               alignment=TA_JUSTIFY, spaceAfter=5),
        'eyebrow': ParagraphStyle('eyebrow', fontName=SANS_BOLD, fontSize=8.2,
                                  leading=11, textColor=C['gold_d'],
                                  spaceAfter=1),
        'small': ParagraphStyle('sm', fontName=SANS, fontSize=8.3,
                                leading=11.2, textColor=C['muted'],
                                alignment=TA_JUSTIFY),
    }


def celulas(linha, fonte, cor, alinhamento, tamanho=8.2):
    """Cada celula vira Paragraph para poder quebrar linha dentro da coluna.

    O alinhamento fica no estilo do Paragraph, e nao no ALIGN da TableStyle:
    quando a celula e um Paragraph, o ALIGN da tabela nao tem efeito nenhum.
    """
    saida = []
    for i, c in enumerate(linha):
        a = ALINHA.get(alinhamento[i] if i < len(alinhamento) else 'e', TA_LEFT)
        st = ParagraphStyle('c%d' % i, fontName=fonte, fontSize=tamanho,
                            leading=tamanho * 1.26, textColor=cor, alignment=a)
        saida.append(Paragraph(str(c), st))
    return saida


def quadro(bloco, vaos=()):
    """Tabela no estilo dos outros documentos, com linhas de vao.

    Uma linha de vao e a conexao: ela nao tem voo, nem horario, nem milha
    propria, e repetir travessao em cinco colunas so suja a leitura. Nessas
    linhas as colunas 1 ate a ultima viram uma celula so, centralizada, com a
    coluna do numero do bilhete preservada a esquerda para nao perder a
    referencia de a qual bilhete a conexao pertence.
    """
    n = len(bloco['colunas'])
    alin = bloco.get('alinhamento') or (['c'] + ['e'] * (n - 2) + ['d'])
    vaos = set(vaos)

    corpo = [celulas(bloco['colunas'], SANS_BOLD, C['cream'], alin)]
    for i, linha in enumerate(bloco['linhas']):
        if i in vaos:
            # O texto do vao vem na coluna 1; as demais entram vazias so para
            # a linha ter o mesmo numero de celulas que o resto da tabela.
            texto = ParagraphStyle('vao', fontName=SANS_OBL, fontSize=8.2,
                                   leading=11, textColor=C['muted'],
                                   alignment=TA_CENTER)
            corpo.append([Paragraph('', texto), Paragraph(linha[1], texto)]
                         + [Paragraph('', texto)] * (n - 2))
        else:
            corpo.append(celulas(linha, SANS, C['text'], alin))

    larguras = [x * cm for x in bloco['larguras']]
    sobra = LARGURA_UTIL - sum(larguras)
    if sobra:
        larguras[-1] += sobra

    t = Table(corpo, colWidths=larguras, repeatRows=1)
    estilo = [
        ('BACKGROUND', (0, 0), (-1, 0), C['deep']),
        ('GRID', (0, 0), (-1, -1), 0.4, C['border']),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0.18 * cm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0.18 * cm),
        ('TOPPADDING', (0, 0), (-1, -1), 0.11 * cm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.11 * cm),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C['cream'], C['sand']]),
    ]
    # Depois do ROWBACKGROUNDS, senao a listra alternada cobre o vao e ele
    # aparece ora claro ora escuro conforme a posicao na tabela.
    for i in sorted(vaos):
        estilo.append(('SPAN', (1, i + 1), (-1, i + 1)))
        estilo.append(('BACKGROUND', (0, i + 1), (-1, i + 1),
                       HexColor('#EFE7CE')))
        estilo.append(('TOPPADDING', (0, i + 1), (-1, i + 1), 0.08 * cm))
        estilo.append(('BOTTOMPADDING', (0, i + 1), (-1, i + 1), 0.08 * cm))
    for i in bloco.get('destaque', []):
        estilo.append(('BACKGROUND', (0, i + 1), (-1, i + 1),
                       HexColor('#F7E1B8')))
    t.setStyle(TableStyle(estilo))
    return t


# --------------------------------------------------------------------------
def montar(d):
    S = estilos_apertados()
    st = []

    st.append(Paragraph(d['eyebrow'], S['eyebrow']))
    st.append(Paragraph(d['titulo'], S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.05 * cm,
                      gap_after=0.22 * cm))
    for p in d['abertura']:
        st.append(Paragraph(p, S['body']))

    st.append(Spacer(1, 0.1 * cm))
    st.append(Callout(d['mudou_titulo'], d['mudou_texto'],
                      kind=d.get('mudou_tipo', 'warn')))

    st.append(Spacer(1, 0.1 * cm))
    st.append(KeepTogether([
        Paragraph(d['voos_titulo'], S['h2']),
        Spacer(1, 0.16 * cm),
        quadro({'colunas': d['voos_colunas'],
                'larguras': d['voos_larguras'],
                'alinhamento': d['voos_alinhamento'],
                'linhas': d['voos_linhas'],
                'destaque': d.get('voos_destaque', [])},
               vaos=d.get('voos_vaos', [])),
    ]))
    st.append(Spacer(1, 0.14 * cm))
    st.append(Paragraph('<i>%s</i>' % d['voos_nota'], S['small']))

    st.append(Spacer(1, 0.1 * cm))
    st.append(KeepTogether([
        Paragraph(d['custos_titulo'], S['h2']),
        Spacer(1, 0.16 * cm),
        quadro({'colunas': d['custos_colunas'],
                'larguras': d['custos_larguras'],
                'alinhamento': d['custos_alinhamento'],
                'linhas': d['custos_linhas'],
                'destaque': d.get('custos_destaque', [])}),
    ]))
    st.append(Spacer(1, 0.14 * cm))
    st.append(Paragraph('<i>%s</i>' % d['custos_nota'], S['small']))

    st.append(Spacer(1, 0.26 * cm))
    st.append(Paragraph(d['fecho'], S['small']))
    st.append(Spacer(1, 0.2 * cm))
    st.append(Paragraph('<b>%s</b>' % d['assinatura'], S['small']))
    return st


def em_aberto(d):
    """Sobrou algum [[campo]] do modelo sem preencher?

    So percorre string: serializar o dicionario inteiro daria falso positivo,
    porque uma lista de listas ja escreve '[[' sozinha.
    """
    faltando = []

    def andar(v):
        if isinstance(v, str):
            if '[[' in v:
                faltando.append(v)
        elif isinstance(v, dict):
            for x in v.values():
                andar(x)
        elif isinstance(v, list):
            for x in v:
                andar(x)

    andar(d)
    return faltando


def main():
    nome = sys.argv[1] if len(sys.argv) > 1 else 'boni'
    caminho = os.path.join(AQUI, 'dados', '%s-conferencia.json' % nome)
    if not os.path.exists(caminho):
        print('Nao achei %s' % caminho)
        return 1

    d = json.load(io.open(caminho, encoding='utf-8'))
    for x in em_aberto(d):
        print('AVISO: campo em aberto -> %s' % x)

    saida = os.path.join(PDF_DIR, '%s.pdf' % d['arquivo'])
    doc = Conferencia(saida, d['titulo_doc'], d['rodape_direita'])
    doc.build(montar(d))
    if doc.page > 1:
        print('ERRO: o documento saiu com %d paginas, e ele so faz sentido'
              ' em uma. Corte texto no JSON.' % doc.page)
        return 1
    print('OK: %s (1 pagina)' % saida)
    return 0


if __name__ == '__main__':
    sys.exit(main())
