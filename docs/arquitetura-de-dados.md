# Arquitetura de dados que guia a programação

Programar sem arquitetura de dados é descobrir o banco por arqueologia daqui a um ano. O Genial
Labs trata os dados como **contrato antes de código**: o documento `ARCHITETURA-DADOS.md` é
commitado junto com o projeto e a skill Cidadela só programa o alvo depois que ele existe
(regra inegociável nº 8: *dados antes de código*).

## As 9 seções do documento

Cada seção tem pergunta e resposta mínima exigida:

1. **Classes de dados e residência** — PII, credencial, financeiro, saúde/jurídico, negócio.
   Para cada classe: região, retenção, quem lê, regra de minimização. Dado fora do inventário
   é achado por definição quando surge no código.
2. **Modelo canônico — um dono por entidade** — cada tabela/conjunto pertence a UM módulo.
   Outro módulo acessa só pela API/evento do dono. Seleção direta na tabela alheia = exceção
   registrada com justificativa e prazo. Fronteira com sistema externo tem camada
   anti-corrupção (o formato deles termina na borda).
3. **Contratos e versionamento** — schema publicado é API: campo documentado (tipo, nulo?,
   significado); campo sem doc não existe. Migrations em **expand → migrate → contract**,
   compatibilidade N-1 (nada destrutivo enquanto a versão anterior vive). Evento tem nome +
   payload versionado; breaking = nome novo. Escrita mutável exige chave de idempotência.
4. **Regras de qualidade (gates de CI)** — integridade referencial em teste de integração,
   invariante única violável de propósito deve falhar, teste negativo de tenancy (A não enxerga
   B), migration com dry-run em snapshot, teste crítico que **não passa com 1 linha** (seed de
   volume), round-trip estável de dinheiro.
5. **Fluxos de dados** — por fluxo (ingestão→transformação→atendimento): gatilho,
   idempotência (rodar 2× é seguro), ordenação importa?, DLQ (aonde vai o erro e quem vê),
   reconciliação periódica. Padrão da casa: at-least-once + chave de idempotência
   (exactly-once só com justificativa de custo).
6. **Estado e tempo** — audit table imutável (quem/quando/o quê/antes-depois) em operação
   sensível; soft delete com retenção + purge duro (direito de eliminação LGPD); relógio único
   UTC (hora local só na exibição); versão otimista por agregado em conflito de escrita.
7. **Escala e evolução (tudo por medido)** — índice/particionamento só com slow-query log
   acima do SLO; réplica de leitura só com desbalanceamento sustentado medido; cache com hit
   ratio + TTL + invalidação na escrita; divisão de banco é último recurso, por gargalo de
   escrita medido. Cada evolução vira ADR com condição-disparo.
8. **Backup, restauração e teardown** — backup cifrado com acesso escopo e retenção;
   **restauração exercitada** (game day ≥ 1×); granularidade por tenant; teardown completo
   (cascade + purge) documentado e testado.
9. **Histórico de decisões** — data, decisão e link do ADR.

## Regras de ouro (resumo executivo)

- **Dinheiro em centavos (inteiro), quantidades em decimal.** Float em valor financeiro é bug.
- **Uma entidade, um dono.** O resto conversa por API/evento.
- **Contrato N-1:** ninguém quebra o consumidor anterior num release.
- **Toda escrita é idempotente** (chave + retry seguro).
- **Operação sensível deixa trilha** (audit table imutável).
- **Evolução sem número não evolui** (sinal medido + ADR).

## Como o `genial init` planta isso

`genial init` gera o `ARCHITETURA-DADOS.md` já preenchido com as 9 seções e os placeholders
do seu projeto (nome, data, stack). O fluxo de uso:

1. o scaffold nasce com o documento em branco estruturado;
2. ao abrir no Codex/Claude, peça: *"cidadela: este projeto é novo — confirme a arquitetura de
   dados"*; a skill percorre as 9 seções com você no checkpoint da Fase 3;
3. aprovado, o documento é commitado — e todo feature novo é validado contra ele (donos,
   contratos, gates).

Para projeto existente, a mesma rotina roda dentro de um diagnóstico completo (Fases 0–3),
onde o estado real dos dados é mapeado antes do alvo ser decidido.
