"""Função serverless de saúde (Vercel Python · WSGI · zero dependência).

Rota: GET /saude → 200 {"ok": true}
Em Vercel, o nome do arquivo vira a rota; localmente teste com qualquer runner WSGI.
"""
import json
import os


def app(environ, start_response):
    if environ.get("PATH_INFO") in ("/", "/saude"):
        corpo = json.dumps({"ok": True,
                            "ambiente": os.environ.get("VERCEL_ENV", "local"),
                            "funcao": "saude"}).encode()
        start_response("200 OK", [("Content-Type", "application/json; charset=utf-8")])
        return [corpo]
    start_response("404 Not Found", [("Content-Type", "application/json")])
    return [json.dumps({"erro": "rota não encontrada"}).encode()]


# alias para runtimes que resolvem o callable pelo nome
handler = app
