"""Lambda de exemplo — API Gateway (proxy integration), zero dependências.

Contrato: event padrão da API Gateway HTTP/REST; resposta proxy integrada.
Segurança mínima: API key opcional via env API_KEY + header x-api-key.
"""
import base64
import json
import os

CHAVE_ESPERADA = os.environ.get("API_KEY", "")  # vazio = sem checagem (apenas dev)


def responder(status, corpo):
    return {"isBase64Encoded": False, "statusCode": status,
            "headers": {"Content-Type": "application/json; charset=utf-8",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "x-api-key,content-type"},
            "body": json.dumps(corpo, ensure_ascii=False)}


def lambda_handler(event, context):
    if event.get("httpMethod", "GET").upper() == "OPTIONS":
        return responder(204, {})
    if CHAVE_ESPERADA:
        keys = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
        if keys.get("x-api-key") != CHAVE_ESPERADA:
            return responder(401, {"erro": "header x-api-key ausente/inválido"})

    rota = event.get("path", "/")
    if rota in ("/", "/saude"):
        return responder(200, {"ok": True, "de": "lambda-exemplo"})
    if rota == "/eco":
        bruto = event.get("body", "")
        if event.get("isBase64Encoded"):
            bruto = base64.b64decode(bruto).decode("utf-8")
        try:
            dados = json.loads(bruto or "{}")
        except Exception:
            return responder(400, {"erro": "corpo deve ser JSON válido"})
        origem = event.get("requestContext", {}).get("identity", {}).get("sourceIp", "?")
        return responder(200, {"eco": dados, "origem": origem})
    return responder(404, {"erro": "rota não encontrada"})
