# FAQ — o que perguntam primeiro

**Funciona no Windows?**
Sim — e agora com **rota nativa**: instale pelo PowerShell com
`irm https://raw.githubusercontent.com/brunao23/genial-labs/main/install.ps1 | iex`
(ou `iwr` + `-ExecutionPolicy Bypass` se o `iex` estiver bloqueado). Quem usa **Git Bash** ou
**WSL2** mantém a linha clássica `curl … | bash` — o instalador foi endurecido para esse cenário
(wrapper que chama o Python explicitamente, clone com `autocrlf=false`). Só precisa do Python 3.7+
no PATH.

**Qual a diferença entre as rotas de instalação?**
Nenhuma no resultado: todas colocam a mesma coisa (pacote em `~/.genial-labs`, skill nos dois
agentes, comando `genial` no PATH). A PowerShell é a mais confiável no Windows porque foge das
particularidades de execução de scripts do Git Bash.

**Meu Python é só `py`/`python`, tem `python3`?**
O instalador procura, nessa ordem: `py -3`, `python`, `python3` — cobre o padrão do python.org no
Windows. O wrapper gerado repete essa mesma lógica a cada uso.

**Quais agentes de IA usam a skill Cidadela?**
**Codex** e **Claude Code** nativamente — ela está no formato aberto Agent Skills (agentskills.io),
então qualquer agente que leia `SKILL.md` funciona. Sem agente, `genial doctor` dá a Fase 0 no terminal.

**Meu código não é Python, Node nem Go.**
A **skill fala qualquer linguagem** (há mapa para 14 stacks em `mapa-linguagens.md`) — diagnóstico,
veredito, ofensiva e blindagem independem de linguagem. Específico das três primeiras é só o
scaffold do `genial init`. Para outro stack: crie os arquivos base do seu jeito e siga com a
skill — ou abra issue pedindo suporte (vira prioridade no roadmap).

**Depois de instalado, preciso de internet?**
Não. Tudo roda localmente. Só atualização e, no futuro, a validação do token conversam com a rede.

**Ela pode quebrar a minha produção?**
O processo foi desenhado para não: **checkpoint humano antes de qualquer escrita**, mudança atrás
de flag (desligada = comportamento antigo), rollback < 5 min, CI verde obrigatório por passo e
error budget — estourou, congela e volta ao checkpoint. Dito isso: software muda comportamento; o
caminho seguro é o dela, não pular etapas.

**Ela lê meus segredos?**
O inventário *aponta* onde segredos vivem (é esse o ponto: achar o que deveria estar escondido),
mas todo processamento é **local**, em Python stdlib, **zero telemetria** — nenhum dado seu sai da
sua máquina por causa do Genial Labs.

**É grátis? Quanto custa?**
Por enquanto: **MIT, aberto e gratuito** (beta). Com o site oficial chegam os **planos comerciais**
definidos por conta cadastrada/token — o plano gratuito deve continuar cobrindo uso individual
(ver [Roadmap](roadmap.md)).

**Como atualizo?**
`genial update` (git pull quando veio por clone) ou rodar de novo a linha do instalador —
idempotente, não duplica nada.

**A skill não apareceu no Codex. E agora?**
1) `genial skills` mostra se está no lugar certo (deve listar `[ok] cidadela`);
2) reinicie o Codex uma vez (o scan é automático, mas há casos);
3) confira se não desativou via `[[skills.config]]` em `~/.codex/config.toml`.

**Qual a diferença de "só pedir pra IA"?**
Prompt sem processo aceita opinião; a Cidadela exige **evidência** (`arquivo:linha`, resposta da
probe), **checkpoint** antes de escrever, **ADR** com condição de reversibilidade e **gate no CI**
que impede a regressão depois. A IA continua fazendo o trabalho — agora com régua.

**Posso desinstalar limpo?**
`genial uninstall -y` (qualquer SO) remove exatamente o que o instalador colocou. No Windows há
também `uninstall.ps1` (limpa até o trecho do PATH). Nada mais é tocado.

**Time: cada um instala na sua máquina?**
Sim — instalação por usuário. Para o time inteiro carregar junto com o projeto, use o instalador
com `--repo` (bash) ou `-Repo` (PowerShell): coloca também em `.agents/skills` e `.claude/skills`
do repositório. Com o token, cada membro usa o próprio.

**Serve para outro CI que não GitHub Actions?**
O workflow pronto é GitHub Actions; os gates por trás (secret-scan no histórico, SCA, SAST, teste
do modificado, imagem, CODEOWNERS) equivalem direto em GitLab CI, CircleCI ou Jenkins — o
protocolo está em `references/ci-cd.md`.

**Onde reporto bug?**
Issue em `brunao23/genial-labs` com: comando executado, SO (e rota de instalação: PowerShell /
Git Bash / WSL / Linux / macOS), versão do Python, saída completa (com `NO_COLOR=1` ajuda) e a
área suspeita (CLI / skill / templates / instalador).
