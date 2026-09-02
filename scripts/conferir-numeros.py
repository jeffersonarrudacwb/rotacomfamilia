# -*- coding: utf-8 -*-
"""Confere se os numeros batem nos tres lugares que os mostram.

    python scripts/conferir-numeros.py

Sai com codigo 1 se algum divergir, entao serve de trava no GitHub.

O gatilho "Atualizar Midia Kit" troca os tres de uma vez, mas nada impede
alguem de editar um JSON na mao e esquecer o outro. O estrago desse esquecimento
nao aparece no site: aparece quando a marca baixa o PDF, compara com a pagina e
encontra dois numeros diferentes para a mesma coisa. Depois disso nenhum dos
dois numeros vale nada para ela.

Confere:
  1. cada metrica de dados/numeros-redes.json contra o que mediakit.html mostra
  2. cada numero de mediakit/mediakit.json contra o texto do PDF gerado
  3. a data do carimbo da pagina contra a data da nota do PDF
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

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REDES = os.path.join(RAIZ, 'dados', 'numeros-redes.json')
KIT = os.path.join(RAIZ, 'mediakit', 'mediakit.json')
PAGINA = os.path.join(RAIZ, 'mediakit.html')
PDF = os.path.join(RAIZ, 'mediakit', 'midia-kit-rota-com-familia.pdf')

# No GitHub o passo imprime isto e a aba de execucao mostra em vermelho.
NO_GITHUB = bool(os.environ.get('GITHUB_ACTIONS'))


def erro(msg):
    print(('::error::' if NO_GITHUB else 'ERRO: ') + msg)


def milhar(n):
    return '{:,}'.format(int(n)).replace(',', '.')


def main():
    redes = json.load(io.open(REDES, encoding='utf-8'))
    kit = json.load(io.open(KIT, encoding='utf-8'))
    html = io.open(PAGINA, encoding='utf-8').read()
    problemas = 0
    conferidos = 0

    # 1. JSON das redes  x  numeros escritos na pagina
    for rede, dados in redes['redes'].items():
        for m in dados.get('metricas', []):
            if m.get('valor') is None:
                continue
            chave = '%s.%s' % (rede, m['chave'])
            esperado = milhar(m['valor'])
            for atributo in ('data-metrica', 'data-rede-metrica'):
                achou = re.search(
                    r'%s="%s">([\d.]+)' % (atributo, re.escape(chave)), html)
                if not achou:
                    continue          # nem toda metrica aparece nos dois lugares
                conferidos += 1
                if achou.group(1) != esperado:
                    erro('%s: a pagina mostra %s e o JSON diz %s (%s)'
                         % (chave, achou.group(1), esperado, atributo))
                    problemas += 1

    # 2. numeros do mediakit.json  x  texto dentro do PDF
    if os.path.exists(PDF):
        import pymupdf
        texto = re.sub(r'\s+', ' ',
                       ''.join(p.get_text() for p in pymupdf.open(PDF)))
        for n in kit.get('numeros', []):
            conferidos += 1
            if n['numero'] not in texto:
                erro('o numero "%s" (%s) nao aparece no PDF gerado'
                     % (n['numero'], n['rotulo']))
                problemas += 1

        # 3. a data escrita nos dois documentos
        na_pagina = re.search(r'Números conferidos em ([^.]+)', html)
        no_pdf = re.search(r'conferidos em ([^,.]+)', texto)
        if na_pagina and no_pdf:
            conferidos += 1
            if na_pagina.group(1).strip() != no_pdf.group(1).strip():
                erro('a data diverge: pagina diz "%s", PDF diz "%s"'
                     % (na_pagina.group(1).strip(), no_pdf.group(1).strip()))
                problemas += 1
    else:
        print('AVISO: o PDF nao existe ainda; conferi so a pagina.')

    print('')
    if problemas:
        print('%d divergencia(s) em %d conferencias.' % (problemas, conferidos))
        return 1
    print('%d conferencias, tudo batendo.' % conferidos)
    print('  dados/numeros-redes.json  =  mediakit.html  =  mediakit.json  =  PDF')
    return 0


if __name__ == '__main__':
    sys.exit(main())
