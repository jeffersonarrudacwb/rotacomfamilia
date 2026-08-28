# -*- coding: utf-8 -*-
"""Andamento da busca: as opcoes encontradas, em quadros.

    python propostas/build_andamento.py boni-ida

E o documento do meio do trabalho. Vem depois da apresentacao comercial
(build_apresentacao.py) e antes do plano final (build_proposta.py): serve para
o cliente ver o que ja apareceu e dizer por onde seguir.

Reaproveita a capa, o rodape e a silhueta de Nova York da apresentacao, para os
tres documentos do mesmo cliente chegarem com a mesma cara.
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
    Paragraph, Spacer, PageBreak, Table, TableStyle, NextPageTemplate,
    KeepTogether,
)
from reportlab.lib.units import cm  # noqa: E402
from reportlab.lib.colors import HexColor  # noqa: E402

from framework import (  # noqa: E402
    C, PAGE, MARGIN, SANS, SANS_BOLD, SERIF, styles, Divider, Callout,
)
from build_apresentacao import Apresentacao, estilos_extra  # noqa: E402

PDF_DIR = os.path.join(AQUI, 'pdf')
os.makedirs(PDF_DIR, exist_ok=True)

LARGURA_UTIL = PAGE[0] - 2 * MARGIN


def quadro_de_voos(bloco, S):
    """A tabela de opcoes.

    As larguras vem dos dados, em centimetros, porque cada quadro tem um
    numero diferente de colunas: o primeiro nao precisa da coluna de companhia,
    ja que todas as linhas sao Avianca, e isso deixa mais espaco para o resto.
    """
    n = len(bloco['colunas'])
    cab = ParagraphList(bloco['colunas'], SANS_BOLD, C['cream'], n)
    corpo = [ParagraphList(l, SANS, C['text'], n) for l in bloco['linhas']]

    larguras = [x * cm for x in bloco['larguras']]
    # a soma das larguras nao pode passar da area util, senao a tabela sangra
    sobra = LARGURA_UTIL - sum(larguras)
    if sobra:
        larguras[-1] += sobra

    t = Table([cab] + corpo, colWidths=larguras, repeatRows=1)
    estilo = [
        ('BACKGROUND', (0, 0), (-1, 0), C['deep']),
        ('GRID', (0, 0), (-1, -1), 0.4, C['border']),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0.22 * cm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0.22 * cm),
        ('TOPPADDING', (0, 0), (-1, -1), 0.16 * cm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.16 * cm),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C['cream'], C['sand']]),
    ]
    for i in bloco.get('destaque', []):
        estilo.append(('BACKGROUND', (0, i + 1), (-1, i + 1), HexColor('#F7E1B8')))
    t.setStyle(TableStyle(estilo))
    return t


def ParagraphList(celulas, fonte, cor, total):
    """Cada celula vira Paragraph para poder quebrar linha dentro da coluna.

    O alinhamento fica no estilo do Paragraph, nao no ALIGN da tabela: quando a
    celula e um Paragraph, o ALIGN da TableStyle nao tem efeito nenhum, e a
    coluna de milhas continuava a esquerda por isso.

    Milhas a direita para os numeros alinharem pela unidade, que e o que
    permite comparar de relance. A coluna do numero da opcao fica centrada.
    """
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER
    saida = []
    for i, c in enumerate(celulas):
        if i == total - 1:
            alin = TA_RIGHT
        elif i == 0:
            alin = TA_CENTER
        else:
            alin = 0  # TA_LEFT
        st = ParagraphStyle('c%d' % i, fontName=fonte, fontSize=8.6,
                            leading=11.4, textColor=cor, alignment=alin)
        saida.append(Paragraph(str(c), st))
    return saida


def linha_escolha(rotulo, texto, S):
    """Bloco do resumo: rotulo dourado a esquerda, explicacao a direita."""
    from reportlab.lib.styles import ParagraphStyle
    rot = ParagraphStyle('rot', fontName=SANS_BOLD, fontSize=9, leading=13,
                         textColor=C['gold_d'])
    t = Table([[Paragraph(rotulo, rot), Paragraph(texto, S['body'])]],
              colWidths=[4.6 * cm, LARGURA_UTIL - 4.6 * cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 0.4 * cm),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.3 * cm),
    ]))
    return t


def montar(d):
    S = styles()
    E = estilos_extra()
    st = []

    # ---------------------------------------------------------------- capa
    st.append(Paragraph(d['capa_linha1'].upper(), E['capa_selo']))
    st.append(Paragraph(d['capa_titulo'], E['capa_titulo']))
    st.append(Spacer(1, 0.6 * cm))
    st.append(Paragraph('<b>Para %s</b>' % d['cliente']['nome'], E['capa_sub']))
    st.append(Paragraph(d['capa_linha2'], E['capa_sub']))
    st.append(Spacer(1, 0.8 * cm))
    st.append(Paragraph('%s<br/>%s' % (d['assinatura'], d['data']), E['capa_pe']))

    # ------------------------------------------------------------- abertura
    st.append(NextPageTemplate('Corpo'))
    st.append(PageBreak())
    st.append(Paragraph('ONDE ESTAMOS', S['eyebrow']))
    st.append(Paragraph('O que a busca encontrou.', S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm))
    for p in d['abertura']:
        st.append(Paragraph(p, S['body']))
    st.append(Spacer(1, 0.25 * cm))
    st.append(Callout(d['alerta_titulo'], d['alerta_texto'], kind='warn'))

    # --------------------------------------------------------- os tres blocos
    # Cada bloco decide se abre pagina. Os grupos 2 e 3 tem poucas linhas e
    # cabem juntos: um PageBreak fixo entre todos deixava duas paginas com uma
    # tabela de quatro linhas e o resto vazio.
    for i, bloco in enumerate(d['blocos']):
        if bloco.get('nova_pagina'):
            st.append(PageBreak())
        else:
            st.append(Spacer(1, 0.5 * cm))

        cabeca = [Paragraph(bloco['eyebrow'], S['eyebrow']),
                  Paragraph(bloco['titulo'], S['h2'])]
        for p in bloco['texto']:
            cabeca.append(Paragraph(p, S['body']))
        cabeca.append(Spacer(1, 0.25 * cm))
        # titulo e tabela andam juntos: cabecalho no pe de uma pagina com a
        # tabela na seguinte e o tipo de quebra que confunde quem le
        st.append(KeepTogether(cabeca + [quadro_de_voos(bloco, S)]))

        if bloco.get('nota'):
            st.append(Spacer(1, 0.2 * cm))
            st.append(Paragraph('<i>%s</i>' % bloco['nota'], S['small']))

    # ------------------------------------------------------------- a escolha
    st.append(PageBreak())
    st.append(Paragraph('A DECISÃO', S['eyebrow']))
    st.append(Paragraph(d['escolha_titulo'], S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.35 * cm))
    for rotulo, texto in d['escolha']:
        st.append(linha_escolha(rotulo, texto, S))

    st.append(Spacer(1, 0.35 * cm))
    st.append(Paragraph(d['taxas_titulo'], S['h2']))
    st.append(Paragraph(d['taxas_texto'], S['body']))

    st.append(Spacer(1, 0.3 * cm))
    st.append(Callout(d['proximo_titulo'], d['proximo_texto'], kind='tip'))
    return st


def main():
    nome = sys.argv[1] if len(sys.argv) > 1 else 'boni-ida'
    caminho = os.path.join(AQUI, 'dados', '%s-andamento.json' % nome)
    if not os.path.exists(caminho):
        print('Nao achei %s' % caminho)
        return 1

    d = json.load(io.open(caminho, encoding='utf-8'))
    saida = os.path.join(PDF_DIR, '%s.pdf' % d['arquivo'])
    doc = Apresentacao(saida, d['titulo_doc'])
    doc.build(montar(d))
    print('OK: %s' % saida)

    faltando = campos_em_aberto(d)
    if faltando:
        print('ATENCAO: %d campo(s) ainda em aberto:' % len(faltando))
        for t in faltando[:6]:
            print('  %s' % t[:70])
    return 0


def campos_em_aberto(no, chave=''):
    """Procura marcadores [[...]] apenas dentro de texto.

    A primeira versao serializava o dicionario inteiro e procurava '[[' na
    string. Acusava sempre, porque a tabela de voos e uma lista de listas e o
    proprio JSON escreve '[[' ao abri-la. Agora percorre a estrutura e olha so
    o que e texto de verdade. Chaves com _ na frente ficam de fora: sao notas
    para nos, nao vao para o PDF.
    """
    achados = []
    if isinstance(no, dict):
        for k, v in no.items():
            if not str(k).startswith('_'):
                achados += campos_em_aberto(v, k)
    elif isinstance(no, list):
        for v in no:
            achados += campos_em_aberto(v, chave)
    elif isinstance(no, str) and '[[' in no:
        achados.append('%s: %s' % (chave, no))
    return achados


if __name__ == '__main__':
    sys.exit(main())
