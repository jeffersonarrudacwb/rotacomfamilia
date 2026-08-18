# -*- coding: utf-8 -*-
"""Gera os QR codes das parcerias.

Dois formatos, com finalidades diferentes:

  assets/qr/<slug>.svg  vai embutido no HTML da pagina de parcerias. SVG
                        porque escala sem borrar e pesa uns 2 KB, contra uns
                        20 KB de um PNG equivalente.

  qrcodes/<slug>.png    e para uso fora do site: story do Instagram, arte de
                        video, material impresso. Fica alto para nao serrilhar
                        quando o pessoal ampliar.

Rode depois de mexer em dados/parcerias.json:

    python scripts/gerar-qrcodes.py
"""
import io
import json
import os
import sys

import segno

sys.stdout.reconfigure(encoding='utf-8')
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)

DIR_SVG = os.path.join('assets', 'qr')
DIR_PNG = 'qrcodes'

# Cores da marca. O QR precisa de contraste alto para ler rapido, entao o
# escuro e o mesmo preto-oliva do site e o claro e branco puro, nao o creme:
# leitor de QR barato erra com fundo colorido.
ESCURO = '#14150D'
CLARO = '#FFFFFF'


def main():
    dados = json.load(io.open(os.path.join('dados', 'parcerias.json'),
                              encoding='utf-8'))
    for d in (DIR_SVG, DIR_PNG):
        if not os.path.isdir(d):
            os.makedirs(d)

    for p in dados['parcerias']:
        slug, url = p['slug'], p['url']
        # error='m' aguenta uns 15% de sujeira, que e o suficiente para tela e
        # impressao domestica sem inflar o tamanho do codigo.
        qr = segno.make(url, error='m')

        svg = os.path.join(DIR_SVG, slug + '.svg')
        qr.save(svg, kind='svg', dark=ESCURO, light=CLARO, border=2,
                scale=1, svgclass=None, lineclass=None, xmldecl=False)

        png = os.path.join(DIR_PNG, slug + '.png')
        qr.save(png, kind='png', dark=ESCURO, light=CLARO, border=3, scale=12)

        print('  %-12s %5.1f KB svg   %5.1f KB png   %s' % (
            slug,
            os.path.getsize(svg) / 1024.0,
            os.path.getsize(png) / 1024.0,
            url[:44] + ('...' if len(url) > 44 else '')))

    print('\n%d QR codes gerados.' % len(dados['parcerias']))


if __name__ == '__main__':
    main()
