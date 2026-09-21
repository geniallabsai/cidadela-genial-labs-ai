# Monolito × Microsserviços — Regras de Veredito

## Padrão (regra-mãe)
**Monolito modular.** Melhor ponto de partida na grande maioria dos casos: um deploy, um banco, transações locais, debug simples — e equipes pequenas não pagam o imposto operacional da máquina distribuída. A modulação vem de fronteiras fortes entre pacotes, não de rede.

## Sinais objetivos para DIVIDIR (precisa de ≥ 2, medidos, não imaginados)
| Sinal | Prova exigida |
|-------|---------------|
| Escala independente | Métrica: módulo Y consome X× o recurso de A (CPU, memória, QPS, p99) |
| Frequência de deploy | Rollback de um domínio fica atrás de outro há N semanas; fila de release documentada |
| Equipe / Lei de Conway | > ~10 pessoas no mesmo módulo; conflitos de merge recorrentes no mesmo diretório (evidenciar por git blame/log) |
| Compliance | Domínio exige isolamento de residência de dados/auditoria (ex.: cartões, saúde, fiscal) |
| Runtime / hardware | GPU × CPU, memória × latência, linguagem que não convive no processo |
| Domínio crítico | Billing/pagamentos não pode morrer junto com catálogo (SLAs distintos) |
| Ciclo de vida | Módulo com vida útil distinta (beta permanente × núcleo estável) |

## Sinais para NÃO dividir (qualquer um presente ⇒ segurar)
- Banco/esquema compartilhado entre "serviços" (é distribuído-monolito; resolver isso antes de qualquer coisa).
- Requisição atravessa > 2 saltos síncronos entre serviços.
- Não existe dono claro por serviço.
- < 5 pessoas, sem SLO, sem pressão de carga medida.
- "É o padrão moderno" / "tudo de verdade é microsserviço".

## Quando CONSOLIDAR (voltar de microsserviços ao monolito modular)
≥ 3 destes: chamadas em cadeia interna dominam o tráfego; schema compartilhado; um serviço não lança sem outro; on-call compartilhado e caótico; a maioria dos incidentes é entre serviços. Ganho: rollback simples, trace trivial, rede vira processo. As fronteiras lógicas permanecem — consolidar não é apagar o domínio.

## Alvo: o que um monolito modular bem feito exige
1. Pacotes por contexto de negócio; **interno privado por padrão**; exposição via interface/evento.
2. Regra de dependência automatizada (linter ou teste de arquitetura) barrando cross-import de interno.
3. Camada anti-correção (ACL) na fronteira com o mundo: provedores externos, legados, formatos alheios.
4. Cada pacote = candidato a serviço futuro: já possui contrato ou fronteira de dados explícitos.
5. A decisão é **por módulo**, nunca "todo o projeto": é legítimo 1 serviço extraído + restante no monolito.

## Registro
Toda decisão vira ADR (`assets/adr-0000-template.md`) e deve conter a **condição de reversibilidade**: "se X passar de Y, reabrimos a decisão".
