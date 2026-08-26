# -*- coding: utf-8 -*-
"""Silhueta de Nova York para o fundo da apresentacao.

Desenhada com retangulos em vez de imagem: fica nitida em qualquer zoom, pesa
uns bytes e muda de cor junto com o tema. Vai em opacidade baixa, rente ao
rodape, para ficar como marca d'agua e nunca competir com o texto.

Se a proxima proposta for para Lisboa, o caminho e escrever outra funcao aqui,
com o mesmo formato: recebe canvas, largura, base e cor.
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
