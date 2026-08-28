# -*- coding: utf-8 -*-
"""Le as capturas de tela da Smiles e monta uma tabela de voos.

Sao mais de duzentas imagens por busca, entao abrir uma a uma e inviavel: o OCR
faz a leitura e este script reconhece os campos que interessam.

A primeira versao agrupava o texto pela ordem de leitura do OCR e nao funcionou:
o preco fica na ponta direita do card, longe do "2 paradas", e o casamento saia
errado. Milhas apareciam em 16 de 147 voos e havia duracao de 1h25 num voo
Navegantes a Nova York.

Esta versao usa a POSICAO de cada texto. Um card da Smiles e uma faixa
horizontal, entao tudo que esta na mesma altura pertence ao mesmo voo,
independente da ordem em que o OCR devolveu.

O que nao for lido com certeza fica como ?. Melhor campo vazio que numero
inventado, ainda mais em documento que vai para cliente.

    python propostas/ler_smiles.py propostas/boni_smiles/_ny
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# LGA entrou depois: o Jefferson tambem buscou LaGuardia e esses voos
# estavam sendo ignorados por falta do codigo aqui.
AEROPORTOS = r'(NVT|FLN|GRU|GIG|JFK|EWR|LGA|YYZ|CGH|POA|CWB|BSB|CNF)'
CIAS = (r'(Avianca|GOL|American Airlines|American|Air Canada|Copa|United|'
        r'Delta|Aerolineas|Air France|KLM|TAP|Iberia|LATAM)')

# O site mistura caixa alta e mista. Sai sempre no mesmo formato.
NOME_CIA = {
    'avianca': 'Avianca', 'gol': 'GOL', 'american airlines': 'American',
    'american': 'American', 'air canada': 'Air Canada', 'copa': 'Copa',
    'united': 'United', 'delta': 'Delta', 'latam': 'LATAM', 'tap': 'TAP',
    'iberia': 'Iberia', 'klm': 'KLM', 'air france': 'Air France',
    'aerolineas': 'Aerolineas',
}


def ler_com_posicao(pasta):
    """Devolve {imagem: [(texto, x, y), ...]} usando as caixas do OCR."""
    from rapidocr_onnxruntime import RapidOCR
    motor = RapidOCR()
    saida = {}
    arqs = sorted(f for f in os.listdir(pasta) if f.lower().endswith('.png'))
    for i, nome in enumerate(arqs, 1):
        res, _ = motor(os.path.join(pasta, nome))
        itens = []
        for caixa, texto, _conf in (res or []):
            xs = [p[0] for p in caixa]
            ys = [p[1] for p in caixa]
            itens.append([texto, sum(xs) / 4.0, sum(ys) / 4.0])
        saida[nome] = itens
        if i % 25 == 0:
            print('  lidas %d de %d' % (i, len(arqs)))
    return saida


def cabecalho(itens):
    """Rota, sentido e data: vem da barra escura no topo da pagina."""
    topo = ' | '.join(t for t, x, y in itens if y < 320)
    tudo = ' | '.join(t for t, x, y in itens)
    cab = {'sentido': '?', 'de': '?', 'para': '?', 'data': '?'}

    m = re.search(r'Passagens de (ida|volta)', topo, re.I)
    if m:
        cab['sentido'] = m.group(1).lower()
    # sem caixa: o OCR devolve NvT, JFk e variantes. Normaliza depois.
    m = re.search(AEROPORTOS + r'[^A-Za-z]{0,8}' + AEROPORTOS, topo, re.I)
    if m:
        cab['de'], cab['para'] = m.group(1).upper(), m.group(2).upper()
    cab['data'] = data_escolhida(itens, topo)
    return cab


DATA = (r'((?:Seg|Ter|Qua|Qui|Sex|Sab|Sáb|Dom),?\s*\d{1,2}\s*'
        r'(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez))')


def data_escolhida(itens, topo):
    """Qual data esta selecionada no carrossel.

    Nao serve pegar a primeira data que aparece: o carrossel mostra sete dias
    lado a lado e a primeira e sempre a da esquerda. Numa captura em que
    "Qua, 25 nov" estava escolhida, a leitura ingenua devolvia "Dom, 22 nov",
    tres dias errado num documento que vai para o cliente.

    A selecionada e a unica com o preco em milhas logo abaixo dela.
    """
    datas = [(t, x, y) for t, x, y in itens if re.search(DATA, t, re.I)]
    precos = [(t, x, y) for t, x, y in itens
              if re.search(r'\d{2,3}\.\d{3}\s*milhas', t, re.I)]

    for t, x, y in datas:
        for _pt, px, py in precos:
            # mesma coluna do carrossel e logo abaixo da data
            if abs(px - x) < 130 and 0 < py - y < 90:
                return re.sub(r'\s+', ' ', re.search(DATA, t, re.I).group(1))

    # sem carrossel na tela (recorte de card), tenta a barra do topo
    m = re.search(DATA, topo, re.I)
    return re.sub(r'\s+', ' ', m.group(1)) if m else '?'


def voos_da_tela(itens, tolerancia=42):
    """Um voo por faixa horizontal.

    A ancora e o texto de paradas ("2 paradas" ou "Direto"). Tudo que estiver
    na mesma altura, mais ou menos a tolerancia, e do mesmo card.
    """
    achados = []
    for texto, x, y in itens:
        t = texto.strip()
        m = re.match(r'^(\d+)\s*parada', t, re.I)
        direto = re.match(r'^(direto|sem escala)$', t, re.I)
        if not (m or direto):
            continue

        faixa = [it for it in itens if abs(it[2] - y) <= tolerancia]
        faixa.sort(key=lambda it: it[1])
        linha = ' '.join(it[0] for it in faixa)

        dur = re.search(r'(\d{1,2})h\s*(\d{2})?\s*min', linha)
        # o OCR costuma grudar tudo: "Apartirde86.800milhasporviajante"
        milhas = re.search(r'(\d{2,3}\.\d{3})\s*milhas', linha, re.I)
        if not milhas:
            milhas = re.search(r'partir\s*de\s*(\d{2,3}\.\d{3})', linha, re.I)
        # o site escreve "AMERICAN AIRLINES" em caixa alta e "Avianca" em
        # caixa mista, entao a comparacao ignora a caixa e o nome e normalizado
        cia = re.search(CIAS, linha, re.I)
        cabine = re.search(r'(Econômica|Economica|Executiva|Premium)', linha)
        horas = re.findall(r'\b(\d{2})h(\d{2})\b', linha)
        bagagem = re.search(r'\b(\d)\s*(?:mala|bagagem)', linha, re.I)
        # Varias capturas sao recorte de um card so, sem a barra do topo. Ai a
        # rota esta escrita dentro do proprio card: "GRU 00h05 -> JFK 12h00".
        # A rota fica uma linha abaixo do resto do card, fora da faixa estreita
        # usada para preco e duracao. Por isso ela tem a sua propria janela,
        # mais alta, olhando so para baixo: e onde o par de aeroportos aparece.
        abaixo = [it for it in itens if 0 <= it[2] - y <= 95]
        abaixo.sort(key=lambda it: it[1])
        linha_rota = ' '.join(it[0] for it in abaixo)
        rota = re.search(AEROPORTOS + r'\s*(\d{2})h(\d{2})[^A-Za-z]{0,10}'
                         + AEROPORTOS + r'\s*(\d{2})h(\d{2})', linha_rota, re.I)
        if not rota:
            rota = re.search(AEROPORTOS + r'\s*\d{2}h\d{2}[^A-Za-z]{0,10}'
                             + AEROPORTOS, linha_rota, re.I)

        achados.append({
            'y': int(y),
            'paradas': 0 if direto else int(m.group(1)),
            'duracao': ('%sh%s' % (dur.group(1), dur.group(2) or '00')) if dur else '?',
            'milhas': milhas.group(1) if milhas else '?',
            'cia': NOME_CIA.get(cia.group(1).lower(), cia.group(1)) if cia else '?',
            'cabine': cabine.group(1) if cabine else '?',
            # os horarios ficam colados na rota, na faixa de baixo
            'saida': ('%s:%s' % (rota.group(2), rota.group(3))
                      if rota and rota.lastindex and rota.lastindex >= 5 else
                      ('%s:%s' % horas[0] if len(horas) >= 1 else '?')),
            'chegada': ('%s:%s' % (rota.group(5), rota.group(6))
                        if rota and rota.lastindex and rota.lastindex >= 6 else
                        ('%s:%s' % horas[1] if len(horas) >= 2 else '?')),
            'bagagem': bagagem.group(1) if bagagem else '?',
            'de_card': rota.group(1).upper() if rota else '?',
            'para_card': (rota.group(4) if rota and rota.lastindex
                          and rota.lastindex >= 4 else
                          (rota.group(2) if rota else '?')).upper(),
        })

    # remove duplicatas da mesma faixa
    vistos, limpos = set(), []
    for v in sorted(achados, key=lambda a: a['y']):
        chave = (v['paradas'], v['duracao'], v['milhas'])
        if chave in vistos:
            continue
        vistos.add(chave)
        limpos.append(v)
    return limpos


def main():
    pasta = sys.argv[1] if len(sys.argv) > 1 else 'propostas/boni_smiles/_ny'
    cache = os.path.join(pasta, '_ocr_pos.json')

    if os.path.exists(cache):
        print('usando OCR ja feito: %s' % cache)
        bruto = json.load(io.open(cache, encoding='utf-8'))
    else:
        print('lendo as imagens com posicao (demora alguns minutos)...')
        bruto = ler_com_posicao(pasta)
        io.open(cache, 'w', encoding='utf-8').write(
            json.dumps(bruto, ensure_ascii=False))
        print('OCR salvo em %s' % cache)

    saida = []
    for nome in sorted(bruto):
        itens = bruto[nome]
        cab = cabecalho(itens)
        for v in voos_da_tela(itens):
            v.pop('y', None)
            linha = {'imagem': nome, **cab, **v}
            if linha['de'] == '?' and v['de_card'] != '?':
                linha['de'], linha['para'] = v['de_card'], v['para_card']
            v.pop('de_card', None); v.pop('para_card', None)
            linha.pop('de_card', None); linha.pop('para_card', None)
            saida.append(linha)

    destino = os.path.join(pasta, '_voos.json')
    io.open(destino, 'w', encoding='utf-8').write(
        json.dumps(saida, ensure_ascii=False, indent=1))

    print('\n%d voo(s) em %s' % (len(saida), destino))
    print('completude dos campos:')
    for campo in ['cia', 'duracao', 'milhas', 'saida', 'cabine']:
        ok = sum(1 for x in saida if x[campo] != '?')
        print('   %-9s %3d/%d' % (campo, ok, len(saida)))


if __name__ == '__main__':
    main()
