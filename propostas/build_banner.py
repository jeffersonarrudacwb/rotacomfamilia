# -*- coding: utf-8 -*-
"""Banner de uma pagina: a viagem inteira desenhada no mapa.

    python propostas/build_banner.py boni

Le o mesmo JSON do roteiro, entao os numeros nunca divergem entre os dois
documentos: se a tabela de custos mudar la, o banner muda junto.

Nao usa Platypus. E uma pagina so, com tudo posicionado a mao no canvas, que e
o que permite texto por cima de mapa sem briga de fluxo.
"""
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
sys.path.insert(0, AQUI)

from reportlab.pdfgen import canvas as canvas_mod  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402

import mapa  # noqa: E402
from framework import C, SANS, SANS_BOLD, SERIF  # noqa: E402

PDF_DIR = os.path.join(AQUI, 'pdf')
os.makedirs(PDF_DIR, exist_ok=True)
W, H = A4

# A ordem em que a viagem acontece. O Panama aparece duas vezes, na ida e na
# volta, entao a rota nao e uma lista de cidades: e uma lista de pernas.
PERNAS = [
    ('FLN', 'PTY', 'ida'), ('PTY', 'MIA', 'ida'), ('MIA', 'JFK', 'ida'),
    ('JFK', 'YYZ', 'volta'), ('YYZ', 'PTY', 'volta'), ('PTY', 'FLN', 'volta'),
]


def arco(c, p1, p2, curvatura, cor, largura, tracejado=False):
    """Liga dois pontos por um arco, e devolve o meio e o angulo ali.

    Reta ligando cidade a cidade fica dura e, pior, duas pernas no mesmo par de
    cidades ficariam uma em cima da outra. A curvatura separa a ida da volta.
    """
    x1, y1 = p1
    x2, y2 = p2
    mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy) or 1.0
    # ponto de controle deslocado na perpendicular
    cx = mx - dy / dist * curvatura
    cy = my + dx / dist * curvatura

    c.saveState()
    c.setStrokeColor(cor)
    c.setLineWidth(largura)
    c.setLineCap(1)
    if tracejado:
        c.setDash(4, 3)
    p = c.beginPath()
    p.moveTo(x1, y1)
    p.curveTo(x1 + (cx - x1) * 2 / 3.0, y1 + (cy - y1) * 2 / 3.0,
              x2 + (cx - x2) * 2 / 3.0, y2 + (cy - y2) * 2 / 3.0, x2, y2)
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()

    # ponto e tangente no meio da curva quadratica (t = 0.5)
    bx = 0.25 * x1 + 0.5 * cx + 0.25 * x2
    by = 0.25 * y1 + 0.5 * cy + 0.25 * y2
    tx = (cx - x1) + (x2 - cx)
    ty = (cy - y1) + (y2 - cy)
    return (bx, by), math.atan2(ty, tx)


def montar(d, saida):
    c = canvas_mod.Canvas(saida, pagesize=A4)
    c.setTitle('Roteiro em mapa · %s' % d['cliente']['nome'])
    c.setAuthor('Rota com Família')

    # ---------------------------------------------------------------- fundo
    c.setFillColor(C['deep'])
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(C['gold'])
    c.rect(0, H - 0.3 * cm, W, 0.3 * cm, fill=1, stroke=0)

    # ------------------------------------------------------------ cabecalho
    c.setFillColor(C['gold'])
    c.setFont(SANS_BOLD, 8.5)
    c.drawString(2 * cm, H - 1.5 * cm, 'ROTA COM FAMÍLIA')
    c.setFillColor(C['cream'])
    c.setFont(SERIF, 27)
    c.drawString(2 * cm, H - 2.75 * cm, d['banner_titulo'])
    c.setFillColor(C['sand'])
    c.setFont(SANS, 10)
    c.drawString(2 * cm, H - 3.42 * cm, d['banner_sub'])

    # ----------------------------------------------------------------- mapa
    mx0, my0 = 1.2 * cm, 6.6 * cm
    mlarg, malt = W - 2.4 * cm, H - 11.2 * cm
    mapa.desenhar_mapa(c, mx0, my0, mlarg, malt,
                       cor_terra=C['fern'], cor_grade=C['gold_d'],
                       opac_terra=0.20)

    pos = {}
    for cod, (lat, lon, _nome) in mapa.CIDADES.items():
        pos[cod] = mapa.projetar(lat, lon, mx0, my0, mlarg, malt)

    # ----------------------------------------------------------------- rota
    for de, para, sentido in PERNAS:
        ida = sentido == 'ida'
        curva = 26 if ida else -30
        cor = C['gold'] if ida else C['sunset']
        meio, ang = arco(c, pos[de], pos[para], curva, cor, 1.5,
                         tracejado=not ida)
        if not ida:                       # aviao aponta para o sentido do voo
            ang += math.pi
        mapa.aviao(c, meio[0], meio[1], ang, 9, cor)

    # -------------------------------------------------------------- cidades
    # Rotulo de cada cidade, com o lado escolhido a mao para nao cobrir a rota.
    LADO = {'FLN': ('d', 0), 'PTY': ('e', 0), 'MIA': ('d', 0),
            'JFK': ('d', 0), 'YYZ': ('e', 0)}
    # Deslocamento do icone em relacao a cidade. Miami e Panama saem para o
    # lado porque a rota passa exatamente por cima deles.
    ICONE_POS = {'FLN': (0, 34), 'PTY': (46, 6), 'MIA': (44, 4),
                 'JFK': (0, 34), 'YYZ': (0, 34)}
    for cod, (x, y) in pos.items():
        c.setFillColor(C['gold'])
        c.circle(x, y, 3.2, fill=1, stroke=0)
        c.setFillColor(C['deep'])
        c.circle(x, y, 1.4, fill=1, stroke=0)

        ix, iy = ICONE_POS[cod]
        mapa.ICONES[cod](c, x + ix, y + iy, 12, C['cream'])

        lado, dy = LADO[cod]
        nome = mapa.CIDADES[cod][2]
        c.setFillColor(C['cream'])
        c.setFont(SANS_BOLD, 8.6)
        if lado == 'd':
            c.drawString(x + 8, y - 3 + dy, nome)
        else:
            c.drawRightString(x - 8, y - 3 + dy, nome)

    # legenda da rota
    lx, ly = mx0 + 8, my0 + 10
    c.setStrokeColor(C['gold'])
    c.setLineWidth(1.5)
    c.line(lx, ly + 10, lx + 18, ly + 10)
    c.setStrokeColor(C['sunset'])
    c.setDash(4, 3)
    c.line(lx, ly, lx + 18, ly)
    c.setDash()
    c.setFillColor(C['sand'])
    c.setFont(SANS, 7.4)
    c.drawString(lx + 23, ly + 7.5, 'ida · 23 a 25 de novembro')
    c.drawString(lx + 23, ly - 2.5, 'volta · 3 a 8 de dezembro')

    # ------------------------------------------------------------- numeros
    caixas = d['banner_numeros']
    larg = (W - 4 * cm) / len(caixas)
    base = 3.5 * cm
    # tarja solida atras: sem ela os numeros caem sobre a America do Sul e
    # nem o mapa nem o numero se leem direito
    c.setFillColor(C['deep'])
    c.rect(0, base - 0.75 * cm, W, 2.1 * cm, fill=1, stroke=0)
    for i, (valor, rot) in enumerate(caixas):
        cx = 2 * cm + larg * i + larg / 2.0
        c.setFillColor(C['gold'])
        c.setFont(SERIF, 19)
        c.drawCentredString(cx, base + 0.62 * cm, valor)
        c.setFillColor(C['sand'])
        c.setFont(SANS, 7.2)
        for j, linha in enumerate(rot.split('|')):
            c.drawCentredString(cx, base + 0.16 * cm - j * 0.33 * cm, linha)
        if i:
            c.setStrokeColor(C['gold_d'])
            c.setLineWidth(0.4)
            c.setStrokeAlpha(0.5)
            c.line(2 * cm + larg * i, base - 0.25 * cm,
                   2 * cm + larg * i, base + 1.05 * cm)
            c.setStrokeAlpha(1)

    # ------------------------------------------------------------- rodape
    c.setFillColor(C['gold_d'])
    c.setLineWidth(0.5)
    c.setStrokeColor(C['gold_d'])
    c.line(2 * cm, 2.75 * cm, W - 2 * cm, 2.75 * cm)
    c.setFillColor(C['cream'])
    c.setFont(SANS, 8.4)
    # a frase saia pela borda direita, entao e quebrada na largura util. A
    # assinatura desce conforme o numero de linhas, senao a segunda linha da
    # frase cai em cima dela.
    from reportlab.lib.utils import simpleSplit
    linhas = simpleSplit(d['banner_frase'], SANS, 8.4, W - 4 * cm)[:2]
    for i, ln in enumerate(linhas):
        c.drawString(2 * cm, 2.28 * cm - i * 0.38 * cm, ln)
    y_ass = 2.28 * cm - len(linhas) * 0.38 * cm - 0.18 * cm
    c.setFillColor(C['fern'])
    c.setFont(SANS, 7.6)
    c.drawString(2 * cm, y_ass, 'Preparado para %s · %s'
                 % (d['cliente']['nome'], d['data']))
    c.setFillColor(C['gold'])
    c.drawRightString(W - 2 * cm, y_ass, 'rotacomfamilia.com.br')

    c.showPage()
    c.save()


def main():
    nome = sys.argv[1] if len(sys.argv) > 1 else 'boni'
    caminho = os.path.join(AQUI, 'dados', '%s-roteiro.json' % nome)
    if not os.path.exists(caminho):
        print('Nao achei %s' % caminho)
        return 1
    d = json.load(io.open(caminho, encoding='utf-8'))
    saida = os.path.join(PDF_DIR, 'banner-%s.pdf' % d['arquivo'])
    montar(d, saida)
    print('OK: %s' % saida)
    return 0


if __name__ == '__main__':
    sys.exit(main())
