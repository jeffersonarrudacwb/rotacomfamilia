# -*- coding: utf-8 -*-
"""Atualiza os numeros das redes nos dois lugares que os mostram.

    python scripts/atualizar-numeros.py --instagram-seguidores 2350
    python scripts/atualizar-numeros.py --youtube-inscritos 2100 --teste

E o que o gatilho "Atualizar Midia Kit" do GitHub chama. Tambem roda na mao.

POR QUE ESTE SCRIPT EXISTE

Os mesmos numeros vivem em dois arquivos:

    dados/numeros-redes.json   a pagina mediakit.html
    mediakit/mediakit.json     o PDF que a pagina oferece para baixar

Editar so um e o erro facil de cometer, e o pior de perceber: a pagina diz
"os mesmos numeros" no botao de download, entao a marca baixa o PDF e encontra
outro valor. Aqui os dois mudam juntos ou nenhum muda.

O QUE NAO PASSA POR AQUI

Numero que nao esta na lista abaixo continua sendo editado a mao no JSON. Isto
aqui cobre o que muda sozinho com o tempo — seguidor, inscrito, video, hora de
exibicao. Texto, foto e formato de parceria mudam por decisao, nao por prazo.
"""
import argparse
import collections
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

MESES = ['janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho', 'julho',
         'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
MESES_ACENTO = {'marco': 'março'}

# (argumento, rede, chave na metrica, rotulo dentro do mediakit.json)
#
# O casamento com o PDF e pelo ROTULO, e nao pela posicao na lista. Posicao
# quebra em silencio no dia em que alguem reordenar os quatro numeros; rotulo
# quebra com aviso, que e o que se quer.
CAMPOS = [
    ('instagram_seguidores',  'instagram', 'seguidores',  'seguidores no Instagram'),
    ('instagram_publicacoes', 'instagram', 'publicacoes', None),
    ('youtube_inscritos',     'youtube',   'inscritos',   'inscritos no YouTube'),
    ('youtube_videos',        'youtube',   'videos',      'vídeos publicados'),
    ('youtube_horas',         'youtube',   'horas',       'horas assistidas'),
    ('tiktok_seguidores',     'tiktok',    'seguidores',  None),
]


def ler(caminho):
    return json.load(io.open(caminho, encoding='utf-8'),
                     object_pairs_hook=collections.OrderedDict)


def gravar(caminho, dados):
    io.open(caminho, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(dados, ensure_ascii=False, indent=2) + '\n')


def milhar(n):
    """1950 -> '1.950'. O separador do Brasil e o ponto."""
    return '{:,}'.format(int(n)).replace(',', '.')


def por_extenso(data):
    """'2026-09-01' -> '1º de setembro de 2026'."""
    a, m, d = (int(x) for x in data.split('-'))
    mes = MESES[m - 1]
    mes = MESES_ACENTO.get(mes, mes)
    return '%s de %s de %d' % ('1º' if d == 1 else str(d), mes, a)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    for arg, _, _, _ in CAMPOS:
        p.add_argument('--' + arg.replace('_', '-'), type=int, default=None)
    p.add_argument('--data', default=None,
                   help='AAAA-MM-DD da conferencia. Padrao: hoje.')
    p.add_argument('--teste', action='store_true',
                   help='Mostra o que mudaria e nao grava nada.')
    a = p.parse_args()

    pedidos = {arg: getattr(a, arg) for arg, _, _, _ in CAMPOS
               if getattr(a, arg) is not None}
    if not pedidos:
        print('Nenhum numero informado. Nada a fazer.')
        print('Veja os disponiveis com --help.')
        return 0

    if a.data:
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', a.data):
            print('ERRO: --data precisa ser AAAA-MM-DD, veio "%s".' % a.data)
            return 1
        data = a.data
    else:
        # datetime so aqui: o resto do script nao depende de relogio.
        import datetime
        data = datetime.date.today().isoformat()

    redes, kit = ler(REDES), ler(KIT)
    mudancas = []

    for arg, rede, chave, rotulo in CAMPOS:
        if arg not in pedidos:
            continue
        novo = pedidos[arg]

        metricas = redes['redes'][rede]['metricas']
        alvo = next((m for m in metricas if m.get('chave') == chave), None)
        if alvo is None:
            print('ERRO: nao achei a metrica "%s" da rede "%s" em %s'
                  % (chave, rede, os.path.basename(REDES)))
            return 1

        antes = alvo.get('valor')
        alvo['valor'] = novo
        redes['redes'][rede]['verificado_em'] = data

        # O PDF: casa pelo rotulo e preserva o sufixo que ja estava la, para
        # "2.900+" nao virar "3.100" e perder o mais.
        no_pdf = '(so na pagina)'
        if rotulo:
            item = next((n for n in kit['numeros']
                         if n.get('rotulo') == rotulo), None)
            if item is None:
                print('ERRO: nao achei o rotulo "%s" em %s.\n'
                      '      Alguem renomeou o numero no PDF; ajuste o CAMPOS '
                      'deste script.' % (rotulo, os.path.basename(KIT)))
                return 1
            sufixo = re.sub(r'[\d.\s]', '', item.get('numero', ''))
            item['numero'] = milhar(novo) + sufixo
            no_pdf = item['numero']

        mudancas.append((rede, chave, antes, novo, no_pdf))

    redes['atualizado_em'] = data

    # A nota do PDF carrega a data da conferencia por escrito. Troca so ela,
    # e avisa se a frase mudou de forma — melhor um aviso do que uma data
    # velha embaixo de numeros novos.
    nota = kit.get('numeros_nota', '')
    nova_nota, trocas = re.subn(
        r'(conferidos em )[^,.]+', r'\g<1>' + por_extenso(data), nota, count=1)
    if trocas:
        kit['numeros_nota'] = nova_nota
    else:
        print('AVISO: nao achei "conferidos em ..." na nota do PDF.')
        print('       A data dentro do texto continua a antiga; ajuste a mao.')

    print('Data da conferencia: %s' % por_extenso(data))
    print('')
    print('rede       metrica            antes    depois')
    for rede, chave, antes, novo, no_pdf in mudancas:
        seta = '=' if antes == novo else '->'
        print('  %-10s %-13s %8s %s %-8s   PDF: %s'
              % (rede, chave, antes, seta, novo, no_pdf))
    print('')

    if a.teste:
        print('MODO TESTE: nada foi gravado.')
        return 0

    gravar(REDES, redes)
    gravar(KIT, kit)
    print('Gravados:')
    print('  dados/numeros-redes.json')
    print('  mediakit/mediakit.json')
    print('')
    print('Falta regerar o PDF:  python mediakit/build_mediakit.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
