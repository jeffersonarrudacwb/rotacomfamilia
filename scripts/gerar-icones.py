# -*- coding: utf-8 -*-
"""Gera o favicon e os icones do site a partir de fotos/logo.png.

    python scripts/gerar-icones.py

A logo original e circular, com o fundo transparente em volta. O arquivo bruto
tem 1083x1113 e 1,7 MB, entao nao serve para ser servido direto: aqui ele e
recortado no circulo, deixado quadrado e reduzido para cada tamanho que o
navegador pede.

Por que varios tamanhos e nao so um PNG grande: o navegador reduz imagem grande
com um filtro rapido e ruim, e a 16 px a logo vira uma mancha. Reduzindo aqui,
com LANCZOS, cada tamanho sai legivel.

Os arquivos ficam em assets/img/, que e a unica pasta de imagem que o
.gitignore deixa passar e que o deploy publica.
"""
import io
import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)

ORIGEM = os.path.join('fotos', 'logo.png')
DESTINO = os.path.join('assets', 'img')

# O que cada arquivo serve:
#   16 e 32  aba do navegador e favoritos
#   180      icone de atalho na tela inicial do iPhone
#   192/512  Android e PWA, tamanhos que o manifest pede
TAMANHOS = [16, 32, 180, 192, 512]


def recortar_no_conteudo(im):
    """Corta a margem transparente e deixa a imagem quadrada.

    Sem isso o circulo fica descentralizado, porque o arquivo original nao e
    quadrado: sao 1083 de largura por 1113 de altura.
    """
    caixa = im.getbbox()
    if caixa:
        im = im.crop(caixa)
    lado = max(im.size)
    quadro = Image.new('RGBA', (lado, lado), (0, 0, 0, 0))
    quadro.paste(im, ((lado - im.width) // 2, (lado - im.height) // 2))
    return quadro


def main():
    if not os.path.exists(ORIGEM):
        print('ERRO: nao achei %s' % ORIGEM)
        return 1
    if not os.path.isdir(DESTINO):
        os.makedirs(DESTINO)

    original = Image.open(ORIGEM).convert('RGBA')
    quadrado = recortar_no_conteudo(original)
    print('origem %dx%d  ->  quadrado %dx%d' % (
        original.width, original.height, quadrado.width, quadrado.height))

    gerados = []
    for n in TAMANHOS:
        img = quadrado.resize((n, n), Image.LANCZOS)
        nome = 'icone-%d.png' % n
        caminho = os.path.join(DESTINO, nome)
        img.save(caminho, 'PNG', optimize=True)
        gerados.append((nome, os.path.getsize(caminho)))

    # favicon.ico na raiz: navegador antigo e alguns leitores de feed ainda
    # procuram /favicon.ico sem olhar o HTML.
    quadrado.resize((64, 64), Image.LANCZOS).save(
        'favicon.ico', 'ICO', sizes=[(16, 16), (32, 32), (48, 48)])
    gerados.append(('../../favicon.ico', os.path.getsize('favicon.ico')))

    # Versao maior para o cabecalho, em tela comum e retina.
    for n in (96, 192):
        img = quadrado.resize((n, n), Image.LANCZOS)
        nome = 'logo-%d.png' % n
        caminho = os.path.join(DESTINO, nome)
        img.save(caminho, 'PNG', optimize=True)
        gerados.append((nome, os.path.getsize(caminho)))

    for nome, tam in gerados:
        print('  %-22s %6.1f KB' % (nome, tam / 1024))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
