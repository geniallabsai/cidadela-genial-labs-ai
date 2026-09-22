# microservicos

Gateway de rotas + 2 serviços (Python e Node), compose com healthchecks, zero dependência externa.

## Regra de ouro antes de copiar
**Monólito primeiro.** Microserviço é remédio, não dieta: só vale a pena quando houver sinais
medidos (equipes pisando uma na outra, escala diferente por parte, deploy acoplado). O critério
completo está em `skills/cidadela/references/monolito-vs-microservicos.md`. Se o projeto tem
menos de ~2 pessoas, este pack serve como **estudo de arquitetura** ou para migrar depois.

## Mapa do pack
```
gateway/        Node  — roteia /api/a/* → serviço A · /api/b/* → serviço B · /healthz agrega
servico-a/      Python — CRUD em memória (/tarefas) + /healthz
servico-b/      Node   — contadores (/stats) + /healthz
docker-compose.yml — sobe tudo; redis opcional via --profile cache
```
Portas: gateway **8080** · A **8001** · B **8002**. Sem banco compartilhado entre A e B —
cada serviço é dono dos seus dados (aqui em memória; em produção: um store por serviço).

## Contrato
- Todo serviço responde `/healthz` → `{"ok": true, "servico": "<nome>"}`.
- O gateway **não tem lógica de negócio**: só roteia, agrega saúde e injeta contexto.
- Rota 404/503 sempre em JSON, nunca HTML de erro cru.

## Rodar
```bash
docker compose up --build            # http://localhost:8080
curl localhost:8080/healthz          # { gateway ok, servico-a ok, servico-b ok }
curl -X POST localhost:8080/api/a/tarefas -d '{"titulo":"deploy"}' -H 'content-type: application/json'
curl localhost:8080/api/b/stats
```
Sem Docker (dev rápido): rode `python servico-a/app.py` e `node servico-b/index.js`, depois
`SERVICO_A=http://localhost:8001 SERVICO_B=http://localhost:8002 node gateway/index.js`.

## Evolução (quando crescer)
1. **Gates de CI**: copie `skills/cidadela/assets/workflow-ci-gates.yml` para cada repositório de serviço.
2. **Um repo por serviço** (monorepo só com time grande e tooling de CI por pasta).
3. **K8s**: namespace por serviço — comece pelos manifestos de `templates/k8s/` adaptando image/name.
4. **Tracing/logs**: antes do 4º serviço, adicione structured logging + request-id (sem isso, debug vira arqueologia).
