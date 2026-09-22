#!/usr/bin/env python3
"""Serviço A de exemplo (stdlib): CRUD de tarefas em memória + /healthz.
Cada serviço é dono dos seus dados — nada de banco compartilhado com o B.
"""
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PORTA = int(os.environ.get("PORTA", "8001"))
NOME = os.environ.get("SERVICO", "servico-a")
_dados = {"tarefas": {}, "_seq": 0}
_trava = threading.Lock()


def tratar(caminho, metodo, corpo):
    if caminho == "/healthz":
        return 200, {"ok": True, "servico": NOME}
    if caminho == "/tarefas" or caminho.startswith("/tarefas/"):
        if metodo == "GET":
            return 200, {"servico": NOME, "tarefas": _dados["tarefas"]}
        if metodo == "POST":
            with _trava:
                _dados["_seq"] += 1
                tarefa = {"id": _dados["_seq"],
                          "titulo": str(corpo.get("titulo", "sem titulo")),
                          "feito": False}
                _dados["tarefas"][str(tarefa["id"])] = tarefa
            return 201, tarefa
    return 404, {"erro": "rota não encontrada"}


class H(BaseHTTPRequestHandler):
    def _responder(self, status, corpo):
        dados = json.dumps(corpo, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def _manejar(self, metodo):
        caminho = urlparse(self.path).path.rstrip("/") or "/"
        corpo = {}
        if metodo == "POST":
            n = int(self.headers.get("Content-Length") or 0)
            try:
                corpo = json.loads(self.rfile.read(n).decode() or "{}")
            except Exception:
                return self._responder(400, {"erro": "JSON inválido"})
        status, saida = tratar(caminho, metodo, corpo)
        self._responder(status, saida)

    def do_GET(self):
        self._manejar("GET")

    def do_POST(self):
        self._manejar("POST")

    def log_message(self, *_args):
        pass


if __name__ == "__main__":
    print("%s ouvindo em :%d" % (NOME, PORTA))
    ThreadingHTTPServer(("0.0.0.0", PORTA), H).serve_forever()
