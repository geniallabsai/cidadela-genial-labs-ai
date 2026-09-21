# Legado e migração

Os dois momentos em que "engenharia de verdade" separa gente que entrega de gente que apaga o
histórico. Ambos são processos graduais, com gate, no Genial Labs.

## Reversão de legado — do código vivo à arquitetura

Quando o código é mais velho que a documentação (ou mais velho que a equipe), não se lê por
ordem: faz-se **arqueologia**. Objetivo: mapa confiável do que o sistema faz e por quê,
suficiente para plantar a nova arquitetura sem susto.

1. **Segurança antes de abrir arquivo** — freeze de mudanças, snapshot das operações críticas,
   backup/restauração exercitado, error budget declarado.
2. **Entradas** — todos os pontos por onde o sistema acorda: rotas HTTP, CLIs chamadas por
   cron/systemd, consumidores de fila, triggers/agendadores do banco, webhooks. Cada cron é um
   comportamento oculto.
3. **Dados são o fóssil que sobrevive** — migrations em ordem = história das decisões;
   tabelas maiores = núcleo de negócio; views/procedures/triggers = regras escondidas fora da
   aplicação; índices = mapa das queries reais.
4. **As 3 operações que sustentam o negócio** (dinheiro, auth/tenancy, relatório principal) —
   traçar da entrada à persistência, diagrama por operação, marcar cada regra descoberta.
5. **Regras ocultas** — flags com anos (cada flag é um ramo de história), config por ambiente,
   constantes mágicas, e-mails fantasma, blocos comentados, clusters de TODO.
6. **Especificação de comportamento** — capturar pares reais entrada/saída e transformar em
   **testes de caracterização**. Suíte verde = permissão para refatorar.
7. **Arquitetura a partir dos fósseis** — classificar o que existe, agrupar tabelas que sempre
   se juntam = candidato a contexto, desenhar o alvo (incluindo dados) e plano strangler por
   costura, começando pela de menor risco.
8. **Entregáveis** — `MAPA-LEGADO.md`, suíte no CI, veredito, plano por fases com error budget,
   ADR com o que é **fato**, o que é **hipótese (rotulada)** e o que segue aberto.

Frase da casa: *hipótese ≠ fato — refatorar sobre hipótese não rotulada é aposta.*

Como acionar: *"cidadela: faça a reversão deste legado antes que alguém toque nele."*

## Migração de linguagem — quando outro runtime serve melhor

Linguagem é meio, não religião. Migrar **tudo** é projeto zero; migrar **módulo por módulo** é
engenharia.

**Sinais objetivos (medir ≥ 2 para considerar):** performance/runtime (p99, memória, CPU —
perfil, não intuição) · ecossistema (biblioteca de domínio ausente/ruim) · equipe (entrega
mediocre comprovada na linguagem atual) · CVEs recorrentes na cadeia (12 meses) · padrão de
escala (IO massivo, backpressure) · licença/custo.

**Contra-sinais (qualquer um presente ⇒ segurar):** dor não medida, "é mais moderna", equipe
sem a outra linguagem, módulo único pequeno, ecossistema atual resolve, prazo de produto em
conflito (a menos que a dor bloqueie o produto).

**Padrões da escada (um degrau por vez):**

| Padrão | Quando |
|--------|--------|
| Ports & adapters | isolar UM componente atrás de HTTP/gRPC/eventos, com dif de saídas |
| Feature a feature | novas features na nova linguagem, antigas seguem; roteamento por flag |
| Extração de módulo quente | o módulo com gargalo medido vira serviço novo (strangler completo) |
| Replatform paralelo | substituição total em sombra, dif por fluxo, cutover por flag (raro) |

**Regra de ouro: um módulo × uma linguagem por vez.** Duas reescritas simultâneas ninguém
aprende nada.

**Gates por salto:** testes de caracterização verdes antes; dif de saídas abaixo do limite
durante (sombra); error budget intacto depois; rollback = reverter o roteamento (< 5 min); CI
verde dos dois lados até o descomissionamento.

**Custo honesto (obrigatório no ADR):** ports & adapters dias a semanas por componente ·
feature a feature contínuo e barato · módulo quente semanas a meses · replatform meses a anos
com equipe duplicada. Migração pode terminar na metade: módulos já migrados ficam — isso é
sucesso, não meia-work.

Como acionar: *"cidadela: avaliarem se outra linguagem serviria melhor neste módulo — com
números."*
