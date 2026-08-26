# -*- coding: utf-8 -*-
"""Gera a proposta de assessoria em PDF, na identidade do site.

    python propostas/build_proposta.py boni-nova-york

Le propostas/dados/<nome>.json e escreve propostas/pdf/<arquivo>.pdf.

O que o arquivo de dados traz e so o que depende da pesquisa: voos, milhas,
taxas, bagagem. O resto do documento, que e a parte que se repete em toda
proposta, nasce aqui: como a gente trabalha, o que conferir antes de emitir e
o que esperar do destino naquelas datas.

Reaproveita o framework dos ebooks para nao existir uma segunda identidade
visual no projeto.
"""
import io
import json
import os
import sys

# o console do Windows abre em cp1252 e nao imprime os colchetes de buraco
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, 'ebooks'))

from reportlab.platypus import Paragraph, Spacer, PageBreak  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from framework import (  # noqa: E402
    EbookDoc, styles, cover_block, bullet_list, data_table, section_opener,
    Callout, Divider, StatStrip, to_content, cell,
)

PDF_DIR = os.path.join(AQUI, 'pdf')
os.makedirs(PDF_DIR, exist_ok=True)

# Marcador de campo em aberto. ASCII de proposito: a fonte embutida no PDF
# nao tem os colchetes brancos do Unicode e desenhava um quadrado preto no
# lugar, que parecia defeito em vez de aviso.
BURACO_ABRE, BURACO_FECHA = '[[', ']]'


def contar_buracos(obj):
    """Quantos campos ainda estao por preencher, em qualquer nivel do JSON."""
    if isinstance(obj, str):
        return obj.count(BURACO_ABRE)
    if isinstance(obj, dict):
        return sum(contar_buracos(v) for k, v in obj.items()
                   if not k.startswith('_'))
    if isinstance(obj, list):
        return sum(contar_buracos(v) for v in obj)
    return 0


def texto(v):
    return '' if v is None else str(v)


def milhar(n):
    try:
        return '{:,}'.format(int(n)).replace(',', '.')
    except (TypeError, ValueError):
        return texto(n)


def montar(dados):
    S = styles()
    cli, via = dados['cliente'], dados['viagem']
    saida = os.path.join(PDF_DIR, dados['arquivo'] + '.pdf')
    doc = EbookDoc(saida, 'Proposta de assessoria · %s' % via['destino'])
    story = []

    # ---------------------------------------------------------------- capa
    story.extend(cover_block(
        title='Proposta de<br/>assessoria',
        subtitle='%s · %s a %s' % (via['destino'], via['ida'], via['volta']),
        badge='PARA %s' % cli['como_chamar'].upper(),
        year=None,
    ))

    # -------------------------------------------------------------- abertura
    story.extend(to_content())
    story.append(Paragraph('O QUE VOCÊ PEDIU', S['eyebrow']))
    story.append(Paragraph('Antes de tudo, conferindo se entendemos.',
                           S['h1']))
    story.append(Divider(width_pct=0.18, gap_before=0.1 * cm, gap_after=0.3 * cm))

    story.append(Paragraph(
        'Boa parte das propostas de milhas erra porque o assessor pesquisa '
        'antes de entender. Então a primeira página é o seu pedido escrito de '
        'volta. <b>Se algo aqui estiver diferente do que você quis dizer, me '
        'avise antes de olhar o resto</b>, porque muda a pesquisa inteira.',
        S['body']))

    story.append(Spacer(1, 0.25 * cm))
    story.append(data_table([
        [cell('Item', header=True), cell('O que anotamos', header=True)],
        [cell('Quem viaja'), cell(texto(cli['passageiros']))],
        [cell('Destino'), cell('%s, chegando em %s'
                               % (via['destino'], via['aeroportos_destino']))],
        [cell('Ida'), cell(texto(via['ida']))],
        [cell('Volta'), cell('%s, %d noites' % (via['volta'], via['noites']))],
        [cell('De onde pode sair'), cell(texto(via['origens_aceitas']))],
        [cell('Preferência'), cell(texto(via['preferencia']))],
        [cell('Flexibilidade'), cell(texto(via['flexibilidade']))],
        [cell('Perfil da viagem'), cell(texto(cli['perfil']))],
    ], col_widths=[4.2 * cm, 12.5 * cm]))

    story.append(Spacer(1, 0.3 * cm))
    car = dados['carteira']
    story.append(Paragraph('O que você tem hoje', S['h2']))
    story.append(data_table([
        [cell('Programa', header=True), cell('Saldo', header=True)],
        [cell('Smiles'), cell(milhar(car['smiles']))],
        [cell('Livelo'), cell(texto(car['livelo']))],
    ], col_widths=[8 * cm, 8.7 * cm]))
    if car.get('nota'):
        story.append(Spacer(1, 0.15 * cm))
        story.append(Paragraph('<i>%s</i>' % car['nota'], S['small']))

    # ------------------------------------------------------------- as opcoes
    story.append(PageBreak())
    story.extend(section_opener(
        'As opções',
        'Os caminhos que encontramos.',
        'Cada opção abaixo foi pesquisada com o seu saldo real e com as datas '
        'que você deu. Onde houver conexão, o tempo dela está na tabela: é o '
        'número que decide se a viagem é tranquila ou se vira corrida.'
    ))

    for op in dados['opcoes']:
        story.append(Paragraph(op['titulo'], S['h2']))
        if op.get('resumo'):
            story.append(Paragraph(op['resumo'], S['body']))
            story.append(Spacer(1, 0.15 * cm))

        linhas = [[cell('Trecho', header=True), cell('Data', header=True),
                   cell('Voo', header=True), cell('Horários', header=True),
                   cell('Conexão', header=True), cell('Milhas', header=True),
                   cell('Taxas', header=True)]]
        for t in op['trechos']:
            linhas.append([
                cell(texto(t['trecho'])), cell(texto(t['data'])),
                cell('%s\n%s' % (texto(t['cia']), texto(t['programa']))),
                cell(texto(t['horarios'])), cell(texto(t['conexao'])),
                cell(milhar(t['milhas_pessoa'])), cell(texto(t['taxas_pessoa'])),
            ])
        story.append(data_table(linhas, col_widths=[2.6 * cm, 1.7 * cm, 2.6 * cm,
                                                    3.0 * cm, 2.2 * cm,
                                                    2.3 * cm, 2.3 * cm]))
        story.append(Spacer(1, 0.15 * cm))
        story.append(Paragraph(
            '<b>Bagagem:</b> %s' % texto(op.get('bagagem')), S['body']))
        if op.get('observacao'):
            story.append(Paragraph(
                '<b>Vale saber:</b> %s' % op['observacao'], S['body']))
        story.append(Spacer(1, 0.4 * cm))

    story.append(Callout(
        'Os números de milhas e taxas valem para o momento da pesquisa',
        'Tarifa de resgate e assento disponível mudam ao longo do dia, e nas '
        'datas de alta temporada mudam mais rápido ainda. Por isso a proposta '
        'tem prazo curto: se a decisão demorar, refazemos a busca antes de '
        'emitir, sem custo.', kind='warn'))

    # --------------------------------------------------------- como trabalhamos
    story.append(PageBreak())
    story.extend(section_opener(
        'Como trabalhamos',
        'As estratégias por trás dessas opções.',
        'Não é segredo nenhum, e a gente publica tudo isso de graça no site. '
        'O que você está pagando é o tempo de aplicar caso a caso, não a '
        'informação.'
    ))

    story.extend(bullet_list([
        '<b>A porta de entrada não precisa ser o destino.</b> A cidade onde '
        'você quer chegar e a cidade por onde entra no país são decisões '
        'separadas. Foi assim que a nossa família entrou nos Estados Unidos '
        'por Los Angeles para chegar a Orlando, porque naquele momento era a '
        'porta mais barata a partir do Brasil.',

        '<b>A mesma perna custa diferente em cada programa.</b> Cada programa '
        'tem acordo com companhias diferentes, então consultamos o mesmo voo '
        'em mais de um lugar. Já voamos pela United emitindo com milha Azul, e '
        'pela American emitindo com Smiles.',

        '<b>Comparar em reais, não em milhas.</b> Milheiro de programa '
        'diferente custa diferente, então 20 mil milhas de um podem sair mais '
        'caro que 30 mil de outro. Toda comparação nesta proposta é feita em '
        'reais, pelo custo do seu saldo.',

        '<b>Bilhete separado só quando compensa muito.</b> Comprar trechos '
        'separados abre preço, mas cada bilhete vira um contrato independente: '
        'se um atrasa e você perde o seguinte, a companhia não deve '
        'reacomodação. Quando propomos isso, vem com conexão folgada e o risco '
        'escrito.',

        '<b>O trecho curto nem sempre vale milha.</b> Perna nacional de uma '
        'hora costuma ser onde a milha rende pior. Já voltamos de ônibus-leito '
        'de São Paulo a Curitiba porque a tarifa de resgate do dia estava '
        'ruim, e guardamos a milha para o trecho longo.',
    ]))

    story.append(Spacer(1, 0.3 * cm))
    hon = dados['honorarios']
    story.append(Callout(
        'Os honorários: %s' % hon['valor'],
        '%s %s' % (hon['escopo'], hon['condicao']), kind='note'))

    # ------------------------------------------------------- conferir antes
    story.append(PageBreak())
    story.extend(section_opener(
        'Antes de emitir',
        'O que precisa ser conferido.',
        'Esta lista não é burocracia nossa: é o que costuma derrubar viagem '
        'já paga. Confira item por item e me diga se algum estiver em aberto.'
    ))

    story.append(Paragraph('Documentos', S['h2']))
    story.extend(bullet_list([
        '<b>Visto americano válido para todos.</b> Brasileiro precisa de visto '
        'B1/B2 para entrar nos Estados Unidos, e ele não é emitido na hora: a '
        'fila de entrevista no consulado costuma ser longa. Se alguém do grupo '
        'não tiver, ou estiver perto de vencer, esse é o primeiro assunto, '
        'antes de qualquer passagem.',

        '<b>Passaporte com validade folgada.</b> Confira a data de todos, '
        'inclusive dos filhos. Passaporte de criança e adolescente vence mais '
        'rápido que o de adulto, e é o que mais pega gente de surpresa.',

        '<b>Nome igual ao do documento.</b> A passagem sai com o nome que '
        'estiver na conta do programa. Divergência de sobrenome depois da '
        'emissão é remarcação, e em bilhete de milhas costuma sair caro.',
    ]))

    story.append(Paragraph('Seguro viagem', S['h2']))
    story.append(Paragraph(
        'Os Estados Unidos não exigem seguro para entrar, e é exatamente por '
        'isso que muita gente viaja sem. O problema não é a fronteira: é a '
        'conta do hospital. Atendimento de emergência lá é dos mais caros do '
        'mundo, e um episódio simples com um dos filhos vira um valor que '
        'paga a viagem inteira várias vezes. <b>Contrate com cobertura médica '
        'de verdade</b>, e confira se cobre a atividade que vocês pretendem '
        'fazer.', S['body']))
    story.append(Paragraph(
        'Vale conferir também se algum cartão da família já oferece seguro '
        'viagem, o que é comum em cartão premium. Se oferecer, leia a '
        'cobertura antes de confiar nela: costuma ter teto baixo e exigir que '
        'a passagem tenha sido paga com aquele cartão, o que não acontece em '
        'emissão com milhas.', S['body']))

    story.append(Paragraph('Bagagem e conexão', S['h2']))
    story.extend(bullet_list([
        '<b>Franquia de bagagem depende da tarifa, não do programa.</b> Duas '
        'emissões no mesmo programa podem ter regras diferentes. A que vale '
        'para a sua está na tabela de cada opção, e conferimos de novo no '
        'momento da emissão.',

        '<b>Conexão nos Estados Unidos tem passo a mais.</b> Na primeira '
        'parada em solo americano você passa pela imigração, retira a bagagem, '
        'passa pela alfândega e despacha de novo, mesmo continuando viagem. '
        'Isso come tempo, e é por isso que conexão curta no primeiro ponto de '
        'entrada é risco.',
    ]))

    return doc, story, saida


def secao_destino(story, S):
    """Nova York entre o fim de novembro e o comeco de dezembro.

    Fica separado do resto porque e a parte que muda por destino e por epoca.
    Quando a proxima proposta for para outro lugar, e esta funcao que se
    reescreve.
    """
    story.append(PageBreak())
    story.extend(section_opener(
        'O destino',
        'Nova York nessas datas.',
        'Vocês escolheram, sem querer, a melhor e a mais movimentada época do '
        'ano na cidade. Vale saber das duas coisas.'
    ))

    story.append(Callout(
        'Vocês chegam na véspera do Dia de Ação de Graças',
        'O feriado cai em 26 de novembro de 2026, e vocês pousam no dia 25. A '
        'véspera é historicamente o dia de maior movimento aéreo do ano nos '
        'Estados Unidos. Para a viagem de vocês isso significa duas coisas: '
        'se o roteiro tiver conexão em solo americano, ela precisa ser folgada, '
        'e vale sair de casa com mais antecedência do que o normal.',
        kind='warn'))

    story.append(Paragraph('O que só acontece nessas duas semanas', S['h2']))
    story.extend(bullet_list([
        '<b>Desfile da Macy\'s, no dia 26.</b> O desfile de balões gigantes '
        'que passa pela Central Park West e termina na Herald Square. É de '
        'graça, começa cedo e enche muito: quem quer ver de perto se posiciona '
        'antes do amanhecer.',

        '<b>A inflagem dos balões, na noite do dia 25.</b> Menos conhecida que '
        'o desfile e, para muita gente, melhor. Na véspera, os balões são '
        'enchidos na rua perto do Museu Americano de História Natural, e dá '
        'para caminhar entre eles. Como vocês chegam nesse dia, é uma boa '
        'primeira noite se o voo pousar cedo.',

        '<b>Acendimento da árvore do Rockefeller Center.</b> Costuma ser na '
        'quarta-feira seguinte ao feriado, o que em 2026 cai por volta do dia '
        '2 de dezembro. Confirme a data quando estiver perto, porque só é '
        'anunciada em cima da hora.',

        '<b>Black Friday, no dia 27.</b> Se compras fazem parte do plano, é o '
        'dia. Se não fazem, é o dia de evitar a Quinta Avenida e os outlets.',

        '<b>Mercados de Natal.</b> Bryant Park, Union Square e Columbus Circle '
        'montam vilas de barracas com comida e artesanato. O de Bryant Park '
        'tem pista de patinação com entrada gratuita, pagando só o aluguel do '
        'patim, e funciona bem com adolescente.',
    ]))

    story.append(Paragraph('O básico que vale o ingresso', S['h2']))
    story.extend(bullet_list([
        '<b>Um mirante, e só um.</b> Empire State, Top of the Rock, Edge e '
        'Summit contam a mesma história de ângulos diferentes. Escolher um e '
        'usar o dinheiro dos outros em outra coisa costuma render mais.',

        '<b>Estátua da Liberdade sem pagar.</b> O ferry de Staten Island é '
        'gratuito, funciona o dia todo e passa perto da estátua. Não desembarca '
        'na ilha, mas resolve a foto e o passeio.',

        '<b>Central Park no fim do outono.</b> Nessa época as árvores já estão '
        'sem folha e o parque fica com outra cara, mais silenciosa. Vale a '
        'caminhada do Bethesda Terrace até o Bow Bridge.',

        '<b>Museus com dia de contribuição voluntária.</b> Vários grandes '
        'museus da cidade têm horário ou dia em que o valor é sugerido, não '
        'obrigatório. Confira no site de cada um na semana da viagem: as '
        'regras mudam com frequência.',
    ]))

    story.append(Spacer(1, 0.25 * cm))
    story.append(Callout(
        'Frio de verdade',
        'Entre o fim de novembro e o começo de dezembro, Nova York fica '
        'próxima de zero grau, com vento entre os prédios e chance de neve. '
        'Não é um detalhe de conforto: é o que decide se o dia rende ou se '
        'todo mundo volta para o hotel às três da tarde. Casaco corta-vento, '
        'gorro, luva e sapato impermeável para os quatro.', kind='tip'))


def main():
    if len(sys.argv) < 2:
        print('uso: python propostas/build_proposta.py <nome-do-json>')
        raise SystemExit(1)
    nome = sys.argv[1].replace('.json', '')
    caminho = os.path.join(AQUI, 'dados', nome + '.json')
    if not os.path.exists(caminho):
        print('nao achei %s' % caminho)
        raise SystemExit(1)

    dados = json.load(io.open(caminho, encoding='utf-8'))
    doc, story, saida = montar(dados)
    secao_destino(story, styles())
    doc.build(story)

    buracos = contar_buracos(dados)
    print('OK: %s' % saida)
    if buracos:
        print('')
        print('ATENCAO: %d campo(s) ainda com [[...]].' % buracos)
        print('Eles aparecem impressos no PDF, de proposito. Preencha em')
        print('  propostas/dados/%s.json' % nome)
        print('e rode de novo antes de mandar para o cliente.')
    else:
        print('Nenhum campo em aberto: pode enviar.')


if __name__ == '__main__':
    main()
