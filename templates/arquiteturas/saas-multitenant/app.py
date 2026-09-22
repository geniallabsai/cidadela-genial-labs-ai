#!/usr/bin/env python3
"""SaaS multi-tenant de exemplo (somente stdlib).

Isolamento: shared schema + namespace por tenant (em memória aqui; em produção,
tabela única com coluna tenant_id e índice composto (tenant_id, id)).
Resolução de tenant: subdomínio > header X-Tenant > query ?tenant=.
Autenticação: X-API-Key própria por tenant (derivada demo, veja README).

Roda local: python app.py · WSGI: `app` (compatível Vercel Python / Lambda WSGI).
"""
import hashlib
import json
import os
from wsgiref.simple_server import make_server

PORTA = int(os.environ.get("PORTA", "8010"))


def chave_demo(tenant):
    return "demo-" + hashlib.sha256(tenant.encode()).hexdigest()[:12]


TENANTS = {
    t.strip().lower(): {"chave": chave_demo(t.strip().lower()), "recursos": {}}
    for t in (os.environ.get("TENANTS_DEMO", "acme,contoso") or "").split(",")
    if t.strip()
}


def resolver_tenant(environ):
    host = environ.get("HTTP_HOST", "").split(":")[0]
    if "." in host:
        candidato = host.split(".", 1)[0]
        if candidato in TENANTS:
            return candidato
    header = environ.get("HTTP_X_TENANT", "").strip().lower()
    if header:
        return header
    for par in (environ.get("QUERY_STRING") or "").split("&"):
        if "=" in par and par.split("=")[0] == "tenant":
            return par.split("=")[1].strip().lower()
    return None


def app(environ, start_response):
    def responder(status, corpo):
        dados = json.dumps(corpo, ensure_ascii=False).encode()
        start_response(status, [("Content-Type", "application/json; charset=utf-8"),
                                ("Content-Length", str(len(dados)))])
        return [dados]

    if environ.get("PATH_INFO") == "/healthz":
        return responder("200 OK", {"ok": True, "tenants": sorted(TENANTS)})

    tenant = resolver_tenant(environ)
    if tenant not in TENANTS:
        return responder("404 Not Found", {
            "erro": "tenant não encontrado",
            "dica": "subdomínio, X-Tenant ou ?tenant= (demo: %s)" % ",".join(sorted(TENANTS))})

    if environ.get("HTTP_X_API_KEY", "") != TENANTS[tenant]["chave"]:
        return responder("401 Unauthorized", {"erro": "X-API-Key inválida para o tenant"})

    caminho = (environ.get("PATH_INFO") or "/").rstrip("/")
    metodo = environ.get("REQUEST_METHOD", "GET").upper()
    if not caminho.startswith("/recursos"):
        return responder("404 Not Found", {"erro": "use /recursos ou /recursos/<id>"})

    recursos = TENANTS[tenant]["recursos"]
    if caminho == "/recursos":
        if metodo == "POST":
            n = int(environ.get("CONTENT_LENGTH") or 0)
            try:
                dados = json.loads(environ["wsgi.input"].read(n).decode() or "{}")
            except Exception:
                return responder("400 Bad Request", {"erro": "JSON inválido"})
            novo_id = str(max((int(k) for k in recursos), default=0) + 1)
            item = {"id": novo_id, "nome": str(dados.get("nome", "recurso"))}
            recursos[novo_id] = item
            return responder("201 Created", {"tenant": tenant, "criado": item})
        return responder("200 OK", {"tenant": tenant, "recursos": recursos})

    item_id = caminho.rsplit("/", 1)[-1]
    if item_id in recursos:
        return responder("200 OK", {"tenant": tenant, "recurso": recursos[item_id]})
    return responder("404 Not Found", {"erro": "recurso não encontrado"})


if __name__ == "__main__":
    print("SaaS de exemplo em http://localhost:%d (tenants demo: %s)" % (PORTA, ", ".join(sorted(TENANTS))))
    make_server("0.0.0.0", PORTA, app).serve_forever()
