#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
otimizar-imagens.py - Rota com Familia
=======================================

Gera as variantes responsivas (WebP + JPEG progressivo) das fotos usadas no
site, a partir dos originais crus da pasta fotos/.

Caracteristicas:
  * Remove TODO metadado EXIF (as fotos de celular/drone carregam GPS).
  * Converte para sRGB quando o original tem outro perfil (ex.: Display P3).
  * Corrige a orientacao pelo EXIF antes de redimensionar.
  * Reamostragem LANCZOS.
  * Nunca faz upscale: largura alvo maior que a origem e pulada.
  * Idempotente: rodar de novo apenas regrava os mesmos arquivos.

Uso:
    python scripts/otimizar-imagens.py            # gera tudo
    python scripts/otimizar-imagens.py --json     # + resumo em JSON no final
    python scripts/otimizar-imagens.py --somente hero-caribe card-lisboa

Para adicionar/remover uma foto do site, edite apenas o dicionario IMAGENS.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import re
import sys
from pathlib import Path

from PIL import Image, ImageCms, ImageOps

# ---------------------------------------------------------------------------
# 1. AS IMAGENS USADAS NO SITE  (edite aqui)
# ---------------------------------------------------------------------------
# Chave   = slug (vira o nome do arquivo: assets/img/{slug}-{largura}.{ext})
# origem  = caminho relativo a raiz do projeto
# larguras= sobrescreve LARGURAS_PADRAO (opcional)
# teto_kb = { largura: kb } -> forca a variante a caber no teto baixando a
#           qualidade progressivamente, respeitando QUALIDADE_MINIMA (opcional)
# og      = True -> tambem gera assets/img/og-default.jpg a partir dela

LARGURAS_PADRAO = [400, 800, 1200, 1600]

IMAGENS: dict[str, dict] = {
    # O hero e o elemento LCP: para nao estourar o orcamento de bytes, o ladder
    # para em 1600 (192 KB). A variante 1920 foi removida de proposito -- em JPEG
    # ela so cabia em 200 KB com qualidade 50, degradacao inaceitavel na capa.
    "hero-caribe": {
        "origem": "fotos/Caribe/DJI_20251222112620_0004_D.JPG",
        "larguras": [400, 800, 1200, 1600],
        "teto_kb": {1600: 200},
        "og": True,
    },
    # Estas duas origens tem apenas 709 px de largura. Sem o degrau de 709 o
    # ladder pularia de 400 direto para 800 (que e barrado pela guarda de
    # upscale), deixando um srcset com um unico candidato e imagem mole em
    # telas de alta densidade.
    "card-orlando":     {"origem": "fotos/orlando/IMG_7613.jpg", "larguras": [400, 709]},
    "card-familia":     {"origem": "fotos/outras/IMG_7780.jpg",  "larguras": [400, 709]},
    "card-lounge-w":    {"origem": "fotos/sala_vip/IMG_5235.jpg"},
    "card-lounge-copa": {"origem": "fotos/sala_vip/IMG_8543.jpg"},
    "card-puntacana":   {"origem": "fotos/Caribe/IMG_6205.jpg"},
    "card-lisboa":      {"origem": "fotos/Lisboa/IMG_0232.jpg"},
    # A foto da secao "Quem somos". Antes era o Caminito, em Buenos Aires, que
    # ilustrava um destino especifico e nao a familia. Esta traz os dois com a
    # camiseta da marca, e o logo aparece legivel. A origem tem 1260 px, entao o
    # ladder para em 1200: pedir 1600 seria upscale.
    "sobre-familia":    {"origem": "fotos/Familia/IMG_7834.jpg",
                         "larguras": [400, 800, 1200]},
    # Criativo do post do Instagram, 1080x1351. Traz o titulo "SAFARI SEM GUIA"
    # embutido na propria imagem, o que fica redundante com o titulo do card.
    # Trocar por uma foto limpa do safari quando houver.
    # Elefantes atravessando a estrada de terra: ilustra literalmente a tese do
    # artigo, que e ter avistado bicho sem guia, dirigindo carro comum. A capa
    # do post do Instagram nao dizia nada disso.
    #
    # A origem e retrato 4:5 e o card e 16:10 com object-fit cover, entao o
    # recorte foi feito a mao em Elefantes-card.jpg, centrado na faixa dos
    # animais. Deixar para o navegador cortaria as patas e o dorso e sobraria
    # muito ceu vazio.
    "card-safari":      {"origem": "fotos/africa do sul/Elefantes-card.jpg",
                         "larguras": [400, 800, 1200, 1600]},
    # As duas executivas. Antes os cards usavam foto de sala VIP e de Lisboa,
    # que ilustravam a espera e o destino - nao a cabine, que e do que os
    # artigos tratam.
    #
    # IMG_8581, a refeicao servida na cabine. Escolha do Jefferson, e encaixa
    # melhor: .post-media e 16/10 com object-fit cover, entao esta foto (16:9)
    # perde so um fio nas laterais, enquanto a alternativa 4:3 perdia bastante
    # de topo e base no recorte.
    "card-executiva-copa":  {"origem": "fotos/Executiva Copa - MCO x PTY/IMG_8581.JPG",
                             "larguras": [400, 800, 1200, 1600]},
    # Esta e a foto certa para o artigo: mostra os SEIS passageiros na cabine,
    # que e exatamente o que o titulo promete.
    "card-executiva-latam": {"origem": "fotos/Executiva Latam - GRU x LIS/1.jpeg",
                             "larguras": [400, 800, 1280]},
    # Cartoes + acesso a sala VIP na mesma imagem, que e a tese do artigo de
    # cartoes: o cartao E a porta da sala.
    #
    # A origem e uma versao RECORTADA do IMG_2022. O enquadramento original
    # incluia o codigo de barras 2D e o numero do e-ticket do cartao de
    # embarque. Esse codigo carrega nome do passageiro e localizador da
    # reserva - com localizador e sobrenome se abre a reserva no site da
    # companhia. O corte tira a faixa inferior e resolve sem borrao.
    "card-cartoes":         {"origem": "fotos/sala_vip/IMG_2022-sem-dados.jpg",
                             "larguras": [400, 800, 1260]},
}

# ---------------------------------------------------------------------------
# 2. PARAMETROS DE CODIFICACAO
# ---------------------------------------------------------------------------
QUALIDADE_WEBP = 82
METODO_WEBP = 6              # 0 = rapido, 6 = melhor compressao
QUALIDADE_JPEG = 80
QUALIDADE_MINIMA = 62        # piso duro quando ha teto de KB
PASSO_QUALIDADE = 2          # de quanto em quanto a qualidade cai

OG_LARGURA, OG_ALTURA = 1200, 630
OG_TETO_KB = 300
OG_QUALIDADE_INICIAL = 88

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "assets" / "img"

REAMOSTRAGEM = Image.Resampling.LANCZOS
PERFIL_SRGB = ImageCms.createProfile("sRGB")


# ---------------------------------------------------------------------------
# 3. UTILITARIOS
# ---------------------------------------------------------------------------
def kb(caminho: Path) -> float:
    """Tamanho do arquivo em KB (1 KB = 1024 bytes), 1 casa decimal."""
    return round(caminho.stat().st_size / 1024, 1)


def para_srgb(im: Image.Image) -> tuple[Image.Image, str]:
    """Converte para sRGB/RGB. Devolve (imagem, descricao do perfil de origem)."""
    icc = im.info.get("icc_profile")
    origem_perfil = "sem perfil (assumido sRGB)"

    if icc:
        try:
            perfil_src = ImageCms.getOpenProfile(io.BytesIO(icc))
            origem_perfil = ImageCms.getProfileDescription(perfil_src).strip() or "desconhecido"
            if "srgb" not in origem_perfil.lower():
                if im.mode not in ("RGB", "CMYK", "L"):
                    im = im.convert("RGB")
                try:
                    im = ImageCms.profileToProfile(
                        im, perfil_src, PERFIL_SRGB,
                        renderingIntent=ImageCms.Intent.PERCEPTUAL,
                        outputMode="RGB",
                    )
                except ImageCms.PyCMSError:
                    # alguns perfis nao trazem a tabela perceptual
                    im = ImageCms.profileToProfile(
                        im, perfil_src, PERFIL_SRGB,
                        renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
                        outputMode="RGB",
                    )
        except Exception as erro:  # perfil corrompido -> segue sem conversao
            print(f"    aviso: perfil ICC ilegivel ({erro}); seguindo sem conversao")

    if im.mode != "RGB":
        im = im.convert("RGB")
    return im, origem_perfil


def limpar(im: Image.Image) -> Image.Image:
    """
    Reconstroi a imagem a partir dos bytes crus de pixel.

    Isso descarta o dicionario .info inteiro (exif, icc_profile, comentarios,
    XMP, GPS...). O plugin WebP do Pillow le exif/icc de im.info quando nao
    recebe os parametros no save, entao apenas "nao passar exif=" nao basta.
    """
    return Image.frombytes(im.mode, im.size, im.tobytes())


def abrir_normalizada(caminho: Path) -> tuple[Image.Image, str, tuple[int, int]]:
    """Abre, corrige orientacao EXIF, converte para sRGB e remove metadados."""
    with Image.open(caminho) as bruta:
        bruta.load()
        tam_bruto = bruta.size
        endireitada = ImageOps.exif_transpose(bruta)
        convertida, perfil = para_srgb(endireitada)
        return limpar(convertida), perfil, tam_bruto


def altura_para(tam: tuple[int, int], largura: int) -> int:
    origem_l, origem_a = tam
    return max(1, round(origem_a * largura / origem_l))


def redimensionar(im: Image.Image, largura: int) -> Image.Image:
    if im.width == largura:
        return im
    return im.resize((largura, altura_para(im.size, largura)), REAMOSTRAGEM)


def gravar_webp(im: Image.Image, destino: Path, qualidade: int) -> None:
    im.save(destino, "WEBP", quality=qualidade, method=METODO_WEBP)


def gravar_jpeg(im: Image.Image, destino: Path, qualidade: int) -> None:
    im.save(destino, "JPEG", quality=qualidade, optimize=True, progressive=True)


def gravar_com_teto(im, destino, gravador, q_inicial, teto_kb, q_minima):
    """
    Grava baixando a qualidade ate caber no teto (ou bater o piso).
    Devolve (qualidade_final, kb_final, coube).
    """
    qualidade = q_inicial
    while True:
        gravador(im, destino, qualidade)
        tamanho = kb(destino)
        if teto_kb is None or tamanho < teto_kb or qualidade <= q_minima:
            return qualidade, tamanho, (teto_kb is None or tamanho < teto_kb)
        qualidade = max(q_minima, qualidade - PASSO_QUALIDADE)


def recorte_cobrindo(im: Image.Image, largura: int, altura: int) -> Image.Image:
    """
    Recorte central "cover": escala pelo menor fator que cobre o frame inteiro
    e corta o excedente pelos dois lados, preservando o centro. Sem distorcer.
    """
    fator = max(largura / im.width, altura / im.height)
    inter = (max(largura, math.ceil(im.width * fator)),
             max(altura, math.ceil(im.height * fator)))
    escalada = im.resize(inter, REAMOSTRAGEM)
    esquerda = (escalada.width - largura) // 2
    topo = (escalada.height - altura) // 2
    return escalada.crop((esquerda, topo, esquerda + largura, topo + altura))


RATIOS_CONHECIDOS = [
    (1, 1), (5, 4), (4, 3), (3, 2), (16, 10), (16, 9), (2, 1), (21, 9),
    (4, 5), (3, 4), (2, 3), (10, 16), (9, 16), (1, 2), (9, 21),
]


def texto_aspecto(largura: int, altura: int) -> str:
    """Aspecto aproximado em texto: '16:9', '4:5', '3:2'..."""
    alvo = largura / altura
    melhor, erro_melhor = None, float("inf")
    for a, b in RATIOS_CONHECIDOS:
        erro = abs(alvo - a / b) / (a / b)
        if erro < erro_melhor:
            melhor, erro_melhor = (a, b), erro
    if erro_melhor <= 0.03:
        return f"{melhor[0]}:{melhor[1]}"
    d = math.gcd(largura, altura)
    return f"{largura // d}:{altura // d}"


# ---------------------------------------------------------------------------
# 4. PROCESSAMENTO
# ---------------------------------------------------------------------------
def processar(slug: str, config: dict) -> dict:
    origem_rel = config["origem"]
    origem = RAIZ / origem_rel
    if not origem.exists():
        raise FileNotFoundError(f"origem nao encontrada: {origem}")

    print(f"\n>> {slug}  <-  {origem_rel}")
    base, perfil, tam_bruto = abrir_normalizada(origem)
    print(f"   origem {tam_bruto[0]}x{tam_bruto[1]} | perfil: {perfil} | "
          f"pos-orientacao {base.width}x{base.height}")

    larguras = sorted(config.get("larguras", LARGURAS_PADRAO))
    tetos = config.get("teto_kb", {})

    variantes, puladas, notas = [], [], []

    for largura in larguras:
        if largura > base.width:
            puladas.append(largura)
            continue

        escalada = redimensionar(base, largura)
        altura = escalada.height
        teto = tetos.get(largura)

        for formato, ext, q_base, gravador in (
            ("webp", ".webp", QUALIDADE_WEBP, gravar_webp),
            ("jpeg", ".jpg", QUALIDADE_JPEG, gravar_jpeg),
        ):
            destino = SAIDA / f"{slug}-{largura}{ext}"
            q_final, tamanho, coube = gravar_com_teto(
                escalada, destino, gravador, q_base, teto, QUALIDADE_MINIMA
            )
            if teto is not None:
                estado = "ok" if coube else f"NAO COUBE (piso q{QUALIDADE_MINIMA})"
                notas.append(
                    f"{destino.name}: teto {teto} KB -> {tamanho} KB "
                    f"com qualidade {q_final} ({estado})"
                )
            variantes.append({
                "caminho": f"assets/img/{destino.name}",
                "largura": largura,
                "altura": altura,
                "formato": formato,
                "kb": tamanho,
                "qualidade": q_final,
            })

    if puladas:
        notas.append(
            f"sem upscale: larguras {', '.join(map(str, puladas))} puladas "
            f"(origem tem so {base.width} px de largura)"
        )

    maior = max(variantes, key=lambda v: v["largura"])
    resultado = {
        "slug": slug,
        "origem": origem_rel,
        "perfilOrigem": perfil,
        "larguraIntrinseca": maior["largura"],
        "alturaIntrinseca": maior["altura"],
        "aspecto": texto_aspecto(maior["largura"], maior["altura"]),
        "variantes": variantes,
        "puladas": puladas,
        "notas": notas,
    }

    if config.get("og"):
        resultado["og"] = gerar_og(base)

    return resultado


def gerar_og(base: Image.Image) -> dict:
    destino = SAIDA / "og-default.jpg"
    recorte = limpar(recorte_cobrindo(base, OG_LARGURA, OG_ALTURA))
    q_final, tamanho, coube = gravar_com_teto(
        recorte, destino, gravar_jpeg, OG_QUALIDADE_INICIAL, OG_TETO_KB, QUALIDADE_MINIMA
    )
    print(f"   og-default.jpg  {OG_LARGURA}x{OG_ALTURA}  {tamanho} KB  q{q_final}"
          f"{'' if coube else '  <-- ESTOUROU O TETO'}")
    return {
        "caminho": "assets/img/og-default.jpg",
        "largura": OG_LARGURA,
        "altura": OG_ALTURA,
        "kb": tamanho,
        "qualidade": q_final,
        "coube": coube,
    }


def tabela(resultados: list[dict]) -> None:
    linhas = [("ARQUIVO", "DIMENSOES", "FORMATO", "QUAL.", "KB")]
    for r in resultados:
        for v in r["variantes"]:
            linhas.append((
                Path(v["caminho"]).name,
                f'{v["largura"]}x{v["altura"]}',
                v["formato"],
                str(v["qualidade"]),
                f'{v["kb"]:.1f}',
            ))
        if "og" in r:
            og = r["og"]
            linhas.append((
                Path(og["caminho"]).name,
                f'{og["largura"]}x{og["altura"]}',
                "jpeg",
                str(og["qualidade"]),
                f'{og["kb"]:.1f}',
            ))

    larg = [max(len(l[i]) for l in linhas) for i in range(5)]
    sep = "-+-".join("-" * w for w in larg)

    print("\n" + "=" * len(sep))
    print("ARQUIVOS GERADOS")
    print("=" * len(sep))
    for i, l in enumerate(linhas):
        print(" | ".join(
            l[c].ljust(larg[c]) if c < 2 else l[c].rjust(larg[c]) for c in range(5)
        ))
        if i == 0:
            print(sep)
    print("=" * len(sep))


def remover_orfaos(resultados: list[dict]) -> list[str]:
    """Apaga variantes de execucoes anteriores que nao existem mais.

    Sem isto, trocar a foto de origem de um slug deixa lixo perigoso para
    tras. Aconteceu com card-executiva-copa: a origem passou de uma foto
    16:9 de 1920 px para uma 4:3 de 1260 px, o ladder deixou de gerar a
    variante 1600 -- mas o arquivo antigo continuou no disco. O srcset
    seguia oferecendo os dois, entao o navegador escolhia a FOTO ANTIGA em
    tela grande e a nova em tela pequena, com proporcao diferente e salto de
    layout junto.

    So mexe nos slugs processados nesta execucao, para que --somente nao
    apague o que nao olhou.
    """
    removidos: list[str] = []

    for r in resultados:
        slug = r["slug"]
        esperados = {Path(v["caminho"]).name for v in r["variantes"]}
        if "og" in r:
            esperados.add(Path(r["og"]["caminho"]).name)

        for existente in SAIDA.glob(f"{slug}-*"):
            # "card-lounge-w" nao pode reivindicar "card-lounge-w-2-400.webp":
            # o sufixo tem de ser largura + extensao, nada mais.
            resto = existente.name[len(slug) + 1:]
            if not re.fullmatch(r"\d+\.(webp|jpg)", resto):
                continue
            if existente.name not in esperados:
                existente.unlink()
                removidos.append(existente.name)

    return removidos


def main() -> int:
    ap = argparse.ArgumentParser(description="Otimiza as imagens do site Rota com Familia.")
    ap.add_argument("--somente", nargs="*", metavar="SLUG",
                    help="processa apenas os slugs informados")
    ap.add_argument("--json", action="store_true",
                    help="imprime um resumo JSON no final")
    args = ap.parse_args()

    alvos = IMAGENS
    if args.somente:
        desconhecidos = [s for s in args.somente if s not in IMAGENS]
        if desconhecidos:
            print(f"slug(s) desconhecido(s): {', '.join(desconhecidos)}", file=sys.stderr)
            return 2
        alvos = {s: IMAGENS[s] for s in args.somente}

    SAIDA.mkdir(parents=True, exist_ok=True)
    print(f"saida: {SAIDA}")

    resultados = [processar(slug, cfg) for slug, cfg in alvos.items()]

    orfaos = remover_orfaos(resultados)
    if orfaos:
        print("\nVARIANTES ORFAS REMOVIDAS")
        for o in orfaos:
            print(f"  - {o}")

    tabela(resultados)

    todas_notas = [n for r in resultados for n in r["notas"]]
    if todas_notas:
        print("\nOBSERVACOES")
        for n in todas_notas:
            print(f"  - {n}")

    total_kb = sum(v["kb"] for r in resultados for v in r["variantes"])
    total_kb += sum(r["og"]["kb"] for r in resultados if "og" in r)
    origem_kb = sum(
        (RAIZ / r["origem"]).stat().st_size / 1024 for r in resultados
    )
    print(f"\norigens: {origem_kb / 1024:.1f} MB  ->  gerados: {total_kb / 1024:.1f} MB "
          f"(soma de TODAS as variantes)")

    if args.json:
        print("\n---JSON---")
        print(json.dumps(resultados, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
