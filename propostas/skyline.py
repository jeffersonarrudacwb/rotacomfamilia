# -*- coding: utf-8 -*-
"""Silhuetas de destino para o fundo da apresentacao.

Desenhadas com retangulos e linhas em vez de imagem: ficam nitidas em qualquer
zoom, pesam uns bytes e mudam de cor junto com o tema. Vao em opacidade baixa,
rente ao rodape, para ficar como marca d'agua e nunca competir com o texto.

Ha duas por enquanto:

    desenhar()          Nova York, os predios
    desenhar_florida()  Orlando e a costa: coqueiro, montanha-russa, roda
                        gigante, foguete e navio
    desenhar_madri()    cupula, mansardas, catedral, Puerta de Alcala e as
                        quatro torres
    desenhar_recife()   sobrados, igreja barroca, torre com cupula, jangada e
                        os predios de Boa Viagem

Para o proximo destino, escreva outra funcao com a mesma assinatura (canvas,
largura, base, cor, altura, opacidade) e registre no SILHUETAS la embaixo. O
build_apresentacao escolhe pelo nome que estiver no JSON, entao destino novo
nao exige mexer no gerador.

ARMADILHA, a mesma nas duas funcoes: setFillColor e setStrokeColor redefinem o
alfa do estado grafico. Pedir transparencia antes da cor nao surte efeito e a
silhueta sai solida por cima do texto. Cor primeiro, alfa depois, sempre.
"""
from reportlab.lib.units import cm

# (x, largura, altura, tipo)
# x e largura em fracao da largura util, altura em fracao da altura da faixa.
# tipo: 'reto', 'antena', 'deco' (topo escalonado), 'agulha'
PREDIOS = [
    (0.000, 0.045, 0.42, 'reto'),
    (0.048, 0.032, 0.58, 'reto'),
    (0.083, 0.040, 0.34, 'reto'),
    (0.126, 0.030, 0.72, 'antena'),     # torre com antena
    (0.159, 0.052, 0.46, 'reto'),
    (0.214, 0.036, 0.62, 'reto'),
    (0.253, 0.044, 0.38, 'reto'),
    (0.300, 0.038, 0.88, 'deco'),       # Empire State
    (0.341, 0.048, 0.44, 'reto'),
    (0.392, 0.034, 0.66, 'reto'),
    (0.429, 0.056, 0.36, 'reto'),
    (0.488, 0.030, 0.78, 'agulha'),     # Chrysler
    (0.521, 0.046, 0.48, 'reto'),
    (0.570, 0.038, 0.60, 'reto'),
    (0.611, 0.050, 0.40, 'reto'),
    (0.664, 0.034, 0.70, 'reto'),
    (0.701, 0.042, 0.52, 'reto'),
    (0.746, 0.036, 1.00, 'antena'),     # One World Trade
    (0.785, 0.048, 0.44, 'reto'),
    (0.836, 0.032, 0.64, 'reto'),
    (0.871, 0.044, 0.38, 'reto'),
    (0.918, 0.036, 0.56, 'reto'),
    (0.957, 0.043, 0.42, 'reto'),
]


def desenhar(canvas, largura, base, cor, altura=3.2 * cm, opacidade=0.10,
             margem=0.0):
    """Desenha a silhueta ocupando a largura toda, com a base em `base`."""
    canvas.saveState()
    # A ordem importa: setFillColor redefine o alfa do estado grafico, entao
    # pedir transparencia antes da cor nao surte efeito nenhum e a silhueta sai
    # solida por cima do texto.
    canvas.setFillColor(cor)
    try:
        canvas.setFillAlpha(opacidade)
    except AttributeError:
        pass
    util = largura - 2 * margem

    for fx, fw, fh, tipo in PREDIOS:
        x = margem + fx * util
        w = fw * util
        h = fh * altura
        canvas.rect(x, base, w, h, fill=1, stroke=0)

        if tipo == 'antena':
            # mastro fino saindo do centro
            mw = max(w * 0.07, 0.6)
            canvas.rect(x + w / 2 - mw / 2, base + h, mw, altura * 0.22,
                        fill=1, stroke=0)
        elif tipo == 'agulha':
            # coroa em degraus e agulha, lembrando o Chrysler
            passo = h * 0.055
            lw = w
            ly = base + h
            for _ in range(4):
                lw *= 0.72
                canvas.rect(x + (w - lw) / 2, ly, lw, passo, fill=1, stroke=0)
                ly += passo
            mw = max(w * 0.06, 0.6)
            canvas.rect(x + w / 2 - mw / 2, ly, mw, altura * 0.16,
                        fill=1, stroke=0)
        elif tipo == 'deco':
            # recuos escalonados do art deco, depois o mastro
            lw, ly = w * 0.62, base + h
            canvas.rect(x + (w - lw) / 2, ly, lw, altura * 0.10, fill=1, stroke=0)
            ly += altura * 0.10
            lw *= 0.55
            canvas.rect(x + (w - lw) / 2, ly, lw, altura * 0.07, fill=1, stroke=0)
            ly += altura * 0.07
            mw = max(w * 0.08, 0.7)
            canvas.rect(x + w / 2 - mw / 2, ly, mw, altura * 0.14,
                        fill=1, stroke=0)

    canvas.restoreState()


# --------------------------------------------------------------------------
# Florida: Orlando e a costa
# --------------------------------------------------------------------------
# Predio nao conta a historia desta viagem. Aqui a linha do horizonte e outra:
# coqueiro, montanha-russa, roda gigante, o foguete do Cabo e o navio saindo do
# porto. Sao os cinco assuntos da viagem do Agnaldo desenhados em fila.
#
# Nada aqui imita marca de parque. As formas sao genericas de proposito: a
# silhueta e nossa e vai em documento de cliente, entao nao pega emprestado o
# desenho de ninguem.

def _coqueiro(c, x, base, altura, escala=1.0):
    """Tronco levemente inclinado e cinco folhas abertas."""
    h = altura * escala
    tw = max(h * 0.035, 0.7)
    # O tronco vai em fatias, cada uma um pouco mais para o lado, o que da a
    # curva sem precisar de path.
    fatias = 14
    for i in range(fatias):
        f = i / float(fatias)
        c.rect(x + f * f * h * 0.10, base + f * h, tw, h / fatias + 0.3,
               fill=1, stroke=0)
    topo_x, topo_y = x + h * 0.10 + tw / 2, base + h
    # As folhas sao linhas grossas caindo do topo, abertas em leque.
    for dx, dy in ((-0.26, 0.10), (-0.19, 0.21), (0.0, 0.25),
                   (0.19, 0.21), (0.26, 0.10)):
        c.setLineWidth(max(h * 0.030, 0.6))
        c.line(topo_x, topo_y, topo_x + dx * h, topo_y + dy * h)
        # a ponta caida, que e o que faz parecer coqueiro e nao antena
        c.setLineWidth(max(h * 0.022, 0.5))
        c.line(topo_x + dx * h, topo_y + dy * h,
               topo_x + dx * h * 1.22, topo_y + dy * h * 0.35)


def _montanha_russa(c, x, base, largura, altura):
    """Tres lombadas em linha continua, sobre pilares."""
    import math
    passos = 60
    lw = max(altura * 0.035, 0.8)
    c.setLineWidth(lw)
    pontos = []
    for i in range(passos + 1):
        f = i / float(passos)
        # a primeira lombada e a alta, como na vida real: sobe devagar e
        # depois so perde altura
        env = (1.0 - f) ** 0.7
        y = abs(math.sin(f * math.pi * 3.0)) * altura * env
        pontos.append((x + f * largura, base + y))
    for (x1, y1), (x2, y2) in zip(pontos, pontos[1:]):
        c.line(x1, y1, x2, y2)
    # pilares
    for i in range(0, passos + 1, 8):
        px, py = pontos[i]
        c.setLineWidth(max(altura * 0.022, 0.5))
        c.line(px, base, px, py)


def _roda_gigante(c, cx, base, raio):
    """Aro, raios, cabines e as duas pernas de apoio."""
    import math
    cy = base + raio * 1.15
    c.setLineWidth(max(raio * 0.055, 0.7))
    c.circle(cx, cy, raio, fill=0, stroke=1)
    for i in range(12):
        a = i * math.pi / 6.0
        c.setLineWidth(max(raio * 0.035, 0.5))
        c.line(cx, cy, cx + math.cos(a) * raio, cy + math.sin(a) * raio)
        # cabine: um quadradinho cheio pendurado no aro
        bx, by = cx + math.cos(a) * raio, cy + math.sin(a) * raio
        lado = raio * 0.10
        c.rect(bx - lado / 2, by - lado / 2, lado, lado, fill=1, stroke=0)
    c.setLineWidth(max(raio * 0.055, 0.7))
    c.line(cx, cy, cx - raio * 0.55, base)
    c.line(cx, cy, cx + raio * 0.55, base)


def _foguete(c, x, base, altura):
    """Foguete na torre de lancamento. O Cabo fica a uma hora de Orlando, e o
    porto do cruzeiro e o mesmo lugar."""
    corpo = altura * 0.036
    c.rect(x, base, corpo * 2, altura * 0.78, fill=1, stroke=0)
    # bico
    p = c.beginPath()
    p.moveTo(x, base + altura * 0.78)
    p.lineTo(x + corpo, base + altura * 1.00)
    p.lineTo(x + corpo * 2, base + altura * 0.78)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    # aletas
    c.rect(x - corpo * 0.7, base, corpo * 0.7, altura * 0.13, fill=1, stroke=0)
    c.rect(x + corpo * 2, base, corpo * 0.7, altura * 0.13, fill=1, stroke=0)
    # torre de servico ao lado, com as passarelas
    tx = x + corpo * 3.2
    c.rect(tx, base, corpo * 0.55, altura * 0.72, fill=1, stroke=0)
    for f in (0.30, 0.50, 0.68):
        c.rect(x + corpo * 2, base + altura * f, corpo * 1.2,
               max(altura * 0.014, 0.5), fill=1, stroke=0)


def _navio(c, x, base, largura, altura):
    """Casco, tombadilho em degraus e duas chamines."""
    casco = altura * 0.30
    p = c.beginPath()
    p.moveTo(x, base + casco)
    p.lineTo(x + largura * 0.06, base)
    p.lineTo(x + largura * 0.93, base)
    p.lineTo(x + largura, base + casco)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    # tres andares, cada um menor que o de baixo
    y, l, e = base + casco, largura * 0.86, x + largura * 0.07
    for altura_andar, encolhe in ((0.20, 0.90), (0.15, 0.84), (0.12, 0.70)):
        c.rect(e, y, l, altura * altura_andar, fill=1, stroke=0)
        y += altura * altura_andar
        novo_l = l * encolhe
        e += (l - novo_l) / 2
        l = novo_l
    # chamines
    for f in (0.38, 0.56):
        c.rect(x + largura * f, y, largura * 0.06, altura * 0.20,
               fill=1, stroke=0)
    # mastro
    c.rect(x + largura * 0.20, y, max(largura * 0.012, 0.6), altura * 0.26,
           fill=1, stroke=0)


def desenhar_florida(canvas, largura, base, cor, altura=3.2 * cm,
                     opacidade=0.10, margem=0.0):
    """A costa da Florida ocupando a largura toda, com a base em `base`."""
    canvas.saveState()
    # Cor primeiro, alfa depois: ver a armadilha no topo do arquivo. Aqui sao
    # os dois, porque esta silhueta usa linha alem de preenchimento.
    canvas.setFillColor(cor)
    canvas.setStrokeColor(cor)
    try:
        canvas.setFillAlpha(opacidade)
        canvas.setStrokeAlpha(opacidade)
    except AttributeError:
        pass
    canvas.setLineCap(1)
    util = largura - 2 * margem

    def X(f):
        return margem + f * util

    _coqueiro(canvas, X(0.048), base, altura, 0.60)
    _coqueiro(canvas, X(0.092), base, altura, 0.84)
    # blocos baixos de hotel, para o horizonte nao ficar so de objeto solto
    for fx, fw, fh in ((0.140, 0.032, 0.26), (0.174, 0.026, 0.38),
                       (0.204, 0.030, 0.22)):
        canvas.rect(X(fx), base, fw * util, fh * altura, fill=1, stroke=0)
    _montanha_russa(canvas, X(0.240), base, util * 0.140, altura * 0.80)
    _roda_gigante(canvas, X(0.488), base, altura * 0.40)
    for fx, fw, fh in ((0.600, 0.028, 0.30), (0.632, 0.022, 0.44)):
        canvas.rect(X(fx), base, fw * util, fh * altura, fill=1, stroke=0)
    _foguete(canvas, X(0.674), base, altura)
    for fx, fw, fh in ((0.724, 0.032, 0.24), (0.760, 0.024, 0.34)):
        canvas.rect(X(fx), base, fw * util, fh * altura, fill=1, stroke=0)
    _navio(canvas, X(0.792), base, util * 0.112, altura * 0.66)
    _coqueiro(canvas, X(0.915), base, altura, 0.80)
    _coqueiro(canvas, X(0.952), base, altura, 0.55)

    canvas.restoreState()


# --------------------------------------------------------------------------
# Madri
# --------------------------------------------------------------------------
# Da esquerda para a direita: predio com cupula, os blocos de telhado inclinado
# da Gran Via, a catedral de duas torres, a Puerta de Alcala e, no fim, as
# quatro torres altas do norte da cidade. Formas genericas de proposito, como
# nas outras: o desenho e nosso.


def _cupula(c, x, base, largura, altura):
    """Bloco com cupula e lanterna em cima."""
    corpo = altura * 0.52
    c.rect(x, base, largura, corpo, fill=1, stroke=0)
    r = largura * 0.42
    cx, cy = x + largura / 2, base + corpo
    # wedge desenha a fatia de pizza: meia volta da uma cupula com a base reta
    # apoiada no bloco. Circulo cheio nao serve -- a metade de baixo sobrepoe o
    # bloco, e com opacidade a sobreposicao escurece e aparece.
    c.wedge(cx - r, cy - r, cx + r, cy + r, 0, 180, fill=1, stroke=0)
    c.rect(cx - largura * 0.09, cy + r, largura * 0.18, altura * 0.10,
           fill=1, stroke=0)
    c.rect(cx - largura * 0.02, cy + r + altura * 0.10,
           max(largura * 0.04, 0.6), altura * 0.12, fill=1, stroke=0)


def _mansarda(c, x, base, largura, altura):
    """Predio de telhado inclinado, dos que fazem a parede da Gran Via."""
    corpo = altura * 0.80
    c.rect(x, base, largura, corpo, fill=1, stroke=0)
    p = c.beginPath()
    p.moveTo(x, base + corpo)
    p.lineTo(x + largura * 0.18, base + altura)
    p.lineTo(x + largura * 0.82, base + altura)
    p.lineTo(x + largura, base + corpo)
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def _catedral(c, x, base, largura, altura):
    """Nave baixa entre duas torres com agulha."""
    torre = largura * 0.24
    c.rect(x + largura * 0.20, base, largura * 0.60, altura * 0.42,
           fill=1, stroke=0)
    for tx in (x, x + largura - torre):
        c.rect(tx, base, torre, altura * 0.72, fill=1, stroke=0)
        p = c.beginPath()
        p.moveTo(tx, base + altura * 0.72)
        p.lineTo(tx + torre / 2, base + altura)
        p.lineTo(tx + torre, base + altura * 0.72)
        p.close()
        c.drawPath(p, fill=1, stroke=0)


def _arco(c, x, base, largura, altura):
    """A Puerta de Alcala: cinco vaos entre pilares, cornija e atico.

    Os vaos sao o espaco ENTRE os pilares, e nao um buraco recortado: com
    preenchimento e opacidade nao da para furar uma forma sem escurecer o que
    esta atras. As curvas dos tres arcos centrais sao tracadas por cima.
    """
    corpo = altura * 0.62
    n = 6                      # seis pilares deixam cinco vaos
    pw = largura / (n * 2.0 - 1)
    for i in range(n):
        c.rect(x + i * pw * 2, base, pw, corpo, fill=1, stroke=0)
    # cornija e atico
    c.rect(x - largura * 0.02, base + corpo, largura * 1.04, altura * 0.10,
           fill=1, stroke=0)
    c.rect(x + largura * 0.30, base + corpo + altura * 0.10, largura * 0.40,
           altura * 0.14, fill=1, stroke=0)
    # as curvas dos tres vaos do meio
    c.setLineWidth(max(altura * 0.022, 0.6))
    for i in (1, 2, 3):
        vx = x + (i * 2 - 1) * pw
        r = pw / 2.0
        cy = base + corpo * 0.62
        c.arc(vx, cy - r, vx + pw, cy + r, 0, 180)


def _torre_moderna(c, x, base, largura, altura, topo):
    """Uma das quatro torres. `topo` muda o remate de cada uma."""
    c.rect(x, base, largura, altura, fill=1, stroke=0)
    if topo == 'inclinado':
        p = c.beginPath()
        p.moveTo(x, base + altura)
        p.lineTo(x + largura, base + altura)
        p.lineTo(x + largura, base + altura * 1.10)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
    elif topo == 'coroa':
        c.rect(x - largura * 0.16, base + altura, largura * 1.32,
               altura * 0.05, fill=1, stroke=0)
    elif topo == 'agulha':
        c.rect(x + largura * 0.42, base + altura, max(largura * 0.16, 0.6),
               altura * 0.16, fill=1, stroke=0)
    elif topo == 'curvo':
        r = largura / 2.0
        cy = base + altura
        c.wedge(x, cy - r, x + largura, cy + r, 0, 180, fill=1, stroke=0)


def desenhar_madri(canvas, largura, base, cor, altura=3.2 * cm,
                   opacidade=0.10, margem=0.0):
    """Madri ocupando a largura toda, com a base em `base`."""
    canvas.saveState()
    # Cor primeiro, alfa depois: ver a armadilha no topo do arquivo.
    canvas.setFillColor(cor)
    canvas.setStrokeColor(cor)
    try:
        canvas.setFillAlpha(opacidade)
        canvas.setStrokeAlpha(opacidade)
    except AttributeError:
        pass
    util = largura - 2 * margem

    def X(f):
        return margem + f * util

    # Blocos estreitos e alturas bem espalhadas, de 0,30 a 1,00 da faixa. Na
    # primeira versao eram largos e quase da mesma altura, e a cidade saia como
    # uma fileira de caixas em vez de um horizonte.
    _cupula(canvas, X(0.012), base, util * 0.062, altura * 0.70)
    _mansarda(canvas, X(0.088), base, util * 0.042, altura * 0.38)
    _mansarda(canvas, X(0.138), base, util * 0.038, altura * 0.54)
    _catedral(canvas, X(0.188), base, util * 0.082, altura * 0.82)
    _mansarda(canvas, X(0.282), base, util * 0.040, altura * 0.34)
    _arco(canvas, X(0.340), base, util * 0.126, altura * 0.64)
    _mansarda(canvas, X(0.485), base, util * 0.038, altura * 0.48)
    _mansarda(canvas, X(0.535), base, util * 0.044, altura * 0.32)
    _cupula(canvas, X(0.595), base, util * 0.054, altura * 0.60)
    _mansarda(canvas, X(0.665), base, util * 0.036, altura * 0.42)
    _mansarda(canvas, X(0.712), base, util * 0.040, altura * 0.30)
    # as quatro torres, o Madri de vidro, cada uma com o seu remate
    for fx, fw, fh, topo in ((0.762, 0.030, 0.86, 'inclinado'),
                             (0.816, 0.028, 1.00, 'agulha'),
                             (0.868, 0.032, 0.78, 'coroa'),
                             (0.926, 0.030, 0.92, 'curvo')):
        _torre_moderna(canvas, X(fx), base, fw * util, fh * altura, topo)

    canvas.restoreState()


# --------------------------------------------------------------------------
# Recife
# --------------------------------------------------------------------------
# Da esquerda para a direita: coqueiros, os sobrados do Recife Antigo, uma
# igreja barroca de duas torres, a torre com cupula, a jangada de vela
# triangular e as torres de Boa Viagem. Os coqueiros sao os mesmos da Florida.


def _sobrado(c, x, base, largura, altura):
    """Casario colonial: corpo baixo e telhado de duas aguas."""
    corpo = altura * 0.74
    c.rect(x, base, largura, corpo, fill=1, stroke=0)
    p = c.beginPath()
    p.moveTo(x - largura * 0.06, base + corpo)
    p.lineTo(x + largura / 2, base + altura)
    p.lineTo(x + largura * 1.06, base + corpo)
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def _igreja(c, x, base, largura, altura):
    """Fachada barroca: duas torres com coruchéu e frontaão no meio."""
    torre = largura * 0.26
    meio = largura - 2 * torre
    # nave, com o frontaão curvo em cima
    c.rect(x + torre, base, meio, altura * 0.56, fill=1, stroke=0)
    r = meio * 0.5
    cy = base + altura * 0.56
    c.wedge(x + torre, cy - r, x + torre + meio, cy + r, 0, 180,
            fill=1, stroke=0)
    for tx in (x, x + largura - torre):
        c.rect(tx, base, torre, altura * 0.70, fill=1, stroke=0)
        # o coruchéu: uma piramide baixa e a cruz
        p = c.beginPath()
        p.moveTo(tx, base + altura * 0.70)
        p.lineTo(tx + torre / 2, base + altura * 0.92)
        p.lineTo(tx + torre, base + altura * 0.70)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        haste = max(torre * 0.10, 0.6)
        c.rect(tx + torre / 2 - haste / 2, base + altura * 0.92, haste,
               altura * 0.08, fill=1, stroke=0)
        c.rect(tx + torre / 2 - torre * 0.16, base + altura * 0.955,
               torre * 0.32, haste, fill=1, stroke=0)


def _torre_cupula(c, x, base, largura, altura):
    """Torre de observação com cupula, como a do Recife Antigo."""
    c.rect(x, base, largura, altura * 0.68, fill=1, stroke=0)
    # a varanda que marca o alto do fuste
    c.rect(x - largura * 0.14, base + altura * 0.68, largura * 1.28,
           altura * 0.05, fill=1, stroke=0)
    r = largura * 0.52
    cx, cy = x + largura / 2, base + altura * 0.73
    c.wedge(cx - r, cy - r, cx + r, cy + r, 0, 180, fill=1, stroke=0)
    haste = max(largura * 0.08, 0.6)
    c.rect(cx - haste / 2, cy + r, haste, altura * 0.12, fill=1, stroke=0)


def _jangada(c, x, base, largura, altura):
    """Casco raso, mastro e a vela triangular."""
    casco = altura * 0.13
    p = c.beginPath()
    p.moveTo(x, base + casco)
    p.lineTo(x + largura * 0.10, base)
    p.lineTo(x + largura * 0.88, base)
    p.lineTo(x + largura, base + casco)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    mastro = max(largura * 0.035, 0.7)
    mx = x + largura * 0.34
    c.rect(mx, base + casco, mastro, altura * 0.87, fill=1, stroke=0)
    # a vela, presa ao mastro e aberta para a direita
    v = c.beginPath()
    v.moveTo(mx + mastro, base + casco + altura * 0.04)
    v.lineTo(mx + mastro, base + altura * 0.96)
    v.lineTo(x + largura * 0.94, base + casco + altura * 0.06)
    v.close()
    c.drawPath(v, fill=1, stroke=0)


def desenhar_recife(canvas, largura, base, cor, altura=3.2 * cm,
                    opacidade=0.10, margem=0.0):
    """O Recife ocupando a largura toda, com a base em `base`."""
    canvas.saveState()
    # Cor primeiro, alfa depois: ver a armadilha no topo do arquivo.
    canvas.setFillColor(cor)
    canvas.setStrokeColor(cor)
    try:
        canvas.setFillAlpha(opacidade)
        canvas.setStrokeAlpha(opacidade)
    except AttributeError:
        pass
    canvas.setLineCap(1)
    util = largura - 2 * margem

    def X(f):
        return margem + f * util

    _coqueiro(canvas, X(0.050), base, altura, 0.58)
    _coqueiro(canvas, X(0.092), base, altura, 0.82)
    for fx, fw, fh in ((0.142, 0.040, 0.34), (0.186, 0.034, 0.42),
                       (0.224, 0.038, 0.30)):
        _sobrado(canvas, X(fx), base, fw * util, fh * altura)
    _igreja(canvas, X(0.276), base, util * 0.078, altura * 0.82)
    for fx, fw, fh in ((0.368, 0.036, 0.32), (0.408, 0.030, 0.40)):
        _sobrado(canvas, X(fx), base, fw * util, fh * altura)
    _torre_cupula(canvas, X(0.452), base, util * 0.032, altura * 0.70)
    for fx, fw, fh in ((0.500, 0.038, 0.28), (0.542, 0.032, 0.36)):
        _sobrado(canvas, X(fx), base, fw * util, fh * altura)
    _jangada(canvas, X(0.590), base, util * 0.098, altura * 0.62)
    # Boa Viagem: a parede de predios altos da praia
    for fx, fw, fh in ((0.706, 0.026, 0.72), (0.740, 0.030, 0.88),
                       (0.778, 0.024, 0.64), (0.810, 0.028, 0.80),
                       (0.846, 0.026, 0.58)):
        canvas.rect(X(fx), base, fw * util, fh * altura, fill=1, stroke=0)
    _coqueiro(canvas, X(0.900), base, altura, 0.80)
    _coqueiro(canvas, X(0.945), base, altura, 0.56)

    canvas.restoreState()


# O nome que vai no JSON da apresentacao, para destino novo nao exigir edicao
# do gerador.
SILHUETAS = {
    'nova-york': desenhar,
    'florida': desenhar_florida,
    'madri': desenhar_madri,
    'recife': desenhar_recife,
}


def escolher(nome):
    """A funcao de desenho pelo nome. Erra alto: silhueta errada no fundo de
    uma proposta e o tipo de coisa que so se percebe depois de enviada."""
    if nome not in SILHUETAS:
        raise SystemExit(
            'Silhueta "%s" nao existe. Ha estas: %s.\n'
            'Escreva a funcao em propostas/skyline.py e registre no SILHUETAS.'
            % (nome, ', '.join(sorted(SILHUETAS))))
    return SILHUETAS[nome]
