# Multitenancy — Detecção, Pontuação, Decisão, Cirurgia e Blindagem

Aplicar quando a Fase 1 detectar (ou o humano informar) que o produto atende múltiplos clientes
num mesmo deployment ("tenants"). Projeto de cliente único ignora este arquivo por completo.
Multitenancy é **ortogonal** à escolha monolito × microsserviços: o alvo padrão continua sendo
monolito modular *e* multi-tenant bem aplicado.

## 1. Qual modelo está em uso (sinais de detecção)

| Modelo | Sinais no código | Onde procurar |
|--------|------------------|---------------|
| **Linhas compartilhadas** (coluna discriminadora) | `tenant_id`/`org_id`/`account_id`/`workspace_id` na quase-totalidade das tabelas; scope/filter global no ORM; `WHERE tenant_id =` | Migrations + queries |
| **Schema por tenant** | `search_path` trocado por request; runner de migration que aplica em N schemas | Fábrica de conexão |
| **Banco por tenant** | Registro tenant → DSN; conexão resolvida por request | Fábrica de conexão |
| **Híbrido** (pool + dedicados) | Os dois: pool compartilhado + lista de exceções com DSN próprio | Registro/config |

Resolução do tenant: subdomain (`host.split`), header (`X-Tenant`), path (`/acme/...`) ou claim do JWT.
**Regra de confiança:** o tenant vem da borda e é **validado contra a sessão autenticada** —
header enviado pelo cliente nunca é identidade sem validação (risco de impersonation).

## 2. Matriz de isolamento (preencher linha a linha no relatório)

| Camada | Pergunta | O que procurar |
|--------|----------|----------------|
| Dados (tabelas) | Toda query filtra por tenant? Tem RLS/backstop? | Scopes do ORM, policies |
| Cache | Keys são namespaced por tenant? | Padrões de `cache.get/set` |
| Filas | Mensagem carrega tenant? Worker pode processar cruzado? | Produtores/consumidores |
| Storage | Prefix/bucket por tenant? Signed URLs restringidas? | Código de upload |
| Sessão/identidade | Token carrega tenant? Sessão pode cruzar? | Middleware de auth |
| Computação | Quotas/rate-limit por tenant? | Limiters, tiers |
| Criptografia | Chaves compartilhadas ou por tenant? | Uso de KMS |
| Região/residência | Mapeamento tenant → região fixado? | Config de provisioning |
| Backup | Granularidade por tenant ou cluster inteiro? | Scripts de restore |
| Teardown | Dá para apagar um tenant completo (cascade + purge)? | Fluxo de exclusão |

## 3. Doenças (marcar cada uma com local; severidade padrão P0)

| Doença | Sintoma | Como verificar |
|--------|---------|----------------|
| **Vazamento cruzado de dados** | Alguma query/report/admin/job sem filtro de tenant | Grep de uso do modelo sem scope; rodar testes negativos |
| **Cache sem namespace** | `cache.set(key)` sem prefixo de tenant | Padrões na camada de cache |
| **Bleed por estado compartilhado** | Singleton/thread guarda "tenant atual" e não reseta entre requests | Pool de threads + globais |
| **Job órfão** | Job em background roda sem contexto de tenant (ou como "system") | Entrypoint dos workers |
| **IDOR cruzado** | Acesso por ID puro sem checar posse do tenant | Rotas `/{id}` |
| **Drift de migration** | Tenants com schemas diferentes (migration aplicada em alguns) | Tabela de version por banco |
| **Noisy neighbor** | Sem limite de conexões/CPU/tempo p/ tenant pesado | Config de limites |
| **Teardown incompleto** | Tenant apagado mas linhas/arquivos/restos ficam | Fluxo de delete |
| **Backup não restaurável** | Restore por data vale pra todo mundo, não por tenant | Fluxo de restore |
| **Chave criptográfica compartilhada** | Mesma chave KMS cifra dados de todos os tenants | Config de cripto |
| **Tenant impersonável** | Header/subdomain não validado contra sessão | Middleware de auth |
| **Auditoria vazada** | Log sem tenant_id (impossível separar por cliente) | Config de logging |
| **Fan-out sem filtro** | Notificação/webhook broadcast sem escopo de tenant | Código de mensagens |
| **Residência violada** | Dado de tenant em região não homologada | Mapeamento de infra |
| **Agregação cruzada** | Relatórios/BI somando sem group-by por tenant | Queries analíticas |

## 4. Pontuação (anexar ao scorecard da Fase 2 quando multi-tenant)

Cada nota com evidência (`arquivo:linha`).

| Dim | Mede | 10 | 4 | 1 |
|-----|------|----|----|----|
| T1 Resolução de tenant | Onde decidido, quem confia, fluxo explícito | Borda + claim validada, contexto implícito porém visível | Só por header, validação inconsistente | Por IP/implícito ou inexistente |
| T2 Isolamento de dados | Aplicação centralizada vs filtro caseiro | RLS + scope no ORM + testes negativos automatizados | Somente filtro manual nas queries | Tabelas sem discriminador |
| T3 Isolamento computacional | Quotas, rate-limit, limites por tenant | Quotas por tier aplicadas na borda | Limites apenas globais | Nenhum |
| T4 Ciclo de vida do tenant | Provisionamento/teardown automáticos, backup por tenant | 1 comando + restore granular | Manual mas scriptado | White-glove |
| T5 Configuração por tenant | Features/ajustes/branding por tenant | Sistema de flags + config por tenant | Env vars espalhadas por tenant | Nenhuma |
| T6 Observabilidade por tenant | Métricas taggeadas, custo por tenant (pronto p/ billing), auditoria separada | Completo | Parcial | Somente global |

Regra: **T2 ≤ 4 ⇒ o risco nº 1 do relatório é vazamento entre tenants**, acima de qualquer outro risco.

## 5. Decisão de destino (qual modelo usar)

Regra-mãe: **linhas compartilhadas com aplicação centralizada** (scope obrigatório no ORM + RLS como backstop). É o melhor custo/isolamento/operação para a grande maioria dos SaaS.

Mudar o modelo exige sinal objetivo, registrado em ADR:

| Sinal | Movimento |
|-------|-----------|
| Compliance/residência (PCI, saúde, público, setor regulado) | Banco dedicado p/ esses tenants |
| SLA contratual de capacidade isolada | Banco dedicado, ou partição/quota garantida |
| Cláusula de saída: cliente exige levar os dados p/ sua infra | Banco dedicado (ou pipeline de export certificado) |
| Dado muito sensível de poucos tenants | Chave por tenant + criptografia de coluna + storage dedicado |
| Longo cauda de muitos tenants pequenos | Manter compartilhado; NÃO fragmentar operações |

**Híbrido (pool + promoção)** é legítimo e comum — mas somente com: registro do modelo por tenant,
**caminho de migração automática compartilhado → dedicado** (expand → migrate → contract por tenant)
e teste de paridade entre os dois caminhos. Sem caminho de migração, não prometer híbrido:
"promover" vira um projeto de engenharia a cada contrato.

## 6. Cirurgia — adicionar tenancy a um projeto existente (caso mais comum)

Passos strangler, cada um atrás de flag e reversível:

1. **Inventariar** tabelas/endpoints/jobs que tocam dado sensível (Fase 1) e quem acessa hoje.
2. **Expand:** coluna discriminadora nula-tolerante + índice; migration em lotes.
3. **Migrate:** backfill assíncrono idempotente atribuindo dados históricos ao tenant fundador (ou vários).
4. **Resolução na borda** (flag): subdomain/header/claim validado contra a sessão; tenant entra no contexto de request.
5. **Shadow enforcement:** scope/RLS em **modo log** (violação = métrica + amostra) por ≥ 1 semana, sem bloquear.
6. **Modo bloqueio** (flag): violação vira erro. A partir daqui, código novo não pode vazar tenant sem o CI reclamar.
7. **Backstop central:** ativar RLS (Postgres) ou equivalente no storage; o scope do ORM permanece (performance), o RLS pega o esquecido.
8. **Namespacing de fila/cache/storage:** mesmo ritual shadow → cutover.
9. **Testes negativos no CI:** "cliente A não lê/escreve dados do cliente B" para as N entidades centrais; suíte corre em todo PR que toca modelos.
10. **Ciclo de vida:** provisionamento e teardown completo (cascade + retenção) como script documentado.

## 7. Cirurgia — extrair um tenant grande (compartilhado → dedicado)

1. Registro tenant → DSN atrás de flag (só novos/dedicados).
2. Dupla escrita p/ o tenant-alvo; leitura shadow com diff de saídas.
3. Backfill + reconciliação (contagens + checksum por tabela).
4. Cutover por rota (flag); rollback = desviar a rota de volta (< 5 min).
5. Manter dupla escrita 1 ciclo de release, então contract (parar de escrever no antigo).

## 8. Blindagem — punch-list multitenant (anexar à Fase 6)

- [ ] **P0** Testes negativos cruzados (A × B) automatizados no CI
- [ ] **P0** Backstop central ativo (RLS/row-level no storage), não só filtro no app
- [ ] **P0** Todo cache/fila/storage namespaced por tenant
- [ ] **P0** Todo job declara tenant (ou é system explícito com justificativa registrada)
- [ ] **P0** Rate-limit/quota por tenant conforme plano
- [ ] **P1** Auditoria com tenant_id em 100% dos eventos; trilha consultável por tenant
- [ ] **P1** Teardown completo testado (cascade + purge + retenção)
- [ ] **P1** Restore por tenant exercitado ao menos 1 vez (game day)
- [ ] **P1** Chave KMS por tenant onde há dado sensível; rotação independente
- [ ] **P1** Residência tenant → região forçada no provisioning
- [ ] **P2** Custo por tenant (finops) alimentando billing
- [ ] **P2** SLO por tenant e dashboards por plano
- [ ] **P2** Pen test cruzado anual com metodologia documentada
