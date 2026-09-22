#!/usr/bin/env python3
"""Smoke test do SaaS sem rede: chama o WSGI direto com environ sintético.
Rode: python test_app.py (na pasta do pack) — sai 0 se tudo passar.
"""
import hashlib
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("TENANTS_DEMO", "acme,contoso")
import app as s  # noqa: E402


def chave(t):
    return "demo-" + hashlib.sha256(t.encode()).hexdigest()[:12]


def chamada(path, metodo="GET", corpo=None, tenant="acme", api_key="errada"):
    entrada = io.BytesIO(json.dumps(corpo or {}).encode())
    env = {"REQUEST_METHOD": metodo, "PATH_INFO": path, "QUERY_STRING": "",
           "HTTP_X_TENANT": tenant, "HTTP_X_API_KEY": api_key,
           "wsgi.input": entrada, "CONTENT_LENGTH": str(len(entrada.getvalue()))}
    resultado = {}

    def iniciar(status, _headers):
        resultado["status"] = status

    corpo_saida = b"".join(s.app(env, iniciar))
    resultado["corpo"] = json.loads(corpo_saida.decode())
    return resultado


falhas = 0


def checa(nome, cond):
    global falhas
    print("  %s %s" % ("OK " if cond else "FALHOU", nome))
    falhas += 0 if cond else 1


r = chamada("/healthz")
checa("healthz responde", r["status"].startswith("200") and r["corpo"]["ok"])
checa("tenant inexistente → 404", chamada("/recursos", tenant="nobody")["status"].startswith("404"))
checa("chave errada → 401", chamada("/recursos", api_key="x")["status"].startswith("401"))

acme, contoso = chave("acme"), chave("contoso")
checa("tenant errado com a chave certa → 401",
      chamada("/recursos", tenant="contoso", api_key=acme)["status"].startswith("401"))

r = chamada("/recursos", "POST", {"nome": "plano-pro"}, api_key=acme)
checa("cria recurso (acme)", r["status"].startswith("201"))
r = chamada("/recursos", "POST", {"nome": "coisa-contoso"}, tenant="contoso", api_key=contoso)
checa("cria recurso (contoso)", r["status"].startswith("201"))

lista_acme = chamada("/recursos", api_key=acme)["corpo"]["recursos"]
lista_contoso = chamada("/recursos", tenant="contoso", api_key=contoso)["corpo"]["recursos"]
checa("isolamento: acme não vê o recurso do contoso",
      len(lista_acme) == 1 and len(lista_contoso) == 1 and lista_acme != lista_contoso)

print("RESULTADO:", "TODOS OS TESTES PASSARAM ✔" if falhas == 0 else "%d FALHA(S)" % falhas)
sys.exit(1 if falhas else 0)
