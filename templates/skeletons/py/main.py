"""{{NOME}} — esqueleto FastAPI com healthz e uma rota de exemplo."""
from fastapi import FastAPI

app = FastAPI(title="{{NOME}}", version="0.1.0")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/api/exemplo")
def exemplo():
    return {"mensagem": "troque esta rota pelo seu domínio (consulte ARCHITETURA-DADOS.md)"}
