"""
Ebook 1 — Manual Completo de Pontos 2026
"""
import os
from reportlab.platypus import Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.units import cm
from framework import (
    EbookDoc, PDF_DIR, styles, cover_block, photo, two_col_photo_row,
    caption, bullet_list, data_table, section_opener, toc, back_cover_block,
    Callout, Divider, StatStrip, to_content, to_cover, C
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
    subtitle='O guia direto da família que vive de milhas há 9 países.',
    year='2026',
))

# ============================================================
# 02 — Boas-vindas
# ============================================================
story.extend(to_content())

story.append(Paragraph('BEM-VINDO', S['eyebrow']))
story.append(Paragraph('Antes de tudo: um café e uma promessa.', S['h1']))
story.append(Divider(width_pct=0.18, gap_before=0.1*cm, gap_after=0.3*cm))

story.append(Paragraph(
    'Este ebook foi escrito pela nossa família — Jefferson, Kharol e Derek — '
    'enquanto planejávamos a nossa próxima viagem internacional. Não tem teoria '
    'que a gente não tenha aplicado. Não tem cartão recomendado que a gente não '
    'use. E não tem estratégia que a gente não tenha testado pessoalmente, '
    'transferindo milhas reais e emitindo passagens reais.', S['body']))

story.append(Paragraph(
    'O que você vai ler aqui é o que aprendemos depois de mais de <b>1 milhão de '
    'pontos acumulados</b> e <b>9 países visitados em 2 anos</b>. Sem fórmula '
    'milagrosa, sem promessa de viagem grátis: <b>milhas não substituem o '
    'planejamento</b>, mas, quando bem usadas, transformam o custo de qualquer '
    'viagem internacional.', S['body']))

story.append(Spacer(1, 0.3*cm))
story.append(Callout(
    'A promessa deste ebook',
    'Ao terminar a leitura você vai saber escolher seu cartão, entender quando '
    'transferir, calcular o custo real de uma milha e desenhar um plano de '
    'acumulação realista para a sua próxima viagem — em qualquer ponto que você '
    'esteja hoje.', kind='note'))

story.append(Spacer(1, 0.4*cm))
story.append(StatStrip([
    ('9', 'países visitados\nem 2 anos'),
    ('1M+', 'pontos sob\nplanejamento'),
    ('R$ 95k', 'em passagens\neconomizadas'),
]))

# ============================================================
# 03 — Sumário
# ============================================================
story.append(PageBreak())
story.append(Paragraph('SUMÁRIO', S['eyebrow']))
story.append(Paragraph('O que você vai aprender.', S['h1']))
story.append(Divider(width_pct=0.18))
story.append(Spacer(1, 0.3*cm))
story.append(toc([
    ('Como funcionam pontos e milhas no Brasil', '05'),
    ('Como escolher seu primeiro cartão (e o próximo)', '08'),
    ('Os programas de coalizão e a transferência', '12'),
    ('Calendário de bônus — o jogo do timing', '15'),
    ('Custo por milha — a regra de ouro', '18'),
    ('Estratégia mês a mês para 2026', '21'),
    ('Salas VIP — a vantagem oculta dos premiums', '24'),
    ('Próximos passos: comunidade e assessoria', '27'),
]))

# ============================================================
# 04 — CAPÍTULO 1 — Como funcionam pontos e milhas
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
    'No Brasil, a viagem com pontos passa por três camadas que conversam entre si — '
    'mas que tem regras próprias. Entender essa separação é o que diferencia quem '
    'acumula pontos de quem realmente viaja com eles.', S['body']))

story.extend(bullet_list([
    '<b>Camada 1 — Emissores:</b> bancos e fintechs que emitem o cartão de '
    'crédito. Bradesco, Itaú, Santander, BTG, Inter, C6, Nubank.',
    '<b>Camada 2 — Programas de coalizão:</b> Livelo, Esfera, Iupp. '
    'Recebem os pontos do seu cartão e podem ser convertidos em diversos '
    'programas finais.',
    '<b>Camada 3 — Programas de companhias aéreas:</b> Latam Pass, Smiles, '
    'TudoAzul/Azul Fidelidade. É onde os pontos viram passagem.',
]))

story.append(Spacer(1, 0.2*cm))
story.append(Callout(
    'O pulo do gato é a camada 2',
    'A maioria das pessoas pula direto do cartão para a passagem. Quem entende a '
    'camada de coalizão (Livelo, Esfera, Iupp) ganha o dobro: pode esperar bônus '
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
    'Pontos têm validade — geralmente 24 meses no Livelo, 24 na Esfera, e '
    'variável em outros. Milhas em programas aéreos costumam ter validade '
    'parecida. Manter os pontos vivos significa fazer ao menos uma '
    'movimentação (compra ou transferência) dentro do prazo. <i>Mantenha um '
    'controle simples disso — vale a pena.</i>',
    S['body']))

# ============================================================
# 05 — CAPÍTULO 2 — Cartões
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
    'pensado — e quando ele compensa.', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(data_table([
    ['Perfil', 'Anuidade típica', 'Pontuação típica', 'Para quem é'],
    ['Entrada', 'Isento ou R$ 0–200', '1 ponto / R$ 2–3', 'Quem está começando, gasto até R$ 3k/mês'],
    ['Intermediário', 'R$ 300–700', '1 ponto / R$ 1,8', 'Gasto R$ 3–8k/mês, quer acumular para nacional'],
    ['Premium', 'R$ 800–1.500', '1,5–2 pontos / R$', 'Gasto R$ 8–20k/mês, mira internacional'],
    ['Ultra-premium', 'R$ 1.800–4.000+', '2–2,5 pontos / R$', 'Gasto alto + benefícios (salas VIP, seguros)'],
], col_widths=[3.2*cm, 3.5*cm, 4*cm, 5.5*cm]))

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
    'Cartões que não passam nessa conta saem da carteira — sem dó.', S['body']))

# ============================================================
# 06 — Cap 3 — Programas de coalizão
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 03',
    'Os programas de coalizão e a transferência.',
    'Aqui mora o jogo. É na transferência entre programas que pontos viram '
    'mais pontos — desde que você saiba esperar o momento certo.'
))

story.append(Paragraph('Os três grandes programas de coalizão', S['h2']))
story.append(Paragraph(
    'No Brasil, três programas concentram a maior parte da movimentação:', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(data_table([
    ['Programa', 'Quem pertence', 'Forte em', 'Transfere para'],
    ['Livelo', 'Bradesco + Banco do Brasil', 'Variedade de transferências', 'Latam, Smiles, TudoAzul, Iberia, AAdvantage…'],
    ['Esfera', 'Santander', 'Bônus agressivos pra Smiles', 'Smiles, Latam, TudoAzul, Air France…'],
    ['Iupp', 'Itaú', 'Integração com cartões Itaucard', 'Latam, Smiles, TudoAzul'],
], col_widths=[2.6*cm, 4*cm, 4.4*cm, 5.2*cm]))

story.append(Spacer(1, 0.3*cm))
story.append(Paragraph('Como uma transferência funciona, na prática', S['h2']))
story.append(Paragraph(
    'O fluxo padrão é: o cartão deposita pontos no programa de coalizão do banco '
    '(ex.: Livelo). Você acessa o programa, escolhe pra onde transferir e o '
    'quanto, e os pontos são convertidos em milhas no programa de destino '
    '(ex.: Latam Pass). Essa transferência <b>tem uma taxa de conversão</b> — em '
    'condições normais é <b>1:1</b>. Mas em campanhas de bônus, vira 1:1,6, '
    '1:1,8 ou até 1:2 (bônus de 100%).', S['body']))

story.append(Callout(
    'O segredo: quase sempre vale a pena esperar',
    'Transferências sem bônus são raramente justificáveis. Em média, 1–2 vezes '
    'por mês surge alguma campanha de bônus de pelo menos 60%. Pra acumular '
    'eficientemente, espere — sempre.', kind='tip'))

# ============================================================
# 07 — Cap 4 — Calendário de bônus
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 04',
    'Calendário de bônus — o jogo do timing.',
    'Esperar o bônus certo é a diferença entre 200k milhas e 400k milhas. '
    'A boa notícia: dá para prever.'
))

story.append(Paragraph('O calendário típico do ano', S['h2']))
story.append(Paragraph(
    'Os programas de coalizão repetem padrões. Em um ano, você costuma '
    'encontrar bônus de pelo menos 60% praticamente todo mês, mas as '
    'campanhas mais agressivas (80%, 100% ou mais) acontecem em janelas '
    'previsíveis:', S['body']))

story.extend(bullet_list([
    '<b>Janeiro:</b> campanhas de "ano novo, milhas novas" — bônus para '
    'incentivar a movimentação após o pico de gastos de dezembro.',
    '<b>Maio/Junho:</b> bônus pré-férias de julho, principalmente para '
    'Smiles e Latam Pass.',
    '<b>Setembro/Outubro:</b> aquecimento de Black Friday — historicamente '
    'os melhores bônus do ano.',
    '<b>Novembro:</b> Black Friday efetiva, com campanhas relâmpago de até 24h.',
    '<b>Dezembro:</b> bônus de fim de ano para captura de saldo antes da '
    'virada.',
]))

story.append(Callout(
    'Onde acompanhar os bônus',
    'Acompanhe o site do programa (notificações ativas), siga páginas de '
    'milhas no Instagram e participe da nossa newsletter — toda semana avisamos '
    'as campanhas que valem a pena. Inscreva-se em rotacomfamilia.com.',
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
# 08 — Cap 5 — Custo por milha
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 05',
    'Custo por milha — a regra de ouro.',
    'Existe uma conta única que separa quem viaja barato de quem acha que '
    'viaja barato. É a conta do custo por milha — e ela vale para qualquer '
    'cartão e qualquer programa.'
))

story.append(Paragraph('A fórmula', S['h2']))
story.append(Paragraph(
    'Custo por milha (R$/k) = (anuidade do cartão + qualquer taxa adicional) '
    '÷ (milhas geradas em um ano com bônus aplicado, em milhares).', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(Callout(
    'Faixas de referência',
    'Abaixo de R$ 25/k = excelente. Entre R$ 25 e R$ 35/k = bom. '
    'Entre R$ 35 e R$ 50/k = aceitável só se você fala muito de salas VIP. '
    'Acima de R$ 50/k = sai do cartão.', kind='note'))

story.append(Paragraph('Exemplo da nossa carteira', S['h2']))
story.append(Paragraph(
    'Nosso cartão principal gera, em média, 240.000 milhas por ano '
    'considerando bônus médios de 80%. A anuidade é R$ 1.180. Conta: '
    'R$ 1.180 ÷ 240 = <b>R$ 4,92/k</b>. Em milhares de milhas. Olhando o '
    'mercado, qualquer compra de milhas avulsas custa entre R$ 30 e R$ 60/k. '
    'Em outras palavras: nossas milhas saem por <b>1/10 do preço de mercado</b>. '
    'É essa conta que mantém o sistema rodando.', S['body']))

story.append(Paragraph('Quando ignorar a regra', S['h2']))
story.append(Paragraph(
    'Em duas situações vale "pagar caro" por uma milha:', S['body']))

story.extend(bullet_list([
    'Quando você precisa de uma data específica e a passagem em dinheiro '
    'está absurdamente cara (alta temporada, evento) — milhas viram seu '
    'desconto, mesmo que o custo por milha esteja em R$ 50.',
    'Quando o saldo está vencendo e você tem certeza de uma viagem nos '
    'próximos meses — melhor usar do que perder.',
]))

# ============================================================
# 09 — Cap 6 — Estratégia mês a mês
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 06',
    'Estratégia mês a mês para 2026.',
    'Um ano de milhas dá pra dividir em quatro estações. Aqui vai o plano '
    'que estamos seguindo na nossa família este ano.'
))

story.append(Paragraph('Trimestre 1 — Janeiro a Março', S['h3']))
story.append(Paragraph(
    'Foco em campanhas de início de ano. Limpe a casa: liste todos os '
    'saldos, anote validades, atualize os logins. Aproveite bônus de janeiro '
    'para Latam Pass se a viagem de meio do ano for via Latam, ou para '
    'Smiles se for via Gol/Air France. Use fevereiro para revisar cartões — '
    'se algum não passou no teste de custo por milha, peça pra trocar.',
    S['body']))

story.append(Paragraph('Trimestre 2 — Abril a Junho', S['h3']))
story.append(Paragraph(
    'Período de bônus pré-férias. Maio e junho costumam trazer campanhas '
    'agressivas para julho. Se a viagem de família é em julho, esta é a '
    'última janela útil pra acumular o saldo necessário sem pagar custos '
    'altos por milha.', S['body']))

story.append(Paragraph('Trimestre 3 — Julho a Setembro', S['h3']))
story.append(Paragraph(
    'Use este período pra acumular pensando em <b>2027</b>. Sim, com '
    'antecedência. Setembro tem bônus de até 100% para Esfera/Smiles — não '
    'perca. Comece a desenhar o destino do ano seguinte: avião com bom '
    'preço em milhas costuma sair em janeiro do ano da viagem.', S['body']))

story.append(Paragraph('Trimestre 4 — Outubro a Dezembro', S['h3']))
story.append(Paragraph(
    'A grande temporada. Black Friday em novembro traz as melhores '
    'condições do ano. Plano: junte saldo ao longo do ano, e na Black '
    'Friday faça a transferência maior. Dezembro é mês de emissão das '
    'passagens de meio de 2026.', S['body']))

# ============================================================
# 10 — Cap 7 — Salas VIP
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Capítulo 07',
    'Salas VIP — a vantagem oculta dos premiums.',
    'Boa parte do valor de um cartão premium não está nos pontos. Está nas '
    'salas VIP — que mudam por completo a experiência da viagem.'
))

story.append(Paragraph(
    'Cartões com anuidade a partir de R$ 800 normalmente já vêm com acesso '
    'a salas VIP nacionais. A partir de R$ 1.500, vêm com Priority Pass — '
    'acesso a centenas de salas no mundo inteiro, inclusive para acompanhantes. '
    'Quando você viaja em família, o benefício é direto: ao invés de pagar '
    'R$ 200–400 por pessoa em cada conexão, você entra de graça e ainda come, '
    'descansa e trabalha com Wi-Fi de qualidade.', S['body']))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('IMG_5235.jpg', 'IMG_4808.jpg', h=6.5*cm))
story.append(caption('W Lounge (GRU, Star Alliance) à esquerda · Bradesco Lounge à direita — duas das salas que mais usamos.'))

story.append(Paragraph('Como aproveitar de verdade', S['h2']))
story.extend(bullet_list([
    'Chegue antes — salas valem pelo conforto e pela refeição. Plano: 3h antes do voo internacional.',
    'Inclua os dependentes: cartões premium permitem acompanhantes, mas regras variam (1, 2 ou ilimitado).',
    'Use mesmo no Brasil — Copa Club, Star Alliance Gold, GRU Lounge, Plaza Premium.',
    'Em escalas internacionais, salas VIP "salvam" viagens de 8h+ de conexão.',
]))

story.append(Spacer(1, 0.3*cm))
story.append(photo('IMG_8543.jpg', max_h=8*cm))
story.append(caption('Copa Club Star Alliance Gold — a sala que viramos clube em viagens longas.'))

# ============================================================
# 11 — Fechamento
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Próximos passos',
    'Continue conosco — você não está sozinho nessa.',
    'A parte teórica acabou. Agora começa a aplicação — e é aí que a '
    'comunidade faz a diferença.'
))

story.append(Paragraph('O que fazer hoje', S['h2']))
story.extend(bullet_list([
    'Anote todos os seus saldos em Livelo, Esfera, Iupp, Latam, Smiles, Azul.',
    'Calcule o custo por milha de cada cartão que você tem hoje.',
    'Decida o destino da próxima viagem em família e a meta de milhas necessárias.',
    'Inscreva-se na newsletter da Rota com Família — alertas semanais de bônus.',
    'Se preferir não fazer sozinho, considere nossa assessoria personalizada.',
]))

story.append(Spacer(1, 0.3*cm))
story.append(Callout(
    'Quer um plano sob medida pra sua família?',
    'Eu (Jefferson) emito passagens com milhas para outras famílias todo mês — '
    'nacional e internacional. Mando o plano em PDF, faço as transferências '
    'junto com você e entrego os bilhetes prontos. Fale comigo no WhatsApp '
    'ou em contato@rotacomfamilia.com.', kind='note'))

story.extend(back_cover_block(
    'Esperamos que este manual seja só o começo da sua próxima viagem em família. '
    'A gente ama trocar ideia com quem está nessa jornada — manda mensagem pra '
    'gente conta o que você está planejando.'))

# ============================================================
# Build
# ============================================================
doc.build(story)
print(f'OK — {OUTFILE}')
