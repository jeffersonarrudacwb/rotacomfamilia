# Logos dos parceiros

Um arquivo por parceiro, com o nome do slug usado em `dados/parcerias.json`.
O gerador procura nesta ordem: `.svg`, `.png`, `.webp`. Se não achar nenhum,
desenha um selo com a inicial nas cores da casa.

Depois de trocar ou adicionar qualquer arquivo:

    python scripts/gerar-parcerias.py

## De onde veio cada um

| Arquivo | Origem |
|---|---|
| `wise.svg` | símbolo oficial servido pelo próprio site da Wise |
| `nomad.png` | ícone de 512 px declarado no `<head>` do nomadglobal.com, reduzido para 128 |
| `holasim.png` | logo do cabeçalho de holasim.com, redimensionado para 72 px de altura |

A HolaSim é a única que não publica um símbolo quadrado: o favicon dela só
existe em 32 px, que fica borrado ampliado. Por isso ali entra o nome escrito,
e a placa fica mais larga que as outras. É de propósito.

## Se for trocar

Prefira SVG. Em PNG, use fundo transparente e pelo menos o dobro do tamanho de
exibição: a placa tem 46 px de altura, então 92 px é o mínimo e 128 é
confortável.

Pegue sempre do site do parceiro ou da área de material de divulgação dele.
Logo tirado de busca de imagens costuma vir em baixa resolução, com fundo
chapado ou numa versão antiga da marca.
