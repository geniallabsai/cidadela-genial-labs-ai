# Migração de linguagem — quando outro runtime serve melhor (e como chegar sem parar)

Linguagem é meio, não religião. Migrar **tudo** é projeto zero; migrar **módulo por módulo** é engenharia.

## 1. Sinais objetivos (medidos; ≥ 2 para considerar)
| Sinal | Prova exigida |
|-------|---------------|
| Runtime/performance | Perfil medido: p99, memória ou CPU da linguagem atual vs a exigência (perfil, não intuição) |
| Ecossistema | Biblioteca de domínio ausente/ruim na linguagem atual (números/financeiro, ML na borda, WASM, concorrência) |
| Equipe | Equipe principal forte em outra linguagem (entrega medíocre comprovada: tempo de PR, bug-rate) |
| CVEs recorrentes | cadeia de dependências/runtime com críticos repetidos nos últimos 12 meses |
| Padrão de escala | IO massivo (goroutines vs threads), backpressure/reatividade exigidas pelo tráfego medido |
| Licença/custo | dependência em fim de manutenção ou licença que dói |

## 2. Contra-sinais (qualquer um presente ⇒ segurar)
Dor não medida; "é mais moderna"; equipe sem a outra linguagem; módulo pequeno (reescrita local sai
mais barata); ecossistema atual resolve com esforço; migração compete com prazo de produto (a menos
que a dor bloqueie o produto).

## 3. Padrões de migração gradual (escada — um degrau por vez)
| Padrão | Quando | Como |
|--------|--------|------|
| Ports & adapters | isolar UM componente (parser, pagamento, relatório) | interface na borda; implementação nova em outra linguagem atrás de gRPC/HTTP/eventos; dif de saídas |
| Feature a feature | novas features na nova linguagem, antigas seguem | módulo/serviço novo no repositório; roteamento por flag na borda |
| Extração de módulo quente | módulo com gargalo medido (perf/custo) | protocolo strangler-fig completo (plano-cirurgia.md) na nova linguagem |
| Replatform paralelo | substituição total (raro) | sistema novo em sombra, dif por fluxo, cutover por flag; antigo entra em manutenção |
**Regra de ouro: um módulo × uma linguagem por vez.** Duas reescritas simultâneas ninguém aprende nada.

## 4. A ponte (onde os dois mundos se tocam)
Contrato por ponte: JSON/protobuf versionado, documentado, testado dos dois lados; consumidores
idempotentes; observabilidade por ponte (latência, erros, versões); circuit breaker — a queda de um
mundo não arrasta o outro.

## 5. Gates por salto (mesma régua da cirurgia)
Antes: testes de caracterização do módulo verdes. Durante: dif de saídas abaixo do limite acordado
(sombras). Depois: error budget intacto; rollback = reverter o roteamento (< 5 min). CI verde dos
dois lados até o descomissionamento.

## 6. Custo honesto (obrigatório no ADR)
Ports & adapters: dias a semanas por componente · Feature a feature: contínuo e barato · Módulo quente:
semanas a meses (strangler completo) · Replatform: meses a anos, custo duplo de equipe.
Decisão sem número é slogan.

## 7. ADR "decisão de linguagem" (obrigatório)
Sinais medidos + padrão escolhido + gates por salto + custo + **condição de parada** ("se X deixar de
ser medido, paramos onde estiver"). Migração pode terminar na metade: módulos já migrados ficam —
isso é sucesso, não meia-work.
