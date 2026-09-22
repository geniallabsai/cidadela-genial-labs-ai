# Referência do comando `genial`

O CLI do Genial Labs. Python 3.7+ (stdlib), sem dependências. Todos os comandos acecem rodar de
qualquer pasta. Cores respeitam `NO_COLOR=1` e ficam off quando a saída não é um terminal.

Variáveis úteis: `GENIAL_HOME=/caminho` aponta o pacote fora do padrão; o local descoberto é
`~/.genial-labs/` (ou a própria árvore do repositório, quando executando daqui).

## `genial` (sem argumentos)

Banner **GENIAL LABS** + resumo dos comandos. Útil para verificar se a instalação está viva.

## `genial banner`

Imprime só a arte (azul tech) + versão. Sem sair do shell, `genial banner`.

## `genial init [DIR] [--stack py|node|go|auto]`

**Cria um projeto novo já com a arquitetura embutida.** Padrão: `DIR=.` (pasta atual),
`--stack auto` (detecta `go.mod`, `package.json`, `pyproject.toml`/`requirements.txt`; senão `py`).

Arquivos gerados (arquivo existente **nunca** é sobrescrito — o scaffold respeita o que já há):

| Arquivo | Função |
|---------|--------|
| `ARCHITETURA-DADOS.md` | fonte da verdade dos dados (donos, contratos, gates) — placeholders `{{NOME}}/{{DATA}}/{{STACK}}` substituídos |
| skeleton do stack | app mínimo com `/healthz` + rota de exemplo + **testes** |
| `Dockerfile` (+`.dockerignore`, `.env.example`, `.gitignore`) | non-root + healthcheck + portas do stack |
| `docker-compose.yml` | paridade local: app + Postgres com healthcheck |
| `k8s/deployment.yaml` · `service.yaml` · `ingress.yaml` · `hpa.yaml` | manifestos mínimos saudáveis (placeholders `{{NOME}}`, `{{PORTA_CONTAINER}}`) |
| `.github/workflows/gates.yml` | gates de segurança que bloqueiam merge (do asset da skill) |
| `Makefile` | `run` / `test` / `docker-build/up/down` / `backup-db` / `k8s-apply` já ajustados ao stack |
| `README.md` | quickstart do projeto |
| `docs/adr/ADR-0000-stack.md` | decisão de stack registrada com condição de reversibilidade |

Exemplos:

```bash
genial init                      # nesta pasta, stack autodetectada
genial init loja-api --stack go  # nova pasta
genial init --stack node         # explicito
```

Próximos passos exibidos no final: `git init`, o que dizer ao agente ("cidadela: confirme a
arquitetura de dados deste projeto novo") e os comandos de execução.

## `genial doctor [DIR]`

**Auditoria no terminal** — roda a Fase 0 (Acervo) da skill Cidadela sobre o projeto:
linguagens/LOC, manifestos/frameworks, topologia de deploy, segredos e canais de vazamento
suspeitos, sinais de multi-tenancy e cheiro de código gerado por IA. Ao final, indica onde
continuar (Fases 1–7 rodam dentro do agente).

```bash
genial doctor            # pasta atual
genial doctor ../outro   # outro caminho
```
O relatório termina com **veredito por componente** (MANTER/BLINDAR/MIGRAR/OBSERVAR):
cada linha traz evidência `arquivo:linha` e a próxima ação concreta.

## `genial skills`

Lista as skills instaladas nos níveis usuário (`~/.agents/skills`, `~/.claude/skills`),
repositório (`.agents/skills`, `.claude/skills` da pasta atual) e no próprio pacote (fonte).
Valida o frontmatter de cada `SKILL.md` (`name` + `description`) e marca `[ok]`/`[!!]`.

## `genial deploy [DIR]`

**Mede a maturidade de infraestrutura** do projeto numa escada 0–5 e indica o próximo passo:

| Degrau | Sinal detectado |
|--------|-----------------|
| 0 | nada ainda |
| 1 | `Dockerfile` |
| 2 | + `docker-compose*.yml` |
| 3 | + workflow de CI (`.github/workflows`, GitLab CI) |
| 4 | + manifestos Kubernetes (`k8s/` ou `*deployment*.yaml`) |
| 5 | + IaC (`.tf`) / cloud |

Exemplo de saída: *"Maturidade: degrau 4/5 — + manifestos K8s · Próximo passo: Terraform +
cloud real (cloud-deploy.md §6)"*.

## `genial update`

Se o pacote foi instalado por `git clone` (`.genial-labs/.git` existe) → `git pull --ff-only`.
Senão (instalado por zip) → mostra o comando de reinstalação, que é idempotente.

## `genial uninstall [-y]`

Remove exatamente o que o instalador colocou: `~/.genial-labs/`, `~/.local/bin/genial` e as
cópicas da skill em `~/.agents/skills/cidadela` e `~/.claude/skills/cidadela`. Sem `-y`, pede
confirmação no terminal.

## Códigos de saída

| Código | Significado |
|--------|-------------|
| 0 | sucesso |
| 1 | falha operacional (pacote incompleto, diretório inexistente, auditoria com alerta) |
| 2 | comando desconhecido |
