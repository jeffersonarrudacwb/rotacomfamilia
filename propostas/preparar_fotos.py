# -*- coding: utf-8 -*-
"""Prepara fotos para entrar no PDF: recorta em 3:2, reduz e tira o EXIF.

    python propostas/preparar_fotos.py boni Panama Miami
    python propostas/preparar_fotos.py --pasta propostas/pdf/reginaldo/cruzeiros

DOIS MODOS, porque apareceram duas convencoes de nome

O primeiro le propostas/pdf/<slug>/hoteis/<cidade>/NN.2 e NN.3, que e como as
capturas de hotel chegam da Booking.

O segundo le uma pasta inteira e mantem o nome de cada arquivo. Nasceu das
fotos dos navios, que chegaram como Carnival_Freedom01.jpg e msc_seashore03.jpg
Renomear dez arquivos para caber na convencao dos hoteis seria trabalho manual
para agradar o script, e nao o contrario.

POR QUE SO O .2 E O .3, E NAO O .1

O .1 nao e foto: e uma captura da pagina da Booking. Tem o nome do hotel em
titulo, o endereco, o link azul "mostrar o mapa", o coracao de favorito, o
botao "Reservar agora" e, embaixo, a tira de miniaturas com o selo "mais 52
fotos" queimado por cima.

Tentei recortar so a faixa de fotos, achando onde o cabecalho branco acaba. Nao
deu: em tres dos seis casos o detector parava na linha azul do "Localizacao
excelente" e o nome do hotel sobrava no topo, e a tira de miniaturas entrava em
todos. Recorte que erra em metade dos casos e pior do que nao recortar, entao a
funcao inteira saiu daqui em vez de ficar como codigo que quase funciona.

O .2 e o .3 sao fotos limpas de 1024 px, e sao justamente o quarto e o cafe da
manha. Para escolher hotel com cafe incluido, sao as duas que importam. Se um
dia quiser uma terceira, salve uma foto limpa como NN.5 e acrescente aqui.

FORMATOS DE ENTRADA: jpg, png, webp e avif. Os tres ultimos aparecem porque
banco de imagem de companhia de cruzeiro entrega em webp e avif. A saida e
sempre JPEG.

PROPORCAO: tudo vira 3:2, cortado pelo centro. As fotos chegam de 1:1 a 2,33:1,
e sem o corte a fila do PDF sairia desalinhada e as imagens esticadas.

TAMANHO: 420 px de largura, em 3:2. Duas lado a lado no PDF ocupam 8 cm cada,
o que da cerca de 133 DPI. Chega para foto de apoio impressa em A4.
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from PIL import Image, ImageOps

AQUI = os.path.dirname(os.path.abspath(__file__))
LARGURA = 420
PROPORCAO = 3.0 / 2.0      # todas viram 3:2, para a fila alinhar no rodape
SUFIXOS = ('2', '3')


def cortar_em_proporcao(im, proporcao):
    """Corta pelo centro ate a proporcao pedida, sem distorcer."""
    l, a = im.size
    if l / a > proporcao:
        novo_l = int(a * proporcao)
        e = (l - novo_l) // 2
        return im.crop((e, 0, e + novo_l, a))
    novo_a = int(l / proporcao)
    t = (a - novo_a) // 2
    return im.crop((0, t, l, t + novo_a))


def preparar(origem, destino):
    im = Image.open(origem)
    im = ImageOps.exif_transpose(im)          # respeita a rotacao da camera
    im = cortar_em_proporcao(im.convert('RGB'), PROPORCAO)
    im = im.resize((LARGURA, int(LARGURA / PROPORCAO)), Image.LANCZOS)
    # Salva sem EXIF: o que sai daqui vai para a mao do cliente.
    im.save(destino, 'JPEG', quality=82, optimize=True)
    return destino


def preparar_cidade(slug, cidade):
    base = os.path.join(AQUI, 'pdf', slug, 'hoteis', cidade)
    if not os.path.isdir(base):
        raise SystemExit('nao achei %s' % base)
    saida = os.path.join(base, 'reduzidas')
    os.makedirs(saida, exist_ok=True)

    hoteis = sorted({f.split('.')[0] for f in os.listdir(base)
                     if f[:2].isdigit()})
    relatorio = []
    for h in hoteis:
        feitas = []
        for sufixo in SUFIXOS:
            achou = None
            for ext in ('jpg', 'jpeg', 'png', 'webp', 'avif'):
                c = os.path.join(base, '%s.%s.%s' % (h, sufixo, ext))
                if os.path.exists(c):
                    achou = c
                    break
            if achou is None:
                continue
            destino = os.path.join(saida, '%s-%s.jpg' % (h, sufixo))
            preparar(achou, destino)
            feitas.append(os.path.basename(destino))
        relatorio.append((h, feitas))
    return saida, relatorio


def preparar_pasta(caminho):
    """Toda imagem da pasta, com o nome preservado.

    Ignora a propria reduzidas/ para nao processar o que ja foi processado, o
    que degradaria a imagem um pouco mais a cada rodada.
    """
    if not os.path.isdir(caminho):
        raise SystemExit('nao achei a pasta %s' % caminho)
    saida = os.path.join(caminho, 'reduzidas')
    os.makedirs(saida, exist_ok=True)
    feitas = []
    for f in sorted(os.listdir(caminho)):
        raiz, ext = os.path.splitext(f)
        # AVIF e WebP entram porque foi assim que as fotos dos navios
        # chegaram. O Pillow 12 le os dois sem plugin, e a saida e sempre
        # JPEG, que e o que o ReportLab embute sem surpresa.
        if ext.lower() not in ('.jpg', '.jpeg', '.png', '.webp', '.avif'):
            continue
        destino = os.path.join(saida, raiz + '.jpg')
        preparar(os.path.join(caminho, f), destino)
        feitas.append(raiz + '.jpg')
    return saida, feitas


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == '--pasta':
        saida, feitas = preparar_pasta(sys.argv[2])
        for f in feitas:
            print('  %s' % f)
        print('')
        print('%d fotos, %d px de largura, em %s'
              % (len(feitas), LARGURA, saida))
        return

    if len(sys.argv) < 3:
        print('uso: python propostas/preparar_fotos.py <slug> <cidade>...')
        print('     python propostas/preparar_fotos.py --pasta <caminho>')
        raise SystemExit(1)
    slug, cidades = sys.argv[1], sys.argv[2:]
    total = 0
    for cidade in cidades:
        saida, rel = preparar_cidade(slug, cidade)
        print('%s' % cidade)
        for h, feitas in rel:
            total += len(feitas)
            falta = '' if len(feitas) == len(SUFIXOS) else '   <- faltou alguma'
            print('  hotel %s: %s%s' % (h, ', '.join(feitas) or 'nenhuma', falta))
    print('')
    print('%d fotos, %d px de largura, em %s' % (total, LARGURA, saida))


if __name__ == '__main__':
    main()
