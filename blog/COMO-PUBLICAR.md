# Como publicar um artigo no blog

Guia de bolso para o Jefferson e a Kharol. Vale a pena seguir na ordem: os
campos de SEO são mais fáceis de preencher **depois** que o texto existe.

---

## Antes de escrever

**A regra que vale mais que todas as outras: só afirme o que aconteceu.**

O site já teve depoimentos com rostos de banco de imagem, um formulário que
fingia enviar email e cards anunciando artigos com autor e tempo de leitura
inventados. Tudo isso foi corrigido. Artigo é onde o risco volta, porque número
errado num texto indexado pelo Google fica anos no ar.

Na dúvida entre um número exato que você não tem certeza e uma faixa
aproximada, **escreva a faixa**. "Entre 80 e 100 mil milhas por pessoa" é
honesto e igualmente útil. "Exatamente 87.430" sem ter conferido não é.

Se não lembra o valor, três saídas honestas:
- escrever a faixa;
- escrever "não anotei na época";
- cortar o trecho.

---

## Escrevendo

### 1. Novo post

`Posts → Adicionar novo`

### 2. Título

O que a pessoa digitaria no Google, não o que soa bonito.

- Bom: `Orlando com criança: quanto custou a nossa viagem de 2026`
- Ruim: `Uma aventura mágica em solo americano`

Até 60 caracteres aparece inteiro no resultado de busca. Passou disso, o
Google corta com reticências.

### 3. Escreva no editor, não cole de qualquer lugar

⚠️ **Nunca cole texto copiado de uma janela de chat, do Word ou de site.**

Isso já nos custou caro uma vez: o email de boas-vindas foi colado de uma
janela de chat no editor do Brevo e veio junto o CSS da interface: 800 bytes
de estilo **por palavra**, um HTML de 137 KB para 2 KB de texto. Resultado: 1%
de proporção de texto, que é assinatura clássica de spam, e o email caiu na
caixa de lixo.

O mesmo acontece no WordPress e deixa o artigo pesado e feio no celular.

**Se precisar colar**, use `Ctrl + Shift + V` (colar sem formatação), ou passe
antes pelo Bloco de Notas.

### 4. Estrutura que funciona

```
Parágrafo de abertura     -> em 2 ou 3 linhas, diga o que a pessoa vai levar
                             daqui. Sem "seja bem-vindo ao nosso blog".

## Subtítulo (H2)         -> um a cada 3 ou 4 parágrafos. Quem lê no celular
                             escaneia os H2 antes de decidir se lê o texto.

Parágrafos curtos         -> 3 a 4 linhas. Bloco grande no celular afasta.

Lista quando for lista    -> passo a passo, itens de bagagem, dias de roteiro

Tabela quando for número  -> custos, milhas por trecho, comparativo de cartão

Foto a cada 2 ou 3 blocos -> quebra a leitura e prova que você esteve lá
```

### 5. Fotos

As originais estão em `fotos/`, organizadas por destino.

**Antes de subir, reduza para no máximo 1600 px de largura.** As fotos da
câmera têm 4000 px e 2,4 MB; no artigo isso só deixa a página lenta.

Para reduzir várias de uma vez, o script do site já faz isso:

```bash
python scripts/otimizar-imagens.py
```

Ao inserir cada imagem, **preencha o texto alternativo**, no campo "Texto
alternativo" na barra lateral direita. Descreva o que se vê:

- Bom: `Derek em frente ao castelo da Cinderella no Magic Kingdom`
- Ruim: `IMG_7613.jpg` ou `foto da viagem`

Isso é o que leitor de tela lê para quem não enxerga, e é também o que o Google
usa para entender a imagem. No Brasil não é só boa prática: a Lei Brasileira de
Inclusão (13.146/2015, art. 63) torna acessibilidade obrigatória em site de uso
público.

### 6. Imagem destacada

Barra lateral → `Imagem destacada`. É a que aparece na listagem do blog e no
card quando alguém compartilha no WhatsApp.

Formato ideal: **1200 × 630**, até 300 KB.

---

## Antes de publicar

### Categoria

Escolha **uma** principal. A estrutura existente:

```
Brasil                    Internacional              Milhas e Cartões
├── Serra                 ├── Estados Unidos
├── Praia                 ├── Europa
└── Parques               └── América Latina
```

Marcar cinco categorias não ajuda ninguém a achar o texto. Atrapalha.

### Link permanente (slug)

Aparece na barra lateral, em `Post → Link`. Deixe curto, sem acento, sem
palavra vazia:

- Bom: `orlando-com-crianca-custos`
- Ruim: `10-dias-em-orlando-com-a-familia-o-roteiro-completo-de-2026`

⚠️ **Depois de publicado, não mude o slug.** O link já pode ter sido
compartilhado e indexado; trocar quebra tudo. Se for inevitável, crie um
redirecionamento.

### Yoast SEO

Role até o bloco Yoast, embaixo do editor.

| Campo | O que preencher |
|---|---|
| **Frase-chave** | O termo que a pessoa buscaria: `orlando com criança` |
| **Título SEO** | Pode ser igual ao título. Mantenha abaixo de 60 caracteres. |
| **Meta descrição** | 2 linhas vendendo o clique, até 155 caracteres. É o texto cinza do resultado do Google. |

Sobre as bolinhas verde/laranja do Yoast: **use como lembrete, não como
prova.** Ele reclama de coisas que não importam ("a frase-chave não aparece no
primeiro parágrafo") e não sabe julgar se o texto é bom. Texto útil e honesto
com bolinha laranja vale mais que texto forçado com bolinha verde.

### Resumo

`Post → Resumo`. Duas linhas. É o que aparece na listagem do blog. Se ficar
vazio, o WordPress corta o começo do texto no meio da frase.

---

## Depois de publicar

1. **Abra o artigo no celular.** É onde a maioria vai ler. Foto esticada,
   tabela estourando a tela e parágrafo gigante aparecem na hora.

2. **Limpe o cache**: SpeedyCache na barra do topo → `Delete all Cache`.
   Senão você vê a versão antiga e acha que algo quebrou.

3. **Cole o link num grupo do WhatsApp** (pode ser conversa com você mesmo) e
   veja se aparece com imagem e título. Se vier link cru, a imagem destacada
   está faltando ou é pesada demais.

4. **Se o artigo corresponde a um dos seis cards da home**, avise que agora ele
   existe: o card precisa deixar de mostrar o selo "Em produção" e passar a
   apontar para o texto.

---

## Ritmo

Um artigo por semana, publicado sempre no mesmo dia, vale mais que cinco numa
semana e nenhum no mês seguinte. Conteúdo é a única coisa do site que compõe:
um artigo bom continua trazendo visita anos depois.

E o mais importante para quem está começando: **os primeiros artigos vão ter
pouca visita.** Isso é normal e não quer dizer que o texto é ruim. Google leva
de semanas a meses para confiar num domínio novo. O que resolve é continuar
publicando, não mexer no texto antigo toda semana.
