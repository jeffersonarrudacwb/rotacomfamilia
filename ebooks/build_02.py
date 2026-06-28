"""
Ebook 2 — Roteiros Prontos: EUA, Europa, Caribe
"""
import os
from reportlab.platypus import Paragraph, Spacer, PageBreak
from reportlab.lib.units import cm
from framework import (
    EbookDoc, PDF_DIR, styles, cover_block, photo, two_col_photo_row,
    caption, bullet_list, data_table, section_opener, toc, back_cover_block,
    Callout, Divider, StatStrip, to_content, C
)

OUTFILE = os.path.join(PDF_DIR, '02-roteiros-eua-europa-caribe.pdf')
TITLE = 'Roteiros Prontos · EUA, Europa, Caribe'

doc = EbookDoc(OUTFILE, TITLE)
S = styles()
story = []

# ============================================================
# COVER
# ============================================================
story.extend(cover_block(
    title='Roteiros<br/>Prontos',
    subtitle='Nove viagens reais da nossa família, com dias, custos e o que vale.',
    year='2026',
))

# ============================================================
# Welcome
# ============================================================
story.extend(to_content())

story.append(Paragraph('UM EBOOK ROTA COM FAMÍLIA', S['eyebrow']))
story.append(Paragraph('Os roteiros que estão nestas páginas.', S['h1']))
story.append(Divider(width_pct=0.18, gap_before=0.1*cm, gap_after=0.3*cm))

story.append(Paragraph(
    'Cada destino que você vai ler aqui foi feito — não pesquisado. Comemos nos '
    'restaurantes que indicamos. Erramos nas paradas. Acertamos em outras. Este '
    'ebook é o que a gente gostaria de ter recebido antes de cada viagem que '
    'fizemos como família entre 2024 e 2026.', S['body']))

story.append(Paragraph(
    'Os roteiros estão escritos no formato <b>3 a 5 dias</b> — o tempo médio que '
    'uma família consegue tirar pra um destino sem virar maratona. Para cada um, '
    'incluímos custo benchmark em milhas, sugestão de hospedagem e nossas dicas '
    'práticas. Não é uma lista exaustiva: é o que a gente faria de novo.',
    S['body']))

story.append(Spacer(1, 0.4*cm))
story.append(StatStrip([
    ('9', 'destinos\nneste ebook'),
    ('3+', 'continentes\nvisitados'),
    ('100%', 'roteiros\ntestados'),
]))

# ============================================================
# TOC
# ============================================================
story.append(PageBreak())
story.append(Paragraph('SUMÁRIO', S['eyebrow']))
story.append(Paragraph('Os 9 destinos.', S['h1']))
story.append(Divider(width_pct=0.18))
story.append(Spacer(1, 0.3*cm))
story.append(toc([
    ('Parte I · Estados Unidos', '05'),
    ('Orlando — Disney & parques', '06'),
    ('Las Vegas + Los Angeles', '10'),
    ('Nova York — clássica e moderna', '14'),
    ('Parte II · Europa', '18'),
    ('Lisboa & Porto', '19'),
    ('Madrid (e por que esticar)', '22'),
    ('Parte III · Caribe', '25'),
    ('Punta Cana — resort all-inclusive', '26'),
    ('Parte IV · América do Sul (bônus)', '29'),
    ('Buenos Aires, Santiago & Assunção', '30'),
]))

# ============================================================
# PARTE I - EUA - opening
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Parte I',
    'Estados Unidos.',
    'Três jeitos completamente diferentes de fazer EUA com a família — do '
    'parque temático ao deserto, da costa leste à costa oeste. Tudo testado '
    'em 3 viagens entre 2024 e 2026.'
))

story.append(Spacer(1, 0.3*cm))
story.append(photo('IMG_7613.jpg', max_h=9*cm))
story.append(caption('Magic Kingdom, Orlando — janeiro de 2026.'))

# ============================================================
# Orlando
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destino 01',
    'Orlando — Disney & parques.',
    'Para a família com filhos de 5 a 14 anos, Orlando é uma viagem que vale '
    'fazer pelo menos uma vez. O nosso Derek tinha 12 quando fomos em janeiro '
    'de 2026 — e funcionou perfeitamente.'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'GRU/GIG → MCO (com escala em Miami ou Panamá)'],
    ['Milhas/pessoa (econômica)', '80–100k Latam Pass · 70–90k Smiles'],
    ['Hospedagem', 'Hotéis Disney "value" (Art of Animation, Pop Century)'],
    ['Duração ideal', '7 dias (incluindo 4 a 5 dias de parque)'],
    ['Melhor época', 'Janeiro/fevereiro (baixa) ou setembro'],
], col_widths=[5*cm, 11.7*cm]))

story.append(Paragraph('Roteiro de 5 dias nos parques', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1 — Magic Kingdom.</b> O parque mais "Disney" de todos. Plano: chegar '
    'antes da abertura e ir direto pro Seven Dwarfs Mine Train. Almoço no Be Our '
    'Guest (reserva com 60 dias). Tarde: Pirates of Caribbean, Big Thunder. Fica '
    'até o show noturno do castelo.',
    '<b>Dia 2 — EPCOT.</b> Mais leve em montanha-russa, perfeito pro dia depois '
    'da maratona do Magic Kingdom. Faça a volta ao mundo pelo World Showcase. '
    'Test Track e Frozen Ever After são imperdíveis.',
    '<b>Dia 3 — Hollywood Studios.</b> Star Wars Galaxy\'s Edge é o highlight — '
    'a atração Rise of the Resistance vale a fila. Toy Story Land é ótimo pra '
    'crianças menores.',
    '<b>Dia 4 — Animal Kingdom.</b> Avatar Flight of Passage é a melhor '
    'atração da Disney inteira, na nossa opinião. Comece por ela.',
    '<b>Dia 5 — Universal (Islands of Adventure + Universal Studios).</b> '
    'Hogsmeade e Diagon Alley em sequência (use o Hogwarts Express). VelociCoaster '
    'pra quem aguenta — Derek adorou.',
]))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('IMG_7845.jpg', 'IMG_5690.jpg', h=6*cm))
story.append(caption('Town Square Theater (esquerda) e Cars Land na Art of Animation (direita) — momentos clássicos da viagem.'))

story.append(Callout(
    'A dica que faz a maior diferença',
    'Reserve restaurantes com 60 dias de antecedência (regra Disney). '
    'Restaurante bom é praticamente impossível de pegar no dia. Os imperdíveis: '
    'Be Our Guest, Cinderella\'s Royal Table, Sci-Fi Dine-In e Tusker House.',
    kind='tip'))

# ============================================================
# Las Vegas + LA
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destino 02',
    'Las Vegas + Los Angeles.',
    'A combinação clássica da costa oeste — uma cidade que é puro espetáculo '
    'e outra que é puro estilo de vida. Fizemos em maio de 2024 e voltamos '
    'em dezembro do mesmo ano (a segunda vez é melhor).'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'GRU → LAX (direto Latam) → LAS terrestre ou voo curto'],
    ['Milhas/pessoa', '95–110k Latam Pass · 85–100k Smiles'],
    ['Hospedagem Vegas', 'The Venetian, Wynn ou MGM Grand (resort fee é caro)'],
    ['Hospedagem LA', 'Santa Monica ou Beverly Hills (centro é menos turístico)'],
    ['Duração ideal', '7 dias (4 LA + 3 Vegas)'],
], col_widths=[5*cm, 11.7*cm]))

story.append(Paragraph('LA — 4 dias', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1:</b> Hollywood (Walk of Fame, TCL Chinese Theatre, Hollywood Sign do Griffith Observatory).',
    '<b>Dia 2:</b> Santa Monica Pier de manhã, Venice Beach de tarde, jantar no The Cheesecake Factory.',
    '<b>Dia 3:</b> Universal Studios — dia inteiro. Studio Tour é melhor que muitas atrações.',
    '<b>Dia 4:</b> Rodeo Drive (Beverly Hills) + The Grove (compras + cinema). Saída noturna pra Vegas.',
]))

story.append(Paragraph('Vegas — 3 dias', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1:</b> Strip de dia (Bellagio fountains, Venetian, Caesars), show de Cirque du Soleil à noite.',
    '<b>Dia 2:</b> Bate-volta ao Grand Canyon de helicóptero (caro, mas inesquecível) OU Red Rock Canyon.',
    '<b>Dia 3:</b> Compras nos outlets (Premium Outlets North) + jantar memorável (Gordon Ramsay).',
]))

story.append(Spacer(1, 0.2*cm))
story.append(photo('IMG_9554.jpg', max_h=7*cm))
story.append(caption('Cybertruck estacionado em Beverly Hills — o nível de surreal que LA entrega.'))

# ============================================================
# Nova York
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destino 03',
    'Nova York — clássica e moderna.',
    'Para a maioria das famílias, é a primeira viagem internacional dos sonhos. '
    'A gente foi em dezembro de 2024 — no Natal nova-iorquino, que é uma das '
    'experiências mais impactantes do ano.'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'GRU/GIG → JFK ou EWR (Latam, American, Delta)'],
    ['Milhas/pessoa', '95–120k Latam Pass · 90–110k Smiles'],
    ['Hospedagem', 'Midtown (38th–58th) — perto de tudo, mas caro'],
    ['Duração ideal', '5 dias'],
    ['Melhor época', 'Dezembro (Natal) ou maio/junho (clima)'],
], col_widths=[5*cm, 11.7*cm]))

story.append(Paragraph('Roteiro de 5 dias', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1:</b> Times Square + Top of the Rock (vista melhor que Empire State) + show da Broadway.',
    '<b>Dia 2:</b> Central Park (de bike) + Metropolitan Museum + jantar no Upper East Side.',
    '<b>Dia 3:</b> Estátua da Liberdade (ferry de manhã cedo) + Wall Street + caminhada na Brooklyn Bridge (volta de Manhattan pro Brooklyn).',
    '<b>Dia 4:</b> SoHo + Chinatown + Little Italy + High Line. Jantar no Meatpacking District.',
    '<b>Dia 5:</b> Compras na Quinta Avenida + Empire State (à noite) + adeus em Times Square.',
]))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('IMG_2567.jpg', 'c1d56598-f55e-4216-89f3-6786180ac897.jpg', h=8*cm))
story.append(caption('Times Square à noite (esquerda) e Brooklyn Bridge ao pôr do sol (direita).'))

story.append(Callout(
    'A dica de mobilidade',
    'Pegue o cartão "OMNY" do metrô — você passa o cartão de crédito direto na '
    'catraca, sem precisar comprar bilhete. Limite diário é US$ 34, ou seja, '
    'depois disso, é grátis pro resto da semana.', kind='tip'))

# ============================================================
# PARTE II - EUROPA - opening
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Parte II',
    'Europa.',
    'Para uma família brasileira começando a fazer Europa, o tripé '
    'Portugal-Espanha é imbatível: a língua ajuda, os voos são bem '
    'precificados em milhas e o ritmo de viagem é mais humano. Fizemos '
    'em abril de 2026.'
))

# ============================================================
# Lisboa & Porto
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destino 04',
    'Lisboa & Porto.',
    'A porta de entrada perfeita pra Europa. Em 6 dias dá pra fazer as '
    'duas cidades sem correr — e ainda esticar pra Sintra.'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'GRU → LIS (TAP, Latam, Air Europa)'],
    ['Milhas/pessoa', '95–115k Smiles · 100–120k Latam Pass'],
    ['Hospedagem Lisboa', 'Bairro Alto / Chiado (caminhável)'],
    ['Hospedagem Porto', 'Ribeira ou Cedofeita'],
    ['Lisboa ↔ Porto', 'Alfa Pendular (~3h) — comprar com antecedência'],
], col_widths=[5*cm, 11.7*cm]))

story.append(Paragraph('Lisboa — 3 dias', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1:</b> Alfama (Castelo de São Jorge, Sé, Miradouro de Santa Luzia). Jantar de fado.',
    '<b>Dia 2:</b> Belém (Torre, Mosteiro dos Jerónimos, MAAT, e claro, Pastéis de Belém).',
    '<b>Dia 3:</b> Sintra (bate-volta — Palácio da Pena + Quinta da Regaleira).',
]))

story.append(Paragraph('Porto — 3 dias', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1:</b> Ribeira, Livraria Lello, Estação São Bento, jantar tradicional.',
    '<b>Dia 2:</b> Vila Nova de Gaia (tour de vinho do Porto), cruzeiro pelos rios.',
    '<b>Dia 3:</b> Bate-volta ao Vale do Douro (vinícolas + paisagem).',
]))

story.append(Callout(
    'Onde Portugal ganha o jogo',
    'Comida boa e barata em qualquer lugar — almoço pra família por € 50 com '
    'sobremesa. E gente em geral muito acolhedora com brasileiro. Em todo lugar '
    'a gente foi tratado como vizinho.', kind='tip'))

# ============================================================
# Madrid
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destino 05',
    'Madrid (e por que esticar).',
    'Lisboa-Madrid é hoje o atalho ideal pra fazer Espanha quando você já '
    'está em Portugal. Voo de 1h15, custo baixo em milhas.'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'LIS → MAD (Iberia, TAP) com milhas'],
    ['Milhas/pessoa', '~15–25k Iberia Plus ou Latam Pass'],
    ['Hospedagem', 'Sol / Gran Vía (centro)'],
    ['Duração ideal', '3 dias'],
], col_widths=[5*cm, 11.7*cm]))

story.append(Paragraph('Roteiro de 3 dias', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1:</b> Plaza Mayor, Mercado de San Miguel (almoço), Palácio Real, El Retiro.',
    '<b>Dia 2:</b> Museu do Prado (pela manhã) + Reina Sofía (à tarde, ver Guernica de Picasso).',
    '<b>Dia 3:</b> Bate-volta a Toledo de trem (45 min) — cidade medieval imperdível.',
]))

story.append(Callout(
    'Quando esticar pra Barcelona',
    'Se você está em Madri por mais de 4 dias, vale dar um pulo a Barcelona via '
    'AVE (trem-bala, 2h30). Sagrada Família + Park Güell + Gótico em 3 dias '
    'dá um upgrade na viagem inteira.', kind='tip'))

# ============================================================
# PARTE III - CARIBE
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Parte III',
    'Caribe.',
    'Quando você quer férias de verdade — daquelas com pulseirinha all-inclusive '
    'e pé na areia. Em dezembro de 2025 fizemos Punta Cana e voltamos resetados.'
))

story.append(Spacer(1, 0.3*cm))
story.append(photo('IMG_6205.jpg', max_h=10*cm))
story.append(caption('Punta Cana, dezembro de 2025 — um dos dias mais leves do ano.'))

# ============================================================
# Punta Cana
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destino 06',
    'Punta Cana — resort all-inclusive.',
    'Nosso refúgio de fim de ano. Para a família que quer descansar de '
    'verdade — sem agenda, sem horário, sem sair do resort se não quiser.'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'GRU → PUJ (Latam, Copa via Panamá, Gol)'],
    ['Milhas/pessoa', '60–85k Latam Pass · 55–75k Smiles'],
    ['Hospedagem', 'Riu, Iberostar, Hyatt Ziva, Hard Rock — all-inclusive'],
    ['Duração ideal', '6 a 7 dias'],
    ['Melhor época', 'Dezembro a abril (alta) · Maio/junho (custo-benefício)'],
], col_widths=[5*cm, 11.7*cm]))

story.append(Paragraph('O ritmo da viagem', S['h2']))
story.extend(bullet_list([
    '<b>Dias 1–2:</b> Aclimatar — praia, piscina, restaurantes do resort.',
    '<b>Dia 3:</b> Excursão a Saona Island (catamarã, almoço na praia). Vale.',
    '<b>Dia 4:</b> Día livre — spa, esportes náuticos, ler na rede.',
    '<b>Dia 5:</b> Excursão a Hoyo Azul ou Macao Beach (snorkel).',
    '<b>Dia 6:</b> Último dia de praia + jantar no melhor restaurante do resort.',
]))

story.append(Callout(
    'A regra das pulseirinhas',
    'Em resort all-inclusive, a pulseirinha é a sua vida. Algumas categorias '
    'liberam restaurantes melhores e bebidas premium. Reservas de '
    'restaurante à la carte costumam abrir 1 ou 2 dias antes — chegue cedo '
    'no concierge no primeiro dia.', kind='tip'))

# ============================================================
# PARTE IV - AMÉRICA DO SUL
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Parte IV',
    'América do Sul (bônus).',
    'Pra família brasileira que quer começar a viajar pra fora, é o melhor '
    'investimento de milhas. Os destinos são culturalmente ricos, '
    'logisticamente fáceis e custam pouco — Buenos Aires, Santiago e Assunção.'
))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('IMG_2693.jpg', 'IMG_4085.jpg', h=7*cm))
story.append(caption('Caminito em Buenos Aires (esquerda) · Letreiro Chile Travel em Santiago (direita).'))

# ============================================================
# Buenos Aires, Santiago, Assunção — combined chapter
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destinos 07-08-09',
    'Buenos Aires, Santiago & Assunção.',
    'Três cidades, três personalidades — todas alcançáveis com baixo gasto '
    'de milhas. Roteiro express pra cada uma.'
))

story.append(Paragraph('Buenos Aires — 4 dias', S['h2']))
story.append(Paragraph(
    '<b>Milhas:</b> ~25–35k Latam Pass por passagem · <b>Voo:</b> 3h GRU → EZE. '
    '<b>Onde ficar:</b> Recoleta ou Palermo Soho. <b>Imperdíveis:</b> Bairro de '
    'La Boca (Caminito + estádio do Boca Juniors), Recoleta (cemitério + '
    'Museu de Belas Artes), Palermo (jantar no Don Julio se conseguir '
    'reserva), Tigre (bate-volta de barco). <b>Comida:</b> bife de chorizo '
    'em qualquer parrilla.', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(photo('1760b412-8ced-413f-84da-b6ee25a3aaf2.jpg', max_h=7*cm))
story.append(caption('Estádio do Boca Juniors — visita guiada vale a pena.'))

story.append(Paragraph('Santiago — 4 dias', S['h2']))
story.append(Paragraph(
    '<b>Milhas:</b> ~30–40k Latam Pass · <b>Voo:</b> 3h30 GRU → SCL. '
    '<b>Onde ficar:</b> Las Condes ou Providencia. <b>Imperdíveis:</b> Cerro San '
    'Cristóbal (teleférico + vista), Bellavista, Mercado Central (almoço de '
    'frutos do mar), Cajón del Maipo (excursão de 1 dia, cordilheira). '
    '<b>Esticar:</b> Vale do Maipo (vinícolas) ou Valparaíso (cidade '
    'colorida na costa).', S['body']))

story.append(Paragraph('Assunção — 2 a 3 dias', S['h2']))
story.append(Paragraph(
    '<b>Milhas:</b> ~20–28k Latam Pass · <b>Voo:</b> 2h GRU → ASU. '
    '<b>Onde ficar:</b> Villa Morra ou centro. <b>Imperdíveis:</b> Palácio dos '
    'Lopes, Costanera, Manzana de la Rivera, Mercado Cuatro. <b>Surpresa:</b> '
    'compra de eletrônicos sai mais barato que no Brasil (loja Ciudad del '
    'Este, se for esticar). Cidade pequena — 2 dias dão conta.', S['body']))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('IMG_6256.jpg', 'IMG_6269.jpg', h=6.5*cm))
story.append(caption('Palácio dos Lopes (esquerda) e letreiro de Asunción (direita) — clichês obrigatórios.'))

# ============================================================
# Closing
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Próximas rotas',
    'Onde a gente vai agora — e onde você pode ir.',
    'Este ebook continua sendo escrito. Cada destino novo que a gente '
    'visitar vira capítulo aqui ou em outro guia.'
))

story.append(Paragraph(
    'Em 2026 ainda vamos pra África do Sul — safari, savana e a viagem mais '
    'aventureira que já planejamos. Em 2027, a meta é Japão. Os roteiros '
    'desses destinos vão entrar na próxima atualização gratuita pra quem '
    'baixou este ebook.', S['body']))

story.append(Paragraph('Como continuar acompanhando', S['h2']))
story.extend(bullet_list([
    'Inscreva-se na nossa newsletter em <b>rotacomfamilia.com</b>.',
    'Siga nosso canal no YouTube — @Rotacomfamilia — vídeos semanais.',
    'Instagram da Kharol — @kharol.antunes — bastidores e dicas do dia a dia.',
    'TikTok — @rotacomfamilia — para conteúdo curto e ágil.',
]))

story.append(Spacer(1, 0.3*cm))
story.append(Callout(
    'Quer um roteiro montado pra sua família?',
    'Se você já sabe pra onde quer ir, mas não tem milhas pra emitir ou tempo '
    'pra planejar, a assessoria personalizada da Rota cuida disso. Mando '
    'plano em PDF, faço as emissões e entrego os bilhetes prontos.',
    kind='note'))

story.extend(back_cover_block(
    'Que essas páginas inspirem a próxima viagem de vocês. E quando ela '
    'acontecer, manda foto pra gente — adoramos ver outras famílias na rota.'))

# ============================================================
doc.build(story)
print(f'OK — {OUTFILE}')
