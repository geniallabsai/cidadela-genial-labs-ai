# Legado — engenharia reversa: do código vivo à arquitetura

Quando o código é mais velho que a documentação (ou mais velho que a equipe): não se lê por ordem,
faz-se **arqueologia**. Objetivo: mapa confiável do que o sistema faz e por quê — suficiente para
plantar a nova arquitetura sem susto.

## 1. Segurança antes de abrir arquivo
Freeze de mudanças (branch trancada ou comunicado); snapshot de caracterização das operações críticas
(entradas/saídas reais); backup/restauração exercitado; error budget declarado para o período de exploração.

## 2. Entradas (como o sistema acorda)
Localizar TODOS os pontos de entrada reais: rotas HTTP, CLIs chamadas por cron/systemd/timer,
consumidores de fila, triggers e agendadores do banco, webhooks recebidos.
Saída: lista processo × entrada × dono (quem ainda respira). Cada cron é um comportamento oculto.

## 3. Os dados são o fóssil que sobrevive (começar por aqui)
- **Migrations em ordem = história das decisões** (o que cresceu, o que foi abandonado).
- Tabelas maiores = núcleo de negócio; tabelas sem query há meses = candidata a recurso morto (confirmar no código).
- **Views/procedures/triggers = regras escondidas fora da aplicação** (billing e validações moram aqui).
- Índices = mapa das queries reais (colunas de WHERE mostram o que o sistema filtra em produção).
Saída: mapa de dados + hipóteses de domínio (marcar como hipótese, não fato).

## 4. As 3 operações que sustentam o negócio
Escolher (dinheiro, autenticação/tenancy, relatório principal): traçar da entrada à transformação à
persistência; diagrama de sequência (mermaid) por operação; marcar cada regra descoberta (fórmula,
exceção, if de contexto). Regra que ninguém explica vira pergunta registrada — e ADR quando respondida.

## 5. Regras ocultas (onde o legado guarda segredo)
Flags com anos (cada flag é um ramo de história — registrar o estado atual de cada); config por ambiente
que muda comportamento; constantes mágicas (usos para reverter o significado); e-mails/notificações
fantasma (evidência de estados antigos); blocos comentados (evidência de reversão); cluster de
TODO/FIXME (dívida confessada).

## 6. Especificação de comportamento (a permissão para mexer)
Para cada operação traçada: capturar pares reais entrada/saída (replay de tráfego ou dados de teste
no shape da produção) → transformar em **testes de caracterização**. Suíte verde = permissão para
refatorar; suíte vermelha antes de mudar = registrar como baseline conhecido (documentar, não esconder).

## 7. Arquitetura a partir dos fósseis
Classificar o que existe (monolito / distribuído-monolito / micro — monolito-vs-microservicos.md);
agrupar tabelas que sempre se juntam = candidato a contexto; desenhar o alvo (incluindo dados alvo —
arquitetura-dados.md); plano strangler por costura (plano-cirurgia.md), começando pela costura de
menor risco, cada uma com flag e rollback.

## 8. Entregáveis do processo
- `MAPA-LEGADO.md`: entradas, mapa de dados, as 3 operações, regras ocultas.
- Suíte de caracterização no CI (verde ou com falhas documentadas).
- Veredito: consolidar / dividir / modularizar + alvo de dados.
- Plano strangler por fases com erro budget.
- ADR "reversão de legado" com o que é fato, o que é hipótese (rótulo explícito) e o que segue aberto.
Hipótese ≠ fato: **hipótese rotulada** é o que separa engenharia de aposta.
