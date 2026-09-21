# Arquitetura de dados — o documento que guia a programação

Programar sem esse documento é descobrir o banco por arqueologia daqui a um ano. Esta é a contraparte
de dados do veredito arquitetural: antes do código, o sistema sabe o que existe, quem é dono, como muda
e quando cresce. Saída: `ARCHITETURA-DADOS.md` commitado na raiz do projeto (template no pacote Genial Labs).

## 1. Classes de dados (inventário primeiro)
Reutilizar o inventário de `vazamento-dados.md` §1 (PII, credencial, financeiro, saúde/jurídico, negócio).
Para cada classe registrar: residência (região), retenção, quem lê, regra de minimização.
Dado que não aparece no inventário é achado por definição quando surge no código.

## 2. Modelo canônico — um dono por entidade
| Entidade | Dono (módulo/contexto) | Como os outros acessam |
|----------|------------------------|------------------------|
Regras:
- Cada entidade tem **um único dono** (um módulo do mapa arquitetural). Outro acesso só via API explícita
  do dono ou evento consumido — nunca SELECT direto na tabela do outro.
- Exceção por performance exige justificativa registrada + prazo de revisão.
- Camada anti-corrupção na fronteira com sistemas externos: o formato alheino termina na borda;
  dentro, fala-se a língua canônica.

## 3. Contrato e versionamento
- **Schema publicado = API**: campo documentado (tipo, nulo?, significado). Campo sem documentação
  não existe para consumidor.
- Versionamento: **expand → migrate → contract** (plano-cirurgia.md); nada destrutivo enquanto a versão
  anterior vive (compatibilidade N-1).
- **Eventos têm contrato**: nome + payload versionado; consumidores aceitam a versão anterior por
  1 ciclo de release; evento breaking ganha nome novo (nunca mudar payload em silêncio).
- **Chaves de idempotência** em toda escrita mutável (retry seguro); invariantes de negócio viram
  constraint único (não só PK).
- **Dinheiro em inteiro (centavos) e quantidades em decimal** — float é proibido em valor financeiro.

## 4. Qualidade — gates no CI (o teste que protege dado)
| Gate | Teste mínimo |
|------|--------------|
| Integridade | integração: inserir/atualizar/apagar em cascata respeitando FKs |
| Restrição | tentar violar invariantes únicos/negócio → deve falhar |
| Tenancy (se houver) | A lê/escreve sem enxergar B (negativo — vazamento-dados.md §3) |
| Migration | dry-run sobre snapshot do shape da produção; nada destrutivo sem duas etapas |
| Volume | teste crítico não passa com 1 linha (seed ≥ 10k no caminho sensível) |
| Dinheiro | round-trip centavo→moeda→centavo estável em todos os formatos de saída |

## 5. Fluxos de dados (mapar os rios)
Para cada fluxo (ingestão → transformação → atendimento): gatilho (cron/evento/manual),
**idempotência** (rodar duas vezes é seguro), ordenação (importa?), **fila de erro** (DLQ: para onde
vai o que falhou e quem vê), **reconciliação** (contagem/checksum periódico origem↔destino).
Regra: exactly-once é caro — preferir at-least-once + chave de idempotência e documentar o tradeoff.

## 6. Estado e tempo
- **Audit table** imutável (quem/quando/o quê/antes-depois) em operação sensível (auth, dinheiro, permissão).
- Soft delete com retenção + purge duro (direito de eliminação LGPD — vazamento-dados.md §5).
- Relógio único **UTC** (hora local só na camada de exibição).
- Versão otimista por agregado (updated_at + row version) para conflito de escrita.

## 7. Escala e evolução (tudo por medido, nunca por moda)
| Evolução | Sinal objetivo exigido |
|----------|------------------------|
| Índice/particionamento | slow-query log: latência acima do SLO em % relevante das leituras |
| Réplica de leitura | desbalanceamento sustentado leitura/escrita (razão + volume absoluto) |
| Cache | hit ratio medido + TTL por classe + invalidação na escrita |
| Batch → stream | requisito de frescor medido (minutos → segundos) |
| Divisão de banco | gargalo de escrita de um domínio (IOPS/locks) — último recurso |
Cada evolução vira ADR com a condição-disparo (mesmo padrão de monolito-vs-microservicos.md).

## 8. Backup, restauração e teardown
Backup cifrado e acessível por escopo, retenção documentada, **restauração exercitada** (game day ≥ 1x),
granularidade por tenant (multitenancy.md T4) e teardown completo (cascade + purge + retenção)
documentado e testado.

## 9. Checklist final antes de assinar o alvo
- [ ] Toda entidade tem dono registrado
- [ ] Todo fluxo tem idempotência + DLQ + reconciliação
- [ ] Dinheiro/quantidade tipados corretamente (centavo/decimal)
- [ ] Audit table em operações sensíveis
- [ ] Gates de qualidade §4 presentes no CI
- [ ] ADR para cada escolha não óbvia (com condição de reversão)
- [ ] `ARCHITETURA-DADOS.md` commitado no repositório (não em wiki: o dado mora com o código)
