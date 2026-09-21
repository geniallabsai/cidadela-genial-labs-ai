# {{NOME}}

Projeto nascido no **Genial Labs** ({{DATA}}) · stack: {{STACK}}.

## Começar
```bash
make run       # roda a aplicação localmente
make test      # suíte de testes
make docker-up # app + Postgres em compose
```

## Arquitetura de dados
`ARCHITETURA-DADOS.md` é a fonte da verdade dos dados (donos, contratos, gates).
Método completo: `skills/cidadela/references/arquitetura-dados.md` (ou rode `genial doctor`).

## CI
`.github/workflows/gates.yml` — gates que BLOQUEIAM merge (secrets, SCA, testes).
Referência: `skills/cidadela/references/ci-cd.md`.

## Infra
`Dockerfile` · `docker-compose.yml` (dev) · `k8s/` (deployment/service/ingress/hpa).
Escada de deploy: `skills/cidadela/references/cloud-deploy.md` · `genial deploy` mostra seu degrau.

## ADRs
Decisões de arquitetura/dados ficam em `docs/adr/`.
