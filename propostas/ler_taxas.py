# -*- coding: utf-8 -*-
"""Le as telas de pagamento da Smiles e extrai a taxa de embarque.

A lista de resultados mostra so as milhas. A taxa em reais aparece uma tela
depois, no resumo do pedido, junto do rotulo "Taxa de embarque".

Este script procura essas telas e casa tres numeros: milhas do pedido, taxa em
reais e quantos viajantes. Sem os tres, a linha nao serve: taxa de 1 pessoa
apresentada como se fosse de 3 seria um erro grosseiro num documento de
cliente.

    python propostas/ler_taxas.py propostas/boni_smiles/_ny
"""
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

REAIS = r'R\$\s*([\d]{1,3}(?:\.[\d]{3})*,[\d]{2})'
MILHAS = r'([\d]{2,3}(?:\.[\d]{3})+)\s*milhas'


def para_float(t):
    return float(t.replace('.', '').replace(',', '.'))


def perto(itens, alvo_y, alvo_x=None, janela=60, largura=None):
    """Textos na mesma faixa horizontal do rotulo."""
    saida = []
    for t, x, y in itens:
        if abs(y - alvo_y) > janela:
            continue
        if largura is not None and alvo_x is not None and abs(x - alvo_x) > largura:
            continue
        saida.append((t, x, y))
    return sorted(saida, key=lambda i: i[1])


def ler_tela(itens):
    """Devolve {milhas, taxa, viajantes} se a tela for um resumo de pedido."""
    tudo = ' '.join(t for t, x, y in itens)
    if not re.search(r'Taxa de embarque', tudo, re.I):
        return None

    dado = {'milhas': None, 'taxa': None, 'viajantes': None}

    # a taxa fica na mesma faixa do rotulo "Taxa de embarque"
    for t, x, y in itens:
        if not re.search(r'^Taxa de embarque', t.strip(), re.I):
            continue
        faixa = perto(itens, y, janela=45)
        linha = ' '.join(i[0] for i in faixa)
        m = re.search(REAIS, linha)
        if m:
            dado['taxa'] = para_float(m.group(1))
        v = re.search(r'(\d+)\s*(?:pessoa|viajante|adulto)', linha, re.I)
        if v:
            dado['viajantes'] = int(v.group(1))
        break

    # milhas: a linha do "Total" e a mais confiavel; senao, "Passagens"
    for rotulo in (r'^Total$', r'^Passagens$'):
        if dado['milhas']:
            break
        for t, x, y in itens:
            if not re.search(rotulo, t.strip(), re.I):
                continue
            linha = ' '.join(i[0] for i in perto(itens, y, janela=45))
            m = re.search(MILHAS, linha)
            if m:
                dado['milhas'] = m.group(1)
            if dado['viajantes'] is None:
                v = re.search(r'(\d+)\s*(?:pessoa|viajante|adulto)', linha, re.I)
                if v:
                    dado['viajantes'] = int(v.group(1))
            break

    # rota e data, quando a barra do topo esta na captura
    m = re.search(r'\b(NVT|FLN|GRU|GIG|JFK|EWR|LGA)\b[^A-Za-z]{0,8}'
                  r'\b(NVT|FLN|GRU|GIG|JFK|EWR|LGA)\b', tudo)
    if m:
        dado['de'], dado['para'] = m.group(1), m.group(2)
    m = re.search(r'((?:Seg|Ter|Qua|Qui|Sex|Sab|Sáb|Dom),?\s*\d{1,2}\s*'
                  r'(?:nov|dez|out))', tudo, re.I)
    if m:
        dado['data'] = re.sub(r'\s+', ' ', m.group(1))
    return dado


def main():
    pasta = sys.argv[1] if len(sys.argv) > 1 else 'propostas/boni_smiles/_ny'
    o = json.load(io.open(os.path.join(pasta, '_ocr_pos.json'), encoding='utf-8'))

    achados = []
    for nome in sorted(o):
        d = ler_tela(o[nome])
        if d and d['taxa']:
            d['imagem'] = nome
            achados.append(d)

    destino = os.path.join(pasta, '_taxas.json')
    io.open(destino, 'w', encoding='utf-8').write(
        json.dumps(achados, ensure_ascii=False, indent=1))

    print('%d tela(s) de pagamento com taxa:\n' % len(achados))
    print('  %-13s %-9s %-11s %-5s %-11s %s' % (
        'imagem', 'rota', 'milhas', 'pax', 'taxa R$', 'taxa/pax'))
    for d in achados:
        pax = d.get('viajantes') or 1
        print('  %-13s %-9s %-11s %-5s %-11s %s' % (
            d['imagem'],
            '%s-%s' % (d.get('de', '?'), d.get('para', '?')),
            d['milhas'] or '?', pax,
            ('%.2f' % d['taxa']).replace('.', ','),
            ('%.2f' % (d['taxa'] / pax)).replace('.', ',')))
    print('\ngravado em %s' % destino)


if __name__ == '__main__':
    main()
