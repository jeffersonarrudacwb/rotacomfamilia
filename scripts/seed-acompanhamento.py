# -*- coding: utf-8 -*-
"""Gera o SQL que carrega um planejamento na area de acompanhamento.

    python scripts/seed-acompanhamento.py boni --pimenta <64 hex>

Le dois arquivos e escreve um:

    propostas/dados/boni-atracoes.json     cidades e atracoes (curadoria)
    propostas/dados/boni-conferencia.json  os voos, fonte autoritativa
    ->  sql/seed-boni.sql

POR QUE ISTO EXISTE, E NAO UMA TELA DE ADMINISTRACAO

Foi decisao: a area do cliente nao tem login, e uma tela de cadastro exigiria
autenticacao de verdade so para mim usar. Enquanto for um punhado de clientes,
gerar SQL e carregar no phpMyAdmin e menos superficie de ataque e menos codigo.

O CODIGO E IMPRESSO UMA VEZ SO

O banco guarda apenas o hash com pimenta. Este script mostra o codigo em claro
na tela, uma unica vez, e nao o escreve em lugar nenhum: nem no SQL, nem em
arquivo, nem no log. Copie na hora e mande para o cliente. Se perder, gere
outro e revogue o antigo -- nao ha como recuperar.

A PIMENTA precisa ser a MESMA que esta no rota-config.php do servidor. Se as
duas divergirem, o hash gerado aqui nunca vai casar com o que o PHP calcula, e
o codigo simplesmente nao abre.
"""
import argparse
import collections
import datetime
import hashlib
import io
import json
import os
import re
import secrets
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, 'propostas', 'dados')
SAIDA = os.path.join(RAIZ, 'sql')

# Crockford base32 sem I, L, O e U. 32 simbolos, 10 posicoes = 50 bits.
# O mesmo alfabeto da constante RCF_ALFABETO no api/acompanhamento.php: se um
# mudar, o outro tem que mudar junto.
ALFABETO = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
TAM = 10

SEMANA = {0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex', 5: 'Sab', 6: 'Dom'}


def gerar_codigo():
    """Dez simbolos de random_bytes, sem vies.

    256 / 32 = 8 exatamente, entao ord(byte) % 32 e uniforme e nao precisa de
    reamostragem. Isto esta escrito porque a proxima pessoa vai olhar o "% 32"
    e querer "consertar" para alguma coisa enviesada.

    secrets e nao random: o modulo random e previsivel a partir do estado, e
    aqui o numero E a senha.
    """
    return ''.join(ALFABETO[b % 32] for b in secrets.token_bytes(TAM))


def hash_codigo(codigo, pimenta):
    """Igual ao do PHP: hash('sha256', $pimenta . '|codigo|' . $codigo, true)."""
    return hashlib.sha256(
        (pimenta + '|codigo|' + codigo).encode('utf-8')).hexdigest()


def sq(valor):
    """Um literal de texto para o MySQL, ou NULL.

    Dobra a aspa simples em vez de usar barra invertida, porque o dobramento
    vale nos dois modos do servidor e a barra quebra sob NO_BACKSLASH_ESCAPES.
    E recusa barra invertida no conteudo em vez de tentar escapar: a curadoria
    nao tem nenhuma, e adivinhar aqui e como se escreve um furo de injecao.
    """
    if valor is None or valor == '':
        return 'NULL'
    texto = str(valor)
    if '\\' in texto:
        raise SystemExit(
            'ERRO: barra invertida no texto, e este gerador nao escapa isso.\n'
            'Tire a barra do JSON:\n  %s' % texto[:120])
    if '\x00' in texto:
        raise SystemExit('ERRO: byte nulo no texto.')
    return "'" + texto.replace("'", "''") + "'"


def data_hora(marca, ano_base):
    """'Seg 23/11 01h30' -> ('2026-11-23 01:30:00', 'Seg').

    Devolve tambem o dia da semana escrito, para poder conferir contra o
    calendario. O boni-roteiro.json ja envelheceu exatamente assim: a data
    mudou e o dia da semana ficou para tras.
    """
    m = re.match(r'^(\w{3})\s+(\d{2})/(\d{2})\s+(\d{2})h(\d{2})$', marca.strip())
    if not m:
        raise SystemExit('ERRO: nao entendi a data "%s"' % marca)
    dia_semana, dia, mes, hora, minuto = m.groups()
    mes_i = int(mes)
    # A viagem comeca em novembro e termina em dezembro do mesmo ano. Mes menor
    # que o de partida quer dizer que virou o ano.
    ano = ano_base if mes_i >= 11 else ano_base + 1
    return ('%04d-%02d-%02d %s:%s:00' % (ano, mes_i, int(dia), hora, minuto),
            dia_semana, datetime.date(ano, mes_i, int(dia)))


def minutos(dur):
    """'07h09' -> 429."""
    m = re.match(r'^(\d+)h(\d+)$', dur.strip())
    if not m:
        return None
    return int(m.group(1)) * 60 + int(m.group(2))


def montar_voos(conf, ano_base):
    """As linhas de rcf_voo, a partir do voos_linhas da conferencia."""
    vaos = set(conf.get('voos_vaos') or [])
    linhas, avisos = [], []

    for i, l in enumerate(conf['voos_linhas']):
        if i in vaos:
            # Linha de conexao: o texto inteiro vem na segunda celula.
            linhas.append({
                'ordem': i + 1, 'tipo': 'conexao', 'bilhete': None,
                'companhia': None, 'numero': None, 'origem': None,
                'destino': None, 'partida': None, 'chegada': None,
                'duracao': None, 'observacao': l[1],
            })
            continue

        bilhete = int(l[0]) if str(l[0]).strip().isdigit() else None
        voo = str(l[1]).strip()
        # 'Air Canada 8873' -> ('Air Canada', '8873')
        p = voo.rsplit(' ', 1)
        companhia, numero = (p[0], p[1]) if len(p) == 2 and p[1].isdigit() else (voo, None)

        trecho = re.split(r'\s*(?:→|->)\s*', str(l[2]))
        origem = trecho[0].strip() if len(trecho) == 2 else None
        destino = trecho[1].strip() if len(trecho) == 2 else None

        partida, ds_p, d_p = data_hora(l[3], ano_base)
        chegada, ds_c, d_c = data_hora(l[4], ano_base)

        # Confere o dia da semana escrito contra o calendario de verdade.
        for marca, escrito, data in ((l[3], ds_p, d_p), (l[4], ds_c, d_c)):
            real = SEMANA[data.weekday()]
            if real.lower()[:3] != escrito.lower()[:3]:
                avisos.append('  "%s": o calendario diz %s' % (marca, real))

        linhas.append({
            'ordem': i + 1, 'tipo': 'voo', 'bilhete': bilhete,
            'companhia': companhia, 'numero': numero,
            'origem': origem, 'destino': destino,
            'partida': partida, 'chegada': chegada,
            'duracao': minutos(l[5]), 'observacao': None,
        })

    return linhas, avisos


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug', help='ex: boni')
    p.add_argument('--pimenta', required=True,
                   help='a MESMA do rota-config.php do servidor')
    p.add_argument('--codigo', default=None,
                   help='reaproveita um codigo ja entregue, em vez de gerar')
    a = p.parse_args()

    if len(a.pimenta) < 32:
        raise SystemExit('ERRO: a pimenta parece curta demais. Use os 64 '
                         'caracteres hexadecimais do rota-config.php.')

    caminho_atr = os.path.join(DADOS, '%s-atracoes.json' % a.slug)
    caminho_conf = os.path.join(DADOS, '%s-conferencia.json' % a.slug)
    for c in (caminho_atr, caminho_conf):
        if not os.path.exists(c):
            raise SystemExit('ERRO: nao achei %s' % c)

    d = json.load(io.open(caminho_atr, encoding='utf-8'),
                  object_pairs_hook=collections.OrderedDict)
    conf = json.load(io.open(caminho_conf, encoding='utf-8'),
                     object_pairs_hook=collections.OrderedDict)

    ano_base = int(d['data_inicio'][:4])
    voos, avisos = montar_voos(conf, ano_base)

    codigo = (a.codigo or gerar_codigo()).upper()
    if len(codigo) != TAM or any(c not in ALFABETO for c in codigo):
        raise SystemExit('ERRO: o codigo precisa ter %d simbolos do alfabeto '
                         '%s' % (TAM, ALFABETO))
    hash_hex = hash_codigo(codigo, a.pimenta)

    # A viagem acaba, mas a linha nao pode ficar aberta para sempre.
    fim = datetime.date(*[int(x) for x in d['data_fim'].split('-')])
    expira = fim + datetime.timedelta(days=90)

    L = []
    w = L.append
    w('-- ' + '=' * 74)
    w('-- Carga do planejamento: %s' % d['titulo'])
    w('-- ' + '=' * 74)
    w('--')
    w('-- GERADO por scripts/seed-acompanhamento.py. Nao edite na mao: rode de')
    w('-- novo com --codigo para manter o mesmo codigo do cliente.')
    w('--')
    w('-- Este arquivo tem dado de terceiro (roteiro e datas de viagem). Esta')
    w('-- no .gitignore e precisa continuar de fora do Git.')
    w('--')
    w('-- O codigo em claro NAO esta aqui, so o hash. Ele foi impresso na tela')
    w('-- na hora em que este arquivo foi gerado, e nao da para recuperar.')
    w('-- ' + '=' * 74)
    w('')
    w('SET NAMES utf8mb4;')
    w('START TRANSACTION;')
    w('')
    w('-- Recarga limpa: apagar o planejamento leva junto voos, cidades,')
    w('-- atracoes e escolhas, por ON DELETE CASCADE.')
    w('DELETE FROM rcf_planejamento WHERE codigo_hash = X%s;' % sq(hash_hex))
    w('')
    w('INSERT INTO rcf_planejamento')
    w('  (codigo_hash, apelido, cliente_nome, titulo, descricao, passageiros,')
    w('   etapa, data_inicio, data_fim, codigo_emitido_em, expira_em)')
    w('VALUES (X%s, %s, %s, %s, %s, %d, %s, %s, %s, NOW(), %s);'
      % (sq(hash_hex), sq(d['codigo_apelido']), sq(d['cliente_nome']),
         sq(d['titulo']), sq(d['descricao']), int(d['passageiros']),
         sq(d['etapa']), sq(d['data_inicio']), sq(d['data_fim']),
         sq(expira.isoformat() + ' 23:59:59')))
    w('SET @plan = LAST_INSERT_ID();')
    w('')

    w('-- ' + '-' * 74)
    w('-- Voos, do %s-conferencia.json' % a.slug)
    w('-- ' + '-' * 74)
    for v in voos:
        w('INSERT INTO rcf_voo (planejamento_id, ordem, tipo, bilhete, '
          'companhia, numero_voo, origem_iata, destino_iata, partida_local, '
          'chegada_local, duracao_min, observacao) VALUES')
        w('  (@plan, %d, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
          % (v['ordem'], sq(v['tipo']),
             'NULL' if v['bilhete'] is None else str(v['bilhete']),
             sq(v['companhia']), sq(v['numero']), sq(v['origem']),
             sq(v['destino']), sq(v['partida']), sq(v['chegada']),
             'NULL' if v['duracao'] is None else str(v['duracao']),
             sq(v['observacao'])))
    w('')

    total_atr = 0
    for c in d['cidades']:
        w('-- ' + '-' * 74)
        w('-- %s, %s' % (c['nome'], c['pais']))
        w('-- ' + '-' * 74)
        w('INSERT INTO rcf_cidade (planejamento_id, ordem, nome, pais, '
          'chegada, saida, noites, nota) VALUES')
        w('  (@plan, %d, %s, %s, %s, %s, %s, %s);'
          % (int(c['ordem']), sq(c['nome']), sq(c['pais']),
             sq(c.get('chegada')), sq(c.get('saida')),
             'NULL' if c.get('noites') is None else str(int(c['noites'])),
             sq(c.get('nota'))))
        w('SET @cidade = LAST_INSERT_ID();')
        for i, at in enumerate(c['atracoes'], 1):
            total_atr += 1
            w('INSERT INTO rcf_atracao (planejamento_id, cidade_id, origem, '
              'nome, descricao, horario, preco_tipo, preco_texto, sazonal, '
              'janela, detalhes, ordem) VALUES')
            w("  (@plan, @cidade, 'curadoria', %s, %s, %s, %s, %s, %d, %s, %s, %d);"
              % (sq(at['nome']), sq(at.get('descricao')), sq(at.get('horario')),
                 sq(at['preco_tipo']), sq(at.get('preco_texto')),
                 1 if at.get('sazonal') else 0,
                 sq(at.get('janela')), sq(at.get('detalhes')), i))
        w('')

    w('COMMIT;')
    w('')

    os.makedirs(SAIDA, exist_ok=True)
    destino = os.path.join(SAIDA, 'seed-%s.sql' % a.slug)
    io.open(destino, 'w', encoding='utf-8', newline='\n').write('\n'.join(L))

    # ---- relatorio ----------------------------------------------------------
    print('gravado: %s' % destino)
    print('')
    print('  %-22s %s' % ('planejamento', d['titulo']))
    print('  %-22s %d' % ('passageiros', d['passageiros']))
    print('  %-22s %s a %s' % ('datas', d['data_inicio'], d['data_fim']))
    print('  %-22s %s' % ('etapa', d['etapa']))
    print('  %-22s %d (%d de conexao)'
          % ('voos', len(voos), sum(1 for v in voos if v['tipo'] == 'conexao')))
    print('  %-22s %d' % ('cidades', len(d['cidades'])))
    print('  %-22s %d' % ('atracoes', total_atr))
    print('  %-22s %s' % ('expira em', expira.isoformat()))

    if avisos:
        print('')
        print('AVISO: dia da semana que nao bate com o calendario:')
        for x in avisos:
            print(x)
        print('  Confira antes de carregar. Foi assim que o boni-roteiro.json')
        print('  envelheceu: a data mudou e o dia da semana ficou para tras.')

    print('')
    print('=' * 62)
    print('  CODIGO DO CLIENTE:   %s' % '-'.join([codigo[:5], codigo[5:]]))
    print('=' * 62)
    print('  Aparece uma vez so. Nao esta no SQL e nao esta em arquivo nenhum.')
    print('  Copie agora e mande para o cliente. Perdeu, gera outro.')
    print('')
    return 0


if __name__ == '__main__':
    sys.exit(main())
