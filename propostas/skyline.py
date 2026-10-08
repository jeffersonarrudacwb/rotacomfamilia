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
    desenhar_panama()   catedral do Casco Viejo, navio na eclusa, guindaste do
                        porto e as torres do centro

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


# --------------------------------------------------------------------------
# Cidade do Panama
# --------------------------------------------------------------------------
# Da esquerda para a direita: coqueiro, a catedral do Casco Viejo, o casario
# colonial, um navio DENTRO da eclusa, o guindaste do porto e o bloco de torres
# do centro, com a torcida no meio. A eclusa com o navio e a imagem do pais.


def _eclusa(c, x, base, largura, altura):
    """As duas comportas e o navio entre elas, com o nivel da agua marcado."""
    parede = largura * 0.055
    h = altura * 0.62
    # comporta da esquerda e da direita
    c.rect(x, base, parede, h, fill=1, stroke=0)
    c.rect(x + largura - parede, base, parede, h, fill=1, stroke=0)
    # o navio no meio, menor que a camara
    _navio(c, x + largura * 0.16, base + altura * 0.10,
           largura * 0.68, altura * 0.52)
    # as linhas da agua, que e o que faz ler como eclusa e nao como ponte
    c.setLineWidth(max(altura * 0.018, 0.5))
    for f in (0.06, 0.11):
        c.line(x + parede, base + altura * f,
               x + largura - parede, base + altura * f)


def _guindaste(c, x, base, largura, altura):
    """Guindaste de portico do porto: duas pernas, viga no alto e o cabo.

    A primeira versao era mastro com duas lancas inclinadas para baixo, e as
    duas juntas formavam um V invertido: na pagina lia como antena, nao como
    guindaste. O que faz ler e a VIGA HORIZONTAL passando das pernas, que e a
    silhueta que todo porto tem.
    """
    perna = max(largura * 0.075, 0.9)
    viga = max(altura * 0.055, 1.0)
    topo = base + altura - viga

    # as duas pernas, afastadas
    c.rect(x + largura * 0.18, base, perna, altura - viga, fill=1, stroke=0)
    c.rect(x + largura * 0.52, base, perna, altura - viga, fill=1, stroke=0)
    # travessa entre elas, na altura do meio
    c.rect(x + largura * 0.18, base + altura * 0.34,
           largura * 0.40, max(altura * 0.022, 0.6), fill=1, stroke=0)
    # a viga, que passa das duas pernas e avanca para a direita sobre a agua
    c.rect(x - largura * 0.10, topo, largura * 1.24, viga, fill=1, stroke=0)
    # a cabine, pendurada na viga entre as pernas
    c.rect(x + largura * 0.34, topo - altura * 0.10,
           largura * 0.13, altura * 0.10, fill=1, stroke=0)
    # o cabo do carrinho, na ponta que avanca
    c.setLineWidth(max(altura * 0.014, 0.5))
    c.line(x + largura * 0.98, topo, x + largura * 0.98, base + altura * 0.30)


def _torre_torcida(c, x, base, largura, altura):
    """A torre que sobe girando, do centro da cidade.

    Nao ha rotacao aqui: sao fatias empilhadas, cada uma deslocada de lado
    seguindo um seno. De longe, e em opacidade baixa, le como torcao, e nao
    depende de transformacao de canvas.
    """
    import math
    fatias = 22
    h = altura / fatias
    for i in range(fatias):
        f = i / float(fatias - 1)
        dx = math.sin(f * math.pi * 1.8) * largura * 0.30
        c.rect(x + dx, base + i * h, largura, h + 0.4, fill=1, stroke=0)


def desenhar_panama(canvas, largura, base, cor, altura=3.2 * cm,
                    opacidade=0.10, margem=0.0):
    """A Cidade do Panama ocupando a largura toda, com a base em `base`."""
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

    _coqueiro(canvas, X(0.032), base, altura, 0.56)
    _igreja(canvas, X(0.072), base, util * 0.070, altura * 0.70)
    for fx, fw, fh in ((0.156, 0.030, 0.26), (0.190, 0.026, 0.34),
                       (0.220, 0.028, 0.22)):
        _sobrado(canvas, X(fx), base, fw * util, fh * altura)
    _eclusa(canvas, X(0.262), base, util * 0.150, altura * 0.66)
    _guindaste(canvas, X(0.432), base, util * 0.070, altura * 0.80)
    # o centro: torres retas, a torcida no meio, e as mais altas ao lado
    for fx, fw, fh in ((0.530, 0.026, 0.62), (0.564, 0.030, 0.84)):
        canvas.rect(X(fx), base, fw * util, fh * altura, fill=1, stroke=0)
    _torre_torcida(canvas, X(0.606), base, util * 0.024, altura * 1.00)
    for fx, fw, fh in ((0.650, 0.028, 0.76), (0.686, 0.024, 0.58),
                       (0.716, 0.030, 0.90), (0.754, 0.026, 0.66),
                       (0.786, 0.028, 0.80), (0.822, 0.024, 0.54),
                       (0.852, 0.030, 0.72)):
        canvas.rect(X(fx), base, fw * util, fh * altura, fill=1, stroke=0)
    _coqueiro(canvas, X(0.916), base, altura, 0.78)
    _coqueiro(canvas, X(0.955), base, altura, 0.54)

    canvas.restoreState()


# --------------------------------------------------------------------------
# Teresina
# --------------------------------------------------------------------------
# Da esquerda para a direita: carnauba, a catedral, o casario do centro, a
# Ponte Estaiada sobre o Poti e o bloco de predios da zona leste. A ponte e o
# cartao-postal da cidade, e e ela que impede a silhueta de virar "qualquer
# capital do Nordeste". Nada de praia nem de jangada aqui: Teresina e a unica
# capital nordestina que nao fica no litoral.


def _ponte_estaiada(c, x, base, largura, altura):
    """Tabuleiro reto, mastro inclinado e o leque de cabos dos dois lados."""
    tabuleiro = base + altura * 0.30
    esp = max(altura * 0.035, 0.8)

    # o rio, duas linhas rasas embaixo do vao
    c.setLineWidth(max(altura * 0.018, 0.5))
    for f in (0.05, 0.11):
        c.line(x, base + altura * f, x + largura, base + altura * f)

    # tabuleiro e os dois pilares que o seguram
    c.rect(x, tabuleiro, largura, esp, fill=1, stroke=0)
    for fx in (0.10, 0.88):
        c.rect(x + largura * fx, base + altura * 0.10,
               max(largura * 0.022, 0.8), tabuleiro - (base + altura * 0.10),
               fill=1, stroke=0)

    # o mastro, inclinado para a direita como o de Teresina
    pe_x = x + largura * 0.44
    topo_x = x + largura * 0.56
    topo_y = base + altura
    meia = max(largura * 0.020, 0.9)
    p = c.beginPath()
    p.moveTo(pe_x, tabuleiro)
    p.lineTo(pe_x + meia, tabuleiro)
    p.lineTo(topo_x + meia, topo_y)
    p.lineTo(topo_x, topo_y)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    # o mirante, a plataforma que fica no alto do mastro
    c.rect(topo_x - largura * 0.020, topo_y - altura * 0.10,
           largura * 0.060, max(altura * 0.022, 0.6), fill=1, stroke=0)

    # Os cabos sao o que faz ler como ponte estaiada. A primeira versao
    # prendia todos no mesmo ponto do topo, e o desenho virava uma tenda de
    # circo. Presos em alturas diferentes do mastro, viram leque, que e como a
    # ponte realmente e.
    c.setLineWidth(max(altura * 0.012, 0.4))
    quedas = ((0.08, 0.97), (0.17, 0.90), (0.26, 0.83), (0.35, 0.76),
              (0.64, 0.76), (0.73, 0.83), (0.82, 0.90), (0.90, 0.97))
    for f, fh in quedas:
        prende = pe_x + (topo_x - pe_x) * fh
        c.line(prende + meia * 0.5, tabuleiro + (topo_y - tabuleiro) * fh,
               x + largura * f, tabuleiro + esp)


def desenhar_teresina(canvas, largura, base, cor, altura=3.2 * cm,
                      opacidade=0.10, margem=0.0):
    """Teresina ocupando a largura toda, com a base em `base`."""
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

    _coqueiro(canvas, X(0.036), base, altura, 0.60)
    _coqueiro(canvas, X(0.078), base, altura, 0.84)
    _igreja(canvas, X(0.130), base, util * 0.074, altura * 0.78)
    for fx, fw, fh in ((0.212, 0.034, 0.30), (0.250, 0.028, 0.38)):
        _sobrado(canvas, X(fx), base, fw * util, fh * altura)
    # A ponte e larga e baixa de proposito: mastro alto sobre vao curto lia
    # como tenda de circo, e nao como ponte.
    _ponte_estaiada(canvas, X(0.296), base, util * 0.340, altura * 0.76)
    # a zona leste, mais alta e mais recente que o centro
    for fx, fw, fh in ((0.666, 0.026, 0.58), (0.700, 0.030, 0.74),
                       (0.738, 0.024, 0.50), (0.770, 0.028, 0.68),
                       (0.806, 0.026, 0.86), (0.840, 0.030, 0.62),
                       (0.878, 0.024, 0.46)):
        canvas.rect(X(fx), base, fw * util, fh * altura, fill=1, stroke=0)
    _coqueiro(canvas, X(0.924), base, altura, 0.78)
    _coqueiro(canvas, X(0.962), base, altura, 0.54)

    canvas.restoreState()


# --------------------------------------------------------------------------
# Italia
# --------------------------------------------------------------------------
# Da esquerda para a direita: pinheiro-manso, o Coliseu com o anel quebrado, a
# cupula de Sao Pedro, o casario, uma igreja, o campanile, a torre inclinada de
# Pisa e mais casario. Nao e uma cidade: e o pais, porque o cliente disse
# "Italia" e nao disse a cidade. Se a cidade fechar, vale desenhar a dela.


def _pinheiro_manso(c, x, base, altura, escala=1.0):
    """Tronco alto e limpo, com a copa achatada em guarda-chuva."""
    h = altura * escala
    tw = max(h * 0.030, 0.7)
    c.rect(x, base, tw, h * 0.72, fill=1, stroke=0)
    cx, cy = x + tw / 2, base + h * 0.78
    rx, ry = h * 0.30, h * 0.13
    c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, fill=1, stroke=0)
    # duas copas menores em cima, que tiram o ar de cogumelo
    for dx, dy, f in ((-0.09, 0.07, 0.50), (0.10, 0.08, 0.44)):
        c.ellipse(cx + dx * h - rx * f, cy + dy * h - ry * f,
                  cx + dx * h + rx * f, cy + dy * h + ry * f,
                  fill=1, stroke=0)


def _coliseu(c, x, base, largura, altura):
    """Arcadas em dois niveis, e o terceiro so na metade que ficou de pe."""
    plinto = altura * 0.07
    c.rect(x, base, largura, plinto, fill=1, stroke=0)

    def arcada(y, h, ate):
        viga = max(h * 0.26, 1.0)
        c.rect(x, y + h - viga, largura * ate, viga, fill=1, stroke=0)
        # Pilar grosso e vao estreito: e a proporcao que faz a arcada ler como
        # ruina e nao como andaime.
        pilares = 8
        pw = largura * 0.072
        for i in range(pilares + 1):
            f = i / float(pilares)
            if f > ate:
                break
            c.rect(x + f * (largura - pw), y, pw, h - viga, fill=1, stroke=0)

    nivel = altura * 0.30
    arcada(base + plinto, nivel, 1.0)
    arcada(base + plinto + nivel, nivel, 1.0)
    # o terceiro nivel so existe na metade esquerda: e o perfil quebrado que
    # faz qualquer um reconhecer o Coliseu de longe
    arcada(base + plinto + 2 * nivel, nivel, 0.58)


def _torre_inclinada(c, x, base, largura, altura):
    """Pisa: um paralelogramo deitando para a direita, com as galerias.

    A primeira versao empilhava fatias deslocadas, como a torre torcida do
    Panama, e o resultado lia como escada. Torre inclinada e um corpo inteiro
    fora de prumo, entao o desenho certo e o paralelogramo.
    """
    caida = largura * 0.30
    p = c.beginPath()
    p.moveTo(x, base)
    p.lineTo(x + largura, base)
    p.lineTo(x + largura + caida, base + altura)
    p.lineTo(x + caida, base + altura)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    # o campanario, mais estreito e no prumo da ponta de cima
    c.rect(x + caida + largura * 0.16, base + altura, largura * 0.68,
           altura * 0.16, fill=1, stroke=0)


def _campanile(c, x, base, largura, altura):
    """Torre quadrada e fina, com a piramide no alto."""
    c.rect(x, base, largura, altura * 0.84, fill=1, stroke=0)
    p = c.beginPath()
    p.moveTo(x - largura * 0.10, base + altura * 0.84)
    p.lineTo(x + largura / 2, base + altura)
    p.lineTo(x + largura * 1.10, base + altura * 0.84)
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def desenhar_italia(canvas, largura, base, cor, altura=3.2 * cm,
                    opacidade=0.10, margem=0.0):
    """A Italia ocupando a largura toda, com a base em `base`."""
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

    _pinheiro_manso(canvas, X(0.030), base, altura, 0.62)
    _pinheiro_manso(canvas, X(0.078), base, altura, 0.86)
    _coliseu(canvas, X(0.122), base, util * 0.205, altura * 0.54)
    _cupula(canvas, X(0.368), base, util * 0.100, altura * 0.86)
    for fx, fw, fh in ((0.455, 0.034, 0.30), (0.495, 0.030, 0.38)):
        _sobrado(canvas, X(fx), base, fw * util, fh * altura)
    _igreja(canvas, X(0.540), base, util * 0.072, altura * 0.66)
    _campanile(canvas, X(0.635), base, util * 0.030, altura * 0.78)
    _torre_inclinada(canvas, X(0.694), base, util * 0.040, altura * 0.58)
    for fx, fw, fh in ((0.760, 0.036, 0.34), (0.802, 0.030, 0.26),
                       (0.838, 0.034, 0.40)):
        _sobrado(canvas, X(fx), base, fw * util, fh * altura)
    _pinheiro_manso(canvas, X(0.900), base, altura, 0.80)
    _pinheiro_manso(canvas, X(0.950), base, altura, 0.58)

    canvas.restoreState()


# --------------------------------------------------------------------------
# Japao
# --------------------------------------------------------------------------
# Da esquerda para a direita: cerejeira, o torii, o pagode de cinco andares, o
# Fuji ocupando o meio, a torre de Toquio e o casario baixo. O Fuji e largo e
# fica atras de tudo, como na cidade: ele e paisagem, nao predio.


def _cerejeira(c, x, base, altura, escala=1.0):
    """Tronco fino e a copa redonda, em tres bolas que se sobrepoem."""
    h = altura * escala
    tw = max(h * 0.035, 0.7)
    c.rect(x, base, tw, h * 0.52, fill=1, stroke=0)
    cx, cy = x + tw / 2, base + h * 0.70
    r = h * 0.26
    for dx, dy, f in ((0.0, 0.0, 1.0), (-0.22, -0.10, 0.62),
                      (0.23, -0.08, 0.58), (0.02, 0.18, 0.54)):
        c.circle(cx + dx * h, cy + dy * h, r * f, fill=1, stroke=0)


def _torii(c, x, base, largura, altura):
    """Dois pilares e as duas travessas, a de cima passando das laterais."""
    pilar = max(largura * 0.17, 1.0)
    c.rect(x + largura * 0.10, base, pilar, altura * 0.86, fill=1, stroke=0)
    c.rect(x + largura * 0.90 - pilar, base, pilar, altura * 0.86,
           fill=1, stroke=0)
    # nuki, a travessa de baixo, entre os pilares
    c.rect(x + largura * 0.08, base + altura * 0.60, largura * 0.84,
           max(altura * 0.055, 0.8), fill=1, stroke=0)
    # kasagi, a de cima, que avanca para fora dos dois lados
    c.rect(x - largura * 0.06, base + altura * 0.86, largura * 1.12,
           max(altura * 0.075, 1.0), fill=1, stroke=0)


def _pagode(c, x, base, largura, altura):
    """Cinco andares, cada um com telhado mais largo que o corpo."""
    andares = 5
    h = altura / (andares + 0.6)
    for i in range(andares):
        f = 1.0 - i * 0.12          # o pagode afina conforme sobe
        w = largura * f
        cx = x + largura / 2
        y = base + i * h
        c.rect(cx - w * 0.34, y, w * 0.68, h * 0.62, fill=1, stroke=0)
        # o telhado, em trapezio, com beiral passando do corpo
        beiral = w * 0.64
        p = c.beginPath()
        p.moveTo(cx - beiral, y + h * 0.62)
        p.lineTo(cx + beiral, y + h * 0.62)
        p.lineTo(cx + beiral * 0.62, y + h * 0.98)
        p.lineTo(cx - beiral * 0.62, y + h * 0.98)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
    # o sorin, a agulha do topo
    haste = max(largura * 0.05, 0.7)
    c.rect(x + largura / 2 - haste / 2, base + andares * h, haste, h * 0.9,
           fill=1, stroke=0)


def _fuji(c, x, base, largura, altura):
    """Cone largo, encosta levemente concava e a cratera no alto."""
    p = c.beginPath()
    p.moveTo(x, base)
    p.lineTo(x + largura * 0.20, base + altura * 0.42)
    p.lineTo(x + largura * 0.38, base + altura * 0.88)
    p.lineTo(x + largura * 0.44, base + altura)
    p.lineTo(x + largura * 0.50, base + altura * 0.94)   # a cratera
    p.lineTo(x + largura * 0.56, base + altura)
    p.lineTo(x + largura * 0.62, base + altura * 0.88)
    p.lineTo(x + largura * 0.80, base + altura * 0.42)
    p.lineTo(x + largura, base)
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def _torre_toquio(c, x, base, largura, altura):
    """Duas pernas que se fecham, dois deques e o mastro."""
    perna = max(largura * 0.16, 1.0)
    topo = base + altura * 0.78
    for lado in (0, 1):
        x0 = x + (largura - perna if lado else 0)
        x1 = x + largura / 2 + (perna * 0.4 if lado else -perna * 1.4)
        p = c.beginPath()
        p.moveTo(x0, base)
        p.lineTo(x0 + perna, base)
        p.lineTo(x1 + perna, topo)
        p.lineTo(x1, topo)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
    # os dois deques, que e o que distingue a torre de uma antena qualquer
    for f, w in ((0.34, 0.74), (0.66, 0.42)):
        c.rect(x + largura * (0.5 - w / 2), base + altura * f, largura * w,
               max(altura * 0.030, 0.6), fill=1, stroke=0)
    haste = max(largura * 0.07, 0.6)
    c.rect(x + largura / 2 - haste / 2, topo, haste, altura * 0.22,
           fill=1, stroke=0)


def desenhar_japao(canvas, largura, base, cor, altura=3.2 * cm,
                   opacidade=0.10, margem=0.0):
    """O Japao ocupando a largura toda, com a base em `base`."""
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

    _cerejeira(canvas, X(0.034), base, altura, 0.66)
    _torii(canvas, X(0.086), base, util * 0.092, altura * 0.62)
    _pagode(canvas, X(0.196), base, util * 0.070, altura * 0.86)
    _fuji(canvas, X(0.300), base, util * 0.300, altura * 0.82)
    _torre_toquio(canvas, X(0.640), base, util * 0.078, altura * 0.96)
    for fx, fw, fh in ((0.736, 0.034, 0.26), (0.776, 0.030, 0.34),
                       (0.812, 0.036, 0.22), (0.856, 0.028, 0.30)):
        _sobrado(canvas, X(fx), base, fw * util, fh * altura)
    _cerejeira(canvas, X(0.922), base, altura, 0.66)
    _cerejeira(canvas, X(0.966), base, altura, 0.48)

    canvas.restoreState()


# O nome que vai no JSON da apresentacao, para destino novo nao exigir edicao
# do gerador.
SILHUETAS = {
    'nova-york': desenhar,
    'florida': desenhar_florida,
    'madri': desenhar_madri,
    'recife': desenhar_recife,
    'panama': desenhar_panama,
    'teresina': desenhar_teresina,
    'italia': desenhar_italia,
    'japao': desenhar_japao,
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
