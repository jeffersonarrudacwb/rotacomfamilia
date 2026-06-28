"""
Ebook 3 — Bônus: Planilhas e Calculadoras
"""
import os
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from framework import (
    EbookDoc, PDF_DIR, styles, cover_block, photo,
    caption, bullet_list, data_table, section_opener, toc, back_cover_block,
    Callout, Divider, StatStrip, to_content,
    C, SANS, SANS_BOLD, SERIF, PAGE, MARGIN
)

OUTFILE = os.path.join(PDF_DIR, '03-planilhas-calculadoras.pdf')
TITLE = 'Bônus · Planilhas & Calculadoras'

doc = EbookDoc(OUTFILE, TITLE)
S = styles()
story = []


def worksheet_row(label, slots=4, slot_w=2.5*cm, label_w=4.5*cm):
    """A single row of an imprimable worksheet (label + N empty cells)."""
    cells = [Paragraph(f'<b>{label}</b>', ParagraphStyleSmall())] + [''] * slots
    t = Table([cells], colWidths=[label_w] + [slot_w]*slots, rowHeights=[0.95*cm])
    t.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1), 0.4, C['border']),
        ('BACKGROUND',(0,0),(0,0), C['sand']),
        ('BACKGROUND',(1,0),(-1,-1), HexColor('#FFFFFF')),
        ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1), 0.3*cm),
        ('RIGHTPADDING',(0,0),(-1,-1), 0.3*cm),
    ]))
    return t


def ParagraphStyleSmall():
    from reportlab.lib.styles import ParagraphStyle
    return ParagraphStyle('ws', fontName=SANS_BOLD, fontSize=9.5, leading=12, textColor=C['deep'])


# ============================================================
# COVER
# ============================================================
story.extend(cover_block(
    title='Planilhas<br/>& Calculadoras',
    subtitle='O kit prático que acompanha o Manual de Pontos 2026.',
    year='Bônus',
))

# ============================================================
# Welcome
# ============================================================
story.extend(to_content())

story.append(Paragraph('BÔNUS · KIT PRÁTICO', S['eyebrow']))
story.append(Paragraph('Para fazer a teoria virar conta.', S['h1']))
story.append(Divider(width_pct=0.18, gap_before=0.1*cm, gap_after=0.3*cm))

story.append(Paragraph(
    'Este caderno é o complemento prático do <b>Manual Completo de Pontos 2026</b>. '
    'Enquanto o manual te ensina <i>como</i> o jogo funciona, aqui você tem as '
    'ferramentas pra colocar tudo em ordem na sua família: 5 calculadoras e '
    'planilhas que a gente usa todo mês.', S['body']))

story.append(Paragraph(
    'Você pode imprimir e preencher à mão, ou usá-las como referência pra montar '
    'a sua versão digital. Quem quiser as versões em Google Sheets prontas pra '
    'editar pode baixar gratuitamente em <b>rotacomfamilia.com/kit</b>.',
    S['body']))

story.append(Spacer(1, 0.4*cm))
story.append(Callout(
    'Como usar este caderno',
    'Faça uma vez no início do ano. Revise no início de cada trimestre. '
    'A mágica não está em preencher uma vez — está em ter o controle vivo, '
    'sabendo onde estão seus pontos e pra onde eles vão.', kind='tip'))

# ============================================================
# TOC
# ============================================================
story.append(PageBreak())
story.append(Paragraph('SUMÁRIO', S['eyebrow']))
story.append(Paragraph('As 5 ferramentas.', S['h1']))
story.append(Divider(width_pct=0.18))
story.append(Spacer(1, 0.3*cm))
story.append(toc([
    ('Calculadora · Custo por milha', '04'),
    ('Planilha · Controle de saldo', '07'),
    ('Plano · Acumulação mensal por destino', '10'),
    ('Comparativo · Avaliação de cartões', '13'),
    ('Calendário · Bônus esperados em 2026', '16'),
]))

# ============================================================
# 01 — CALCULADORA: Custo por milha
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Ferramenta 01',
    'Calculadora de custo por milha.',
    'A conta única que decide se um cartão fica ou sai da carteira. Faça '
    'pra cada um dos cartões que você tem hoje — e pros cartões que está '
    'pensando em pegar.'
))

story.append(Paragraph('A fórmula', S['h2']))
story.append(Paragraph(
    'Custo por milha (R$ por mil milhas) = '
    '<b>(Anuidade + tarifas anuais)</b>  ÷  '
    '<b>(Milhas geradas no ano com bônus ÷ 1.000)</b>.', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(Callout(
    'Faixas de referência',
    'Abaixo de R$ 25/k = excelente · R$ 25–35/k = bom · R$ 35–50/k = aceitável '
    'só se houver benefícios (sala VIP, seguros) · acima de R$ 50/k = troque '
    'o cartão.', kind='note'))

story.append(Paragraph('Exemplo preenchido', S['h2']))
story.append(data_table([
    ['Item', 'Valor'],
    ['Cartão', 'Premium ABC'],
    ['Anuidade anual', 'R$ 1.180'],
    ['Outras tarifas (saque, manutenção)', 'R$ 0'],
    ['Gasto mensal médio', 'R$ 8.500'],
    ['Pontuação (pontos por R$ gasto)', '2,0'],
    ['Pontos gerados no ano (gasto × 12 × pontuação)', '204.000'],
    ['Bônus médio de transferência aplicado', '+80%'],
    ['Milhas finais no ano', '367.200'],
    ['Custo por mil milhas', 'R$ 1.180 ÷ 367,2 = R$ 3,21/k'],
    ['Avaliação', 'Excelente — manter'],
], col_widths=[8*cm, 8.7*cm]))

# Empty worksheet
story.append(PageBreak())
story.append(Paragraph('FOLHA IMPRIMÍVEL', S['eyebrow']))
story.append(Paragraph('Preencha pra cada cartão da sua carteira.', S['h2']))
story.append(Divider(width_pct=0.15, gap_before=0.1*cm, gap_after=0.3*cm))

# Worksheet rows
ws_rows = [
    'Nome do cartão',
    'Anuidade anual (R$)',
    'Outras tarifas (R$)',
    'Gasto mensal (R$)',
    'Pontos por R$',
    'Pontos no ano',
    'Bônus médio (%)',
    'Milhas no ano',
    'Custo / mil (R$/k)',
    'Avaliação',
]
for r in ws_rows:
    story.append(worksheet_row(r, slots=4, slot_w=2.8*cm, label_w=4.5*cm))

story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    '<i>Espaço pros 4 cartões mais importantes da sua carteira. '
    'Se tiver mais, imprima outra folha.</i>', S['small']))

# ============================================================
# 02 — Controle de saldo
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Ferramenta 02',
    'Planilha de controle de saldo.',
    'Onde estão seus pontos agora — e quando eles vencem. Sem isso, ponto '
    'vencido é prejuízo certo.'
))

story.append(Paragraph('Estrutura sugerida', S['h2']))
story.append(data_table([
    ['Programa', 'Saldo atual', 'Validade', 'Próxima ação'],
    ['Livelo', '189.400', 'Mar/2027', 'Esperar bônus Latam 80%'],
    ['Esfera', '120.900', 'Set/2027', 'Esperar bônus Smiles'],
    ['Iupp', '34.200', 'Dez/2026', 'Acumular mais (juntar 50k)'],
    ['Latam Pass', '78.100', 'Jul/2027', 'Reservar pra Orlando 2027'],
    ['Smiles', '24.000', 'Out/2026', 'URGENTE: usar ou transferir'],
    ['Azul/TudoAzul', '12.500', 'Mai/2027', 'Acumular ou trocar produto'],
], col_widths=[3.8*cm, 3*cm, 3*cm, 6.9*cm]))

story.append(Callout(
    'Frequência ideal de atualização',
    'A cada 15 dias, somando 3–5 minutos de checagem em cada programa. '
    'O calendário aqui é o seu seguro contra pontos vencidos.', kind='tip'))

# Empty version
story.append(PageBreak())
story.append(Paragraph('FOLHA IMPRIMÍVEL', S['eyebrow']))
story.append(Paragraph('Seu saldo, sua estratégia.', S['h2']))
story.append(Divider(width_pct=0.15, gap_before=0.1*cm, gap_after=0.3*cm))

# Empty 10-row table
empty_rows = [['Programa', 'Saldo atual', 'Validade', 'Próxima ação']]
for _ in range(10):
    empty_rows.append(['', '', '', ''])
empty_t = Table(empty_rows, colWidths=[3.8*cm, 3*cm, 3*cm, 6.9*cm], rowHeights=[0.9*cm]*11)
empty_t.setStyle(TableStyle([
    ('GRID',(0,0),(-1,-1), 0.4, C['border']),
    ('BACKGROUND',(0,0),(-1,0), C['deep']),
    ('TEXTCOLOR',(0,0),(-1,0), C['cream']),
    ('FONTNAME',(0,0),(-1,0), SANS_BOLD),
    ('FONTSIZE',(0,0),(-1,0), 9.5),
    ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
    ('LEFTPADDING',(0,0),(-1,-1), 0.3*cm),
]))
story.append(empty_t)

# ============================================================
# 03 — Plano de acumulação
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Ferramenta 03',
    'Plano de acumulação mensal por destino.',
    'Quanta milha você precisa juntar até o embarque — e quanto isso '
    'representa por mês? Esta planilha resolve.'
))

story.append(Paragraph('Como funciona', S['h2']))
story.append(Paragraph(
    '<b>Passo 1:</b> defina o destino e a quantidade de milhas por passageiro '
    '(use as tabelas de Benchmark do Ebook de Roteiros).<br/>'
    '<b>Passo 2:</b> multiplique pelo número de passageiros.<br/>'
    '<b>Passo 3:</b> conte os meses até o embarque.<br/>'
    '<b>Passo 4:</b> divida — esta é a sua meta mensal de pontos.',
    S['body']))

story.append(Paragraph('Exemplo: Família para Orlando, abril de 2027', S['h2']))
story.append(data_table([
    ['Item', 'Valor'],
    ['Destino', 'Orlando (MCO)'],
    ['Mês do embarque', 'Abril/2027'],
    ['Milhas por pessoa (econômica)', '90.000 Latam Pass'],
    ['Número de passageiros', '3'],
    ['Total de milhas necessárias', '270.000'],
    ['Saldo atual de pontos (Livelo + Esfera)', '142.000'],
    ['Faltam', '128.000'],
    ['Meses até embarque', '12'],
    ['Bônus médio esperado (transferência)', '80%'],
    ['Pontos a acumular por mês', '~5.900'],
    ['Gasto mensal necessário (a 1,8 pts/R$)', '~R$ 3.300'],
], col_widths=[8*cm, 8.7*cm]))

story.append(Spacer(1, 0.3*cm))
story.append(Callout(
    'A leitura honesta',
    'Se a meta mensal pede um gasto que você não tem hoje, três caminhos: '
    '(a) estender o prazo da viagem em 6–12 meses, (b) escolher destino mais '
    'barato em milhas, ou (c) revisar a categoria do cartão pra puxar mais '
    'pontos por R$ gasto.', kind='note'))

# Empty
story.append(PageBreak())
story.append(Paragraph('FOLHA IMPRIMÍVEL', S['eyebrow']))
story.append(Paragraph('Seu plano de acumulação.', S['h2']))
story.append(Divider(width_pct=0.15, gap_before=0.1*cm, gap_after=0.3*cm))

plan_labels = [
    'Destino',
    'Mês do embarque',
    'Milhas por pessoa',
    'Número de passageiros',
    'Total necessário',
    'Saldo atual',
    'Faltam',
    'Meses até embarque',
    'Bônus médio esperado (%)',
    'Pontos a acumular / mês',
    'Gasto mensal necessário (R$)',
]
for lbl in plan_labels:
    story.append(worksheet_row(lbl, slots=1, slot_w=10*cm, label_w=6.5*cm))

# ============================================================
# 04 — Comparativo de cartões
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Ferramenta 04',
    'Comparativo de cartões.',
    'Quando você está decidindo entre 2 ou 3 cartões, esta planilha mostra '
    'o vencedor em segundos.'
))

story.append(Paragraph('Como ler', S['h2']))
story.append(Paragraph(
    'Coloque os candidatos lado a lado. O cartão vencedor é aquele com '
    '<b>maior ganho líquido</b> dentro do seu padrão de gasto. Cuidado: salas '
    'VIP e seguros valem dinheiro real — pra família que viaja, podem '
    'compensar uma anuidade R$ 500 maior.', S['body']))

story.append(Paragraph('Modelo preenchido', S['h2']))
story.append(data_table([
    ['Critério', 'Cartão A', 'Cartão B', 'Cartão C'],
    ['Anuidade anual', 'R$ 580', 'R$ 1.180', 'R$ 2.700'],
    ['Pontuação (pts/R$)', '1,8', '2,2', '2,5'],
    ['Programa atrelado', 'Livelo', 'Esfera', 'Latam Pass direto'],
    ['Sala VIP nacional', 'Não', 'Sim', 'Sim'],
    ['Priority Pass', 'Não', '4/ano', 'Ilimitado'],
    ['Seguros (auto/viagem)', 'Básico', 'Completo', 'Completo+'],
    ['Pontos/ano com R$ 6k/mês', '129.600', '158.400', '180.000'],
    ['Valor estimado dos pontos', 'R$ 4.500', 'R$ 5.500', 'R$ 6.300'],
    ['Ganho líquido', 'R$ 3.920', 'R$ 4.320', 'R$ 3.600'],
    ['Veredito', '✓ Bom', '★ Melhor', 'Avaliar uso'],
], col_widths=[4.5*cm, 4*cm, 4.2*cm, 4*cm]))

# Empty version
story.append(PageBreak())
story.append(Paragraph('FOLHA IMPRIMÍVEL', S['eyebrow']))
story.append(Paragraph('Compare seus candidatos.', S['h2']))
story.append(Divider(width_pct=0.15, gap_before=0.1*cm, gap_after=0.3*cm))

comp_labels = [
    'Nome do cartão',
    'Anuidade (R$)',
    'Pontos por R$',
    'Programa atrelado',
    'Sala VIP nacional?',
    'Priority Pass?',
    'Seguros',
    'Pontos/ano (gasto × 12 × pts)',
    'Valor dos pontos (R$)',
    'Ganho líquido (R$)',
    'Sua nota',
]
for lbl in comp_labels:
    story.append(worksheet_row(lbl, slots=3, slot_w=3.5*cm, label_w=4.7*cm))

# ============================================================
# 05 — Calendário de bônus
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Ferramenta 05',
    'Calendário visual de bônus 2026.',
    'O que esperar de cada mês, baseado em 5 anos de histórico de campanhas '
    'no mercado brasileiro de milhas.'
))

cal_rows = [
    ['Mês', 'Bônus típico', 'Foco recomendado'],
    ['Janeiro', '60–80%', 'Limpeza de saldo + transferência se viagem em junho'],
    ['Fevereiro', '50–70%', 'Mês mais fraco — só transfira se urgência'],
    ['Março', '70–90%', 'Latam Pass costuma puxar — bom mês para fechar saldo'],
    ['Abril', '60–80%', 'Boa janela pra emitir passagens de julho'],
    ['Maio', '80–100%', '★ Janela pré-férias — uma das melhores do ano'],
    ['Junho', '60–80%', 'Já é tarde pra viagem de julho — pense em outubro'],
    ['Julho', '50–70%', 'Mês fraco — aproveite pra acumular pontos'],
    ['Agosto', '70–90%', 'Mês ótimo de transferência pra Smiles'],
    ['Setembro', '80–100%', '★ Pré-Black Friday — bom espelho de novembro'],
    ['Outubro', '90–110%', '★★ Black Friday warm-up — transfira aqui'],
    ['Novembro', '100–130%', '★★★ Black Friday cheia — o pico do ano'],
    ['Dezembro', '70–90%', 'Janela final pra emitir passagens do 1º semestre'],
]

cal_t = Table(cal_rows, colWidths=[2.5*cm, 3.5*cm, 10.7*cm])
cal_t.setStyle(TableStyle([
    ('GRID',(0,0),(-1,-1), 0.4, C['border']),
    ('BACKGROUND',(0,0),(-1,0), C['deep']),
    ('TEXTCOLOR',(0,0),(-1,0), C['cream']),
    ('FONTNAME',(0,0),(-1,0), SANS_BOLD),
    ('FONTSIZE',(0,0),(-1,0), 10),
    ('FONTNAME',(0,1),(-1,-1), SANS),
    ('FONTSIZE',(0,1),(-1,-1), 9.5),
    ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
    ('LEFTPADDING',(0,0),(-1,-1), 0.3*cm),
    ('TOPPADDING',(0,0),(-1,-1), 0.22*cm),
    ('BOTTOMPADDING',(0,0),(-1,-1), 0.22*cm),
    ('ROWBACKGROUNDS',(0,1),(-1,-1), [C['cream'], C['sand']]),
    ('TEXTCOLOR',(0,1),(-1,-1), C['text']),
    # Highlight strong months
    ('BACKGROUND',(0,5),(-1,5), HexColor('#F7E1B8')),   # Mai
    ('BACKGROUND',(0,9),(-1,9), HexColor('#F7E1B8')),   # Set
    ('BACKGROUND',(0,10),(-1,10), HexColor('#F2D29A')),  # Out
    ('BACKGROUND',(0,11),(-1,11), HexColor('#E8B66C')),  # Nov
]))
story.append(cal_t)

story.append(Spacer(1, 0.3*cm))
story.append(Callout(
    'O melhor mês de 2026 (provavelmente)',
    'Históricamente, novembro entrega os bônus mais altos. Para a família que '
    'tem viagem em meados de 2027, novembro de 2026 é a sua hora — guarde '
    'saldo até lá, faça a maior transferência do ano em uma única janela.',
    kind='tip'))

# ============================================================
# Closing
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Próximos passos',
    'Pegue as versões digitais.',
    'Tudo isso aqui em Google Sheets editável, gratuito, em '
    'rotacomfamilia.com/kit. Imprima, preencha, atualize.'
))

story.append(Paragraph('Por que vale digitalizar?', S['h2']))
story.extend(bullet_list([
    'Você atualiza saldos em tempo real (e dispara alertas automáticos).',
    'Compartilha a planilha com o cônjuge — orçamento + viagem em um lugar só.',
    'Histórico salvo: ano que vem você usa o mesmo modelo, sem retrabalho.',
    'Soma com calculadora de bolso = decisão em segundos.',
]))

story.append(Spacer(1, 0.3*cm))
story.append(Callout(
    'Quer que a gente monte o plano?',
    'Assessoria personalizada da Rota faz o serviço completo: '
    'analisa sua carteira, monta o plano, transfere com você e emite. '
    'Para detalhes, contato@rotacomfamilia.com.', kind='note'))

story.extend(back_cover_block(
    'Esperamos que esse kit te ajude tanto quanto nos ajudou. '
    'Manda foto da sua planilha preenchida — adoramos ver outras '
    'famílias entrando no controle.'))

# ============================================================
doc.build(story)
print(f'OK — {OUTFILE}')
