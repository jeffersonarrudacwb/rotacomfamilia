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
    'entre uma viagem e outra, no intervalo em que a gente planeja a seguinte. '
    'Não tem teoria '
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
    ('Como escolher seu primeiro cartão (e o próximo)', '05'),
    ('Acumular sem gastar a mais', '07'),
    ('Os programas de coalizão e a transferência', '09'),
    ('Calendário de bônus: o jogo do timing', '11'),
    ('Custo por milha: a regra de ouro', '12'),
    ('Uma emissão de verdade, trecho a trecho', '14'),
    ('Estratégia mês a mês para 2026 e 2027', '16'),
    ('Salas VIP, a vantagem oculta dos premiums', '17'),
    ('Próximos passos: comunidade e assessoria', '19'),
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
    'depositados no programa de uma companhia aérea. '
    'A regra geral é manter o saldo em <b>pontos</b> o máximo possível e só '
    'transferir para milhas quando há bônus relevante ou quando você já vai emitir.',
    S['body']))

story.append(Paragraph(
    'E vale desfazer uma ideia comum: <b>milha não serve só para passagem.</b> '
    'Os programas aéreos também trocam milhas por hospedagem, aluguel de carro, '
    'produtos e experiências. Nem sempre compensa, mas às vezes compensa muito.',
    S['body']))

story.append(Callout(
    'Um resort inteiro pago com milhas',
    'A nossa hospedagem no Nickelodeon, em Punta Cana, saiu com milhas da Azul. '
    'Fizemos a conta antes, como sempre: comparamos o valor da diária em '
    'dinheiro com o que aquelas milhas custaram para a gente acumular. Nesse '
    'caso a troca valeu muito a pena. Antes de assumir que milha é só para voar, '
    'faça essa comparação, porque de vez em quando o resgate fora do avião é o '
    'melhor negócio do ano.', kind='tip'))

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
    [cell('Perfil', header=True), cell('Anuidade', header=True),
     cell('Pontos por dólar', header=True), cell('Tem sala VIP?', header=True)],
    [cell('Entrada'), cell('Isento a R$ 300'), cell('1 a 1,2'), cell('Quase nunca')],
    [cell('Intermediário'), cell('R$ 300 a 800'), cell('1,5 a 1,8'), cell('Cerca de um terço')],
    [cell('Premium'), cell('R$ 800 a 1.800'), cell('2 a 3'), cell('Sempre')],
    [cell('Ultra-premium'), cell('Acima de R$ 1.800'), cell('3 ou mais'), cell('Sempre')],
], col_widths=[3.2*cm, 3.6*cm, 4.0*cm, 5.5*cm]))

story.append(Spacer(1, 0.15*cm))
story.append(Paragraph(
    '<i>Esses são os números que a gente encontra de verdade no mercado que dá '
    'para alcançar. Existem cartões que pagam 7, 9 e até 11 pontos por dólar, '
    'mas eles cobram anuidades de R$ 15 mil a R$ 30 mil e são de private '
    'banking. Não adianta comparar a sua carteira com a deles: a tabela acima é '
    'a faixa em que a decisão realmente acontece.</i>', S['small']))

story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    'A unidade é sempre <b>pontos por dólar gasto</b>, e não por real. É assim '
    'que os bancos anunciam e é assim que dá para comparar dois cartões de '
    'bancos diferentes. Compra em reais também pontua: o banco converte pelo '
    'câmbio do dia antes de creditar.', S['body']))

story.append(Paragraph(
    'Repare que a pontuação quase triplica da primeira linha para a última. É o '
    'que faz o cartão de anuidade alta se pagar, desde que o seu gasto mensal '
    'justifique. Abaixo desse volume, o cartão intermediário quase sempre '
    'entrega mais ganho líquido, e é por isso que a conta da próxima página '
    'vale mais que qualquer recomendação de cartão que você leia por aí, '
    'inclusive as nossas.', S['body']))

story.append(Paragraph(
    'E repare na última coluna, porque ela é mais nítida do que parece: '
    '<b>a partir de R$ 900 de anuidade, praticamente todo cartão dá sala VIP</b>. '
    'Abaixo de R$ 400, quase nenhum. A faixa do meio é onde vale conferir caso '
    'a caso, porque só um terço oferece.', S['body']))

story.append(Callout(
    'Cuidado com o "até" do anúncio',
    'Um em cada dez cartões anuncia a pontuação como "até X pontos por '
    'dólar", e esse X quase nunca é o que você vai ganhar no dia a dia: '
    'costuma ser bônus de categoria, que vale só em compras na loja do parceiro, '
    'na plataforma de viagens do banco ou para quem assina um clube. '
    'O número que importa é o da compra comum. Procure a letra miúda: é esse '
    'que vai valer no seu mês.', kind='warn'))

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
    '<b>Exemplo.</b> Cartão intermediário, anuidade de R$ 600 no ano, '
    'pontuação de 1,8 ponto por dólar. Você gasta R$ 5.000 por mês, ou seja '
    'R$ 60.000 no ano. A um câmbio de R$ 5,50, isso são cerca de '
    'US$ 10.900, que a 1,8 viram <b>19.600 pontos no ano</b>.', S['body']))

story.append(Paragraph(
    'Agora o outro lado da conta. Com um bônus de 80% na transferência, esses '
    'pontos viram cerca de 35.300 milhas. Dividindo a anuidade por elas, o '
    'custo fica em <b>R$ 17 por milheiro</b>, dentro do teto da Smiles e '
    'acima do da Azul. É um cartão que se sustenta, sem ser brilhante.',
    S['body']))

story.append(Paragraph(
    'Faça a mesma conta trocando a pontuação por 3,0, que é o topo do premium, '
    'e você vai ver o motivo de gente com gasto alto pagar anuidade cara sem '
    'reclamar: o mesmo gasto rende quase o dobro de milhas, e o milheiro cai '
    'junto. O contrário também vale, e é o alerta mais útil aqui: se o seu '
    'gasto mensal é baixo, a anuidade alta não se paga nunca, por mais bonito '
    'que seja o cartão.', S['body']))

story.append(Paragraph(
    'Repita o exercício pra cada cartão que você tem ou está pensando em pegar. '
    'Cartões que não passam nessa conta saem da carteira, sem dó.', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(Callout(
    'Os três cartões que estão na nossa carteira hoje',
    'C6 Carbon, que é o nosso principal para gasto internacional. AmEx The '
    'Platinum Card do Bradesco, o principal aqui dentro, e o que mais abre sala '
    'VIP. E o AAdvantage do Santander, que usamos no passado e vale para quem '
    'mira emissões pela American. Não citamos cartão que a gente não tenha '
    'passado na maquininha. A tabela completa, com pontuação e perfil de cada '
    'um, está no caderno de Planilhas e Calculadoras.', kind='tip'))

# ============================================================
# 06 - Cap 3 - Acumular sem gastar a mais
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 03',
    'Acumular sem gastar a mais.',
    'O maior salto não vem de gastar mais. Vem de fazer o gasto que você já '
    'tem passar pelo caminho certo antes de virar fatura.'
))

story.append(Paragraph(
    'Quase todo mundo que começa acha que a conta é simples: passo o cartão, '
    'ganho ponto. É verdade, e é também a menor parte do que dá para ganhar. '
    'A mesma compra pode pontuar <b>três vezes</b>, e a diferença entre uma vez '
    'e três vezes é o que decide se a viagem sai neste ano ou no que vem.',
    S['body']))

story.append(Paragraph('As três camadas da mesma compra', S['h2']))
story.extend(bullet_list([
    '<b>1. O portal de compras.</b> Antes de comprar na loja, entre pelo site do '
    'seu programa (Livelo, Esfera e afins) e clique no link da loja por lá. '
    'A compra é a mesma, o preço é o mesmo, e ela rende pontos extras.',
    '<b>2. O cartão, na mesma compra.</b> Os pontos do portal não substituem os '
    'do cartão: eles se somam.',
    '<b>3. O bônus de conversão.</b> Na hora de transferir para a companhia '
    'aérea, espere a campanha. Numa temporada boa, o saldo dobra.',
]))

story.append(Callout(
    'Quanto isso rendeu para nós',
    'Só pelo portal de compras, sem comprar nada que não fosse comprar de '
    'qualquer jeito, passamos de 100 mil pontos Livelo numa única '
    'temporada. É o passo que mais gente pula, porque exige lembrar de abrir '
    'uma aba antes de finalizar a compra. Vale criar o hábito: é o ponto mais '
    'barato que existe.', kind='tip'))

story.append(Paragraph('O gasto que já está no seu mês', S['h2']))
story.append(Paragraph(
    'Além do portal, boa parte do que a família já gasta pode ser redirecionada '
    'para pontuar mais. Vale olhar, um por um, os canais em que você gasta todo '
    'mês sem pensar:', S['body']))

story.extend(bullet_list([
    '<b>Combustível.</b> Postos e aplicativos de abastecimento têm parceria com '
    'programas de pontos. É gasto recorrente e previsível, o melhor tipo.',
    '<b>Farmácia e supermercado.</b> Redes grandes acumulam em programas '
    'próprios que depois convertem, e às vezes rodam campanhas de pontuação '
    'multiplicada.',
    '<b>Transporte por aplicativo e delivery.</b> Parcerias mudam com frequência, '
    'mas quando existem rendem sobre um gasto que já é seu.',
    '<b>Contas de casa e assinaturas.</b> Luz, internet, streaming e mensalidade '
    'de escola no cartão certo é pontuação garantida todo mês.',
]))

story.append(Paragraph('O clube de pontos', S['h2']))
story.append(Paragraph(
    'Os programas vendem assinaturas mensais que depositam uma quantidade fixa '
    'de pontos todo mês, por um valor fixo. Assinado em promoção, é a forma '
    'mais barata de ter <b>entrada previsível</b> de pontos, e foi assim que '
    'completamos o saldo de mais de uma viagem nossa. Entre na conta do seu '
    'custo por milheiro: a mensalidade é desembolso e precisa aparecer lá.',
    S['body']))

story.append(Callout(
    'Nada disso é milha de graça',
    'Você vai ver por aí a promessa de acumular milhas "100% de graça". Preferimos '
    'ser francos: nenhum desses canais dá ponto de graça. O que eles fazem '
    'é aumentar o rendimento de um dinheiro que ia sair do seu bolso de qualquer '
    'forma. A diferença é enorme e a distinção importa, porque a promessa de '
    'gratuidade leva gente a gastar mais para "ganhar" pontos, o que é '
    'exatamente o contrário do que a gente faz. Se você comprou algo que não '
    'ia comprar, o ponto saiu caríssimo.', kind='warn'))

# ============================================================
# 07 - Cap 4 - Programas de coalizão
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 04',
    'Os programas de coalizão e a transferência.',
    'Aqui mora o jogo. É na transferência entre programas que pontos viram '
    'mais pontos, desde que você saiba esperar o momento certo.'
))

story.append(Paragraph('Os dois grandes programas de coalizão', S['h2']))
story.append(Paragraph(
    'Hoje no Brasil, dois programas concentram a maior parte da movimentação. '
    'É pra um deles que quase todo cartão brasileiro deposita seus pontos:', S['body']))

story.append(Spacer(1, 0.2*cm))
# Esta tabela estava com texto vazando por cima da coluna vizinha: as celulas
# eram strings cruas, e string em tabela do ReportLab nao quebra linha. So o
# Paragraph quebra, e quem devolve Paragraph aqui e o cell().
story.append(data_table([
    [cell('Programa', header=True), cell('Quem pertence', header=True),
     cell('Forte em', header=True), cell('Transfere para', header=True)],
    [cell('Livelo'), cell('Bradesco e Banco do Brasil'),
     cell('Variedade de destinos'),
     cell('Latam, Smiles, TudoAzul, Iberia, AAdvantage e outros')],
    [cell('Esfera'), cell('Santander'),
     cell('Bônus agressivos para a Smiles'),
     cell('Smiles, Latam, TudoAzul, Air France e outros')],
], col_widths=[2.6*cm, 4.2*cm, 4.2*cm, 5.7*cm]))

story.append(Spacer(1, 0.25*cm))
story.append(Paragraph('Nem todo cartão passa por essas duas', S['h3']))
story.append(Paragraph(
    'Nem todo banco deposita os pontos na Livelo ou na Esfera. Itaú, Banco '
    'Inter e C6 Bank, entre outros, mantêm o próprio programa e mandam os '
    'pontos direto para as companhias aéreas. Isso não é defeito: é só um '
    'caminho diferente, e vale acompanhar as campanhas <b>de cada banco</b>, '
    'não só as das duas coalizões. Quem olha apenas Livelo e Esfera perde '
    'metade das oportunidades.', S['body']))

story.append(Callout(
    'O C6 Bank tem um detalhe que resolve muita coisa',
    'Ele permite mandar os pontos para a Livelo na paridade de 1 para 1. Se '
    'você já tem saldo lá, dá para juntar tudo num lugar só em vez de manter '
    'dois montinhos pequenos que nunca chegam ao total de uma passagem. '
    'Concentrar saldo é o que permite emitir: ponto espalhado em quatro '
    'programas é ponto que não vira viagem.', kind='tip'))

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
story.append(Paragraph('Nosso bônus mínimo por programa', S['h3']))
story.append(Paragraph(
    'Só apertamos "transferir" quando o bônus atinge estes patamares. Abaixo '
    'disso, os pontos ficam parados aguardando a próxima janela.', S['body']))
story.append(Spacer(1, 0.1*cm))
story.append(data_table([
    [cell('Programa destino', header=True), cell('Bônus mínimo aceitável', header=True), cell('Frequência típica', header=True)],
    [cell('Latam Pass'), cell('≥ 30%'), cell('Trimestral')],
    [cell('Smiles (Gol)'), cell('≥ 80%'), cell('Trimestral')],
    [cell('TudoAzul / Azul Fidelidade'), cell('≥ 90%'), cell('Trimestral')],
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
    'Capítulo 05',
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

story.append(Paragraph('Exemplo prático: um bônus de 100%', S['h2']))
story.append(Paragraph(
    'Imagine que você acumulou 100.000 pontos Livelo ao longo de oito meses. '
    'Sem bônus, viram 100.000 milhas. Com bônus de 100%, viram <b>200.000</b>. '
    'Para levar a família a Orlando em alta temporada, a diferença é decisiva: '
    '200 mil milhas costumam cobrir duas passagens intercontinentais, e 100 mil '
    'mal cobrem uma. <b>O bônus é o que viabiliza a viagem.</b>', S['body']))

story.append(Callout(
    'Bônus de 100% existe, mas não em qualquer programa',
    'Esse exemplo só acontece com Smiles e TudoAzul, que são os programas '
    'que chegam a 80% e 90% e ocasionalmente encostam nos 100%. A Latam Pass '
    'não entra nessa conta: as campanhas dela saem em torno de 25%, e 30% já é '
    'uma oferta muito boa. Esperar 100% da Latam é esperar por algo que não '
    'costuma vir.', kind='warn'))

# ============================================================
# 08 - Cap 5 - Custo por milha
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 06',
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
    [cell('Latam Pass'), cell('R$ 24,50 / k'), cell('R$ 25,50 / k')],
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
    'desconto, mesmo que o custo por milha esteja alto.',
    'Quando o saldo está vencendo e você tem certeza de uma viagem nos '
    'próximos meses: melhor usar do que perder.',
    '<b>Quando falta pouco para fechar uma emissão.</b> Se a passagem sai por '
    '60 mil milhas e você tem 57 mil, comprar ou transferir as 3 mil que faltam '
    'quase sempre compensa, mesmo pagando caro nelas. O custo alto incide sobre '
    'uma fatia pequena, e sem ela as outras 57 mil não viram nada.',
]))

story.append(Paragraph('E quando a resposta certa é não usar milha', S['h2']))
story.append(Paragraph(
    'Saber o seu milheiro serve para as duas direções. Ele diz quando emitir, e '
    'diz quando <b>não</b> emitir, o que quase nenhum conteúdo sobre milhas '
    'admite.', S['body']))

story.append(Paragraph(
    'Voltando da África do Sul, precisávamos do último trecho, de São Paulo a '
    'Curitiba. Não apareceu preço bom em nenhum programa, e insistir ali sairia '
    'caro em milha que a gente tinha guardado para viagem internacional. '
    'Fomos de <b>ônibus-leito</b>, por volta de R$ 280. Foi confortável, virou '
    'uma experiência diferente no fim da viagem, e as milhas continuaram na '
    'conta rendendo para o próximo destino.', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(Callout(
    'A pergunta que evita desperdício',
    'Antes de emitir qualquer trecho curto, faça a conta em reais e compare com '
    'o preço em dinheiro, com o ônibus e até com o carro alugado. Trecho '
    'nacional de uma hora é onde a milha costuma render pior, porque a passagem '
    'em dinheiro é barata e a tarifa em milhas nem sempre acompanha. Guarde a '
    'milha para o trecho longo, que é onde ela devolve muito mais.', kind='tip'))

# ============================================================
# 09 - Cap 6 - Caso real, a emissao de 7 trechos
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 07',
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

story.append(Spacer(1, 0.25*cm))
story.append(Paragraph('Outras emissões que fizemos depois', S['h2']))
story.append(Paragraph(
    'Aquela viagem foi em 2024. Para você ver que o método não foi sorte de uma '
    'vez, estas são emissões nossas mais recentes, com os números que '
    'apareceram na tela:', S['body']))

story.append(Spacer(1, 0.15*cm))
story.append(data_table([
    [cell('Trecho', header=True), cell('Quando', header=True),
     cell('Voou', header=True), cell('Emitiu', header=True),
     cell('Milhas', header=True)],
    [cell('GRU → LIS, executiva'), cell('Abr/2026'), cell('Latam'), cell('Latam Pass'), cell('200.000')],
    [cell('GRU → JNB'), cell('Jul/2026'), cell('TAAG'), cell('TudoAzul'), cell('96.000')],
    [cell('CWB → FOR'), cell('Out/2026'), cell('Gol'), cell('AAdvantage'), cell('7.000')],
], col_widths=[4.4*cm, 2.4*cm, 2.4*cm, 3.3*cm, 3.8*cm]))

story.append(Spacer(1, 0.2*cm))
story.extend(bullet_list([
    '<b>Lisboa, seis passageiros.</b> Buscar os seis assentos de uma vez subia '
    'o preço, então dividimos a busca em duas contas. Executiva para a Europa a '
    '200 mil milhas por pessoa.',
    '<b>África do Sul pela TAAG.</b> Companhia angolana, paga com milha '
    'brasileira, emitida no Azul pelo Mundo. É o tipo de combinação que só '
    'aparece quando você olha além das parceiras óbvias.',
    '<b>Fortaleza por 7 mil milhas.</b> A American cobra preço fixo em trechos '
    'assim, mesmo o voo sendo da Gol. A mesma passagem estava R$ 1.400 em '
    'dinheiro.',
]))

story.append(Spacer(1, 0.25*cm))
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
    'Capítulo 08',
    'Estratégia mês a mês para 2026 e 2027.',
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
    'Use este período pra acumular pensando <b>no ano seguinte</b>. Sim, com '
    'essa antecedência toda. Setembro costuma trazer o aquecimento da Black Friday, que '
    'historicamente traz os melhores bônus do ano. Comece a desenhar o destino '
    'do ano seguinte: avião com bom preço em milhas costuma sair em janeiro do '
    'ano da viagem.', S['body']))

story.append(Paragraph('Trimestre 4: Outubro a Dezembro', S['h3']))
story.append(Paragraph(
    'A grande temporada. Black Friday em novembro traz as melhores '
    'condições do ano. Plano: junte saldo ao longo do ano, e na Black '
    'Friday faça a transferência maior. Dezembro é o mês de emitir, '
    'transformando em passagem o que você acumulou o ano inteiro.', S['body']))

# ============================================================
# 11 - Cap 8 - Salas VIP
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 09',
    'Salas VIP, a vantagem oculta dos premiums.',
    'Boa parte do valor de um cartão premium não está nos pontos. Está nas '
    'salas VIP, que mudam por completo a experiência da viagem.'
))

story.append(Paragraph(
    'Cartões com anuidade a partir de R$ 800 normalmente já vêm com acesso a '
    'salas VIP nacionais. Quando você viaja em família, o benefício é direto: '
    'em vez de pagar R$ 200 a R$ 400 por pessoa em cada conexão, vocês entram '
    'sem pagar e ainda comem, descansam e trabalham com Wi-Fi decente.',
    S['body']))

story.append(Paragraph('Os programas que dão o acesso', S['h2']))
story.append(Paragraph(
    'O acesso quase nunca vem do banco direto: vem de um programa de salas que '
    'o cartão te dá de brinde. Vale saber o nome deles, porque é o que você vai '
    'procurar na descrição do cartão:', S['body']))

story.extend(bullet_list([
    '<b>Priority Pass.</b> O mais conhecido e o de maior rede mundial.',
    '<b>LoungeKey.</b> Muito comum em cartões Mastercard no Brasil.',
    '<b>Dragon Pass.</b> Forte na Ásia, e aparece em cartões brasileiros.',
    '<b>Visa Airport Companion.</b> O programa da Visa, que substituiu o antigo '
    'acesso via LoungeKey em boa parte dos cartões.',
]))

story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    'Conferir qual desses o cartão oferece, e quantas entradas por ano, vale '
    'mais do que olhar o nome do metal do cartão. Dois cartões de anuidade '
    'parecida podem dar acessos completamente diferentes.', S['body']))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('sala_vip/IMG_6353.jpg', 'sala_vip/IMG_7453.jpg', h=6.5*cm))
story.append(caption('Centurion Lounge, da American Express, e uma das salas que usamos nos Estados Unidos.'))

story.append(Paragraph('E tem o caminho de fora da lista', S['h2']))
story.append(Paragraph(
    'Nem todo acesso passa por esses programas. Alguns cartões abrem portas por '
    'rede própria, e às vezes bem mais portas do que um Priority Pass básico.',
    S['body']))

story.append(Callout(
    'O nosso caso: Amex The Platinum Card',
    'É o cartão que mais nos dá sala, e a gente o usa sem pagar anuidade, '
    'que é o tipo de negociação que vale sempre tentar. Com ele entramos nas '
    'salas Bradesco e parceiras, o que cobre praticamente todo aeroporto '
    'brasileiro relevante, e também em salas na maior parte dos aeroportos '
    'grandes dos Estados Unidos. Numa viagem com sete embarques, como a que '
    'contamos no capítulo 06, isso muda a viagem inteira.', kind='tip'))

story.append(Paragraph('Como aproveitar de verdade', S['h2']))
story.extend(bullet_list([
    'Chegue antes. A sala vale pelo conforto e pela refeição, então 3h antes do voo internacional é um plano, não um exagero.',
    'Confira a regra de acompanhante <b>antes de chegar na porta</b>: alguns cartões liberam um, outros dois, outros nenhum. Com criança junto, esse detalhe decide se a família entra inteira.',
    'Use no Brasil também, não só lá fora: Bradesco, Copa Club, Star Alliance, GRU Lounge, Plaza Premium.',
    'Em conexão longa, de 8h ou mais, a sala deixa de ser luxo e vira a diferença entre chegar inteiro ou destruído.',
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
