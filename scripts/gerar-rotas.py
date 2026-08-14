# -*- coding: utf-8 -*-
"""Gera os cards de emissoes reais do index.html a partir de dados/rotas.json.

Por que existe: aqueles cards eram HTML fixo com numeros inventados. Separando
o dado da apresentacao, editar uma emissao vira editar uma linha de JSON, e se
um dia entrar uma fonte automatica (parceria com seats.aero ou tripmilhas) ela
so precisa escrever o mesmo JSON: o HTML e o CSS ficam como estao.

A troca e feita entre dois marcadores por corte de string, nunca por regex.
Regex multilinha em HTML ja comeu o fechamento de uma tag neste projeto.

    python scripts/gerar-rotas.py
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON = os.path.join(RAIZ, 'dados', 'rotas.json')
HTML = os.path.join(RAIZ, 'index.html')

INICIO = '<!-- ROTAS:INICIO -->'
FIM = '<!-- ROTAS:FIM -->'

SETA = ('<svg viewBox="0 0 24 24" class="h-4 w-4 text-brand-orange" fill="none" '
        'stroke="currentColor" stroke-width="2"><path d="M2 12h20M14 5l7 7-7 7"/></svg>')

# A companhia dona de cada programa. Serve para o card so mencionar quem operou
# o voo quando for outra empresa: "Smiles - Executiva - voo Copa" ensina algo,
# "Smiles - Economica - voo Gol" e obvio e so ocupa espaco.
DONA = {
    'Latam Pass': 'Latam',
    'Smiles': 'Gol',
    'TudoAzul': 'Azul',
    'AAdvantage': 'American',
}


def milhar(n):
    """2600 -> '2.600'."""
    return '{:,}'.format(int(n)).replace(',', '.')


def reais(v):
    """1386.8 -> 'R$ 1.387'. Arredonda para real inteiro: a precisao de
    centavos seria falsa, porque o milheiro ja e uma media."""
    return 'R$ ' + milhar(round(v))


def custo(e, milheiro):
    """Custo por pessoa. Retorna (texto, tem_taxa)."""
    tabela = e['programa']
    if tabela not in milheiro:
        raise SystemExit('Programa sem milheiro definido: %s' % tabela)
    das_milhas = e['milhas'] / 1000.0 * milheiro[tabela]
    if e.get('taxas') is None:
        return ('Só em milhas, cerca de <strong>%s</strong>' % reais(das_milhas), False)
    return ('Custou cerca de <strong>%s</strong>' % reais(das_milhas + e['taxas']), True)


def card(e, milheiro):
    texto, _ = custo(e, milheiro)
    escopo = 'No Brasil' if e['escopo'] == 'nacional' else 'Internacional'
    nota = ''
    if e.get('nota'):
        nota = '\n          <p class="flight-nota">%s</p>' % e['nota']

    linha = '%s · %s' % (e['programa'], e['cabine'])
    operou = e.get('companhia')
    if operou and operou != DONA.get(e['programa']):
        linha += ' · voo %s' % operou
    return (
        '        <article class="reveal flight-card">\n'
        '          <div class="flight-escopo">%s</div>\n'
        '          <div class="flight-route"><span>%s</span>%s<span>%s</span></div>\n'
        '          <div class="flight-price">%s <span class="flight-unit">milhas</span></div>\n'
        '          <div class="flight-cost">%s por pessoa</div>\n'
        '          <div class="flight-info"><span>%s</span><span>%s</span></div>%s\n'
        '        </article>'
    ) % (escopo, e['origem'], SETA, e['destino'], milhar(e['milhas']),
         texto, linha, e['quando'], nota)


def main():
    dados = json.load(io.open(JSON, encoding='utf-8'))
    milheiro = {k: v for k, v in dados['milheiro'].items() if not k.startswith('_')}
    emissoes = dados['emissoes']

    # Nacionais primeiro; dentro de cada grupo, preserva a ordem do arquivo,
    # que e a ordem em que o Jefferson quer que aparecam.
    emissoes = ([e for e in emissoes if e['escopo'] == 'nacional'] +
                [e for e in emissoes if e['escopo'] != 'nacional'])

    blocos = '\n\n'.join(card(e, milheiro) for e in emissoes)
    novo = '%s\n%s\n        %s' % (INICIO, blocos, FIM)

    html = io.open(HTML, encoding='utf-8').read()
    if html.count(INICIO) != 1 or html.count(FIM) != 1:
        raise SystemExit('Marcadores ROTAS ausentes ou duplicados em index.html')

    antes, resto = html.split(INICIO, 1)
    _, depois = resto.split(FIM, 1)
    io.open(HTML, 'w', encoding='utf-8', newline='').write(antes + novo + depois)

    n_nac = sum(1 for e in emissoes if e['escopo'] == 'nacional')
    print('%d cards gravados (%d no Brasil, %d internacionais)'
          % (len(emissoes), n_nac, len(emissoes) - n_nac))
    for e in emissoes:
        texto, tem_taxa = custo(e, milheiro)
        limpo = texto.replace('<strong>', '').replace('</strong>', '')
        print('  %s-%s  %9s milhas  %-34s %s' % (
            e['origem'], e['destino'], milhar(e['milhas']), limpo,
            '' if tem_taxa else '(taxa nao informada)'))


if __name__ == '__main__':
    main()
