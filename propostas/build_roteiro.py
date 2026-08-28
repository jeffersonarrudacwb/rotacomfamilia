# -*- coding: utf-8 -*-
"""Roteiro fechado, em uma pagina: capa mais o detalhamento.

    python propostas/build_roteiro.py boni

E o documento que o cliente leva para embarcar. Diferente do andamento, que
mostra opcoes para escolher, aqui ja esta decidido: numero de voo, horario,
bagagem e a conta fechada.

Capa, rodape e silhueta vem da apresentacao comercial, e a tabela vem do
andamento, para os documentos do mesmo cliente terem a mesma cara.
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

from framework import (  # noqa: E402
    C, PAGE, MARGIN, SANS_BOLD, styles, Divider, Callout,
)
from build_apresentacao import Apresentacao, estilos_extra  # noqa: E402
from build_andamento import quadro_de_voos, LARGURA_UTIL  # noqa: E402

PDF_DIR = os.path.join(AQUI, 'pdf')
os.makedirs(PDF_DIR, exist_ok=True)


def momento(rotulo, texto, S):
    """Uma etapa da viagem: data e cidade a esquerda, o que acontece a direita."""
    from reportlab.lib.styles import ParagraphStyle
    rot = ParagraphStyle('m', fontName=SANS_BOLD, fontSize=9, leading=12.5,
                         textColor=C['gold_d'])
    t = Table([[Paragraph(rotulo, rot), Paragraph(texto, S['body'])]],
              colWidths=[3.5 * cm, LARGURA_UTIL - 3.5 * cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 0.4 * cm),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.16 * cm),
    ]))
    return t


def montar(d):
    S = styles()
    E = estilos_extra()
    st = []

    # ------------------------------------------------------------------ capa
    st.append(Paragraph(d['capa_linha1'].upper(), E['capa_selo']))
    st.append(Paragraph(d['capa_titulo'], E['capa_titulo']))
    st.append(Spacer(1, 0.6 * cm))
    st.append(Paragraph('<b>Para %s</b>' % d['cliente']['nome'], E['capa_sub']))
    st.append(Paragraph(d['capa_linha2'], E['capa_sub']))
    st.append(Paragraph(d['capa_linha3'], E['capa_sub']))
    st.append(Spacer(1, 0.8 * cm))
    st.append(Paragraph('%s<br/>%s' % (d['assinatura'], d['data']), E['capa_pe']))

    # --------------------------------------------------------- pagina unica
    st.append(NextPageTemplate('Corpo'))
    st.append(PageBreak())
    st.append(Paragraph(d['intro_eyebrow'], S['eyebrow']))
    st.append(Paragraph(d['intro_titulo'], S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.22 * cm))
    for p in d['intro']:
        st.append(Paragraph(p, S['body']))

    st.append(Spacer(1, 0.18 * cm))
    for rotulo, texto in d['momentos']:
        st.append(momento(rotulo, texto, S))

    st.append(Spacer(1, 0.2 * cm))
    st.append(KeepTogether([
        Paragraph(d['voos_titulo'], S['h2']),
        Spacer(1, 0.18 * cm),
        quadro_de_voos({'colunas': d['voos_colunas'],
                        'larguras': d['voos_larguras'],
                        'linhas': d['voos_linhas'],
                        'destaque': d.get('voos_destaque', []),
                        'alinhamento': d.get('voos_alinhamento')}, S),
    ]))
    # A volta so existe quando o roteiro e de ciclo completo. Enquanto o
    # documento tinha so a ida, esta chave nem estava nos dados.
    if d.get('volta_linhas'):
        st.append(Spacer(1, 0.28 * cm))
        st.append(KeepTogether([
            Paragraph(d['volta_titulo'], S['h2']),
            Spacer(1, 0.18 * cm),
            quadro_de_voos({'colunas': d['volta_colunas'],
                            'larguras': d['volta_larguras'],
                            'linhas': d['volta_linhas'],
                            'destaque': d.get('volta_destaque', []),
                            'alinhamento': d.get('volta_alinhamento')}, S),
        ]))

    # A espera de 22h no Panama so aparece quando se cruza a chegada de um voo
    # com a saida do seguinte, e e o tipo de coisa que estraga viagem se
    # ninguem perceber antes de emitir.
    if d.get('espera_texto'):
        st.append(Spacer(1, 0.18 * cm))
        # tipo vem dos dados: a noite no Panama comecou como alerta e virou
        # parte do roteiro quando o Jefferson explicou que foi proposital
        st.append(Callout(d['espera_titulo'], d['espera_texto'],
                          kind=d.get('espera_tipo', 'warn')))

    st.append(Spacer(1, 0.18 * cm))
    st.append(Callout(d['bagagem_titulo'], d['bagagem_texto'], kind='warn'))

    st.append(Spacer(1, 0.18 * cm))
    st.append(KeepTogether([
        Paragraph(d['custos_titulo'], S['h2']),
        Spacer(1, 0.18 * cm),
        quadro_de_voos({'colunas': d['custos_colunas'],
                        'larguras': d['custos_larguras'],
                        'linhas': d['custos_linhas'],
                        'destaque': d.get('custos_destaque', []),
                        'alinhamento': d.get('custos_alinhamento')}, S),
    ]))
    st.append(Spacer(1, 0.15 * cm))
    st.append(Paragraph('<i>%s</i>' % d['custos_nota'], S['small']))

    # A pergunta que o cliente vai fazer sozinho depois de ver o total: cabe no
    # meu saldo? Melhor responder antes dele perguntar.
    if d.get('saldo_linhas'):
        st.append(Spacer(1, 0.3 * cm))
        st.append(KeepTogether([
            Paragraph(d['saldo_titulo'], S['h2']),
            Paragraph(d['saldo_texto'], S['body']),
            Spacer(1, 0.18 * cm),
            quadro_de_voos({'colunas': d['saldo_colunas'],
                            'larguras': d['saldo_larguras'],
                            'linhas': d['saldo_linhas'],
                            'destaque': d.get('saldo_destaque', []),
                            'alinhamento': d.get('saldo_alinhamento')}, S),
        ]))
        st.append(Spacer(1, 0.15 * cm))
        st.append(Paragraph('<i>%s</i>' % d['saldo_nota'], S['small']))

    if d.get('viaje_texto'):
        st.append(Spacer(1, 0.28 * cm))
        st.append(Callout(d['viaje_titulo'], d['viaje_texto'], kind='tip'))

    # O fecho era um Callout. Virou paragrafo simples porque a caixa custa
    # cerca de um centimetro so de padding, e era exatamente o que faltava
    # para o documento caber na pagina unica que o Jefferson pediu.
    st.append(Spacer(1, 0.3 * cm))
    # ------------------------------------------------- documentacao por pais
    st.append(PageBreak())
    st.append(Paragraph('ANTES DE VIAJAR', S['eyebrow']))
    st.append(Paragraph(d['doc_titulo'], S['h1']))
    st.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm))
    st.append(Paragraph(d['doc_texto'], S['body']))
    st.append(Spacer(1, 0.25 * cm))
    st.append(quadro_de_voos({'colunas': d['doc_colunas'],
                              'larguras': d['doc_larguras'],
                              'alinhamento': d['doc_alinhamento'],
                              'linhas': d['doc_linhas']}, S))
    st.append(Spacer(1, 0.2 * cm))
    st.append(Paragraph('<i>%s</i>' % d['doc_nota'], S['small']))

    # ------------------------------------------------------ a historia da busca
    st.append(Spacer(1, 0.55 * cm))
    st.append(Paragraph(d['historia_titulo'], S['h2']))
    for par in d['historia']:
        st.append(Paragraph(par, S['body']))
    st.append(Spacer(1, 0.2 * cm))
    st.append(Callout('Em resumo', d['historia_fecho'], kind='tip'))

    st.append(Spacer(1, 0.35 * cm))
    st.append(Paragraph('<b>%s.</b> %s' % (d['fecho_titulo'], d['fecho_texto']),
                        S['small']))
    return st


def main():
    nome = sys.argv[1] if len(sys.argv) > 1 else 'boni'
    caminho = os.path.join(AQUI, 'dados', '%s-roteiro.json' % nome)
    if not os.path.exists(caminho):
        print('Nao achei %s' % caminho)
        return 1

    d = json.load(io.open(caminho, encoding='utf-8'))
    saida = os.path.join(PDF_DIR, '%s.pdf' % d['arquivo'])
    doc = Apresentacao(saida, d['titulo_doc'])
    doc.build(montar(d))
    print('OK: %s' % saida)
    return 0


if __name__ == '__main__':
    sys.exit(main())
