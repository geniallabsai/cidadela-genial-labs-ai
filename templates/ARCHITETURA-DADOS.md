# Arquitetura de Dados — {{NOME}}

Dono do documento: ______ (equipe/pessoa) · Criado: {{DATA}} · Stack: {{STACK}}
Estado: RASCUNHO → APROVADO (assinar na Fase 3 da skill cidadela)

> Este documento é a contraparte de dados da arquitetura: nada entra em produção sem dono,
> contrato e gate de qualidade. Método completo: `skills/cidadela/references/arquitetura-dados.md`.

## 1. Classes de dados e residência
| Classe | Exemplos neste projeto | Região/Residência | Retenção | Quem lê | Minimização |
|--------|------------------------|-------------------|----------|---------|-------------|
| PII | | | | | |
| Credencial | | | | | |
| Financeiro | | | | | |
| Saúde/Jurídico | | | | | |
| Negócio | | | | | |

## 2. Modelo canônico (um dono por entidade)
| Entidade | Dono (módulo) | Outros acessam via | Exceções (justificativa + prazo) |
|----------|---------------|--------------------|-----------------------------------|
| | | API / evento | |

Regras fixas: sem dono não existe entidade · SELECT direto em tabela alheia = exceção registrada ·
camada anti-corrupção na fronteira com sistemas externos.

## 3. Contratos e versionamento
- Schema publicado = API: campos documentados (tipo, nulo?, significado). Campo sem doc não existe.
- Migrations: expand → migrate → contract; compatibilidade N-1 (nenhuma quebra enquanto a versão anterior vive).
- Eventos: nome + payload versionado; breaking = nome novo; consumidores aceitam N-1 por 1 ciclo.
- Chaves de idempotência em toda escrita mutável; invariantes de negócio = constraint único.
- Dinheiro em **centavos (inteiro)**, quantidades em **decimal**. Float em valor financeiro é bug.

## 4. Gates de qualidade (CI)
| Gate | Onde roda | Status |
|------|-----------|--------|
| Integridade referencial (FKs em cascata) | | |
| Invariantes únicos/negócio (tentar violar = falhar) | | |
| Tenancy negativo (A não enxerga B) — se multi-tenant | | |
| Migration: dry-run em snapshot + nada destrutivo sem 2 etapas | | |
| Volume: teste crítico não passa com 1 linha | | |
| Dinheiro: round-trip estável em todas as saídas | | |

## 5. Fluxos de dados
| Fluxo | Gatilho | Idempotente? | Ordenação importa? | DLQ (onde/quem vê) | Reconciliação |
|-------|---------|--------------|--------------------|--------------------|---------------|
| | | | | | |

Padrão da casa: at-least-once + chave de idempotência (exactly-once só com justificativa de custo).

## 6. Estado e tempo
- Audit table imutável (quem/quando/o quê/antes-depois) em: ______
- Soft delete + retenção + purge duro (eliminação LGPD): ______
- Relógio único UTC (hora local só na exibição).
- Versão otimista por agregado em: ______

## 7. Escala e evolução (por medido)
| Evolução possível | Sinal objetivo que dispara | ADR |
|--------------------|----------------------------|-----|
| Índice/particionamento | slow-query > SLO em % das leituras | |
| Réplica de leitura | razão leitura/escrita sustentada + volume | |
| Cache | hit ratio + TTL + invalidação na escrita | |
| Batch → stream | frescor medido (min → s) | |
| Divisão de banco | gargalo de escrita (IOPS/locks) | |

## 8. Backup, restauração e teardown
- Backup: cifra, acesso, retenção: ______
- Restore exercitado (game day): data ______
- Teardown completo (cascade + purge + retenção): ______
- Granularidade por tenant (se multi-tenant): ______

## 9. Histórico de decisões
| Data | Decisão | ADR |
|------|---------|-----|
