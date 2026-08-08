"""
Servidor estatico para testar o site localmente.

Imita o que o Apache da HostGator faz em producao, para que problema de URL
apareca aqui e nao no ar. Duas coisas justificam este arquivo existir:

1. Tipos MIME. O `python -m http.server` entrega .webp como
   application/octet-stream em algumas instalacoes e o navegador se recusa a
   exibir a imagem, fazendo parecer que o site esta quebrado quando nao esta.

2. URL sem .html. Em producao o .htaccess faz /ebooks servir ebooks.html.
   Sem imitar isso aqui, um link interno quebrado so aparece depois de publicar
   -- foi exatamente assim que /ebooks e /mediakit foram para o ar devolvendo
   403, porque existiam pastas com o mesmo nome das paginas.

Serve a pasta dist/ quando ela existe, que e o conjunto exato de arquivos que
sobe para o servidor, incluindo downloads/. Se dist/ nao existir, cai na raiz do
repositorio e avisa -- nesse modo os links de PDF nao funcionam, porque eles so
recebem o caminho publico ao montar o dist.

Uso:  python scripts/servidor-local.py [porta]
      python scripts/gerar-deploy.py --dist   (rode antes, para o preview fiel)
"""
import http.server
import mimetypes
import os
import pathlib
import socketserver
import sys

PORTA = int(sys.argv[1]) if len(sys.argv) > 1 else 4173
REPO = pathlib.Path(__file__).resolve().parent.parent
DIST = REPO / "dist"

USANDO_DIST = DIST.is_dir()
RAIZ = DIST if USANDO_DIST else REPO

for ext, tipo in {
    ".webp": "image/webp",
    ".avif": "image/avif",
    ".svg": "image/svg+xml",
    ".js": "application/javascript",
    ".mjs": "application/javascript",
    ".json": "application/json",
    ".woff2": "font/woff2",
    ".pdf": "application/pdf",
}.items():
    mimetypes.add_type(tipo, ext)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RAIZ), **kwargs)

    def translate_path(self, path):
        """Resolve /pagina para pagina.html, como a regra de reescrita faz.

        Mesmo criterio do .htaccess: um unico segmento, sem ponto nem barra, e
        somente quando o .html correspondente existe de fato.
        """
        limpo = path.split("?", 1)[0].split("#", 1)[0].strip("/")
        if limpo and "/" not in limpo and "." not in limpo:
            candidato = RAIZ / f"{limpo}.html"
            if candidato.is_file():
                return str(candidato)
        return super().translate_path(path)

    def end_headers(self):
        # Sem cache no desenvolvimento, senao o navegador segura o CSS antigo.
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def list_directory(self, path):
        # Producao roda com Options -Indexes. Listar pasta aqui daria uma falsa
        # sensacao de que a URL funciona.
        self.send_error(403, "Listagem de diretorio desabilitada")
        return None

    def log_message(self, formato, *args):
        codigo = str(args[1]) if len(args) > 1 else ""
        if codigo.startswith(("4", "5")):
            sys.stderr.write("  %s -> %s\n" % (args[0], codigo))


class Servidor(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    if USANDO_DIST:
        print(f"Servindo dist/ (identico ao que vai para o ar) em http://localhost:{PORTA}")
    else:
        print(f"Servindo a raiz do repositorio em http://localhost:{PORTA}")
        print("AVISO: dist/ nao existe, entao os links de PDF em /downloads/ vao dar 404.")
        print("       Rode  python scripts/gerar-deploy.py --dist  e reinicie para um preview fiel.")
    print("Somente erros 4xx/5xx aparecem abaixo. Ctrl+C para parar.")
    with Servidor(("127.0.0.1", PORTA), Handler) as httpd:
        httpd.serve_forever()
