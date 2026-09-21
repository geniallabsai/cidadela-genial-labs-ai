# A skill Cidadela — o cérebro do pacote

A Cidadela é uma **Agent Skill** (formato aberto agentskills.io) que lê a base de código real —
legado ou gerada por IA — e conduz o projeto inteiro: diagnóstico, veredito, cirurgia, ataque,
blindagem e plataforma. Roda idêntica no **Codex** e no **Claude Code**, em qualquer linguagem.

Quatro chapéus num corpo só: engenheiro staff (arquitetura), red teamer (ofensiva), arquiteto de
dados (contratos e evolução) e auditor de privacidade (LGPD e canais de vazamento).

## As 8 regras inegociáveis

1. **Evidência antes de opinião** — todo achado cita `arquivo:linha` ou a resposta/probe que o sustenta.
2. **Ordem dos chapéus** — diagnóstico primeiro; escrita só depois.
3. **Checkpoint obrigatório** — o relatório completo vai para aprovação humana **antes** de qualquer código escrito.
4. **Nada quebra** — cada passo termina entregável: CI verde, flag desligada = comportamento antigo, rollback < 5 min.
5. **Sem dogma** — monolito, micro e meio-termo são meios; decide sinal medido, nunca moda.
6. **Qualquer linguagem** — stack desconhecida vira protocolo genérico + no máximo UMA pergunta.
7. **Ataque antes do atacante** — P0 encontrado congela tudo até corrigir.
8. **Dados antes de código** — sem `ARCHITETURA-DADOS.md` não se programa o alvo.

## As 8 fases

| Fase | O que faz | Principal referência |
|------|-----------|----------------------|
| **0 — Acervo** | leitura mecânica: inventário (LOC, topologia, segredos, multi-tenancy, **cheiro de código-IA**) + grafo mermaid de serviços | `scripts/inventario.py` |
| **1 — Raio-X** | topologia real, distribuído-monolito, contextos, superfícies públicas, estado; se houver **legado**, entra a reversão; inventário de dados atual | `legado-reverse.md` |
| **2 — Diagnóstico** | scorecard 10 dimensões (1–10 com evidência) + **T1–T6** (multi-tenant) + probabilidade de quebra (mudança/carga/ataque/equipe) + Top 10 riscos | `rubrica-diagnostico.md`, `multitenancy.md` |
| **3 — Veredito** | decide arquitetura × linguagem × **dados alvo**; ADRs com condição de reversibilidade; **CHECKPOINT HUMANO** | `monolito-vs-microservicos.md`, `migracao-linguagem.md`, `arquitetura-dados.md` |
| **4 — Cirurgia** | strangler-fig costura por costura: caracterizar → flag → sombra → cutover 1/10/100 → descomissionar; banco em expand→migrate→contract | `plano-cirurgia.md` |
| **5 — Ofensiva** | red-team em staging: árvore de ataque, probes da "primeira hora do atacante", triagem do cheiro de IA, severidade P0/P1/P2 | `ofensiva.md` |
| **6 — Blindagem** | 12 canais de vazamento auditados, punch-list OWASP ASVS/STRIDE, gates de CI/CD que **bloqueiam** merge | `vazamento-dados.md`, `blindagem-seguranca.md`, `ci-cd.md` |
| **7 — Plataforma** | escada VPS→Compose→containers gerenciados→K8s→AWS, deploy zero-downtime, Terraform desde o dia 1, OIDC no CI, **IA no produto** | `cloud-deploy.md` |

## O checkpoint (por que ela não assusta)

Ao fim da Fase 3 a Cidadela **para**: entrega `RELATORIO-CIDADELA.md` na raiz, lê o veredito em
3 frases e aguarda sua aprovação explícita. Nada de ela "aproveitar e mexer". Erro budget
estourado durante a cirurgia ⇒ congela e volta ao checkpoint.

## Entregas finais de um ciclo completo

- `RELATORIO-CIDADELA.md` — diagnóstico, veredito, ofensiva, canais de vazamento, gates, plano;
- `ARCHITETURA-DADOS.md` — o destino dos dados (donos, contratos, gates, escala, backup/teardown);
- ADR por decisão significativa, **cada uma com condição de reversibilidade**;
- diagramas mermaid atualizados (contexto + deploy);
- punch-list P0/P1/P2 + `workflow-ci-gates.yml` commitado;
- manifestos de infra (compose/k8s/IaC) + runbook de deploy com rollback < 5 min.

## Como invocar

**Codex:** `/skills` → `cidadela`, ou escreva naturalmente. A description da skill dispara
invocação implícita quando o assunto bate:

- *"Cidadela: proteja este repositório de ponta a ponta"*
- *"Faça a reversão deste legado antes que alguém toque nele"*
- *"Meu código é todo gerado por IA — o que um red team encontra na primeira hora?"*
- *"Acha vazamento aqui? Meu cliente é multi-tenant"*
- *"Esse CI não segura nada: monta o gate"*
- *"Isso sobe em AWS sem parar produção?"*

**Claude Code:** mesma skill (mesma pasta, mesmo formato) — mencione "cidadela" no prompt ou
use o mecanismo de skills do Claude Code.

**Sem agente, direto no terminal:** `genial doctor` dá a Fase 0; a interpretação completa pede
um agente com a skill (Codex/Claude).

## Mapa do conhecimento (onde cada saber mora)

| Área | Arquivo |
|------|---------|
| Rubrica 10 dimensões + cenários de quebra | `references/rubrica-diagnostico.md` |
| Monolito × microsserviços (sinais objetivos) | `references/monolito-vs-microservicos.md` |
| Cirurgia strangler-fig (regras de ouro) | `references/plano-cirurgia.md` |
| Blindagem defensiva OWASP ASVS + camadas | `references/blindagem-seguranca.md` |
| Vazamento de dados: 12 canais, PII BR, LGPD | `references/vazamento-dados.md` |
| Ofensiva: árvores, probes, severidade, cheiro de IA | `references/ofensiva.md` |
| Gates de CI/CD + práticas de deploy | `references/ci-cd.md` |
| Arquitetura de dados (o documento-guia) | `references/arquitetura-dados.md` |
| Reversão de legado (dados como fóssil) | `references/legado-reverse.md` |
| Migração de linguagem (gradual, medida) | `references/migracao-linguagem.md` |
| Plataforma: VPS/Docker/K8s/AWS + IA no produto | `references/cloud-deploy.md` |
| Multi-tenancy T1–T6 + modelo + sequência | `references/multitenancy.md` |
| Mapas por stack (14 linguagens) | `references/mapa-linguagens.md` |
| Anti-padrões (inclui 5 específicos de código-IA) | `references/anti-padroes.md` |
