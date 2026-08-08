"""
Monta o zip de deploy com APENAS o que o site serve.

As 664 MB em fotos/ ficam fora de proposito: o site referencia unicamente
assets/img/, e as fotos originais so existem dentro dos PDFs dos ebooks,
onde ja estao embutidas.
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(ROOT, "deploy-rotacomfamilia.zip")

ARQUIVOS = [
    # Paginas
    "index.html",
    "ebooks.html",
    "assessoria.html",
    "cursos.html",
    "mediakit.html",
    "privacidade.html",
    "termos.html",
    # Estilos e scripts
    "styles.css",
    "script.js",
    "assets/tailwind.css",
    "assets/rota-forms.js",
    # Configuracao do servidor e SEO
    ".htaccess",
    "robots.txt",
    "sitemap.xml",
    # PDFs
    "ebooks/pdf/01-manual-pontos-2026.pdf",
    "ebooks/pdf/02-roteiros-eua-europa-caribe.pdf",
    "ebooks/pdf/03-planilhas-calculadoras.pdf",
    "mediakit/midia-kit-rota-com-familia.pdf",
]

PASTAS = ["assets/img"]


def coletar():
    for rel in ARQUIVOS:
        caminho = os.path.join(ROOT, rel.replace("/", os.sep))
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"Faltando: {rel}")
        yield rel, caminho
    for pasta in PASTAS:
        base = os.path.join(ROOT, pasta.replace("/", os.sep))
        for dirpath, _, files in os.walk(base):
            for f in sorted(files):
                caminho = os.path.join(dirpath, f)
                rel = os.path.relpath(caminho, ROOT).replace(os.sep, "/")
                yield rel, caminho


def main():
    if os.path.exists(DESTINO):
        os.remove(DESTINO)

    itens = list(coletar())
    bruto = 0
    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel, caminho in itens:
            z.write(caminho, arcname=rel)
            bruto += os.path.getsize(caminho)

    final = os.path.getsize(DESTINO)
    print(f"{len(itens)} arquivos | {bruto/1024/1024:.2f} MB em disco "
          f"-> {final/1024/1024:.2f} MB compactado")
    print(f"{DESTINO}")

    # Conferencia: nada de fotos brutas nem arquivos de build no pacote
    with zipfile.ZipFile(DESTINO) as z:
        nomes = z.namelist()
    vazou = [n for n in nomes if n.startswith(("fotos/", "src/", "node_modules/", "scripts/"))]
    if vazou:
        print(f"\nATENCAO: {len(vazou)} arquivo(s) que nao deveriam estar no zip:")
        for n in vazou[:10]:
            print(f"  {n}")
    else:
        print("Conferido: sem fotos brutas, sem arquivos de build.")


if __name__ == "__main__":
    main()
