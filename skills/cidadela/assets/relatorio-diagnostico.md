# Relatório Cidadela — <repo>

Data: <YYYY-MM-DD> · Analista: <agente/humano> · Skill: cidadela

## 1. Veredito em 3 frases
<topologia atual> + <nota global X/10> + <decisão: reforçar módulos / dividir módulo X / consolidar>.

## 2. Identidade do projeto
Stacks encontradas, deployables, CI, bancos/filas/caches, superfícies públicas, tamanho (LOC, arquivos).
Multi-tenant: sim/não (modelo: linhas compartilhadas / schema / banco por tenant / híbrido).
Código gerado por IA: fração estimada + categorias de cheiro detectadas pela Fase 0.
Classes de dado presentes: PII / credencial / financeiro / saúde-jurídico / negócio (detalhe em §11).

## 3. Scorecard
| Dimensão | Nota | Evidência |
|----------|------|-----------|
| 1 Acoplamento | /10 | |
| 2 Coesão | /10 | |
| 3 Rede de segurança | /10 | |
| 4 Isolamento de falha | /10 | |
| 5 Despliegueabilidade | /10 | |
| 6 Observabilidade | /10 | |
| 7 Dados & migrations | /10 | |
| 8 Escalabilidade | /10 | |
| 9 Onboarding | /10 | |
|10 Segurança (resumo) | /10 | |
| T1 Resolução de tenant* | /10 | |
| T2 Isolamento de dados* | /10 | |
| T3 Isolamento computacional* | /10 | |
| T4 Ciclo de vida do tenant* | /10 | |
| T5 Configuração por tenant* | /10 | |
| T6 Observabilidade por tenant* | /10 | |

*Só quando multi-tenant (references/multitenancy.md §4).

## 4. Probabilidade de quebra
| Cenário | % | Fator dominante |
|---------|---|-----------------|
| Mudança funcional | | |
| Pico de carga | | |
| Ataque | | |
| Crescimento de equipe | | |

## 5. Mapa da arquitetura
```mermaid
flowchart TD
  %% contexto: quem conversa com quem
```
```mermaid
flowchart TD
  %% deploy: serviços detectados (completar com dados)
```

## 6. Multitenancy (omitir se single-tenant)
- Modelo em uso: ______
- Matriz de isolamento (10 camadas): preenchida (multitenancy.md §2)
- Doenças encontradas: ______ (local de cada)
- Regra de leitura: se T2 ≤ 4, risco nº 1 = vazamento entre tenants

## 7. Top 10 de riscos
| # | Risco | Evidência | Cenário | Custo de esperar 6 meses |
|---|-------|-----------|---------|--------------------------|

## 8. Anti-padrões presentes
(item de anti-padroes.md × local — incluir os de código-IA)

## 9. Decisão arquitetural
Opção + sinais medidos + condição que reverte + ADR criado.
(Multi-tenant: modelo de tenancy alvo + sinal objetivo p/ dedicado, se houver.)

## 10. Relatório ofensivo (achados da Fase 5)
| ID | Superfície | Vetor | Entrada usada | Saída/resposta | Severidade | Mitigação |
|----|-----------|-------|---------------|----------------|------------|-----------|
| OF-1 | | | | | P0/P1/P2 | |

Resumo de probes da "primeira hora do atacante" (status de cada, com resposta curta).

## 11. Canais de vazamento de dados (12 × status)
| # | Canal | Status (limpo/achado/não avaliado) | Evidência | Correção |
|---|-------|-------------------------------------|-----------|----------|
| 1 | Logs e stack trace | | | |
| 2 | Páginas de erro | | | |
| 3 | URL / query string | | | |
| 4 | Headers de resposta | | | |
| 5 | Cookies | | | |
| 6 | Cache (browser/CDN/API) | | | |
| 7 | Analytics / telemetria | | | |
| 8 | Terceiros (SDK, pagamento, e-mail) | | | |
| 9 | Backup / dump / export | | | |
|10 | Superfícies de dev em produção | | | |
|11 | Mensagens (e-mail/SMS/push) | | | |
|12 | DNS/subdomínio e cliente local | | | |

Testes negativos no CI: adicionados (lista) / pendentes.

## 12. Plano de cirurgia
| Passo | Costura | Flag | Rollback | Verificação |
|-------|---------|------|----------|-------------|

## 13. Gates de CI/CD (estado × alvo)
| Gate | Estado atual | Alvo | Onde fica |
|------|--------------|------|-----------|
| Secrets (histórico) | | | |
| SCA | | | |
| SAST | | | |
| Teste do arquivo modificado | | | |
| Imagem de container | | | |
| Review/CODEOWNERS | | | |
| Lockfile / build reproduzível | | | |
| Canary + rollback < 5 min | | | |

Workflow `assets/workflow-ci-gates.yml`: commitado / adaptado p/ outro runner / pendente.

## 14. Blindagem — punch-list
| ID | Item | Status (evidência) | Alvo | Prioridade | Esforço |
|----|------|--------------------|------|------------|---------|

## 15. Próximos 30 / 60 / 90 dias
- 30:
- 60:
- 90:
