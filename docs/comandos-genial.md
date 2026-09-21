# `genial` — referência de comandos

Todos os comandos rodam a partir de qualquer pasta. Sem cor: `NO_COLOR=1 genial …`

## `genial`
Banner GENIAL LABS (azul tech) + resumo dos comandos.

## `genial banner`
Somente a arte.

## `genial init [DIR] [--stack py|node|go|auto]`
Cria um projeto novo **já com a arquitetura embutida**:
- `ARCHITETURA-DADOS.md` (fonte da verdade dos dados: donos, contratos, gates)
- skeleton com `/healthz` + rota de exemplo + **testes**
- `Dockerfile` (non-root, healthcheck), `.dockerignore`, `.env.example`, `.gitignore`
- `docker-compose.yml` (app + Postgres, paridade local)
- `k8s/` — deployment (securityContext restrito), service, ingress (rate limit + TLS), hpa
- `.github/workflows/gates.yml` — gates que BLOQUEIAM merge (secrets no histórico, SCA, testes)
- `Makefile` (run/test/docker-backup/k8s-apply)
- `README.md` + `docs/adr/ADR-0000-stack.md`
Arquivos existentes nunca são sobrescritos (o scaffold respeita o que já há).

## `genial doctor [DIR]`
Roda a Fase 0 (Acervo) da skill cidadela sobre o projeto: linguagens/LOC, topologia,
segredos, sinais multi-tenant e **cheiro de código gerado por IA**. A interpretação das
Fases 1–7 (veredito, cirurgia, ofensiva, blindagem, plataforma) continua no Codex/Claude
basta dizer "cidadela".

## `genial skills`
Lista as skills instaladas (usuário e repositório, Codex e Claude Code) com validação do
frontmatter (name + description).

## `genial deploy [DIR]`
Mede o degrau de infraestrutura (0–5): Dockerfile → compose → gates CI → K8s → IaC/cloud —
e indica o próximo passo com a seção certa de `cloud-deploy.md`.

## `genial update`
`git pull` se o pacote foi clonado; senão, indica o comando de reinstalação.

## `genial uninstall [-y]`
Remove `~/.genial-labs`, `~/.local/bin/genial` e as cópias da skill cidadela.
