# -*- coding: utf-8 -*-
"""Apresentacao comercial da assessoria, em tres paginas.

    python propostas/build_apresentacao.py boni-nova-york

E o documento que vai ANTES do trabalho: o que entendemos, como trabalhamos e
quanto custa. O plano com voos, milhas e taxas e outro documento, gerado pelo
build_proposta.py, e vai depois.

A silhueta de Nova York no rodape das paginas vem de skyline.py.
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
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak, Table,
    TableStyle, NextPageTemplate,
)
from reportlab.lib.units import cm  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.enums import TA_CENTER  # noqa: E402

import skyline  # noqa: E402
from framework import (  # noqa: E402
    C, PAGE, MARGIN, SANS, SANS_BOLD, SERIF, styles, Divider, Callout,
    bullet_list,
)

PDF_DIR = os.path.join(AQUI, 'pdf')
os.makedirs(PDF_DIR, exist_ok=True)


# --------------------------------------------------------------------------
# Paginas
# --------------------------------------------------------------------------
def fundo_capa(canvas, doc):
    w, h = PAGE
    canvas.saveState()
    canvas.setFillColor(C['deep'])
    canvas.rect(0, 0, w, h, fill=1, stroke=0)

    # faixa dourada no topo
    canvas.setFillColor(C['gold'])
    canvas.rect(0, h - 0.28 * cm, w, 0.28 * cm, fill=1, stroke=0)

    # a cidade, grande e discreta, ocupando o terco de baixo
    skyline.desenhar(canvas, w, base=1.9 * cm, cor=C['gold'],
                     altura=5.2 * cm, opacidade=0.22)

    # linha do horizonte
    canvas.saveState()
    canvas.setStrokeColor(C['gold'])
    canvas.setLineWidth(0.6)
    try:
        canvas.setStrokeAlpha(0.35)
    except AttributeError:
        pass
    canvas.line(MARGIN, 1.9 * cm, w - MARGIN, 1.9 * cm)
    canvas.restoreState()

    canvas.setFillColor(C['cream'])
    canvas.setFont(SANS, 8)
    canvas.drawCentredString(w / 2, 1.05 * cm, 'rotacomfamilia.com.br')
    canvas.restoreState()


def fundo_conteudo(canvas, doc):
    w, h = PAGE
    canvas.saveState()
    canvas.setFillColor(C['cream'])
    canvas.rect(0, 0, w, h, fill=1, stroke=0)

    # topo
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

    # a cidade em marca d'agua, acima do rodape
    skyline.desenhar(canvas, w, base=0.75 * cm, cor=C['gold_d'],
                     altura=2.6 * cm, opacidade=0.13)

    # rodape
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


class Apresentacao(BaseDocTemplate):
    def __init__(self, filename, title):
        BaseDocTemplate.__init__(
            self, filename, pagesize=PAGE,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=1.5 * cm, bottomMargin=1.2 * cm,
            title=title, author='Rota com Família', creator='Rota com Família')
        self.ebook_title = title
        capa = Frame(0, 0, PAGE[0], PAGE[1], leftPadding=2.5 * cm,
                     rightPadding=2.5 * cm, topPadding=3.2 * cm,
                     bottomPadding=8 * cm, id='capa')
        # espaco extra embaixo para o texto nao encostar na silhueta
        corpo = Frame(MARGIN, 1.15 * cm, PAGE[0] - 2 * MARGIN,
                      PAGE[1] - 2.35 * cm, leftPadding=0, rightPadding=0,
                      topPadding=0.4 * cm, bottomPadding=0, id='corpo')
        self.addPageTemplates([
            PageTemplate(id='Capa', frames=[capa], onPage=fundo_capa),
            PageTemplate(id='Corpo', frames=[corpo], onPage=fundo_conteudo),
        ])


# --------------------------------------------------------------------------
# Blocos
# --------------------------------------------------------------------------
def estilos_extra():
    return {
        'capa_selo': ParagraphStyle(
            'capa_selo', fontName=SANS_BOLD, fontSize=9, leading=13,
            textColor=C['gold'], spaceAfter=14),
        'capa_titulo': ParagraphStyle(
            'capa_titulo', fontName=SERIF, fontSize=40, leading=44,
            textColor=C['cream'], spaceAfter=10),
        'capa_sub': ParagraphStyle(
            'capa_sub', fontName=SANS, fontSize=12.5, leading=19,
            textColor=C['sand'], spaceAfter=6),
        'capa_pe': ParagraphStyle(
            'capa_pe', fontName=SANS, fontSize=10, leading=15,
            textColor=C['fern']),
        'preco': ParagraphStyle(
            'preco', fontName=SERIF, fontSize=34, leading=38,
            textColor=C['deep'], alignment=TA_CENTER),
        'preco_rot': ParagraphStyle(
            'preco_rot', fontName=SANS_BOLD, fontSize=8.5, leading=12,
            textColor=C['muted'], alignment=TA_CENTER),
    }


def passo(numero, titulo, texto, S):
    """Uma etapa do metodo: numero dourado grande + titulo + explicacao."""
    n = Paragraph('<font color="#D4A437">%s</font>' % numero,
                  ParagraphStyle('n', fontName=SERIF, fontSize=22, leading=24))
    corpo = [Paragraph('<b>%s</b>' % titulo, S['h2']),
             Paragraph(texto, S['body'])]
    t = Table([[n, corpo]], colWidths=[1.5 * cm, 15.2 * cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 0.3 * cm),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.34 * cm),
    ]))
    return t


def montar(d):
    S = styles()
    E = estilos_extra()
    cli, via, hon = d['cliente'], d['viagem'], d['honorarios']
    saida = os.path.join(PDF_DIR, 'apresentacao-%s.pdf' % d['slug'])
    doc = Apresentacao(saida, 'Assessoria de emissão · %s' % via['destino'])
    st = []

    # ---------------------------------------------------------- 1. capa
    st.append(Paragraph('PROPOSTA DE ASSESSORIA', E['capa_selo']))
    st.append(Paragraph('%s,<br/>vamos para<br/>Nova York.' % cli['como_chamar'],
                        E['capa_titulo']))
    st.append(Spacer(1, 0.5 * cm))
    st.append(Paragraph(
        '%s · %s a %s' % (via['destino'], via['ida'], via['volta']),
        E['capa_sub']))
    st.append(Paragraph(via['passageiros_resumo'], E['capa_sub']))
    st.append(Spacer(1, 0.8 * cm))
    st.append(Paragraph(
        'Preparado por Jefferson · Rota com Família<br/>%s' % d['data'],
        E['capa_pe']))

    # ------------------------------------------------ 2. o que entendemos
    # Sem o NextPageTemplate a capa vale para o documento inteiro, e as paginas
    # seguintes saem com fundo escuro e texto escuro, ou seja, ilegiveis.
    st.append(NextPageTemplate('Corpo'))
    st.append(PageBreak())
    st.append(Paragraph('O QUE ENTENDEMOS', S['eyebrow']))
    st.append(Paragraph('O seu pedido, escrito de volta.', S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm))

    st.append(Paragraph(
        'Antes de qualquer pesquisa, esta página existe para você conferir se '
        'entendemos certo. <b>Se algum item estiver diferente do que você quis '
        'dizer, me avise antes de a gente começar</b>, porque cada um deles '
        'muda o caminho da busca.', S['body']))
    st.append(Spacer(1, 0.35 * cm))

    linhas = [[Paragraph('<b>%s</b>' % k,
                         ParagraphStyle('k', fontName=SANS_BOLD, fontSize=9.5,
                                        leading=13, textColor=C['deep'])),
               Paragraph(v, ParagraphStyle('v', fontName=SANS, fontSize=9.5,
                                           leading=13, textColor=C['text']))]
              for k, v in d['entendimento']]
    t = Table(linhas, colWidths=[4.6 * cm, 12.1 * cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 0.4 * cm),
        ('TOPPADDING', (0, 0), (-1, -1), 0.22 * cm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.22 * cm),
        ('LINEBELOW', (0, 0), (-1, -2), 0.4, C['border']),
    ]))
    st.append(t)

    st.append(Spacer(1, 0.4 * cm))
    st.append(Callout(
        'A data de chegada não é uma data qualquer',
        'Vocês pousam em 25 de novembro, véspera do Dia de Ação de Graças. É '
        'historicamente o dia de maior movimento aéreo do ano nos Estados '
        'Unidos, e isso pesa na escolha entre voo direto e voo com conexão. '
        'Vai estar considerado no plano.', kind='note'))

    # ----------------------------------------------- 3. o que e como fazemos
    st.append(PageBreak())
    st.append(Paragraph('O TRABALHO', S['eyebrow']))
    st.append(Paragraph('O que fazemos, e como.', S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm))

    st.append(Paragraph(
        'A assessoria é uma busca organizada, feita com o seu saldo e as suas '
        'datas na mão. Estes são os passos, na ordem em que acontecem:',
        S['body']))
    st.append(Spacer(1, 0.35 * cm))

    for i, (titulo, texto) in enumerate(d['metodo'], 1):
        st.append(passo('%02d' % i, titulo, texto, S))

    st.append(Callout(
        'O que a gente promete, e o que não promete',
        'Não prometemos economia alta, e desconfie de quem promete: quem '
        'define o preço do resgate é a companhia, não o assessor. O que '
        'fazemos é procurar em vários programas e combinações, achar as '
        'melhores oportunidades disponíveis naquelas datas e montar o plano '
        'em cima delas. Se a conta não fechar a seu favor, a gente diz isso '
        'com todas as letras, e você não emite.', kind='warn'))

    # ------------------------------------------------------ 4. valores
    st.append(PageBreak())
    st.append(Paragraph('VALORES', S['eyebrow']))
    st.append(Paragraph('Quanto custa e o que vem junto.', S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm))

    caixa = Table([[
        Paragraph('ASSESSORIA COMPLETA', E['preco_rot']),
    ], [
        Paragraph('<b>%s</b>' % hon['valor'], E['preco']),
    ], [
        Paragraph(hon['resumo'], ParagraphStyle(
            'cx', fontName=SANS, fontSize=9.5, leading=14,
            textColor=C['text'], alignment=TA_CENTER)),
    ]], colWidths=[16.7 * cm])
    caixa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C['sand']),
        ('BOX', (0, 0), (-1, -1), 1.2, C['gold']),
        ('TOPPADDING', (0, 0), (-1, 0), 0.5 * cm),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 0.55 * cm),
        ('LEFTPADDING', (0, 0), (-1, -1), 1 * cm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1 * cm),
    ]))
    st.append(caixa)

    st.append(Spacer(1, 0.45 * cm))
    st.append(Paragraph('Está incluído', S['h2']))
    st.extend(bullet_list(d['incluido']))

    st.append(Spacer(1, 0.25 * cm))
    st.append(Paragraph('Junto com o plano, você recebe', S['h2']))
    st.append(Paragraph(
        'Não é só a lista de voos. O documento final vem com o que costuma '
        'derrubar viagem já paga, conferido para o seu caso:', S['body']))
    st.extend(bullet_list(d['extras']))

    st.append(Spacer(1, 0.3 * cm))
    st.append(Callout(
        'Como seguimos daqui',
        d['proximo_passo'], kind='tip'))

    return doc, st, saida


def main():
    if len(sys.argv) < 2:
        print('uso: python propostas/build_apresentacao.py <nome-do-json>')
        raise SystemExit(1)
    nome = sys.argv[1].replace('.json', '')
    caminho = os.path.join(AQUI, 'dados', nome + '-apresentacao.json')
    if not os.path.exists(caminho):
        print('nao achei %s' % caminho)
        raise SystemExit(1)

    d = json.load(io.open(caminho, encoding='utf-8'))
    doc, st, saida = montar(d)
    doc.build(st)
    print('OK: %s' % saida)

    # Conta so dentro de texto. Contar no JSON serializado dava falso
    # positivo, porque lista dentro de lista tambem escreve "[[".
    def buracos_em(o):
        if isinstance(o, str):
            return o.count('[[')
        if isinstance(o, dict):
            return sum(buracos_em(v) for k, v in o.items()
                       if not k.startswith('_'))
        if isinstance(o, list):
            return sum(buracos_em(v) for v in o)
        return 0

    buracos = buracos_em(d)
    if buracos:
        print('ATENCAO: %d campo(s) ainda com [[...]].' % buracos)
    else:
        print('Nenhum campo em aberto: pode enviar.')


if __name__ == '__main__':
    main()
