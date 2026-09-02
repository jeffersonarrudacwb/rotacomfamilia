"""
Monta o zip de deploy com APENAS o que o site serve.

As 664 MB em fotos/ ficam fora de proposito: o site referencia unicamente
assets/img/, e as fotos originais so existem dentro dos PDFs dos ebooks,
onde ja estao embutidas.
"""
import hashlib
import io
import os
import re
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
    "parcerias.html",
    "mediakit.html",
    "privacidade.html",
    "termos.html",
    # Estilos e scripts
    "styles.css",
    "script.js",
    "assets/tailwind.css",
    "assets/rota-forms.js",
    # Ponte de inscricao no Brevo. A chave de API NAO vem daqui: fica em
    # rota-config.php, um nivel acima da public_html, fora do deploy.
    "api/inscrever.php",
    # Numeros das redes para o midia kit. O .php atualiza o YouTube sozinho e
    # le o .json como base; sem o .json ele devolve 503 e a pagina fica com os
    # numeros escritos no proprio HTML. Os dois precisam subir juntos.
    "api/numeros.php",
    "dados/numeros-redes.json",
    # Configuracao do servidor e SEO
    ".htaccess",
    "robots.txt",
    # Navegador antigo e leitor de feed procuram /favicon.ico direto na raiz,
    # sem olhar as tags do HTML.
    "favicon.ico",
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

# assets/logos entrou junto com a pagina de parcerias: os QR codes vao
# embutidos no HTML, mas o logo dos parceiros e arquivo de verdade.
PASTAS = ["assets/img", "assets/logos"]


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


# Assets que o .htaccess manda o navegador guardar por 30 dias. Sem versao na
# URL, quem ja visitou o site continua rodando a copia velha por ate um mes —
# foi assim que uma correcao publicada do formulario ficou invisivel para quem
# tinha o rota-forms.js antigo em cache, e o cadastro caiu no modo manual.
ASSETS_VERSIONADOS = [
    "assets/rota-forms.js",
    "assets/tailwind.css",
    "styles.css",
    "script.js",
]


def versionar_assets(dist):
    """Acrescenta ?v=<hash> as referencias dos assets no HTML de dist/.

    O hash vem do conteudo: se o arquivo nao mudou, a URL nao muda e o cache do
    visitante continua valido. Se mudou, a URL muda e o navegador e obrigado a
    baixar de novo. Os arquivos fonte nao sao tocados, so a copia em dist/.
    """
    hashes = {}
    for rel in ASSETS_VERSIONADOS:
        caminho = os.path.join(dist, rel.replace("/", os.sep))
        if not os.path.exists(caminho):
            continue
        with open(caminho, "rb") as f:
            hashes[rel] = hashlib.sha1(f.read()).hexdigest()[:8]

    if not hashes:
        return

    alterados = 0
    for nome in os.listdir(dist):
        if not nome.endswith(".html"):
            continue
        caminho = os.path.join(dist, nome)
        with open(caminho, "r", encoding="utf-8") as f:
            html = f.read()

        original = html
        for rel, h in hashes.items():
            # Casa href="styles.css", src="assets/rota-forms.js", com ou sem ./
            for ref in (rel, "./" + rel, "/" + rel):
                html = html.replace('"' + ref + '"', '"' + ref + "?v=" + h + '"')

        if html != original:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(html)
            alterados += 1

    print("Versionados: " + ", ".join(f"{r}?v={h}" for r, h in hashes.items()))
    print(f"Reescritos {alterados} arquivos HTML em dist/")


# Extensoes que sao arquivo de verdade no servidor. Link de pagina fica de
# fora: /ebooks e /parcerias existem por causa da regra de URL sem extensao do
# .htaccess, e nao como arquivo com esse nome.
EXTENSOES_DE_ARQUIVO = (
    ".css", ".js", ".png", ".jpg", ".jpeg", ".webp", ".avif", ".svg",
    ".pdf", ".ico", ".woff2", ".webmanifest", ".xml", ".txt", ".php",
)


def referencias_do_html(texto):
    """Todo caminho local que a pagina pede: src, href e srcset."""
    achados = set()
    for atr in ("src", "href"):
        achados.update(re.findall(r'%s="([^"]+)"' % atr, texto))
    for conjunto in re.findall(r'srcset="([^"]+)"', texto):
        for parte in conjunto.split(","):
            url = parte.strip().split(" ")[0]
            if url:
                achados.add(url)
    return achados


def conferir_referencias(dist):
    """Falha se alguma pagina pedir arquivo que nao esta indo junto.

    Existe por causa de um erro real: o .gitignore tinha um *.png abrangente e
    engoliu em silencio o logo de dois parceiros. O git add nao reclama de
    arquivo ignorado, o build local passou porque os arquivos estavam no disco,
    e o site foi ao ar pedindo duas imagens que nunca chegaram ao servidor.

    Conferir aqui pega qualquer caso dessa familia: arquivo esquecido no
    .gitignore, caminho digitado errado, arquivo renomeado sem atualizar o HTML.
    """
    faltando = []
    for dirpath, _, files in os.walk(dist):
        for nome in files:
            if not nome.endswith(".html"):
                continue
            caminho = os.path.join(dirpath, nome)
            pagina = os.path.relpath(caminho, dist).replace(os.sep, "/")
            texto = io.open(caminho, encoding="utf-8").read()
            for url in referencias_do_html(texto):
                if url.startswith(("http://", "https://", "//", "mailto:",
                                   "tel:", "#", "data:", "javascript:")):
                    continue
                limpa = url.split("?")[0].split("#")[0]
                if not limpa or limpa.startswith("/blog"):
                    continue
                if not limpa.lower().endswith(EXTENSOES_DE_ARQUIVO):
                    continue
                alvo = os.path.join(dist, limpa.lstrip("/").replace("/", os.sep))
                if not os.path.exists(alvo):
                    faltando.append((pagina, limpa))

    if faltando:
        print("")
        print("ERRO: %d referencia(s) apontam para arquivo que nao esta "
              "em dist/:" % len(faltando))
        for pagina, url in sorted(set(faltando)):
            print("  %-20s -> %s" % (pagina, url))
        print("")
        print("Se o arquivo existe no seu disco mas nao aqui, o culpado "
              "costuma ser o .gitignore:")
        print("  git check-ignore -v <caminho>")
        raise SystemExit(1)
    print("Conferido: toda imagem, folha e script referenciado esta em dist/.")


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
    versionar_assets(dist)

    # O .htaccess e oculto e alguns clientes de FTP o ignoram. Se ele nao
    # subir, /ebooks para de funcionar sem o .html, os WebP saem com o tipo
    # errado e o HTTPS deixa de ser forcado. Falha ruidosamente aqui.
    if not os.path.exists(os.path.join(dist, ".htaccess")):
        print("\nERRO: .htaccess nao entrou em dist/")
        raise SystemExit(1)
    print("Conferido: .htaccess presente em dist/")
    conferir_referencias(dist)


if __name__ == "__main__":
    if "--dist" in sys.argv:
        montar_dist()
    else:
        montar_zip()
