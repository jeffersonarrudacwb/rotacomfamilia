# Logos dos parceiros

Coloque aqui o SVG oficial de cada parceiro, com o nome do slug usado em
`dados/parcerias.json`:

    assets/logos/wise.svg
    assets/logos/nomad.svg
    assets/logos/holasim.svg

Assim que o arquivo existir, `scripts/gerar-parcerias.py` passa a usá-lo no
lugar do selo com a inicial. Não precisa mexer em código: rode

    python scripts/gerar-parcerias.py

Onde conseguir: praticamente todo programa de indicação tem uma área de
material de divulgação, com o logo em SVG ou PNG e as regras de uso. É de lá
que o arquivo deve sair, não de busca de imagens: logo tirado do Google costuma
vir em baixa resolução, com fundo errado ou numa versão antiga da marca.

Prefira SVG. Se só houver PNG, use fundo transparente e pelo menos 200 px de
largura.
