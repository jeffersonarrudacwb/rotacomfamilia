"""
Ebook 1: Manual Completo de Pontos 2026
"""
import os
from reportlab.platypus import Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.units import cm
from framework import (
    EbookDoc, PDF_DIR, styles, cover_block, photo, two_col_photo_row,
    caption, bullet_list, data_table, section_opener, toc, back_cover_block,
    Callout, Divider, StatStrip, to_content, to_cover, C, cell
)

OUTFILE = os.path.join(PDF_DIR, '01-manual-pontos-2026.pdf')
TITLE = 'Manual Completo de Pontos 2026'

doc = EbookDoc(OUTFILE, TITLE)
S = styles()
story = []

# ============================================================
# COVER
# ============================================================
story.extend(cover_block(
    title='Manual Completo<br/>de Pontos',
    subtitle='O guia de quem acumula, transfere e emite para a própria família.',
    year='2026',
))

# ============================================================
# 02 - Boas-vindas
# ============================================================
story.extend(to_content())

story.append(Paragraph('BEM-VINDO', S['eyebrow']))
story.append(Paragraph('Antes de tudo: um café e uma promessa.', S['h1']))
story.append(Divider(width_pct=0.18, gap_before=0.1*cm, gap_after=0.3*cm))

story.append(Paragraph(
    'Este ebook foi escrito pela nossa família (Jefferson, Kharol e Derek) '
    'enquanto planejávamos a nossa próxima viagem internacional. Não tem teoria '
    'que a gente não tenha aplicado. Não tem cartão recomendado que a gente não '
    'use. E não tem estratégia que a gente não tenha testado pessoalmente, '
    'transferindo milhas reais e emitindo passagens reais.', S['body']))

story.append(Paragraph(
    'O que você vai ler aqui é o que aprendemos depois de mais de <b>5 milhões de '
    'milhas acumuladas</b> e <b>10 países visitados em 2 anos</b>. Sem fórmula '
    'milagrosa, sem promessa de viagem grátis: <b>milhas não substituem o '
    'planejamento</b>, mas, quando bem usadas, transformam o custo de qualquer '
    'viagem internacional.', S['body']))

story.append(Spacer(1, 0.3*cm))
story.append(Callout(
    'A promessa deste ebook',
    'Ao terminar a leitura você vai saber escolher seu cartão, entender quando '
    'transferir, calcular o custo real de uma milha e desenhar um plano de '
    'acumulação realista para a sua próxima viagem, em qualquer ponto que você '
    'esteja hoje.', kind='note'))

story.append(Spacer(1, 0.4*cm))
# O terceiro numero era "R$ 95k em passagens economizadas". Saiu: economia
# depende de comparar com um preco em dinheiro que ninguem chegou a pagar, e o
# site inteiro ja foi limpo desse tipo de conta. Trocado por emissoes feitas,
# que e um numero que da pra contar.
story.append(StatStrip([
    ('10', 'países visitados\nem 2 anos'),
    ('5M+', 'milhas já\nutilizadas'),
    ('100+', 'emissões\nrealizadas'),
]))

# ============================================================
# 03 - Sumário
# ============================================================
story.append(PageBreak())
story.append(Paragraph('SUMÁRIO', S['eyebrow']))
story.append(Paragraph('O que você vai aprender.', S['h1']))
story.append(Divider(width_pct=0.18))
story.append(Spacer(1, 0.3*cm))
story.append(toc([
    ('Como funcionam pontos e milhas no Brasil', '03'),
    ('Como escolher seu primeiro cartão (e o próximo)', '04'),
    ('Os programas de coalizão e a transferência', '05'),
    ('Calendário de bônus: o jogo do timing', '07'),
    ('Custo por milha: a regra de ouro', '08'),
    ('Uma emissão de verdade, trecho a trecho', '09'),
    ('Estratégia mês a mês para 2026', '11'),
    ('Salas VIP, a vantagem oculta dos premiums', '12'),
    ('Próximos passos: comunidade e assessoria', '14'),
]))

# ============================================================
# 04 - CAPÍTULO 1 - Como funcionam pontos e milhas
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 01',
    'Como funcionam pontos e milhas no Brasil.',
    'Antes de qualquer estratégia, é preciso entender as três camadas do '
    'ecossistema brasileiro. Sem isso, qualquer cartão que você escolher pode '
    'acabar virando dinheiro queimado.'
))

story.append(Paragraph('As três camadas do ecossistema', S['h2']))
story.append(Paragraph(
    'No Brasil, a viagem com pontos passa por três camadas que conversam entre si, '
    'mas que tem regras próprias. Entender essa separação é o que diferencia quem '
    'acumula pontos de quem realmente viaja com eles.', S['body']))

story.extend(bullet_list([
    '<b>Camada 1, Emissores:</b> bancos e fintechs que emitem o cartão de '
    'crédito. Bradesco, Itaú, Santander, BTG, Inter, C6, Nubank.',
    '<b>Camada 2, Programas de coalizão:</b> Livelo (Bradesco + Banco do Brasil) '
    'e Esfera (Santander). Recebem os pontos do seu cartão e podem ser convertidos '
    'em diversos programas finais.',
    '<b>Camada 3, Programas de companhias aéreas:</b> Latam Pass, Smiles, '
    'TudoAzul/Azul Fidelidade. É onde os pontos viram passagem.',
]))

story.append(Spacer(1, 0.2*cm))
story.append(Callout(
    'O pulo do gato é a camada 2',
    'A maioria das pessoas pula direto do cartão para a passagem. Quem entende a '
    'camada de coalizão (Livelo, Esfera) ganha o dobro: pode esperar bônus '
    'de transferência e escolher pra qual companhia mandar.', kind='tip'))

story.append(Paragraph('Pontos × milhas: a diferença que importa', S['h2']))
story.append(Paragraph(
    'É comum tratar tudo como "milhas", mas há uma distinção operacional: '
    '<b>pontos</b> são acumulados em programas de bancos e coalizões e podem virar '
    'várias coisas (transferência, produtos, dinheiro). <b>Milhas</b> são pontos já '
    'depositados no programa de uma companhia aérea, prontos para virar passagem. '
    'A regra geral é manter o saldo em <b>pontos</b> o máximo possível e só '
    'transferir para milhas quando há bônus relevante ou quando você já vai emitir.',
    S['body']))

story.append(Paragraph(
    'Pontos têm validade: geralmente 24 meses no Livelo, 24 na Esfera, e '
    'variável em outros. Milhas em programas aéreos costumam ter validade '
    'parecida. Manter os pontos vivos significa fazer ao menos uma '
    'movimentação (compra ou transferência) dentro do prazo. <i>Mantenha um '
    'controle simples disso, vale a pena.</i>',
    S['body']))

# ============================================================
# 05 - CAPÍTULO 2 - Cartões
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 02',
    'Como escolher seu primeiro cartão (e o próximo).',
    'Escolher cartão não é sobre status nem sobre o cartão mais bonito da '
    'carteira. É sobre a equação anuidade × pontuação × programa atrelado. '
    'Aqui está o framework que usamos pra avaliar qualquer cartão.'
))

story.append(Paragraph('Os 4 perfis de cartão no Brasil', S['h2']))
story.append(Paragraph(
    'Independente de banco, a maioria dos cartões brasileiros cai em um destes '
    'quatro perfis. Saber o perfil te diz para que tipo de uso o cartão foi '
    'pensado, e quando ele compensa.', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(data_table([
    [cell('Perfil', header=True), cell('Anuidade típica', header=True), cell('Pontuação', header=True), cell('Para quem é', header=True)],
    [cell('Entrada'), cell('Isento ou R$ 0–200'), cell('1 pt / R$ 2–3'), cell('Quem está começando, gasto até R$ 3k/mês')],
    [cell('Intermediário'), cell('R$ 300–700'), cell('1 pt / R$ 1,8'), cell('Gasto R$ 3–8k/mês, mira acúmulo nacional')],
    [cell('Premium'), cell('R$ 800–1.500'), cell('2 pts / USD internacional'), cell('Gasto R$ 8–20k/mês, mira internacional')],
    [cell('Ultra-premium'), cell('R$ 1.800–4.000+'), cell('2,2–2,5 pts / USD'), cell('Gasto alto + benefícios (salas VIP, seguros)')],
], col_widths=[3*cm, 3.2*cm, 3.6*cm, 6.5*cm]))

story.append(Spacer(1, 0.3*cm))
story.append(Paragraph('A conta que você precisa fazer', S['h2']))
story.append(Paragraph(
    'Antes de escolher um cartão, faça a conta simples:', S['body']))
story.append(Spacer(1, 0.2*cm))

story.append(Callout(
    'Fórmula do "vale a pena"',
    'Pontos gerados no ano  ×  valor médio de cada ponto  =  retorno bruto.\n'
    'Retorno bruto  −  anuidade total  =  ganho líquido.\n'
    'Se o ganho líquido for negativo, troque o cartão. Se for menor que R$ 500, '
    'reavalie no perfil de cima ou de baixo.', kind='tip'))

story.append(Paragraph(
    '<b>Exemplo:</b> Cartão intermediário com anuidade de R$ 600/ano e '
    'pontuação 1 ponto por R$ 1,80. Se você gasta R$ 5.000/mês, gera '
    '~33.000 pontos/ano. Considerando o ponto a R$ 0,035 (R$ 35 / mil pontos), '
    'isso vale ~R$ 1.155. Ganho líquido: <b>R$ 555/ano</b>. Faz sentido manter.',
    S['body']))

story.append(Paragraph(
    'Repita o exercício pra cada cartão que você tem ou está pensando em pegar. '
    'Cartões que não passam nessa conta saem da carteira, sem dó.', S['body']))

# ============================================================
# 06 - Cap 3 - Programas de coalizão
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 03',
    'Os programas de coalizão e a transferência.',
    'Aqui mora o jogo. É na transferência entre programas que pontos viram '
    'mais pontos, desde que você saiba esperar o momento certo.'
))

story.append(Paragraph('Os dois grandes programas de coalizão', S['h2']))
story.append(Paragraph(
    'Hoje no Brasil, dois programas concentram a maior parte da movimentação. '
    'É pra um deles que quase todo cartão brasileiro deposita seus pontos:', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(data_table([
    ['Programa', 'Quem pertence', 'Forte em', 'Transfere para'],
    ['Livelo', 'Bradesco + Banco do Brasil', 'Variedade de transferências', 'Latam, Smiles, TudoAzul, Iberia, AAdvantage…'],
    ['Esfera', 'Santander', 'Bônus agressivos pra Smiles', 'Smiles, Latam, TudoAzul, Air France…'],
], col_widths=[2.6*cm, 4*cm, 4.4*cm, 5.2*cm]))

story.append(Spacer(1, 0.3*cm))
story.append(Paragraph('Como uma transferência funciona, na prática', S['h2']))
story.append(Paragraph(
    'O fluxo padrão é: o cartão deposita pontos no programa de coalizão do banco '
    '(ex.: Livelo). Você acessa o programa, escolhe pra onde transferir e o '
    'quanto, e os pontos são convertidos em milhas no programa de destino '
    '(ex.: Latam Pass). Essa transferência <b>tem uma taxa de conversão</b>: em '
    'condições normais é <b>1:1</b>. Mas em campanhas de bônus, vira 1:1,6, '
    '1:1,8 ou até 1:2 (bônus de 100%).', S['body']))

story.append(Callout(
    'O segredo: quase sempre vale a pena esperar',
    'Transferir sem bônus raramente se justifica. O ponto que mudou nos últimos '
    'anos é a frequência: houve época de campanha boa quase todo mês, e hoje o '
    'intervalo é bem maior, em torno de uma por trimestre em cada programa. '
    'Isso não muda a regra de esperar, muda o planejamento: a transferência '
    'passou a ser decidida com meses de antecedência, não com semanas.',
    kind='tip'))

story.append(Spacer(1, 0.2*cm))
story.append(Paragraph('Nossos thresholds por programa', S['h3']))
story.append(Paragraph(
    'Só apertamos "transferir" quando o bônus atinge estes patamares. Abaixo '
    'disso, os pontos ficam parados aguardando a próxima janela.', S['body']))
story.append(Spacer(1, 0.1*cm))
story.append(data_table([
    [cell('Programa destino', header=True), cell('Bônus mínimo aceitável', header=True), cell('Frequência típica', header=True)],
    [cell('Latam Pass'), cell('≥ 30%'), cell('Cerca de 1x por trimestre')],
    [cell('Smiles (Gol)'), cell('≥ 80%'), cell('Cerca de 1x por trimestre')],
    [cell('TudoAzul / Azul Fidelidade'), cell('≥ 90%'), cell('Cerca de 1x por trimestre')],
], col_widths=[5.5*cm, 4.5*cm, 6.3*cm]))
story.append(Spacer(1, 0.2*cm))
story.append(Callout(
    'Atenção ao caso da Latam',
    'As campanhas da Latam costumam sair em 25%, então 30% já é uma oferta muito '
    'boa e não vale segurar os pontos esperando um número alto que não vem. '
    'Smiles e Azul são o oposto: exigem mais milhas por trecho, então só '
    'compensam com bônus grande na entrada.', kind='note'))

# ============================================================
# 07 - Cap 4 - Calendário de bônus
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 04',
    'Calendário de bônus: o jogo do timing.',
    'Esperar o bônus certo é a diferença entre 200k milhas e 400k milhas. '
    'A boa notícia: dá para prever.'
))

story.append(Paragraph('O calendário típico do ano', S['h2']))
story.append(Paragraph(
    'Os programas de coalizão repetem padrões. Não espere campanha boa todo mês: '
    'hoje o ritmo é de mais ou menos uma por trimestre em cada programa. O que '
    'continua valendo é <b>quando</b> elas costumam aparecer:', S['body']))

story.extend(bullet_list([
    '<b>Janeiro:</b> campanhas de "ano novo, milhas novas", bônus para '
    'incentivar a movimentação após o pico de gastos de dezembro.',
    '<b>Maio/Junho:</b> bônus pré-férias de julho, principalmente para '
    'Smiles e Latam Pass.',
    '<b>Setembro/Outubro:</b> aquecimento de Black Friday, historicamente '
    'os melhores bônus do ano.',
    '<b>Novembro:</b> Black Friday efetiva, com campanhas relâmpago de até 24h.',
    '<b>Dezembro:</b> bônus de fim de ano para captura de saldo antes da '
    'virada.',
]))

story.append(Callout(
    'Onde acompanhar os bônus',
    'Acompanhe o site do programa (notificações ativas), siga páginas de '
    'milhas no Instagram e participe da nossa newsletter: toda semana avisamos '
    'as campanhas que valem a pena. Inscreva-se em rotacomfamilia.com.br.',
    kind='tip'))

story.append(Paragraph('Exemplo prático: bônus de 100%', S['h2']))
story.append(Paragraph(
    'Imagine que você acumulou 100.000 pontos Livelo ao longo de 8 meses. '
    'Sem bônus, viram 100.000 milhas Latam Pass. Com bônus de 100%, viram '
    '200.000 milhas. Para a família ir a Orlando em alta temporada, a '
    'diferença é decisiva: 200.000 milhas costumam cobrir 2 passagens '
    'intercontinentais; 100.000 mal cobrem uma. <b>O bônus é o que viabiliza '
    'a viagem.</b>', S['body']))

# ============================================================
# 08 - Cap 5 - Custo por milha
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 05',
    'Custo por milha: a regra de ouro.',
    'Existe uma conta única que separa quem viaja barato de quem acha que '
    'viaja barato. É a conta do custo por milha, e ela vale para qualquer '
    'cartão e qualquer programa.'
))

story.append(Paragraph('A fórmula', S['h2']))
story.append(Paragraph(
    'Custo por milheiro (R$/k) = <b>tudo o que você desembolsou</b> ÷ '
    '(milhas que entraram, em milhares). Tudo mesmo: anuidade, o custo de '
    'antecipar uma compra que você não faria, clube de assinatura, taxas de '
    'transferência. Se saiu dinheiro do seu bolso, entra na conta.', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(Callout(
    'Cuidado com a conta que só divide a anuidade',
    'É comum ver a conta feita só com a anuidade dividida pelas milhas do ano. '
    'Ela dá um número lindo, na casa de R$ 5 o milheiro, e é falsa: ignora que '
    'você precisou gastar para pontuar. A conta honesta é a de cima, e ela dá '
    'um número três a cinco vezes maior. Melhor saber o número certo.',
    kind='note'))

story.append(Paragraph('O nosso custo, programa por programa', S['h2']))
story.append(Paragraph(
    'Não existe "o meu milheiro": existe um custo por programa, porque cada um '
    'tem bônus e regras diferentes. Este é o nosso, e é com ele que decidimos '
    'toda emissão:', S['body']))
story.append(Spacer(1, 0.1*cm))
story.append(data_table([
    [cell('Programa', header=True), cell('Nosso custo', header=True), cell('Acima disso, não transferimos', header=True)],
    [cell('TudoAzul'), cell('R$ 14,00 / k'), cell('R$ 15,00 / k')],
    [cell('Smiles'), cell('R$ 15,00 / k'), cell('R$ 16,00 / k')],
    [cell('Latam Pass'), cell('R$ 24,50 / k'), cell('R$ 25,00 / k')],
], col_widths=[5.0*cm, 5.0*cm, 6.3*cm]))

story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    'Repare no tamanho da diferença: <b>a milha Latam custa 75% mais que a '
    'Azul</b>. Isso tem uma consequência que muda toda comparação de passagem: '
    '20 mil milhas Latam custam mais caro que 30 mil milhas Azul. '
    '<b>Compare trechos em reais, nunca em milhas.</b>', S['body']))

story.append(Paragraph('Quando ignorar a regra', S['h2']))
story.append(Paragraph(
    'Em duas situações vale "pagar caro" por uma milha:', S['body']))

story.extend(bullet_list([
    'Quando você precisa de uma data específica e a passagem em dinheiro '
    'está absurdamente cara (alta temporada, evento): milhas viram seu '
    'desconto, mesmo que o custo por milha esteja em R$ 50.',
    'Quando o saldo está vencendo e você tem certeza de uma viagem nos '
    'próximos meses: melhor usar do que perder.',
]))

# ============================================================
# 09 - Cap 6 - Caso real, a emissao de 7 trechos
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 06',
    'Uma emissão de verdade, trecho a trecho.',
    'Toda a teoria dos capítulos anteriores cabe numa viagem só. Esta é a '
    'nossa, com os números que apareceram na tela na hora de emitir.'
))

story.append(Paragraph(
    'Levamos os três de Curitiba a Orlando, passando por Los Angeles e '
    'Minneapolis, e voltamos de <b>classe executiva</b>. No mapa o roteiro não '
    'faz sentido nenhum. Na planilha faz: <b>nenhum dos sete voos foi comprado '
    'junto com outro</b>. Cada trecho foi emitido onde estava mais barato, '
    'somando quatro companhias e três programas.', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(data_table([
    [cell('Trecho', header=True), cell('Voou', header=True), cell('Emitiu', header=True),
     cell('Milhas', header=True), cell('Custo', header=True)],
    [cell('CWB → GRU'), cell('Latam'), cell('Latam Pass'), cell('2.600'), cell('R$ 107')],
    [cell('GRU → LAX'), cell('Latam'), cell('Latam Pass'), cell('46.400'), cell('R$ 1.387')],
    [cell('LAX → MSP'), cell('United'), cell('TudoAzul'), cell('18.000'), cell('R$ 296')],
    [cell('MSP → MCO'), cell('American'), cell('Smiles'), cell('27.500'), cell('R$ 413')],
    [cell('MCO → PTY'), cell('Copa'), cell('TudoAzul'), cell('42.000'), cell('R$ 748')],
    [cell('PTY → CNF'), cell('Copa'), cell('Smiles'), cell('105.000'), cell('R$ 1.575')],
    [cell('CNF → CWB'), cell('Latam'), cell('Latam Pass'), cell('11.000'), cell('R$ 300')],
    [cell('Total', bold=True), cell(''), cell(''), cell('252.500', bold=True), cell('R$ 4.826', bold=True)],
], col_widths=[3.6*cm, 2.5*cm, 3.4*cm, 2.8*cm, 4.0*cm]))

story.append(Spacer(1, 0.15*cm))
story.append(Paragraph(
    'Os custos acima usam o nosso milheiro do capítulo anterior e incluem as '
    'taxas que localizamos. Faltam as taxas de dois trechos, os dois da Smiles, '
    'então o total real é um pouco maior.', S['caption']))

story.append(Spacer(1, 0.25*cm))
story.append(Paragraph('As duas linhas do meio', S['h2']))
story.append(Paragraph(
    '<b>Voamos pela United emitindo pela Azul. Voamos pela American emitindo '
    'pela Smiles.</b> Não é erro de digitação: cada programa tem acordo com '
    'companhias diferentes, e o assento que está caro num lugar pode estar '
    'barato em outro. Consultar a mesma perna em mais de um programa é o hábito '
    'que mais economiza.', S['body']))

story.append(Paragraph('Comece pela porta, não pelo destino', S['h2']))
story.append(Paragraph(
    'A formatura era em Minneapolis e a Disney fica em Orlando. Nenhuma das '
    'duas é porta barata de entrada nos Estados Unidos. Em vez de perguntar '
    '"quanto custa ir a Minneapolis", perguntamos <b>"qual cidade americana '
    'está mais barata a partir do Brasil?"</b>. A resposta foi Los Angeles, e o '
    'resto resolvemos por dentro. A cidade onde você quer chegar e a cidade por '
    'onde você entra no país não precisam ser a mesma.', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(Callout(
    'O preço disso: bilhetes separados são contratos separados',
    'Se um voo atrasa e você perde o seguinte, a companhia não te deve nada. '
    'Não há reacomodação, não há reembolso, não há hotel: para efeito de '
    'contrato, você não apareceu para embarcar. Reduza o risco com conexões '
    'longas e confirmando se precisa retirar e despachar a bagagem de novo. '
    'Se essa possibilidade te tira o sono, a estratégia não é para você.',
    kind='warn'))

story.append(Spacer(1, 0.2*cm))
story.append(Paragraph('O trecho que a gente perdeu', S['h2']))
story.append(Paragraph(
    'O CNF → CWB, por 11 mil milhas Latam. Deixamos essa perna para o fim de '
    'propósito, esperando uma janela melhor que nunca apareceu. Com os outros '
    'seis já emitidos, chegou o dia em que não dava mais para esperar. Fica o '
    'registro: <b>segurar um trecho à espera de preço melhor é uma aposta como '
    'outra qualquer</b>, e essa a gente perdeu.', S['body']))

# ============================================================
# 10 - Cap 7 - Estratégia mês a mês
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 07',
    'Estratégia mês a mês para 2026.',
    'Um ano de milhas dá pra dividir em quatro estações. Aqui vai o plano '
    'que estamos seguindo na nossa família este ano.'
))

story.append(Paragraph('Trimestre 1: Janeiro a Março', S['h3']))
story.append(Paragraph(
    'Foco em campanhas de início de ano. Limpe a casa: liste todos os '
    'saldos, anote validades, atualize os logins. Aproveite bônus de janeiro '
    'para Latam Pass se a viagem de meio do ano for via Latam, ou para '
    'Smiles se for via Gol/Air France. Use fevereiro para revisar cartões: '
    'se algum não passou no teste de custo por milha, peça pra trocar.',
    S['body']))

story.append(Paragraph('Trimestre 2: Abril a Junho', S['h3']))
story.append(Paragraph(
    'Período de bônus pré-férias. Maio e junho costumam trazer campanhas '
    'agressivas para julho. Se a viagem de família é em julho, esta é a '
    'última janela útil pra acumular o saldo necessário sem pagar custos '
    'altos por milha.', S['body']))

story.append(Paragraph('Trimestre 3: Julho a Setembro', S['h3']))
story.append(Paragraph(
    'Use este período pra acumular pensando em <b>2027</b>. Sim, com '
    'antecedência. Setembro costuma trazer o aquecimento da Black Friday, que '
    'historicamente traz os melhores bônus do ano. Comece a desenhar o destino '
    'do ano seguinte: avião com bom preço em milhas costuma sair em janeiro do '
    'ano da viagem.', S['body']))

story.append(Paragraph('Trimestre 4: Outubro a Dezembro', S['h3']))
story.append(Paragraph(
    'A grande temporada. Black Friday em novembro traz as melhores '
    'condições do ano. Plano: junte saldo ao longo do ano, e na Black '
    'Friday faça a transferência maior. Dezembro é mês de emissão das '
    'passagens de meio de 2026.', S['body']))

# ============================================================
# 11 - Cap 8 - Salas VIP
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 08',
    'Salas VIP, a vantagem oculta dos premiums.',
    'Boa parte do valor de um cartão premium não está nos pontos. Está nas '
    'salas VIP, que mudam por completo a experiência da viagem.'
))

story.append(Paragraph(
    'Cartões com anuidade a partir de R$ 800 normalmente já vêm com acesso '
    'a salas VIP nacionais. A partir de R$ 1.500, vêm com Priority Pass, '
    'acesso a centenas de salas no mundo inteiro, inclusive para acompanhantes. '
    'Quando você viaja em família, o benefício é direto: ao invés de pagar '
    'R$ 200–400 por pessoa em cada conexão, você entra de graça e ainda come, '
    'descansa e trabalha com Wi-Fi de qualidade.', S['body']))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('sala_vip/IMG_5235.jpg', 'sala_vip/IMG_4808.jpg', h=6.5*cm))
story.append(caption('W Lounge (GRU, Star Alliance) à esquerda · Bradesco Lounge à direita, duas das salas que mais usamos.'))

story.append(Paragraph('Como aproveitar de verdade', S['h2']))
story.extend(bullet_list([
    'Chegue antes: salas valem pelo conforto e pela refeição. Plano: 3h antes do voo internacional.',
    'Inclua os dependentes: cartões premium permitem acompanhantes, mas regras variam (1, 2 ou ilimitado).',
    'Use mesmo no Brasil: Copa Club, Star Alliance Gold, GRU Lounge, Plaza Premium.',
    'Em escalas internacionais, salas VIP "salvam" viagens de 8h+ de conexão.',
]))

story.append(Spacer(1, 0.3*cm))
story.append(photo('sala_vip/IMG_8543.jpg', max_h=8*cm))
story.append(caption('Copa Club Star Alliance Gold, a sala que viramos clube em viagens longas.'))

# ============================================================
# 11 - Fechamento
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Próximos passos',
    'Continue conosco, você não está sozinho nessa.',
    'A parte teórica acabou. Agora começa a aplicação, e é aí que a '
    'comunidade faz a diferença.'
))

story.append(Paragraph('O que fazer hoje', S['h2']))
story.extend(bullet_list([
    'Anote todos os seus saldos em Livelo, Esfera, Latam Pass, Smiles, TudoAzul.',
    'Calcule o custo por milha de cada cartão que você tem hoje.',
    'Decida o destino da próxima viagem em família e a meta de milhas necessárias.',
    'Inscreva-se na newsletter da Rota com Família: alertas semanais de bônus.',
    'Se preferir não fazer sozinho, considere nossa assessoria personalizada.',
]))

story.append(Spacer(1, 0.3*cm))
story.append(Callout(
    'Quer um plano sob medida pra sua família?',
    'Eu (Jefferson) emito passagens com milhas para outras famílias todo mês, '
    'nacional e internacional. Mando o plano em PDF, faço as transferências '
    'junto com você e entrego os bilhetes prontos. Fale comigo no WhatsApp '
    'ou em contato@rotacomfamilia.com.br.', kind='note'))

story.extend(back_cover_block(
    'Esperamos que este manual seja só o começo da sua próxima viagem em família. '
    'A gente ama trocar ideia com quem está nessa jornada: manda mensagem pra '
    'gente conta o que você está planejando.'))

# ============================================================
# Build
# ============================================================
doc.build(story)
print(f'OK: {OUTFILE}')
