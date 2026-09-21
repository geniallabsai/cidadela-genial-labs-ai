# Genial Labs

> O instalador que faz produto construído com IA render como engenharia de software profissional:
> **arquitetura** (com **dados**, **segurança ofensiva e defensiva**, **CI/CD** e **infra**) que guia cada projeto — em qualquer linguagem.

```
██████╗   ██████╗  ███╗   ███╗  ███╗  █████╗  ██╗       ██████╗  ██████╗  ██████╗  ███████╗
██╔══██╗ ██╔═══██╗ ██╔██╗ ██╔╝  ████╗ ██╔══██╗██║      ██╔═══██╗██╔═══██╗██╔═══██╗ ██╔════╝
██████╔╝ ██║   ██║ ███████║    ██╔██╗ ███████║██║      ██║   ██║██║   ██║██║   ██║ ███████╗
██╔══██╗ ██║   ██║ ██╔══██║    ██║╚██╗ ██╔══██║██║      ██║   ██║██║   ██║██║   ██║ ██╔══╝
██║  ██║ ╚██████╔╝ ██║  ██║    ██║ ╚████╗██║  ██║██║    ╚██████╔╝╚██████╔╝╚██████╔╝ ███████╗
╚═╝  ╚═╝  ╚═════╝  ╚═╝  ╚═╝    ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝    ╚═════╝  ╚═════╝  ╚═════╝  ╚══════╝
```

O argumento contra "projeto feito com IA" quase sempre é o mesmo: vai vazar dado, a arquitetura
quebra e o pipeline não segura nada. A resposta do Genial Labs não é tecla — é um pacote que o
instalador coloca na sua máquina e que **guia o projeto inteiro**: a skill **Cidadela** (8 fases de
engenharia) + o comando `genial` (scaffold guiado, auditoria, escada de infra) + templates de
arquitetura de dados e de deploy.

## Instalação (uma linha no terminal)

```bash
curl -fsSL https://raw.githubusercontent.com/brunao23/genial-labs/main/install.sh | bash
```

- Linux/macOS · bash + python3 ≥ 3.7 (só stdlib) · git/curl opcionais (há fallback por zip+urllib)
- `--repo` também instala a skill nas pastas `.agents/skills` e `.claude/skills` do repositório atual
- No final, o instalador mostra o bloco GENIAL LABS em azul tech e já fez self-test (`genial init` em diretório de teste)

Remover: `genial uninstall` (ou `bash uninstall.sh`).

## O que ele instala

| Onde | O quê |
|------|-------|
| `~/.genial-labs/` | pacote completo (skill, templates, docs) |
| `~/.agents/skills/cidadela` + `~/.claude/skills/cidadela` | a skill Cidadela (Codex **e** Claude Code) |
| `~/.local/bin/genial` | o comando terminal |

## Como ele guia o projeto

1. **Novo projeto**: `genial init meu-projeto --stack py\|node\|go`
   → nasce com `ARCHITETURA-DADOS.md` (donos por entidade, contratos, gates), skeleton com testes,
   Dockerfile/compose/k8s, gates de CI que bloqueiam merge e ADR-0000.
2. **A arquitetura entra no código**: abra no Codex/Claude e diga `"cidadela: este projeto é novo — confirme a arquitetura de dados"` — ou deixe a skill se acionar sozinha (`/skills` → `cidadela`).
3. **Código legado**: `"cidadela: faça a reversão deste legado"` → arqueologia pelos dados (fósseis), as 3 operações vitais, regras ocultas, suíte de caracterização e plano strangler (`legado-reverse.md`).
4. **Código gerado por IA**: o inventário detecta o cheiro (segredo em log, SQL por concatenação, CORS `*`, JWT fraco, webhook sem assinatura, debug ligado…) e a Fase 5 ofensiva roda as probes contra ele.
5. **Outra linguagem serve melhor?**: `migracao-linguagem.md` — sinais medidos (≥ 2), padrões graduais (ports & adapters → feature a feature → módulo quente → replatform), um módulo × uma linguagem por vez.
6. **Dados**: `arquitetura-dados.md` — inventário PII/credencial/financeiro, contrato N-1, idempotência, dinheiro em centavos, gates de qualidade no CI.
7. **Infra**: `genial deploy` mostra seu degrau 0–5 (VPS → Compose → gates CI → K8s → IaC/cloud); `cloud-deploy.md` cobre VPS sábio, Docker, K8s mínimo saudável, AWS prático (Fargate/App Runner, RDS, OIDC no CI, Terraform desde o dia 1) e **IA no produto** (abstração de provedor, teto de custo, evals no CI, human-in-the-loop).
8. **Entrega sem parar produção**: canary 1→10→100%, rollback < 5 min, expand-contract no banco, smoke pós-deploy.

## Comandos

| Comando | Faz |
|---------|-----|
| `genial init [DIR] --stack py\|node\|go` | projeto novo com arquitetura embutida |
| `genial doctor [DIR]` | auditoria (Fase 0 da Cidadela) direto no terminal |
| `genial deploy [DIR]` | degrau de infra 0–5 + próximo passo |
| `genial skills` | lista skills instaladas (Codex/Claude) |
| `genial update` | atualiza o pacote |
| `genial uninstall [-y]` | remove tudo |

Detalhes: [`docs/comandos-genial.md`](docs/comandos-genial.md).

## A skill Cidadela (núcleo do pacote)

8 fases, sempre com evidência `arquivo:linha` e checkpoint humano antes de escrever código:

| Fase | O quê |
|------|-------|
| 0 Acervo | inventário estrutural + cheiro de código-IA + grafo de serviços |
| 1 Raio-X | topologia, distribuído-monolito, legados, multi-tenant, estado de dados |
| 2 Diagnóstico | 10 dimensões + T1–T6 (tenancy) + probabilidade de quebra (4 cenários) |
| 3 Veredito | monolito × micro × linguagem × **dados alvo** → ADRs + **CHECKPOINT** |
| 4 Cirurgia | strangler-fig: caracterizar → flag → sombra → cutover 1/10/100 → descomissionar |
| 5 Ofensiva | red-team em staging: primeira hora do atacante, severidade P0/P1/P2 |
| 6 Blindagem | 12 canais de vazamento, OWASP ASVS/STRIDE, gates de CI/CD que bloqueiam merge |
| 7 Plataforma | escada VPS/Docker/K8s/AWS + deploy zero-downtime + IA no produto |

A mesma skill existe no repositório dedicado [cidadela.skill](https://github.com/brunao23/cidadela.skill)
(conteúdo idêntico, sincronizado) — instale por lá se preferir só a skill, sem o CLI.

## Estrutura do pacote

```
genial-labs/
├── install.sh / uninstall.sh     # instalador de terminal (banner azul tech + self-test)
├── genial                        # CLI (python3 stdlib): init/doctor/skills/deploy/update/uninstall
├── skills/cidadela/              # a skill (8 fases — idêntica à de cidadela.skill)
│   ├── SKILL.md                  # orquestrador (frontmatter name+description)
│   ├── references/               # 14 protocolos: dados, legado, linguagem, cloud, ofensiva, vazamentos…
│   ├── scripts/                  # inventario.py (cheiro de IA) + grafico-servicos.py
│   └── assets/                   # relatório, ADR, workflow-ci-gates.yml
├── templates/                    # ARCHITETURA-DADOS.md, Dockerfiles, compose, k8s/, skeletons py/node/go
└── docs/comandos-genial.md       # referência do CLI
```

## Requisitos

bash 3.2+ · python3 ≥ 3.7 (stdlib) · git/curl opcionais · para os projetos: a toolchain da stack escolhida.

## Changelog

- **v1.0.0** (2026-09-21): primeiro pacote — skill Cidadela v3 (8 fases: + arquitetura de dados, reversão de legado, migração de linguagem e plataforma cloud), CLI `genial`, instalador com banner GENIAL LABS, templates de dados/infra, gates de CI.
