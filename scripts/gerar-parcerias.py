# -*- coding: utf-8 -*-
"""Escreve o HTML das parcerias a partir de dados/parcerias.json.

Mexe em dois lugares, sempre entre marcadores:

  parcerias.html  os cards completos, com QR code e contexto de uso
  index.html      a chamada curta que leva para la

Nao ha template externo: o HTML e montado aqui e injetado entre
PARCERIAS:INICIO e PARCERIAS:FIM. Substituicao por split, nao por regex, que
ja quebrou HTML neste projeto uma vez.

    python scripts/gerar-parcerias.py
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)

INICIO = '<!-- PARCERIAS:INICIO -->'
FIM = '<!-- PARCERIAS:FIM -->'


def escapar(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def svg_do_qr(slug):
    """Le o SVG gerado pelo gerar-qrcodes.py para embutir inline.

    Inline em vez de <img src>: sao 2 KB, poupam uma requisicao e o QR aparece
    junto com o resto da pagina, sem piscar.
    """
    caminho = os.path.join('assets', 'qr', slug + '.svg')
    if not os.path.exists(caminho):
        return '<p class="parceria-qr-falta">QR code ainda nao gerado.</p>'
    svg = io.open(caminho, encoding='utf-8').read().strip()
    # o SVG do segno nao traz papel de acessibilidade; sem isso, leitor de tela
    # anuncia um grafico sem nome
    svg = svg.replace('<svg', '<svg role="img" aria-label="QR code do link"', 1)
    return svg


def logo_do_parceiro(p):
    """Marca visual do parceiro, tirada do site do proprio parceiro.

    Procura assets/logos/<slug> em svg, png ou webp, nessa ordem. Se nao achar
    nenhum, cai para um selo com a inicial nas cores da casa, que e melhor do
    que desenhar de memoria a marca de outra empresa e errar.

    A placa tem altura fixa e largura livre porque nem toda marca existe em
    formato quadrado. Wise e Nomad publicam um simbolo quadrado; a HolaSim so
    tem o nome escrito, e forcar isso num quadrado deixaria a palavra do
    tamanho de uma formiga.
    """
    base = os.path.join('assets', 'logos', p['slug'])
    for ext in ('.svg', '.png', '.webp'):
        if os.path.exists(base + ext):
            alt = 'Logo %s' % p['nome']
            if ext == '.svg':
                svg = io.open(base + ext, encoding='utf-8').read().strip()
                svg = svg.replace('<svg', '<svg role="img" aria-hidden="true"', 1)
                corpo = svg
            else:
                # sem loading=lazy de proposito: sao tres arquivos de 6 a 10 KB
                # e sao a identidade visual do card. Adiar isso nao economiza
                # nada relevante e ainda deixa o logo aparecer depois do resto.
                corpo = ('<img src="%s%s" alt="%s" width="%d" height="%d" '
                         'decoding="async" />'
                         % (base.replace(os.sep, '/'), ext, escapar(alt),
                            *dimensoes(base + ext)))
            return '<span class="parceria-logo parceria-logo-real">%s</span>' % corpo
    inicial = escapar(p['nome'][:1].upper())
    return ('<span class="parceria-logo parceria-logo-letra" aria-hidden="true">'
            '%s</span>' % inicial)


def dimensoes(caminho):
    """Largura e altura reais do arquivo, para o HTML reservar o espaco certo.

    Sem isso a pagina pula quando o logo carrega.
    """
    try:
        from PIL import Image
        with Image.open(caminho) as im:
            return im.size
    except Exception:
        return (46, 46)


def card(p):
    cupom = ''
    if p.get('cupom'):
        cupom = (
            '\n          <div class="parceria-cupom">'
            '<span class="parceria-cupom-rot">Cupom</span>'
            '<code data-copiar="%s">%s</code></div>'
        ) % (escapar(p['cupom']), escapar(p['cupom']))

    validade = p.get('validade')
    aviso = ('Oferta do parceiro, pode mudar sem aviso.' if not validade
             else 'Válido até %s, segundo o parceiro.' % escapar(validade))

    return (
        '\n        <article class="parceria-card">'
        '\n          <div class="parceria-topo">'
        '\n            %(logo)s'
        '\n            <div>'
        '\n              <span class="parceria-cat">%(cat)s</span>'
        '\n              <h3 class="parceria-nome">%(nome)s</h3>'
        '\n            </div>'
        '\n          </div>'
        '\n          <p class="parceria-beneficio">%(beneficio)s</p>%(cupom)s'
        '\n          <p class="parceria-porque">%(porque)s</p>'
        '\n          <p class="parceria-quando"><strong>Quando usar:</strong> %(quando)s</p>'
        '\n          <a class="parceria-btn" href="%(url)s" target="_blank" rel="noopener sponsored"'
        ' data-parceiro="%(slug)s">Abrir o %(nome)s</a>'
        '\n          <details class="parceria-qr" open>'
        '\n            <summary>Ver QR code</summary>'
        '\n            <div class="parceria-qr-img">%(qr)s</div>'
        '\n            <p class="parceria-qr-nota">Aponte a câmera do celular para abrir sem digitar.</p>'
        '\n          </details>'
        '\n          <p class="parceria-validade">%(aviso)s</p>'
        '\n        </article>'
    ) % {
        'cat': escapar(p['categoria']), 'nome': escapar(p['nome']),
        'beneficio': escapar(p['beneficio']), 'cupom': cupom,
        'porque': escapar(p['porque']), 'quando': escapar(p['quando']),
        'url': escapar(p['url']), 'slug': escapar(p['slug']),
        'qr': svg_do_qr(p['slug']), 'aviso': aviso,
        'logo': logo_do_parceiro(p),
    }


def bloco_pagina(parcerias):
    return ('\n      <div class="parcerias-grid">%s\n      </div>\n      '
            % ''.join(card(p) for p in parcerias))


def bloco_home(parcerias):
    """Versao curta para o index: nome, categoria e beneficio em uma linha."""
    itens = ''.join(
        '\n          <li class="parceria-mini">'
        '\n            %s'
        '\n            <span class="parceria-mini-nome">%s</span>'
        '\n            <span class="parceria-mini-cat">%s</span>'
        '\n            <span class="parceria-mini-ben">%s</span>'
        '\n          </li>' % (logo_do_parceiro(p), escapar(p['nome']),
                               escapar(p['categoria']), escapar(p['beneficio']))
        for p in parcerias)
    return '\n        <ul class="parcerias-mini">%s\n        </ul>\n      ' % itens


def injetar(arquivo, bloco):
    if not os.path.exists(arquivo):
        print('  AUSENTE: %s' % arquivo)
        return False
    s = io.open(arquivo, encoding='utf-8').read()
    if INICIO not in s or FIM not in s:
        print('  SEM MARCADORES: %s' % arquivo)
        return False
    antes, resto = s.split(INICIO, 1)
    _, depois = resto.split(FIM, 1)
    novo = antes + INICIO + bloco + FIM + depois
    io.open(arquivo, 'w', encoding='utf-8', newline='').write(novo)
    return True


def main():
    d = json.load(io.open(os.path.join('dados', 'parcerias.json'),
                          encoding='utf-8'))
    ps = d['parcerias']
    ok1 = injetar('parcerias.html', bloco_pagina(ps))
    ok2 = injetar('index.html', bloco_home(ps))
    print('%d parceria(s) escritas em %s' % (
        len(ps), ', '.join(n for n, ok in
                           [('parcerias.html', ok1), ('index.html', ok2)] if ok)))
    for p in ps:
        print('  %-10s %-26s cupom: %s' % (
            p['slug'], p['categoria'], p.get('cupom') or '(sem)'))


if __name__ == '__main__':
    main()
