# -*- coding: utf-8 -*-
"""Desenho do mapa e dos icones do banner de roteiro.

Separado do build para poder ser ajustado sem mexer na montagem da pagina.

A projecao e equirretangular simples (x = longitude, y = latitude). Para uma
janela estreita como esta, das Guianas ao sul do Brasil, a distorcao e pequena
e o desenho fica honesto: as cidades ficam na posicao real uma em relacao a
outra, e nao espalhadas a esmo.
"""
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor

# Coordenadas reais dos aeroportos usados no roteiro
CIDADES = {
    'FLN': (-27.67, -48.55, 'Florianópolis'),
    'PTY': (9.07, -79.38, 'Cidade do Panamá'),
    'MIA': (25.79, -80.29, 'Miami'),
    'JFK': (40.64, -73.78, 'Nova York'),
    'YYZ': (43.68, -79.63, 'Toronto'),
}

# Janela do mapa, em graus. Sobra proposital nas bordas para os rotulos.
LON_MIN, LON_MAX = -95.0, -38.0
LAT_MIN, LAT_MAX = -34.0, 52.0


def projetar(lat, lon, x0, y0, larg, alt):
    """Grau para ponto na pagina."""
    fx = (lon - LON_MIN) / (LON_MAX - LON_MIN)
    fy = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN)
    return x0 + fx * larg, y0 + fy * alt


# Contorno bem simplificado das Americas dentro da janela. Nao e carta
# nautica: serve para dar a forma do continente atras da rota, em opacidade
# baixa. Pontos em (lat, lon).
AMERICA_SUL = [
    (12.4, -71.7), (10.6, -66.9), (10.7, -61.9), (8.6, -60.0), (5.0, -52.6),
    (1.5, -48.5), (-2.5, -44.3), (-5.1, -36.5), (-8.1, -34.9), (-13.0, -38.5),
    (-18.0, -39.7), (-22.9, -42.0), (-25.5, -48.3), (-30.0, -50.2),
    (-33.0, -53.4), (-34.9, -56.2), (-38.0, -57.5), (-40.8, -62.3),
    (-42.8, -64.9), (-45.9, -67.5), (-50.0, -68.9), (-52.4, -68.5),
    (-54.9, -67.0), (-53.5, -70.9), (-50.0, -75.0), (-46.0, -75.5),
    (-41.5, -74.0), (-37.0, -73.7), (-33.0, -71.6), (-27.0, -70.9),
    (-23.0, -70.4), (-18.3, -70.3), (-14.0, -76.2), (-12.0, -77.0),
    (-8.0, -79.0), (-4.0, -81.1), (-1.0, -80.9), (1.0, -79.0), (5.0, -77.4),
    (7.9, -77.4), (8.5, -79.5), (9.5, -79.9), (9.0, -82.0), (11.0, -83.9),
    (12.4, -71.7),
]

AMERICA_NORTE = [
    (25.2, -80.4), (26.7, -80.0), (28.9, -80.8), (30.7, -81.5), (32.8, -79.9),
    (35.2, -75.5), (37.0, -76.0), (38.8, -75.0), (40.6, -73.8), (41.5, -71.0),
    (42.6, -70.6), (44.8, -67.0), (45.2, -66.0), (46.8, -60.0), (47.6, -52.7),
    (49.5, -55.0), (51.5, -55.6), (52.0, -60.0), (51.5, -66.0), (50.0, -66.5),
    (48.5, -68.5), (46.8, -71.2), (44.0, -76.5), (43.2, -79.2), (42.3, -83.0),
    (45.0, -83.0), (46.5, -84.5), (48.0, -88.0), (52.0, -95.0), (30.0, -95.0),
    (29.7, -93.9), (29.2, -90.1), (30.4, -88.0), (29.7, -84.9), (28.0, -82.7),
    (26.0, -81.8), (25.2, -80.4),
]

# Antilhas, em poligonos proprios: juntas ao continente elas puxavam o
# contorno para o meio do Caribe e fechavam uma mancha unica.
ANTILHAS = [
    [(23.1, -81.5), (22.4, -78.0), (20.2, -74.2), (19.9, -75.9), (21.9, -84.9),
     (23.1, -81.5)],
    [(19.9, -71.7), (18.4, -68.3), (18.0, -71.7), (19.9, -71.7)],
    [(18.5, -66.9), (18.0, -65.6), (17.9, -67.2), (18.5, -66.9)],
]


def desenhar_mapa(c, x0, y0, larg, alt, cor_terra, cor_grade, opac_terra=0.16):
    """Fundo do mapa: grade de coordenadas e silhueta do continente."""
    c.saveState()
    c.setLineWidth(0.4)
    c.setStrokeColor(cor_grade)
    c.setFillColor(cor_grade)
    c.setFont('Helvetica', 5.4)

    # paralelos de 20 em 20 graus, com o rotulo na margem
    # o zero fica de fora: a linha do Equador ja e desenhada em destaque logo
    # abaixo, com nome, e os dois rotulos no mesmo lugar se sobrepunham
    for lat in (-20, 20, 40):
        _, y = projetar(lat, LON_MIN, x0, y0, larg, alt)
        if y0 < y < y0 + alt:
            c.setDash(1, 3)
            c.line(x0, y, x0 + larg, y)
            c.setDash()
            c.drawString(x0 + 2, y + 2, '%d°' % lat)

    # meridianos de 15 em 15
    lon = -90
    while lon <= LON_MAX:
        x, _ = projetar(LAT_MIN, lon, x0, y0, larg, alt)
        if x0 < x < x0 + larg:
            c.setDash(1, 3)
            c.line(x, y0, x, y0 + alt)
            c.setDash()
        lon += 15

    # a linha do Equador ganha peso: e a referencia que da escala ao desenho
    _, ye = projetar(0, LON_MIN, x0, y0, larg, alt)
    c.setDash(3, 2)
    c.setLineWidth(0.7)
    c.line(x0, ye, x0 + larg, ye)
    c.setDash()
    c.drawString(x0 + 2, ye + 3, 'EQUADOR')

    # continentes
    c.setFillColor(cor_terra)
    c.setFillAlpha(opac_terra)
    c.setStrokeAlpha(0)
    for pontos in [AMERICA_SUL, AMERICA_NORTE] + ANTILHAS:
        p = c.beginPath()
        for i, (la, lo) in enumerate(pontos):
            x, y = projetar(la, lo, x0, y0, larg, alt)
            (p.moveTo if i == 0 else p.lineTo)(x, y)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
    c.setFillAlpha(1)
    c.setStrokeAlpha(1)
    c.restoreState()


# ---------------------------------------------------------------------------
# Icones
# Desenhados a mao com primitivas, em vez de imagem: ficam nitidos em qualquer
# zoom, pesam nada e acompanham a cor do documento.
# ---------------------------------------------------------------------------
def icone_ponte(c, x, y, s, cor):
    """Florianopolis: a ponte Hercilio Luz, cartao postal da cidade."""
    c.saveState()
    c.setStrokeColor(cor)
    c.setLineWidth(s * 0.09)
    c.line(x - s, y - s * 0.35, x + s, y - s * 0.35)          # tabuleiro
    p = c.beginPath()                                          # arco principal
    p.moveTo(x - s, y - s * 0.35)
    p.curveTo(x - s * 0.4, y + s * 0.75, x + s * 0.4, y + s * 0.75,
              x + s, y - s * 0.35)
    c.drawPath(p, fill=0, stroke=1)
    c.setLineWidth(s * 0.05)
    for f in (-0.5, 0, 0.5):                                   # pendurais
        c.line(x + s * f, y - s * 0.35, x + s * f, y + s * (0.45 - abs(f) * 0.5))
    c.restoreState()


def icone_navio(c, x, y, s, cor):
    """Panama: um cargueiro, pelo Canal."""
    c.saveState()
    c.setStrokeColor(cor)
    c.setFillColor(cor)
    c.setLineWidth(s * 0.08)
    p = c.beginPath()                                          # casco
    p.moveTo(x - s, y - s * 0.15)
    p.lineTo(x + s, y - s * 0.15)
    p.lineTo(x + s * 0.7, y - s * 0.6)
    p.lineTo(x - s * 0.75, y - s * 0.6)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.rect(x - s * 0.15, y - s * 0.15, s * 0.55, s * 0.5, fill=1, stroke=0)
    c.rect(x - s * 0.75, y - s * 0.15, s * 0.45, s * 0.28, fill=1, stroke=0)
    c.setLineWidth(s * 0.07)                                   # agua
    c.line(x - s, y - s * 0.85, x + s, y - s * 0.85)
    c.restoreState()


def icone_palmeira(c, x, y, s, cor):
    """Miami: palmeira."""
    c.saveState()
    c.setStrokeColor(cor)
    c.setLineWidth(s * 0.11)
    p = c.beginPath()                                          # tronco
    p.moveTo(x, y - s * 0.8)
    p.curveTo(x + s * 0.08, y - s * 0.2, x - s * 0.1, y + s * 0.1, x, y + s * 0.4)
    c.drawPath(p, fill=0, stroke=1)
    c.setLineWidth(s * 0.09)
    for dx, dy in ((-1, 0.25), (-0.6, 0.7), (0.6, 0.7), (1, 0.25)):
        f = c.beginPath()
        f.moveTo(x, y + s * 0.4)
        f.curveTo(x + s * dx * 0.5, y + s * (0.4 + dy * 0.55),
                  x + s * dx * 0.9, y + s * (0.4 + dy * 0.35),
                  x + s * dx, y + s * (0.4 + dy * 0.05))
        c.drawPath(f, fill=0, stroke=1)
    c.restoreState()


def icone_liberdade(c, x, y, s, cor):
    """Nova York: a tocha da Estatua da Liberdade."""
    c.saveState()
    c.setFillColor(cor)
    c.setStrokeColor(cor)
    c.setLineWidth(s * 0.09)
    c.line(x, y - s * 0.9, x, y + s * 0.15)                    # braco
    p = c.beginPath()                                          # chama
    p.moveTo(x - s * 0.22, y + s * 0.2)
    p.curveTo(x - s * 0.3, y + s * 0.75, x + s * 0.3, y + s * 0.75,
              x + s * 0.22, y + s * 0.2)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.rect(x - s * 0.3, y + s * 0.05, s * 0.6, s * 0.14, fill=1, stroke=0)
    c.setLineWidth(s * 0.07)                                   # base
    c.line(x - s * 0.45, y - s * 0.9, x + s * 0.45, y - s * 0.9)
    c.restoreState()


def icone_cntower(c, x, y, s, cor):
    """Toronto: a CN Tower."""
    c.saveState()
    c.setFillColor(cor)
    c.setStrokeColor(cor)
    c.setLineWidth(s * 0.1)
    c.line(x, y - s * 0.9, x, y + s * 0.9)                     # haste
    p = c.beginPath()                                          # disco
    p.moveTo(x - s * 0.42, y + s * 0.18)
    p.lineTo(x + s * 0.42, y + s * 0.18)
    p.lineTo(x + s * 0.2, y + s * 0.42)
    p.lineTo(x - s * 0.2, y + s * 0.42)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.setLineWidth(s * 0.16)                                   # base
    c.line(x - s * 0.2, y - s * 0.9, x + s * 0.2, y - s * 0.9)
    c.restoreState()


ICONES = {'FLN': icone_ponte, 'PTY': icone_navio, 'MIA': icone_palmeira,
          'JFK': icone_liberdade, 'YYZ': icone_cntower}


def aviao(c, x, y, ang, s, cor):
    """Aviaozinho apontando na direcao do voo."""
    import math
    c.saveState()
    c.translate(x, y)
    c.rotate(math.degrees(ang))
    c.setFillColor(cor)
    p = c.beginPath()
    p.moveTo(s, 0)                       # nariz
    p.lineTo(-s * 0.25, s * 0.28)        # asa de cima
    p.lineTo(-s * 0.1, 0.0)
    p.lineTo(-s * 0.25, -s * 0.28)       # asa de baixo
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    p2 = c.beginPath()                   # cauda
    p2.moveTo(-s * 0.1, 0)
    p2.lineTo(-s * 0.55, s * 0.2)
    p2.lineTo(-s * 0.45, 0)
    p2.lineTo(-s * 0.55, -s * 0.2)
    p2.close()
    c.drawPath(p2, fill=1, stroke=0)
    c.restoreState()
