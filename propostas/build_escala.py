# -*- coding: utf-8 -*-
"""Roteiro de uma cidade, no padrao dos outros documentos do cliente.

    python propostas/build_escala.py boni-panama

E o documento que conta o que fazer numa parada: hora a hora, quanto custa e
onde comer. Diferente da conferencia, que so olha a emissao, e diferente do
roteiro geral, que so olha os voos.

POR QUE ELE E DIRIGIDO POR BLOCOS, E NAO POR SECOES FIXAS

O build_conferencia tem duas tabelas com nome proprio no codigo, voos e
custos, porque aquele documento e sempre igual. Aqui nao: a escala do Panama
precisa de linha do tempo e comparacao de transporte, a noite da volta precisa
de tabela de hotel, e Miami, Nova York e Toronto ainda vao pedir outra coisa.
Secao fixa aqui viraria uma lista de campos opcionais que quase nunca se usam.

Entao o JSON traz uma lista de blocos, cada um com o seu "tipo", e este
arquivo so sabe desenhar cada tipo. Cidade nova e JSON novo, sem tocar aqui.

Cabecalho, rodape, silhueta e tabela vem do build_conferencia, para os
documentos do mesmo cliente chegarem com a mesma cara.
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
    Paragraph, Spacer, PageBreak, KeepTogether, Image, Table, TableStyle,
    NextPageTemplate,
)
from reportlab.lib.units import cm  # noqa: E402

from framework import Divider, Callout, bullet_list  # noqa: E402
from build_conferencia import (  # noqa: E402
    Conferencia, estilos_apertados, quadro, em_aberto, LARGURA_UTIL,
)
from build_apresentacao import estilos_extra  # noqa: E402

FOTOS = os.path.join(AQUI, 'pdf')

PDF_DIR = os.path.join(AQUI, 'pdf')
os.makedirs(PDF_DIR, exist_ok=True)


def bloco_quadro(b, S):
    """Titulo, tabela e nota juntos, para o titulo nao ficar orfao no rodape.

    KeepTogether na tabela inteira so funciona porque nenhuma delas passa de
    meia pagina. Se um dia passar, o ReportLab desiste do agrupamento e quebra
    onde der -- o que ainda e melhor do que a alternativa de titulo sozinho no
    fim de uma folha.
    """
    partes = []
    if b.get('titulo'):
        partes.append(Paragraph(b['titulo'], S['h2']))
    partes.append(Spacer(1, 0.12 * cm))
    partes.append(quadro({
        'colunas': b['colunas'],
        'larguras': b['larguras'],
        'alinhamento': b.get('alinhamento'),
        'linhas': b['linhas'],
        'destaque': b.get('destaque', []),
    }, vaos=b.get('vaos', [])))
    if b.get('nota'):
        partes.append(Spacer(1, 0.15 * cm))
        partes.append(Paragraph('<i>%s</i>' % b['nota'], S['small']))
    return KeepTogether(partes)


def fila_de_fotos(caminhos, legenda=None):
    """As fotos de um hotel numa fila so, todas da mesma altura.

    Sao 3:2 vindas do preparar_fotos.py, entao a altura sai da largura e
    a fila fecha alinhada sem eu precisar medir nada aqui. Se um dia entrar uma
    foto de outra proporcao, ela estica: o lugar de consertar isso e o
    preparador, e nao este arquivo.
    """
    vao = 0.35 * cm
    n = len(caminhos)
    larg = (LARGURA_UTIL - vao * (n - 1)) / n
    # Teto de largura: uma foto sozinha ocuparia os 16,6 cm da folha e sairia
    # com 11 cm de altura, que e tamanho de poster num documento de apoio.
    # Presa na largura de uma fila de duas, ela fica do tamanho das vizinhas.
    larg = min(larg, (LARGURA_UTIL - vao) / 2)
    alt = larg / (3.0 / 2.0)
    linha = [Image(c, width=larg, height=alt) for c in caminhos]
    t = Table([linha], colWidths=[larg + vao] * (n - 1) + [larg])
    t.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-2, -1), vao),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    partes = [t]
    if legenda:
        partes.append(Spacer(1, 0.1 * cm))
        partes.append(Paragraph('<i>%s</i>' % legenda,
                                estilos_apertados()['small']))
    return KeepTogether(partes)


def montar(d):
    S = estilos_apertados()
    E = estilos_extra()
    saida = os.path.join(PDF_DIR, '%s.pdf' % d['arquivo'])
    doc = Conferencia(saida, d['titulo_doc'], d['rodape_direita'],
                      silhueta=d.get('silhueta', 'nova-york'),
                      com_capa=bool(d.get('capa')))
    st = []

    # A capa sai do bloco "capa" no topo do JSON, e nao da lista de blocos: ela
    # e sempre a primeira pagina ou nao existe.
    if d.get('capa'):
        c = d['capa']
        st.append(Paragraph(c['selo'].upper(), E['capa_selo']))
        st.append(Paragraph(c['titulo'], E['capa_titulo']))
        st.append(Spacer(1, 0.6 * cm))
        for linha in c.get('linhas', []):
            st.append(Paragraph(linha, E['capa_sub']))
        st.append(Spacer(1, 0.8 * cm))
        st.append(Paragraph(c['pe'], E['capa_pe']))
        # Sem esta troca a capa escura vale para o documento inteiro, e o
        # texto preto das paginas seguintes some no fundo preto.
        st.append(NextPageTemplate('Corpo'))
        st.append(PageBreak())

    for b in d['blocos']:
        t = b['tipo']

        if t == 'pagina':
            st.append(PageBreak())

        elif t == 'secao':
            st.append(Paragraph(b['eyebrow'], S['eyebrow']))
            st.append(Paragraph(b['titulo'], S['h1']))
            st.append(Divider(width_pct=0.18, gap_before=0.05 * cm,
                              gap_after=0.25 * cm))

        elif t == 'texto':
            for p in b['paragrafos']:
                st.append(Paragraph(p, S['body']))

        elif t == 'h2':
            st.append(Paragraph(b['texto'], S['h2']))

        elif t == 'lista':
            st.extend(bullet_list(b['itens']))

        elif t == 'fotos':
            caminhos = [os.path.join(FOTOS, x.replace('/', os.sep))
                        for x in b['arquivos']]
            faltando = [c for c in caminhos if not os.path.exists(c)]
            if faltando:
                # Erra alto e cedo. Foto que falta e o ReportLab desenhando um
                # retangulo vazio no lugar, o que passa despercebido ate o PDF
                # chegar no cliente com um buraco.
                for c in faltando:
                    print('foto que nao existe: %s' % c)
                raise SystemExit(
                    'Rode antes: python propostas/preparar_fotos.py '
                    '<slug> <cidade>, ou --pasta <caminho>')
            st.append(Spacer(1, 0.15 * cm))
            st.append(fila_de_fotos(caminhos, b.get('legenda')))
            st.append(Spacer(1, 0.2 * cm))

        elif t == 'quadro':
            st.append(Spacer(1, 0.2 * cm))
            st.append(bloco_quadro(b, S))
            st.append(Spacer(1, 0.15 * cm))

        elif t == 'callout':
            st.append(Spacer(1, 0.15 * cm))
            st.append(Callout(b['titulo'], b['texto'],
                              kind=b.get('kind', 'note')))
            st.append(Spacer(1, 0.1 * cm))

        elif t == 'nota':
            st.append(Paragraph('<i>%s</i>' % b['texto'], S['small']))

        elif t == 'assinatura':
            st.append(Spacer(1, 0.3 * cm))
            st.append(Paragraph('<b>%s</b>' % b['texto'], S['small']))

        else:
            raise SystemExit(
                'Bloco de tipo "%s" nao existe. Ha estes: pagina, secao, '
                'texto, h2, lista, quadro, callout, nota, assinatura, '
                'fotos.' % t)

    return doc, st, saida


def main():
    if len(sys.argv) < 2:
        print('uso: python propostas/build_escala.py <nome-do-json>')
        raise SystemExit(1)
    nome = sys.argv[1].replace('.json', '')
    caminho = os.path.join(AQUI, 'dados', nome + '.json')
    if not os.path.exists(caminho):
        print('nao achei %s' % caminho)
        raise SystemExit(1)

    d = json.load(io.open(caminho, encoding='utf-8'))
    doc, st, saida = montar(d)
    doc.build(st)
    print('OK: %s (%d pagina%s)'
          % (saida, doc.page, 's' if doc.page != 1 else ''))

    buracos = em_aberto(d)
    if buracos:
        print('ATENCAO: %d campo(s) ainda com [[...]].' % buracos)
    else:
        print('Nenhum campo em aberto: pode enviar.')


if __name__ == '__main__':
    main()
