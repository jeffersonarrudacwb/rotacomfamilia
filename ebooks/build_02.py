"""
Ebook 2: Roteiros Prontos: EUA, Europa, Caribe
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
    subtitle='Onze destinos reais da nossa família, com dias, custos e o que vale.',
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
    'Cada destino que você vai ler aqui foi feito, não pesquisado. Comemos nos '
    'restaurantes que indicamos. Erramos nas paradas. Acertamos em outras. Este '
    'ebook é o que a gente gostaria de ter recebido antes de cada viagem que '
    'fizemos como família entre 2024 e 2026.', S['body']))

story.append(Paragraph(
    'Os roteiros estão escritos no formato <b>3 a 5 dias</b>, o tempo médio que '
    'uma família consegue tirar pra um destino sem virar maratona. Para cada um, '
    'incluímos custo benchmark em milhas, sugestão de hospedagem e nossas dicas '
    'práticas. Não é uma lista exaustiva: é o que a gente faria de novo.',
    S['body']))

story.append(Spacer(1, 0.4*cm))
story.append(StatStrip([
    ('11', 'destinos\nneste ebook'),
    ('4', 'continentes\nvisitados'),
    ('100%', 'roteiros\ntestados'),
]))

# ============================================================
# TOC
# ============================================================
story.append(PageBreak())
story.append(Paragraph('SUMÁRIO', S['eyebrow']))
story.append(Paragraph('Os 11 destinos.', S['h1']))
story.append(Divider(width_pct=0.18))
story.append(Spacer(1, 0.3*cm))
story.append(toc([
    ('Parte I · Estados Unidos', '03'),
    ('Orlando: Disney e parques', '04'),
    ('Las Vegas + Los Angeles', '06'),
    ('Nova York: clássica e moderna', '08'),
    ('Parte II · Europa', '10'),
    ('Lisboa & Porto', '11'),
    ('Madrid (e por que esticar)', '13'),
    ('Parte III · Caribe', '14'),
    ('Punta Cana: resort all-inclusive', '15'),
    ('Parte IV · América do Sul (bônus)', '16'),
    ('Buenos Aires, Santiago, Assunção e Colonia', '17'),
    ('Parte V · África', '19'),
    ('África do Sul: safári por conta própria', '20'),
]))

# ============================================================
# PARTE I - EUA - opening
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Parte I',
    'Estados Unidos.',
    'Três jeitos completamente diferentes de fazer EUA com a família: do '
    'parque temático ao deserto, da costa leste à costa oeste. Tudo testado '
    'em 3 viagens entre 2024 e 2026.'
))

story.append(Spacer(1, 0.3*cm))
story.append(photo('orlando/IMG_7613.jpg', max_h=9*cm))
story.append(caption('Magic Kingdom, Orlando, janeiro de 2026.'))

# ============================================================
# Orlando
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destino 01',
    'Orlando: Disney e parques.',
    'Para a família com filhos de 5 a 14 anos, Orlando é uma viagem que vale '
    'fazer pelo menos uma vez. O nosso Derek tinha 10 anos na primeira vez, '
    'em 2024, e voltamos com ele em janeiro de 2026 já com 12.'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'GRU/GIG → MCO (com escala em Miami ou Panamá)'],
    ['Milhas por pessoa, ida e volta', '50 a 70 mil Latam Pass · 70 a 100 mil Smiles ou TudoAzul'],
    ['Hospedagem', 'Hotéis Disney "value" (Art of Animation, Pop Century)'],
    ['Duração ideal', '7 dias (incluindo 4 a 5 dias de parque)'],
    ['Melhor época', 'Fim de fevereiro e março, quando a fila diminui'],
], col_widths=[5*cm, 11.7*cm]))

story.append(Paragraph('Roteiro de 5 dias nos parques', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1, Magic Kingdom.</b> O parque mais "Disney" de todos. Plano: chegar '
    'antes da abertura e ir direto pro Seven Dwarfs Mine Train. Almoço no Be Our '
    'Guest (reserva com 60 dias). Tarde: Pirates of Caribbean, Big Thunder. Fica '
    'até o show noturno do castelo.',
    '<b>Dia 2, EPCOT.</b> Mais leve em montanha-russa, perfeito pro dia depois '
    'da maratona do Magic Kingdom. Faça a volta ao mundo pelo World Showcase. '
    'Test Track e Frozen Ever After são imperdíveis.',
    '<b>Dia 3, Hollywood Studios.</b> Star Wars Galaxy\'s Edge é o highlight: '
    'a atração Rise of the Resistance vale a fila. Toy Story Land é ótimo pra '
    'crianças menores.',
    '<b>Dia 4, Animal Kingdom.</b> Avatar Flight of Passage é a melhor '
    'atração da Disney inteira, na nossa opinião. Comece por ela.',
    '<b>Dia 5, Universal (Islands of Adventure + Universal Studios).</b> '
    'Hogsmeade e Diagon Alley em sequência (use o Hogwarts Express). VelociCoaster '
    'pra quem aguenta, e o Derek adorou.',
]))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('orlando/IMG_7845.jpg', 'orlando/IMG_5690.jpg', h=6*cm))
story.append(caption('Town Square Theater (esquerda) e Cars Land na Art of Animation (direita): momentos clássicos da viagem.'))

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
    'A combinação clássica da costa oeste: uma cidade que é puro espetáculo '
    'e outra que é puro estilo de vida. Passamos por Los Angeles em maio de '
    '2024, a caminho de Minneapolis e Orlando, e voltamos em dezembro do mesmo '
    'ano para fazer a dupla com calma.'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'GRU → LAX (direto Latam) → LAS terrestre ou voo curto'],
    ['Milhas por pessoa, ida e volta', '50 a 70 mil Latam Pass · 70 a 110 mil Smiles ou TudoAzul'],
    ['Hospedagem Vegas', 'The Venetian, Wynn ou MGM Grand (resort fee é caro)'],
    ['Hospedagem LA', 'Santa Monica ou Beverly Hills (centro é menos turístico)'],
    ['Duração ideal', '7 dias (4 LA + 3 Vegas)'],
], col_widths=[5*cm, 11.7*cm]))

story.append(Paragraph('LA, 4 dias', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1:</b> Hollywood (Walk of Fame, TCL Chinese Theatre, Hollywood Sign do Griffith Observatory).',
    '<b>Dia 2:</b> Santa Monica Pier de manhã, Venice Beach de tarde, jantar no The Cheesecake Factory.',
    '<b>Dia 3:</b> Universal Studios, dia inteiro. Studio Tour é melhor que muitas atrações.',
    '<b>Dia 4:</b> Rodeo Drive (Beverly Hills) + The Grove (compras + cinema). Saída noturna pra Vegas.',
]))

story.append(Paragraph('Vegas, 3 dias', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1:</b> Strip de dia (Bellagio fountains, Venetian, Caesars), show de Cirque du Soleil à noite.',
    '<b>Dia 2:</b> Bate-volta ao Grand Canyon de helicóptero (caro, mas inesquecível) OU Red Rock Canyon.',
    '<b>Dia 3:</b> Compras nos outlets (Premium Outlets North) + jantar memorável (Gordon Ramsay).',
]))

story.append(Spacer(1, 0.2*cm))
story.append(photo('Las Vegas/IMG_6889.JPG', max_h=7*cm))
story.append(caption('Teto de vidro Chihuly no lobby do Bellagio, o cartão-postal instantâneo de Vegas.'))

# ============================================================
# Nova York
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destino 03',
    'Nova York: clássica e moderna.',
    'Para a maioria das famílias, é a primeira viagem internacional dos sonhos. '
    'A gente foi em dezembro de 2024, no Natal nova-iorquino, que é uma das '
    'experiências mais impactantes do ano.'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'GRU/GIG → JFK ou EWR (Latam, American, Delta)'],
    ['Milhas por pessoa, ida e volta', '70 a 100 mil Latam Pass, às vezes 60 mil · 80 a 120 mil Smiles ou TudoAzul'],
    ['Hospedagem', 'Midtown é perto de tudo e caro. A gente ficou longe, entre Bronx e Yonkers'],
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
story.append(two_col_photo_row('Nova Iorque/IMG_2010.jpg', 'Nova Iorque/c1d56598-f55e-4216-89f3-6786180ac897.jpg', h=8*cm))
story.append(caption('Memorial do 11 de setembro em noite de Natal (esquerda) · Brooklyn Bridge ao pôr do sol (direita).'))

story.append(Callout(
    'A dica de mobilidade',
    'Pegue o cartão "OMNY" do metrô: você passa o cartão de crédito direto na '
    'catraca, sem precisar comprar bilhete. Limite diário é US$ 34, ou seja, '
    'depois disso, é grátis pro resto da semana.', kind='tip'))

story.append(Paragraph('Grupo grande muda a conta da hospedagem', S['h2']))
story.append(Paragraph(
    'A gente foi em sete pessoas, e aí a matemática de Manhattan deixa de '
    'fechar: quarto de hotel em Nova York é pequeno e cobra por pessoa, então '
    'sete viram três quartos. Alugamos um Airbnb inteiro entre o Bronx e '
    'Yonkers, bem mais longe do centro, e pagamos por uma casa em vez de por '
    'cabeça.', S['body']))

story.append(Paragraph(
    'A troca é honesta: você ganha espaço e economiza muito, e perde tempo de '
    'deslocamento todo dia. Com o metrô funcionando 24 horas e o teto diário do '
    'OMNY, o transporte extra custa pouco, mas some uma hora por dia no ida e '
    'volta. Para casal ou família de três, Midtown provavelmente compensa. '
    'De cinco pessoas pra cima, vale rodar as duas contas antes de decidir.',
    S['body']))

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

story.append(Spacer(1, 0.3*cm))
story.append(photo('Porto/IMG_9664.jpg', max_h=10*cm))
story.append(caption('Ribeira do Porto ao entardecer, a foto favorita da nossa viagem pela Europa.'))

# ============================================================
# Lisboa & Porto
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destino 04',
    'Lisboa & Porto.',
    'A porta de entrada perfeita pra Europa. Em 6 dias dá pra fazer as '
    'duas cidades sem correr, e ainda esticar pra Sintra.'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'GRU → LIS (TAP, Latam, Air Europa)'],
    ['Milhas por pessoa, ida e volta', '60 a 100 mil Latam Pass · 90 a 130 mil Smiles ou TudoAzul'],
    ['Hospedagem Lisboa', 'Bairro Alto / Chiado (caminhável)'],
    ['Hospedagem Porto', 'Ribeira ou Cedofeita'],
    ['Lisboa ↔ Porto', 'Alfa Pendular (cerca de 3h), comprar com antecedência'],
], col_widths=[5*cm, 11.7*cm]))

story.append(Paragraph('Lisboa, 3 dias', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1:</b> Alfama (Castelo de São Jorge, Sé, Miradouro de Santa Luzia). Jantar de fado.',
    '<b>Dia 2:</b> Belém (Torre, Mosteiro dos Jerónimos, MAAT, e claro, Pastéis de Belém).',
    '<b>Dia 3:</b> Sintra (bate-volta: Palácio da Pena + Quinta da Regaleira).',
]))

story.append(Paragraph('Porto, 3 dias', S['h2']))
story.extend(bullet_list([
    '<b>Dia 1:</b> Ribeira, Livraria Lello, Estação São Bento, jantar tradicional.',
    '<b>Dia 2:</b> Vila Nova de Gaia (tour de vinho do Porto), cruzeiro pelos rios.',
    '<b>Dia 3:</b> Bate-volta ao Vale do Douro (vinícolas + paisagem).',
]))

story.append(Callout(
    'Onde Portugal ganha o jogo',
    'Comida boa e barata em qualquer lugar: almoço pra família por € 50 com '
    'sobremesa. E gente em geral muito acolhedora com brasileiro. Em todo lugar '
    'a gente foi tratado como vizinho.', kind='tip'))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('Lisboa/IMG_0232.jpg', 'Lisboa/IMG_0371.jpg', h=7*cm))
story.append(caption('Terreiro do Paço em Lisboa (esquerda) · Bonde 28 subindo pela Alfama (direita).'))

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
    '<b>Dia 3:</b> Bate-volta a Toledo de trem (45 min), cidade medieval imperdível.',
]))

story.append(Callout(
    'Quando esticar pra Barcelona',
    'Se você está em Madri por mais de 4 dias, vale dar um pulo a Barcelona via '
    'AVE (trem-bala, 2h30). Sagrada Família + Park Güell + Gótico em 3 dias '
    'dá um upgrade na viagem inteira.', kind='tip'))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('Madri/IMG_9393.jpg', 'Malaga/IMG_5371.jpg', h=7*cm))
story.append(caption('Parque do Retiro em Madri (esquerda) · Málaga com bandeira da Espanha (direita): vale esticar até o sul.'))

# ============================================================
# PARTE III - CARIBE
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Parte III',
    'Caribe.',
    'Quando você quer férias de verdade, daquelas com pulseirinha all-inclusive '
    'e pé na areia. Em dezembro de 2025 fizemos Punta Cana e voltamos resetados.'
))

story.append(Spacer(1, 0.3*cm))
story.append(photo('Caribe/DJI_20251222112620_0004_D.JPG', max_h=10*cm))
story.append(caption('Punta Cana, dezembro de 2025, um dos dias mais leves do ano.'))

# ============================================================
# Punta Cana
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destino 06',
    'Punta Cana: resort all-inclusive.',
    'Nosso refúgio de fim de ano. Para a família que quer descansar de '
    'verdade: sem agenda, sem horário, sem sair do resort se não quiser.'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'GRU → PUJ (Latam, Copa via Panamá, Gol)'],
    ['Milhas por pessoa, ida e volta', '40 a 60 mil Latam Pass · 80 a 110 mil Smiles ou TudoAzul'],
    ['Hospedagem', 'Riu, Iberostar, Hyatt Ziva, Hard Rock, all-inclusive'],
    ['Duração ideal', '6 a 7 dias'],
    ['Melhor época', 'Dezembro a abril (alta) · Maio/junho (custo-benefício)'],
], col_widths=[5*cm, 11.7*cm]))

story.append(Paragraph('O ritmo da viagem', S['h2']))
story.extend(bullet_list([
    '<b>Dias 1 e 2:</b> aclimatar, praia, piscina, restaurantes do resort.',
    '<b>Dia 3:</b> Excursão a Saona Island (catamarã, almoço na praia). Vale.',
    '<b>Dia 4:</b> dia livre, spa, esportes náuticos, ler na rede.',
    '<b>Dia 5:</b> Excursão a Hoyo Azul ou Macao Beach (snorkel).',
    '<b>Dia 6:</b> Último dia de praia + jantar no melhor restaurante do resort.',
]))

story.append(Callout(
    'A regra das pulseirinhas',
    'Em resort all-inclusive, a pulseirinha é a sua vida. Algumas categorias '
    'liberam restaurantes melhores e bebidas premium. Reservas de '
    'restaurante à la carte costumam abrir 1 ou 2 dias antes, chegue cedo '
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
    'logisticamente fáceis e custam pouco: Buenos Aires, Santiago, Assunção, e '
    'Colonia del Sacramento de bate-volta.'
))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('argentina/IMG_4258.JPG', 'chile/IMG_4085.jpg', h=7*cm))
story.append(caption('Família em La Boca / Caminito (esquerda) · Letreiro Chile Travel em Santiago (direita).'))

# ============================================================
# Buenos Aires, Santiago, Assunção - combined chapter
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destinos 07 a 09, mais o Uruguai',
    'Buenos Aires, Santiago, Assunção e Colonia.',
    'Três cidades, três personalidades, todas alcançáveis com baixo gasto '
    'de milhas. Roteiro express pra cada uma.'
))

story.append(Paragraph('Buenos Aires, 4 dias', S['h2']))
story.append(Paragraph(
    '<b>Milhas:</b> ~25–35k Latam Pass por passagem · <b>Voo:</b> 3h GRU → EZE. '
    '<b>Onde ficar:</b> Recoleta ou Palermo Soho. <b>Imperdíveis:</b> Bairro de '
    'La Boca (Caminito + estádio do Boca Juniors), Recoleta (cemitério + '
    'Museu de Belas Artes), Palermo (jantar no Don Julio se conseguir '
    'reserva), Tigre (bate-volta de barco). <b>Comida:</b> bife de chorizo '
    'em qualquer parrilla.', S['body']))

story.append(Spacer(1, 0.2*cm))
story.append(photo('argentina/1760b412-8ced-413f-84da-b6ee25a3aaf2.jpg', max_h=7*cm))
story.append(caption('Estádio do Boca Juniors: a visita guiada vale a pena.'))

story.append(Paragraph('Santiago, 4 dias', S['h2']))
story.append(Paragraph(
    '<b>Milhas:</b> ~30–40k Latam Pass · <b>Voo:</b> 3h30 GRU → SCL. '
    '<b>Onde ficar:</b> Las Condes ou Providencia. <b>Imperdíveis:</b> Cerro San '
    'Cristóbal (teleférico + vista), Bellavista, Mercado Central (almoço de '
    'frutos do mar), Cajón del Maipo (excursão de 1 dia, cordilheira). '
    '<b>Esticar:</b> Vale do Maipo (vinícolas) ou Valparaíso (cidade '
    'colorida na costa).', S['body']))

story.append(Paragraph('Assunção, 2 a 3 dias', S['h2']))
story.append(Paragraph(
    '<b>Milhas:</b> ~20–28k Latam Pass · <b>Voo:</b> 2h GRU → ASU. '
    '<b>Onde ficar:</b> Villa Morra ou centro. <b>Imperdíveis:</b> Palácio dos '
    'Lopes, Costanera, Manzana de la Rivera, Mercado Cuatro. <b>Surpresa:</b> '
    'compra de eletrônicos sai mais barato que no Brasil (loja Ciudad del '
    'Este, se for esticar). Cidade pequena: 2 dias dão conta.', S['body']))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('Paraguai-Assuncao/IMG_6256.jpg', 'Paraguai-Assuncao/IMG_6269.jpg', h=6.5*cm))
story.append(caption('Palácio dos Lopes (esquerda) e letreiro de Asunción (direita): clichês obrigatórios.'))

story.append(Paragraph('Colonia del Sacramento, 1 dia', S['h2']))
story.append(Paragraph(
    'Esse é o país mais barato que já colocamos no passaporte, porque ele não '
    'custou passagem nenhuma. Estando em <b>Buenos Aires</b>, dá para atravessar '
    'o Rio da Prata de barco e passar o dia em <b>Colonia del Sacramento</b>, no '
    'Uruguai. A travessia leva pouco mais de uma hora e você volta no fim da '
    'tarde.', S['body']))

story.append(Paragraph(
    '<b>Como é:</b> o centro histórico é português do século XVII, tombado pela '
    'Unesco, todo de rua de pedra, e se percorre a pé numa manhã. '
    '<b>Imperdíveis:</b> a Calle de los Suspiros, o farol com vista do rio e o '
    'almoço em qualquer restaurante de frente para a água. <b>Leve o '
    'passaporte:</b> é fronteira de verdade, com controle nos dois lados. '
    '<b>Vale a pena?</b> Se você tem quatro dias em Buenos Aires, sim. Se tem '
    'só três, fique na Argentina.', S['body']))

story.append(Spacer(1, 0.3*cm))
story.append(two_col_photo_row('Uruguai/IMG_3985.jpg', 'Uruguai/IMG_4026.jpg', h=6.5*cm))
story.append(caption('Colonia del Sacramento: o centro histórico português a uma hora de barco de Buenos Aires.'))

# ============================================================
# PARTE V - AFRICA
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Parte V',
    'África.',
    'A viagem que parecia impossível e acabou sendo a mais marcante. '
    'Fomos em julho de 2026 e voltamos convencidos de que safári cabe no '
    'orçamento de família brasileira.'
))

story.append(Spacer(1, 0.3*cm))
story.append(photo('africa do sul/Familia 9.jpg', max_h=9*cm))
story.append(caption('Bourke\'s Luck Potholes, no Blyde River Canyon: parada '
                     'obrigatória na Rota Panorâmica, a caminho do Kruger.'))

# ============================================================
# Africa do Sul
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Destino 10',
    'África do Sul: safári por conta própria.',
    'O Kruger é um dos poucos parques grandes do mundo onde você pode entrar '
    'dirigindo o seu próprio carro. Isso muda o preço da viagem e muda a '
    'experiência.'
))

story.append(Paragraph('Benchmark da viagem', S['h2']))
story.append(data_table([
    ['Item', 'Referência'],
    ['Trecho aéreo', 'GRU → JNB'],
    ['O que pagamos', '96 mil milhas TudoAzul por pessoa, voando pela TAAG'],
    ['Como emitimos', 'Azul pelo Mundo, que é onde a Azul abre as parceiras'],
    ['Duração', 'Duas semanas, sendo 5 dias dentro do Kruger'],
    ['Carro', '3.200 rands o período inteiro, pouco mais de mil reais'],
    ['Melhor época', 'Junho a setembro, o inverno seco de lá'],
], col_widths=[5*cm, 11.7*cm]))

story.append(Callout(
    'Por que o inverno é a melhor época para ver bicho',
    'Na seca, o mato fica ralo e os animais se concentram nos poucos pontos de '
    'água que sobraram. Você enxerga mais longe e sabe onde procurar. No verão '
    'a savana fica verde e bonita, e o bicho some dentro dela.', kind='tip'))

story.append(Paragraph('O safári sem guia, na prática', S['h2']))
story.append(Paragraph(
    'A dúvida que todo mundo tem é se funciona sem guia. Funciona, e a resposta '
    'honesta é que funciona bem, desde que você aceite duas trocas.', S['body']))

story.extend(bullet_list([
    '<b>Você vê menos que um guia veria.</b> Eles têm rádio, sabem onde o leão '
    'apareceu de manhã e enxergam o que você passa direto. Sozinho, você '
    'depende mais de sorte e de paciência.',
    '<b>Em compensação, o tempo é seu.</b> Ficar quarenta minutos parado '
    'olhando um grupo de elefantes atravessar, sem ninguém com pressa de '
    'cumprir roteiro, é uma experiência diferente. Com criança, isso pesa.',
    '<b>Carro comum dá conta.</b> As estradas principais do Kruger são '
    'asfaltadas e as secundárias são de cascalho firme. Não precisa de 4x4 '
    'para o circuito clássico.',
]))

story.append(Spacer(1, 0.3*cm))
story.append(photo('africa do sul/Guepardo.jpg', max_h=9*cm))
story.append(caption('Guepardo a poucos metros do carro, no Kruger. A porta no '
                     'canto da foto é a do nosso carro alugado.'))

story.append(Paragraph('As regras que você precisa saber antes', S['h2']))
story.extend(bullet_list([
    '<b>Portão abre ao nascer e fecha ao pôr do sol.</b> O horário muda por mês '
    'e é levado a sério: chegar atrasado no acampamento dá multa.',
    '<b>Não se sai do carro</b>, exceto nos pontos sinalizados. Não é '
    'formalidade, é um parque aberto com predador solto.',
    '<b>Velocidade baixa</b>, 50 km/h no asfalto e 40 no cascalho. Além de ser '
    'a regra, é o que permite enxergar alguma coisa.',
    '<b>Comece cedo.</b> As primeiras duas horas depois da abertura do portão '
    'rendem mais que o resto do dia inteiro.',
]))

story.append(Spacer(1, 0.3*cm))
story.append(photo('africa do sul/Elefantes-card.jpg', max_h=7.5*cm))
story.append(caption('Elefantes atravessando a estrada: aqui a regra é simples, '
                     'desliga o carro e espera.'))

story.append(Paragraph('O nosso roteiro, dia a dia', S['h2']))
story.append(Paragraph(
    'O Kruger não é um destino que se faz de bate-volta a partir de '
    'Joanesburgo. São umas cinco horas de estrada até a região dos portões, e a '
    'graça está justamente no que tem no meio do caminho.', S['body']))

story.extend(bullet_list([
    '<b>Joanesburgo, chegada.</b> Alguns dias na cidade para descansar do voo '
    'e pegar o carro.',
    '<b>Dullstroom, 1 dia.</b> Cidadezinha de clima frio no meio da subida, boa '
    'parada para quebrar a estrada em vez de encarar tudo de uma vez.',
    '<b>Rota Panorâmica.</b> Blyde River Canyon, os Three Rondavels e a God\'s '
    'Window. É o trecho mais bonito da viagem fora do parque.',
    '<b>Phalaborwa.</b> Dormimos ao lado do parque, para entrar logo na '
    'abertura do portão no dia seguinte.',
    '<b>Kruger, 5 dias.</b> Duas noites no <b>Mopani Rest Camp</b>, na parte '
    'norte, e duas no <b>Pretoriuskop</b>, no sul. Dormir dentro do parque em '
    'dois pontos distantes muda o que você vê: o norte é mais vazio e o sul '
    'concentra mais bicho.',
    '<b>Saída pelo Crocodile Bridge, às 17h30.</b> Jantamos na estrada e '
    'dormimos em <b>Nelspruit</b>, no Coyotes Hotel & Conference Centre, para '
    'não fazer a volta inteira à noite.',
    '<b>Joanesburgo, mais 2 dias</b> antes de voltar.',
]))

story.append(Spacer(1, 0.2*cm))
story.append(Callout(
    'Reserve os campos do Kruger direto no SANParks',
    'As acomodações dentro do parque são administradas pelo SANParks, o órgão '
    'dos parques nacionais, e se reservam no site deles. Fora do parque a gente '
    'usou o Booking normalmente: as diárias ficaram em torno de <b>R$ 300 para '
    'nós três</b>, e a de Joanesburgo ainda vinha com um café da manhã muito '
    'bom. Some o carro, que saiu por pouco mais de mil reais o período inteiro, '
    'e a parte terrestre de duas semanas na África custa menos do que a maioria '
    'das pessoas imagina.', kind='tip'))

story.append(Callout(
    'A Rota Panorâmica vale os dois dias',
    'Muita gente pega a estrada direto para o parque e pula tudo. Reserve dois '
    'dias: é paisagem de outro planeta e fica no caminho.', kind='note'))

story.append(Paragraph('O último trecho foi de ônibus', S['h2']))
story.append(Paragraph(
    'Vale contar como a viagem terminou, porque é o tipo de decisão que ninguém '
    'mostra. Desembarcando em São Paulo, faltava chegar em Curitiba, e não '
    'apareceu resgate com preço decente em nenhum programa. Em vez de queimar '
    'milha boa num trecho de uma hora, fomos de <b>ônibus-leito</b>, por volta '
    'de R$ 280.', S['body']))

story.append(Paragraph(
    'Foi confortável e acabou virando um fecho tranquilo depois de duas semanas '
    'de estrada. A regra que a gente segue: <b>milha é para trecho longo</b>. '
    'Em perna curta, compare sempre com dinheiro, ônibus e carro antes de '
    'emitir.', S['body']))

# ============================================================
# Closing
# ============================================================
story.append(PageBreak())
story.extend(section_opener(
    'Próximas rotas',
    'Onde a gente vai agora, e onde você pode ir.',
    'Este ebook continua sendo escrito. Cada destino novo que a gente '
    'visitar vira capítulo aqui ou em outro guia.'
))

story.append(Paragraph(
    'A África do Sul saiu da lista de planos e virou o capítulo anterior. '
    'Para 2027 a gente ainda não fechou o destino, e tem um motivo divertido '
    'pra isso: durante a Copa a gente prometeu, nos vídeos, que iria para o '
    'país do campeão. Deu <b>Espanha</b>. Já conhecemos Madrid, então voltar '
    'é fácil de justificar, mas o país é muito maior que a capital e tem '
    'bastante coisa que a gente ainda não viu.', S['body']))

story.append(Paragraph(
    'Seja qual for a decisão, o roteiro entra aqui depois que a viagem '
    'acontecer, na próxima atualização gratuita para quem baixou este ebook. '
    'A regra deste material não muda: destino só vira capítulo depois que a '
    'gente pisa nele.', S['body']))

story.append(Paragraph('Como continuar acompanhando', S['h2']))
story.extend(bullet_list([
    'Inscreva-se na nossa newsletter em <b>rotacomfamilia.com.br</b>.',
    'Siga nosso canal no YouTube (@Rotacomfamilia): vídeos semanais.',
    'Instagram da Kharol (@kharol.antunes): bastidores e dicas do dia a dia.',
    'TikTok (@rotacomfamilia): para conteúdo curto e ágil.',
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
    'acontecer, manda foto pra gente, adoramos ver outras famílias na rota.'))

# ============================================================
doc.build(story)
print(f'OK: {OUTFILE}')
