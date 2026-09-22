"""Função de exemplo: processa POST {"texto": "..."} e devolve métricas stateless.

Rota: POST /processar → 200 {"palavras": n, "minutos_leitura": x, "top_termos": [...]}
Estado: nenhum — todo o trabalho cabe numa única execução (regra do serverless).
"""
import json
from collections import Counter

STOP = set("a o e em de da do das dos um uma para com por no na nos nas que se ao aos".split())


def metricas(texto):
    palavras = [p for p in texto.lower().replace(",", " ").split() if len(p) > 2]
    top = [t for t, _ in Counter(p for p in palavras if p not in STOP).most_common(5)]
    return {"palavras": len(palavras),
            "minutos_leitura": round(len(palavras) / 200, 1),
            "top_termos": top}


def app(environ, start_response):
    def responder(status, corpo):
        dados = json.dumps(corpo, ensure_ascii=False).encode()
        start_response(status, [("Content-Type", "application/json; charset=utf-8")])
        return [dados]

    if environ.get("REQUEST_METHOD") != "POST":
        return responder("405 Method Not Allowed",
                         {"erro": "use POST com JSON {\"texto\": \"...\"}"})
    try:
        dados = json.loads(environ["wsgi.input"].read().decode("utf-8"))
        texto = str(dados.get("texto", "")).strip()
        if not texto:
            raise ValueError
    except Exception:
        return responder("400 Bad Request", {"erro": "esperado POST JSON válido com campo 'texto'"})
    return responder("200 OK", metricas(texto))


handler = app
