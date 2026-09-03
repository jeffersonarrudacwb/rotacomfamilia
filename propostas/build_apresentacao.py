# -*- coding: utf-8 -*-
"""Apresentacao comercial da assessoria.

    python propostas/build_apresentacao.py boni-nova-york
    python propostas/build_apresentacao.py agnaldo-orlando

E o documento que vai ANTES do trabalho: o que entendemos, como trabalhamos e
quanto custa. O plano com voos, milhas e taxas e outro documento, gerado pelo
build_proposta.py, e vai depois.

TRES COISAS SAO OPCIONAIS, e e por elas que o mesmo gerador serve trabalhos de
tamanhos diferentes:

  "silhueta"      qual desenho vai no fundo (skyline.py). Sem isto, Nova York.
  "paginas_extra" paginas de assunto proprio entre o entendimento e o metodo.
                  A do Agnaldo explica a conta das milhas, que e o miolo
                  daquele trabalho e nao cabia em nenhuma das outras.
  "planos"        duas faixas de preco lado a lado, com uma tabela dizendo o
                  que cada uma cobre. Sem isto, vale "honorarios", que e uma
                  caixa so -- que e o caso do Boni.
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

    # o destino, grande e discreto, ocupando o terco de baixo
    doc.silhueta(canvas, w, base=1.9 * cm, cor=C['gold'],
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

    # o destino em marca d'agua, acima do rodape
    doc.silhueta(canvas, w, base=0.75 * cm, cor=C['gold_d'],
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
    def __init__(self, filename, title, silhueta='nova-york'):
        self.silhueta = skyline.escolher(silhueta)
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


def caixa_preco(plano, E, largura, compacta=False):
    """Uma faixa de preco: selo dourado, valor grande, uma linha do que cobre.

    O selo fica numa faixa colada no topo para o olho bater nele antes do
    numero. Nao ha preco riscado em lugar nenhum deste documento: nunca
    cobramos outro valor, entao inventar um "de R$ X por" seria mentira.
    """
    # Compacta e a caixa de meia largura, quando ha duas lado a lado. As
    # medidas soltas sao as da caixa larga, e nao podem mudar: o documento do
    # Boni ja foi enviado com elas.
    tam = 26 if compacta else 34
    fol = 0.5 * cm if compacta else 1 * cm
    selo = Paragraph('<b>%s</b>' % plano['selo'], ParagraphStyle(
        'selo', fontName=SANS_BOLD, fontSize=8.5 if compacta else 9,
        leading=12, textColor=C['deep'], alignment=TA_CENTER))
    linhas = [
        [selo],
        [Paragraph('<b>%s</b>' % plano['valor'], ParagraphStyle(
            'pr', parent=E['preco'], fontSize=tam, leading=tam + 4))],
        [Paragraph(plano['resumo'], ParagraphStyle(
            'cx', fontName=SANS, fontSize=8.5 if compacta else 9.5,
            leading=12 if compacta else 14, textColor=C['text'],
            alignment=TA_CENTER))],
    ]
    if plano.get('aviso'):
        linhas.append([Paragraph(plano['aviso'], ParagraphStyle(
            'cxa', fontName=SANS, fontSize=8.5 if compacta else 9,
            leading=12 if compacta else 13, textColor=C['gold_d'],
            alignment=TA_CENTER))])

    # Duas caixas saem com o mesmo peso, e o cliente escolhe sozinho. So a
    # borda engrossa no plano marcado com "destaque". Nunca ha seta nem "mais
    # vendido": nao vendemos nada duas vezes dentro do mesmo documento.
    grossa = 1.8 if plano.get('destaque') else 0.8
    t = Table(linhas, colWidths=[largura])
    estilo = [
        ('BACKGROUND', (0, 0), (-1, -1), C['sand']),
        ('BACKGROUND', (0, 0), (0, 0), C['gold']),
        ('BOX', (0, 0), (-1, -1), grossa if compacta else 1.2, C['gold']),
        ('TOPPADDING', (0, 0), (0, 0), 0.2 * cm if compacta else 0.22 * cm),
        ('BOTTOMPADDING', (0, 0), (0, 0), 0.2 * cm if compacta else 0.22 * cm),
        ('TOPPADDING', (0, 1), (-1, 1), 0.25 * cm if compacta else 0.35 * cm),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 0.4 * cm if compacta else 0.5 * cm),
        ('LEFTPADDING', (0, 0), (-1, -1), fol),
        ('RIGHTPADDING', (0, 0), (-1, -1), fol),
    ]
    if plano.get('aviso'):
        # linha fina separando o que e preco do que e condicao
        estilo.append(('LINEABOVE', (0, -1), (-1, -1), 0.5, C['gold']))
        estilo.append(('TOPPADDING', (0, -1), (-1, -1),
                       0.3 * cm if compacta else 0.35 * cm))
    t.setStyle(TableStyle(estilo))
    return t


def tabela_planos(planos, comparativo):
    """O que cada faixa cobre, em colunas de check.

    Escolhi tabela em vez de duas listas porque a pergunta do cliente e "o que
    eu ganho pagando mais", e duas listas lado a lado obrigam ele a cruzar item
    por item na cabeca. Aqui a linha vazia responde sozinha.

    O que nao entra no plano leva ponto medio, e nao travessao. Travessao ali
    virava traço de texto no meio da tabela e sujava a pagina; o ponto medio ja
    e o separador da marca, aparece no rodape e na capa.

    ARMADILHA: o ✓ e o · saem em ZapfDingbats, e o texto extraido do PDF volta
    como lixo. Conferencia desta tabela e no olho, nao com get_text().
    """
    largura_item = 16.7 * cm - len(planos) * 2.5 * cm
    cab = [Paragraph('', ParagraphStyle('vazio', fontSize=8))]
    for pl in planos:
        cab.append(Paragraph('<b>%s</b>' % pl['coluna'], ParagraphStyle(
            'cab', fontName=SANS_BOLD, fontSize=8, leading=10,
            textColor=C['deep'], alignment=TA_CENTER)))

    linhas = [cab]
    for item, marcas in comparativo:
        celulas = [Paragraph(item, ParagraphStyle(
            'it', fontName=SANS, fontSize=9, leading=12, textColor=C['text']))]
        for tem in marcas:
            # Bolinha cinza para o que nao entra, e nao tracinho: tracinho de
            # qualquer tamanho le como travessao no meio da tabela.
            #
            # Circulo VAZADO seria o ideal e nao da: a Helvetica embutida nao
            # tem o glifo, e o ReportLab troca por um quadrado preto solido,
            # que na pagina vira um borrao. Bolinha cheia, pequena e clara,
            # resolve. Ponto medio foi tentado antes e sumia na folha.
            cor, marca, corpo = (('#A8821F', '✓', 11) if tem
                                 else ('#BBB3A1', '●', 7))
            celulas.append(Paragraph(
                '<font color="%s">%s</font>' % (cor, marca),
                ParagraphStyle('mk', fontName=SANS_BOLD, fontSize=corpo,
                               leading=13, alignment=TA_CENTER)))
        linhas.append(celulas)

    t = Table(linhas, colWidths=[largura_item] + [2.5 * cm] * len(planos),
              repeatRows=1)
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, -1), 0.3 * cm),
        ('LEFTPADDING', (1, 0), (-1, -1), 0),
        ('RIGHTPADDING', (1, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0.16 * cm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.16 * cm),
        ('LINEBELOW', (0, 0), (-1, -2), 0.4, C['border']),
        ('LINEBELOW', (0, 0), (-1, 0), 0.8, C['gold_d']),
    ]))
    return t


def pagina_extra(pg, S):
    """Uma pagina de assunto proprio: titulo, abertura, blocos e caixa.

    Existe para o trabalho que nao cabe nas tres paginas fixas. A do Agnaldo
    e a conta das milhas: sem ela, a proposta pediria R$ 579 sem nunca mostrar
    que ha uma conta a fazer.
    """
    fora = [PageBreak(),
            Paragraph(pg['eyebrow'], S['eyebrow']),
            Paragraph(pg['titulo'], S['h1']),
            Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm)]
    if pg.get('intro'):
        fora.append(Paragraph(pg['intro'], S['body']))
        fora.append(Spacer(1, 0.15 * cm))
    for titulo, texto in pg.get('blocos', []):
        fora.append(Paragraph('<b>%s</b>' % titulo, S['h2']))
        fora.append(Paragraph(texto, S['body']))
    if pg.get('callout'):
        titulo, texto, tipo = pg['callout']
        fora.append(Spacer(1, 0.2 * cm))
        fora.append(Callout(titulo, texto, kind=tipo))
    return fora


def montar(d):
    S = styles()
    E = estilos_extra()
    cli, via = d['cliente'], d['viagem']
    planos = d.get('planos')
    saida = os.path.join(PDF_DIR, 'apresentacao-%s.pdf' % d['slug'])
    # O que aparece no canto do cabecalho de todas as paginas. Vem dos dados
    # porque nem todo trabalho e emissao: o do Agnaldo inclui hotel, carro e
    # parque, e chamar aquilo de "assessoria de emissao" seria vender menos do
    # que se entrega.
    doc = Apresentacao(
        saida,
        d.get('titulo_corrente', 'Assessoria de emissão · %s' % via['destino']),
        silhueta=d.get('silhueta', 'nova-york'))
    st = []

    # ---------------------------------------------------------- 1. capa
    # O titulo vem dos dados, nao daqui: proposta de outro destino nao deveria
    # exigir edicao de codigo.
    st.append(Paragraph('PROPOSTA DE ASSESSORIA', E['capa_selo']))
    st.append(Paragraph(d['capa_titulo'], E['capa_titulo']))
    st.append(Spacer(1, 0.6 * cm))
    st.append(Paragraph('<b>Preparado para %s</b>' % cli['nome'], E['capa_sub']))
    # Nem toda viagem tem ida e volta com data. O Anderson quer so a ida, "entre
    # outubro e novembro": escrever "13/12/2026 a " ali seria inventar data que
    # o cliente nao deu. Com "periodo" no JSON, a linha e essa e ponto.
    st.append(Paragraph(
        '%s · %s' % (via['destino'],
                     via.get('periodo') or '%s a %s' % (via['ida'],
                                                        via['volta'])),
        E['capa_sub']))
    st.append(Paragraph(via['passageiros_resumo'], E['capa_sub']))
    st.append(Spacer(1, 0.8 * cm))
    st.append(Paragraph(
        'Jefferson · Rota com Família<br/>%s' % d['data'], E['capa_pe']))

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

    if d.get('entendimento_callout'):
        titulo, texto, tipo = d['entendimento_callout']
        st.append(Spacer(1, 0.4 * cm))
        st.append(Callout(titulo, texto, kind=tipo))

    # ------------------------------------- 3. paginas de assunto proprio
    for pg in d.get('paginas_extra', []):
        st.extend(pagina_extra(pg, S))

    # ----------------------------------------------- 4. o que e como fazemos
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
        d['promessa'], kind='warn'))

    # ------------------------------------------------------ 5. valores
    st.append(PageBreak())
    st.append(Paragraph('VALORES', S['eyebrow']))
    st.append(Paragraph(d.get('valores_titulo',
                              'Quanto custa e o que vem junto.'), S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm))

    if planos:
        vao = 0.5 * cm
        largura = (16.7 * cm - vao * (len(planos) - 1)) / len(planos)
        par = Table([[caixa_preco(pl, E, largura, compacta=True)
                      for pl in planos]],
                    colWidths=[largura + vao] * (len(planos) - 1) + [largura])
        par.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-2, -1), vao),
            ('RIGHTPADDING', (-1, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        st.append(par)
        st.append(Spacer(1, 0.4 * cm))
        st.append(Paragraph('O que cada um cobre', S['h2']))
        st.append(Spacer(1, 0.1 * cm))
        st.append(tabela_planos(planos, d['comparativo']))
    else:
        hon = d['honorarios']
        st.append(caixa_preco(hon, E, 16.7 * cm))
        st.append(Spacer(1, 0.45 * cm))
        st.append(Paragraph('Está incluído', S['h2']))
        st.extend(bullet_list(d['incluido']))

    if d.get('extras_resumo'):
        st.append(Spacer(1, 0.2 * cm))
        st.append(Paragraph('Junto com o plano, você recebe', S['h2']))
        # Era uma lista com marcador. Virou paragrafo unico porque a pagina de
        # valores precisa caber inteira: o fluxo de pagamento importa mais que
        # o detalhamento dos extras, e este texto diz o mesmo em menos espaco.
        st.append(Paragraph(d['extras_resumo'], S['body']))

    st.append(Spacer(1, 0.3 * cm))
    st.append(Paragraph('Como funciona na prática', S['h2']))
    st.extend(bullet_list(d['fluxo']))

    st.append(Spacer(1, 0.25 * cm))
    st.append(Callout('Como seguimos daqui', d['proximo_passo'], kind='tip'))

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
