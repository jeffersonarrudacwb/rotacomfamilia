"""
Monta o zip de deploy com APENAS o que o site serve.

As 664 MB em fotos/ ficam fora de proposito: o site referencia unicamente
assets/img/, e as fotos originais so existem dentro dos PDFs dos ebooks,
onde ja estao embutidas.
"""
import os
import shutil
import sys
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
    # PDFs — vao todos para downloads/ no servidor.
    #
    # Os nomes de pasta ebooks/ e mediakit/ NAO podem existir na raiz do site:
    # colidem com ebooks.html e mediakit.html. Quando isso acontece, o Apache
    # ve a pasta, redireciona /ebooks para /ebooks/, tenta listar o diretorio e
    # devolve 403 por causa do Options -Indexes. A regra de reescrita para URL
    # sem .html nunca chega a rodar. Por isso o destino aqui e outro.
    ("ebooks/pdf/01-manual-pontos-2026.pdf", "downloads/01-manual-pontos-2026.pdf"),
    ("ebooks/pdf/02-roteiros-eua-europa-caribe.pdf", "downloads/02-roteiros-eua-europa-caribe.pdf"),
    ("ebooks/pdf/03-planilhas-calculadoras.pdf", "downloads/03-planilhas-calculadoras.pdf"),
    ("mediakit/midia-kit-rota-com-familia.pdf", "downloads/midia-kit-rota-com-familia.pdf"),
]

PASTAS = ["assets/img"]


def coletar():
    """Devolve (caminho_no_servidor, caminho_local).

    Cada item de ARQUIVOS e uma string, quando origem e destino coincidem, ou
    uma tupla (origem_local, destino_no_servidor) quando o caminho publico e
    diferente de onde o arquivo mora no repositorio.
    """
    for item in ARQUIVOS:
        origem, destino = item if isinstance(item, tuple) else (item, item)
        caminho = os.path.join(ROOT, origem.replace("/", os.sep))
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"Faltando: {origem}")
        yield destino, caminho
    for pasta in PASTAS:
        base = os.path.join(ROOT, pasta.replace("/", os.sep))
        for dirpath, _, files in os.walk(base):
            for f in sorted(files):
                caminho = os.path.join(dirpath, f)
                rel = os.path.relpath(caminho, ROOT).replace(os.sep, "/")
                yield rel, caminho


PROIBIDOS = ("fotos/", "src/", "node_modules/", "scripts/", ".git")


def conferir(nomes):
    """Nada de foto bruta, arquivo de build ou segredo indo para o servidor."""
    vazou = [n for n in nomes if n.startswith(PROIBIDOS)]
    suspeitos = [n for n in nomes if os.path.basename(n) in
                 (".env", ".env.deploy", "package.json", "package-lock.json",
                  "tailwind.config.js", ".gitignore")]
    problemas = vazou + suspeitos
    if problemas:
        print(f"\nERRO: {len(problemas)} arquivo(s) que nao deveriam ser publicados:")
        for n in problemas[:10]:
            print(f"  {n}")
        raise SystemExit(1)
    print("Conferido: sem fotos brutas, sem arquivos de build, sem segredos.")


def montar_zip():
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
    print(DESTINO)

    with zipfile.ZipFile(DESTINO) as z:
        conferir(z.namelist())


def montar_dist():
    """Copia os arquivos publicaveis para dist/, que e o que sobe por FTP.

    Recria a pasta do zero a cada execucao para que um arquivo removido da
    lista tambem desapareca daqui.
    """
    dist = os.path.join(ROOT, "dist")
    if os.path.exists(dist):
        shutil.rmtree(dist)

    itens = list(coletar())
    total = 0
    for rel, origem in itens:
        alvo = os.path.join(dist, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        shutil.copy2(origem, alvo)
        total += os.path.getsize(origem)

    print(f"{len(itens)} arquivos | {total/1024/1024:.2f} MB em dist/")
    conferir([rel for rel, _ in itens])

    # O .htaccess e oculto e alguns clientes de FTP o ignoram. Se ele nao
    # subir, /ebooks para de funcionar sem o .html, os WebP saem com o tipo
    # errado e o HTTPS deixa de ser forcado. Falha ruidosamente aqui.
    if not os.path.exists(os.path.join(dist, ".htaccess")):
        print("\nERRO: .htaccess nao entrou em dist/")
        raise SystemExit(1)
    print("Conferido: .htaccess presente em dist/")


if __name__ == "__main__":
    if "--dist" in sys.argv:
        montar_dist()
    else:
        montar_zip()
