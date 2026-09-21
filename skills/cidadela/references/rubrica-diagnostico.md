# Rubrica de Diagnóstico (1–10 por dimensão)

Regra de uso: cada nota **requer evidência** (`arquivo:linha` ou artefato). Nota sem evidência vira "não avaliado".
Ancoragens gerais: **10** = exemplar com mecanismos ativos (gate, teste, automação) · **7** = sólido com ressalvas pontuais · **4** = funciona por inércia · **1** = ativo.

| # | Dimensão | Como medir | 10 | 7 | 4 | 1 |
|---|----------|-----------|----|---|---|---|
| 1 | Acoplamento entre módulos | Grafo de imports/referências; quem toca quem | Fronteiras explícitas (interfaces/eventos), zero import cruzado de interno | Poucos cruzamentos, todos visíveis | Cross-import constante de interno | Toda mudança arrasta meio repo |
| 2 | Coesão interna | Cada módulo tem 1 responsabilidade? Nome bate com conteúdo? | Módulos por contexto de negócio, alta coesão | Maioria coesa, 1–2 ilhas | Módulos genéricos (utils, common, core) crescendo | Big ball of mud |
| 3 | Rede de segurança (testes) | Testes nas costuras, integração, CI verde e rápido | Caracterização nas fronteiras + integração; regressão pega em minutos | Núcleo coberto, bordas com buraco | Fragmentado, lento ou flaky | Sem rede; muda no escuro |
| 4 | Isolamento de falha | O que morre junto? Blast radius de um bug/OOM/timeout | Falha contida no módulo; circuitos e timeouts | Contágio raro, sem proteção sistemática | Falha de 1 componente degrada vários | 1 timeout derruba o fluxo inteiro |
| 5 | Despliegueabilidade | Dá para lançar 1 unidade sozinha? Rollback barato? | Independente, rollback < 5 min, zero-downtime | Rollback possível com esforço | Lançamento acoplado (tudo junto ou nada) | Deploy é evento: horas, manual |
| 6 | Observabilidade | Log/métrica/trace atravessam as costuras? | Traces ponta-a-ponta, SLOs, alerta de anomalia | Métricas principais + logs estruturados | Log no stdout, sem correlação | Voa às cegas |
| 7 | Dados & migrations | Versionadas? expand-contract? escrita dupla? | Reversíveis, sem escrita dupla manual | Boas; migração rara e limpa | Destrutivas; run longo em produção | Schema mudado à mão |
| 8 | Escalabilidade | Gargalos horizontais vs verticais? Estado preso ao processo? | Horizontal por módulo, estado externo, cache | Gargalos conhecidos e mitigados | Escale vertical até doer | Estado no processo; escala 1 |
| 9 | Onboarding | Novo dev entrega PR em quantos dias? Docs × realidade | Arquitetura + ambiente em 1 comando | Guia razoável, 1–2 atritos | Docs defasadas, conhecimento tribal | Segredo |
|10 | Postura de segurança (resumo) | Secrets, auth, input, deps, gates (detalhe em blindagem-seguranca.md) | ASVS L2 efetivo com gates | L1 sólida, gaps conhecidos | Gaps P1 abertos | P0 abertos (credencial em código, admin aberto) |

**Probabilidade de quebra — cenários** (estime % e cite o fator dominante de cada um):

- **Cenário M — Mudança funcional:** "uma feature típica toca quantos módulos? alguém consegue dizer antes de digitar?"
- **Cenário C — Pico de carga:** "onde estoura primeiro? existe cascata síncrona sem timeout/budget?"
- **Cenário A — Ataque:** "área exposta × credenciais vivas × dependências vencidas críticas".
- **Cenário E — Equipe:** "duas pessoas tocam o mesmo arquivo por semana? há dono claro por área?"

Leitura: se ≥2 cenários ficam acima de 50%, o sistema sobrevive por inércia — a cirurgia vem antes da funcionalidade, não depois.
RUMOR: a coluna "Ataque" é alimentada pela Fase Ofensiva (ofensiva.md), não por impressão.
