"""
Servidor estatico para testar o site localmente.

Existe porque o `python -m http.server` entrega .webp como
application/octet-stream em algumas instalacoes, e o navegador se recusa a
exibir a imagem -- o que faz parecer que o site esta quebrado quando nao esta.
Aqui os tipos MIME sao registrados na mao, batendo com o que o .htaccess
declara em producao.

Uso:  python scripts/servidor-local.py [porta]
"""
import http.server
import mimetypes
import socketserver
import sys
import pathlib

PORTA = int(sys.argv[1]) if len(sys.argv) > 1 else 4173
RAIZ = pathlib.Path(__file__).resolve().parent.parent

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

    def end_headers(self):
        # Sem cache no desenvolvimento, senao o navegador segura o CSS antigo.
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, formato, *args):
        codigo = str(args[1]) if len(args) > 1 else ""
        if codigo.startswith(("4", "5")):
            sys.stderr.write("  %s -> %s\n" % (args[0], codigo))


class Servidor(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with Servidor(("127.0.0.1", PORTA), Handler) as httpd:
        print(f"Servindo {RAIZ} em http://localhost:{PORTA}")
        print("Somente erros 4xx/5xx aparecem abaixo. Ctrl+C para parar.")
        httpd.serve_forever()
