# cidadela — skill de auditoria, cirurgia e blindagem (arquitetura + dados + segurança + infra)

Audita a arquitetura de qualquer base de código (qualquer linguagem), pontua a saúde (1–10 com
evidências), estima probabilidade de quebra, faz **reversão de legado** a partir dos dados, decide
monolito × microsserviços por sinais objetivos, define a **arquitetura de dados alvo**
(`ARCHITETURA-DADOS.md`), **migração gradual de linguagem**, caça **vazamento de dados em 12 canais**,
executa **fase ofensiva** (probes de red-team + cheiro de código gerado por IA), blinda em camadas
(OWASP ASVS, STRIDE, multi-tenant T1–T6), instala **gates de CI/CD** e planeja a **plataforma**
(Docker, Compose, Kubernetes, VPS, AWS, deploy zero-downtime) — tudo em passos reversíveis (strangler-fig).

Feita para o caso real: produto construído com IA, cobrado como profissional, auditado por gente que
só sabe zomba. A resposta não é tecla — é checklist executado, evidência `arquivo:linha` e gate que
bloqueia merge.

**Parte do pacote Genial Labs** (instalador terminal com CLI `genial`, templates de arquitetura de
dados e infra): `curl -fsSL https://raw.githubusercontent.com/geniallabsai/genial-labs/main/install.sh | bash`
Instalada pelo pacote ou manualmente abaixo, o comportamento é o mesmo.

## Instalação no Codex
O Codex lê skills locais em `.agents/skills/`:

```bash
cp -r cidadela $RAIZ_DO_REPO/.agents/skills/   # repositório (equipe)
cp -r cidadela $HOME/.agents/skills/           # usuário (todos os projetos)
cp -r cidadela /etc/codex/skills/              # máquina (opcional)
```

Ou direto do GitHub: `$skill-installer install https://github.com/geniallabsai/cidadela.skill`

Regras do Codex (docs oficiais, "Build skills"):
- O scan parte da pasta de trabalho e sobe até a raiz do repositório; links simbólicos são aceitos.
- Mudanças detectadas automaticamente; se não aparecer, reinicie o Codex.
- Desativar sem apagar — em `~/.codex/config.toml`: `[[skills.config]]` com `path` + `enabled = false`.
- Distribuir: repositório GitHub (`$skill-installer <url>`) ou plugin.

Invocação: `/skills` → `cidadela`, ou implícita: "cidadela: audite este repositório".

## Instalação no Claude Code (mesmo formato)
```bash
cp -r cidadela .claude/skills/     # projeto
# ou ~/.claude/skills/             # global
```

## Uso
As 8 fases (0–7): Acervo → Raio-X → Diagnóstico → Veredito → **CHECKPOINT** → Cirurgia → Ofensiva →
Blindagem → Plataforma. Entregas: `RELATORIO-CIDADELA.md` + `ARCHITETURA-DADOS.md` + ADRs +
punch-list + workflow de gates + manifestos de infra.

## Estrutura
- `SKILL.md` — orquestrador das 8 fases (frontmatter `name` + `description`)
- `agents/openai.yaml` — metadados OpenAI (nome de exibição, prompt padrão, invocação implícita)
- `references/` — rubrica 10 dimensões, monolito × micro, cirurgia, blindagem, **arquitetura-dados**,
  **legado-reverse**, **migracao-linguagem**, **cloud-deploy** (inclui IA no produto), vazamento-dados
  (12 canais + PII BR + LGPD), ofensiva (probes + cheiro de IA), ci-cd (gates), multitenancy T1–T6,
  mapa de linguagens, anti-padrões
- `scripts/` — `inventario.py` (inclui detecção de cheiro de código-IA) e `grafico-servicos.py`
- `assets/` — templates de relatório/ADR + `workflow-ci-gates.yml`

## Requisitos
Python 3.8+ (apenas stdlib) para os scripts. Sem Python, use os comandos manuais no rodapé de cada script.
