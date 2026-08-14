# -*- coding: utf-8 -*-
"""Confere se o sumario de cada ebook aponta para as paginas certas.

Existe porque os tres ebooks foram publicados com o sumario errado: o de
pontos, por exemplo, mandava o leitor para as paginas 05, 08, 12, 15, 18, 21,
24 e 27 num PDF que tem 13 paginas. Metade dos ponteiros caia fora do arquivo.

Isso acontece porque o numero da pagina e escrito na mao dentro de toc([...]),
enquanto a paginacao real so existe depois do build. Qualquer paragrafo a mais
desalinha tudo e nada reclama.

Uso:
    python ebooks/conferir_sumario.py            confere e lista divergencias
    python ebooks/conferir_sumario.py --corrigir reescreve os numeros no .py

Depois de --corrigir, rode o build de novo e confira mais uma vez: o proprio
ato de mudar "05" para "04" nao muda a paginacao, entao uma passada resolve.
"""
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
AQUI = os.path.dirname(os.path.abspath(__file__))

EBOOKS = [
    ('build_01.py', 'pdf/01-manual-pontos-2026.pdf'),
    ('build_02.py', 'pdf/02-roteiros-eua-europa-caribe.pdf'),
    ('build_03.py', 'pdf/03-planilhas-calculadoras.pdf'),
]


def simples(texto):
    """Minusculas, sem acento e sem pontuacao, para casar titulo com pagina."""
    t = unicodedata.normalize('NFKD', texto)
    t = ''.join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'[^a-z0-9 ]', ' ', t.lower()).strip()


def entradas_do_fonte(codigo):
    """Le os pares (titulo, pagina) de dentro da chamada toc([...])."""
    m = re.search(r'toc\(\[(.*?)\]\)', codigo, re.S)
    if not m:
        return None, None
    bloco = m.group(1)
    itens = re.findall(r"\(\s*'((?:[^'\\]|\\.)*)'\s*,\s*'(\d+)'\s*\)", bloco)
    return [(t.replace("\\'", "'"), p) for t, p in itens], m.span(1)


def aberturas(caminho_pdf):
    """As paginas de abertura de capitulo, na ordem, anotadas pelo build.

    O arquivo .paginas.json e escrito por EbookDoc.build a partir dos
    SectionMark. E a fonte confiavel: quem pagina o documento e o build.
    """
    lado = os.path.splitext(caminho_pdf)[0] + '.paginas.json'
    if not os.path.exists(lado):
        return None
    return json.load(io.open(lado, encoding='utf-8'))


def total_de_paginas(caminho_pdf):
    """Ultimo numero IMPRESSO, para comparar com o sumario na mesma escala.

    A capa nao e numerada, entao um PDF de 15 folhas termina na pagina 14.
    """
    import pymupdf
    return len(pymupdf.open(caminho_pdf)) - 1


def pagina_do_sumario(titulos, paginas):
    """Qual pagina e o proprio sumario.

    Ela cita todos os titulos, entao seria encontrada como resposta para cada
    um deles. E a pagina que contem o maior numero de titulos.
    """
    melhor, quantos = 0, 0
    for i, texto in enumerate(paginas):
        n = sum(1 for t in titulos if simples(t)[:24] in texto)
        if n > quantos:
            melhor, quantos = i, n
    return melhor if quantos >= 2 else -1


VAZIAS = {'de', 'do', 'da', 'dos', 'das', 'e', 'a', 'o', 'os', 'as', 'em', 'no',
          'na', 'para', 'por', 'com', 'que', 'seu', 'sua', 'um', 'uma', 'mais'}


def achar(titulo, paginas, a_partir_de):
    """Em que pagina, depois do sumario, esse titulo comeca.

    O rotulo do sumario nem sempre e igual ao titulo impresso na pagina:
    "Calculadora - Custo por milheiro" no sumario vira "Calculadora de custo
    por milheiro." no papel. Por isso vai afunilando: texto inteiro, comeco do
    texto e, por ultimo, a pagina que reune mais palavras distintivas dele.
    """
    alvo = simples(titulo)
    for t in ([alvo, alvo[:24]] if len(alvo) > 24 else [alvo]):
        for i in range(a_partir_de, len(paginas)):
            if t and t in paginas[i]:
                return i + 1

    palavras = [p for p in alvo.split() if len(p) > 3 and p not in VAZIAS]
    if not palavras:
        return None
    melhor, pontos = None, 0
    for i in range(a_partir_de, len(paginas)):
        n = sum(1 for p in palavras if p in paginas[i])
        if n > pontos:
            melhor, pontos = i + 1, n
    # exige maioria das palavras, senao e coincidencia
    return melhor if pontos >= max(2, len(palavras) // 2) else None


def main():
    corrigir = '--corrigir' in sys.argv
    problemas = 0

    for fonte, pdf in EBOOKS:
        caminho_fonte = os.path.join(AQUI, fonte)
        caminho_pdf = os.path.join(AQUI, pdf)
        if not os.path.exists(caminho_pdf):
            print('%s: PDF ainda nao construido, pulando' % fonte)
            continue

        codigo = io.open(caminho_fonte, encoding='utf-8').read()
        itens, span = entradas_do_fonte(codigo)
        if not itens:
            print('%s: sem chamada toc([...])' % fonte)
            continue

        total = total_de_paginas(caminho_pdf)
        marcas = aberturas(caminho_pdf)
        if marcas is None:
            print('%s: falta o .paginas.json, rode o build de novo' % fonte)
            continue

        print('=== %s (%d paginas, %d aberturas) ===' % (fonte, total, len(marcas)))
        if len(marcas) < len(itens):
            print('   ATENCAO: o sumario tem %d entradas e o documento tem %d '
                  'aberturas de capitulo.' % (len(itens), len(marcas)))
            problemas += 1

        novos = []
        for i, (titulo, escrito) in enumerate(itens):
            # sumario e capitulos estao na mesma ordem, entao a i-esima entrada
            # corresponde a i-esima abertura
            real = marcas[i]['pagina'] if i < len(marcas) else None
            if real is None:
                marca = 'sem abertura correspondente'
                novos.append((titulo, escrito))
                problemas += 1
            elif int(escrito) != real:
                fora = ' (fora do arquivo!)' if int(escrito) > total else ''
                marca = 'diz %s, esta na %d%s' % (escrito, real, fora)
                novos.append((titulo, '%02d' % real))
                problemas += 1
            else:
                marca = 'ok (%s)' % escrito
                novos.append((titulo, escrito))
            print('   %-50s %s' % (titulo[:50], marca))

        if corrigir and novos != itens:
            linhas = ',\n'.join(
                "    ('%s', '%s')" % (t.replace("'", "\\'"), p) for t, p in novos)
            codigo = codigo[:span[0]] + '\n' + linhas + ',\n' + codigo[span[1]:]
            io.open(caminho_fonte, 'w', encoding='utf-8', newline='').write(codigo)
            print('   -> numeros reescritos em %s' % fonte)
        print()

    if problemas and not corrigir:
        print('%d divergencia(s). Rode com --corrigir para acertar.' % problemas)
        return 1
    if problemas and corrigir:
        print('%d numero(s) corrigido(s). Rode o build e confira de novo.' % problemas)
        return 0
    print('Sumarios conferem com a paginacao real.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
