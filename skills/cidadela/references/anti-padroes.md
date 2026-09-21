# Anti-padrões Arquiteturais — detecção e correção

Marcar cada um encontrado, com local (caminho:linha ou módulo) e o custo concreto que causa.

| Anti-padrão | Sintoma observável | Onde procurar | Correção |
|-------------|--------------------|---------------|----------|
| God file/class | arquivo/classe > ~800–1500 linhas fazendo 5 coisas | top do inventário (maiores arquivos) | extrair por responsabilidade; testes de caracterização antes |
| Big ball of mud | sem camadas/fronteira visível; imports cruzam tudo | grafo de imports; leitura de 3–5 módulos aleatórios | definir contextos e impor regra de dependência |
| Cemitério utils/common | `utils`, `common`, `core`, `misc` crescem e viram dependência universal | pacotes com nome genérico | devolver conteúdo ao dono; reexportar só o que estabilizou |
| Dependência circular | A importa B e B importa A (pacote, módulo, service) | análise de imports; warnings de build | inverter via interface/porta; mover código pro lado certo |
| Distribuído-monolito | vários deployables com banco compartilhado e/ou chamadas em cadeia | compose/k8s + strings de conexão + rotas | consolidar ou desacoplar de verdade (fronteira de dados) |
| Cadeia de serviços síncronos | 1 requisição atravessa >2 serviços antes de responder | rotas, clients HTTP internos, traces | mesclar o que é transacional; eventos pro resto |
| Banco compartilhado entre serviços | mesma DSN/schema em 2+ unidades de deploy | strings de conexão nos configs | fronteira de dados por serviço; API em vez de SELECT alheio |
| Camadas vazadas | controller fala SQL; UI chama banco; service importa HTTP | leitura de 3–5 camadas | restabelecer camadas; ACL na borda |
| Modelo anêmico | entidades só DTOs; toda lógica em services/controllers | model/entity sem comportamento | recolocar invariante no modelo ou serviço de domínio explícito |
| Flag zumbi | feature flag há mais de 1 release sem limpeza; código morto | código + painel de flags | programa de descomissionar (passo 7 do protocolo de cirurgia) |
| Big-bang rewrite | "vamos reescrever em X" sem estrangular o legado | git history; branches gigantes | strangler-fig: fatias reversíveis |
| Espaguete de configuração | `if env == "prod"` em N lugares; config duplicada | grep de nomes de ambiente | config tipada na borda; por ambiente |
| N+1 | loop fazendo 1 query por item | repositories/services com query em loop | join/batch; cache quando fizer sentido |
| Fan-out síncrono | espera N chamadas externas em sequência dentro de 1 pedido | handlers com múltiplos awaits em série | paralelizar + timeout por chamada + circuit breaker |
| Migration gigante | migration de mil linhas misturando schema + backfill | pasta de migrations | separar schema (rápida) de backfill (assíncrono) |
| Monorepo sem fronteira | tudo num repo, tudo importa tudo, CI demora e quebra pra todo mundo | estrutura + tempo de CI | workspaces com regra de dependência e CI incremental |
| Micro por vaidade | serviço de 3 endpoints existindo por "padrão" | k8s/compose com muitos minúsculos | consolidar (critérios em monolito-vs-microservicos.md) |
| Erro engolido | catch que loga (ou não) e segue; retorno vazio como sucesso | grep de catch/exceção vazia | erro tipado; fail-fast; métrica por exceção |
| Global/estático como DI | singleton com estado mutável; new em tudo que importa | símbolos globais, estado de módulo | injeção de dependência explícita; estado por request/contexto |
| Doc fantasma | README/diagrama descrevem sistema que não existe | comparar doc × código × CI | doc viva: gerar diagrama do próprio código (grafico-servicos.py) |
| Stub de autorização | `if (user?.isAdmin \|\| DEBUG)`; middleware esquecido numa rota; rota fora do auth | grep `\|\|.*DEBUG` perto de permissão; rotas × middlewares | auth na borda; teste "sem token = 401" no CI |
| Segredo com fallback | `secret \|\| 'dev-secret'`; JWT secret fixo; `changeme` em produção | grep `\|\|`/default perto de secret/token | fail-fast: segredo ausente = não sobe |
| Endpoint temporário virou permanente | rota de debug/backdoor/admin "desligada" por flag | grep debug/tmp/fix/emergency em rotas | remover, ou flag + dono + prazo de morte escrito |
| Source map / artefato de dev em produção | `.js.map` acessível expõe fonte; `/debug` responde | HEAD em `X.map` de cada bundle; probes da ofensiva.md | gerar sem map em produção ou servir atrás de auth |
| Webhook sem verificação | handler aceita POST forjado (sem HMAC/timestamp/nonce) | rotas de webhook × uso de hmac/signature | origem assinada + replay protection |
