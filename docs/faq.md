# FAQ — o que perguntam primeiro

**Funciona no Windows?**
Sim, via **WSL2** (Ubuntu recomendado). O instalador é `bash` e o pacote roda em cima do
Python do WSL. Docker Desktop com integração WSL2 completa o cenário de containers.

**Quais agentes de IA usam a skill Cidadela?**
**Codex** e **Claude Code** nativamente — ela está no formato aberto Agent Skills
(agentskills.io), então qualquer agente que leia `SKILL.md` funciona. Sem agente, `genial
doctor` dá a Fase 0 direto no terminal.

**Meu código não é Python, Node nem Go.**
A **skill fala qualquer linguagem** (há mapa para 14 stacks em `mapa-linguagens.md`) —
diagnóstico, veredito, ofensiva e blindagem não dependem da linguagem. Quem é específico das
três primeiras é só o scaffold do `genial init` (esqueleto inicial). Para outro stack: crie os
arquivos base do seu jeito e siga com a skill — ou abra uma issue pedindo suporte, que vira
prioridade de roadmap.

**Depois de instalado, preciso de internet?**
Não. Tudo roda localmente. Só a atualização (`genial update`/reinstalação) e, no futuro, a
validação do token conversam com a rede.

**Ela pode quebrar a minha produção?**
O processo foi desenhado para não: **checkpoint humano antes de qualquer escrita**, mudança
atrás de flag (desligada = comportamento antigo), rollback < 5 min, CI verde obrigatório por
passo e error budget — estourou, congela e volta ao checkpoint. Dito isso: software muda
comportamento; o caminho seguro é o dela, não pular etapas.

**Ela lê meus segredos?**
O inventário *aponta* onde segredos vivem (é esse o ponto: achar o que deveria estar escondido),
mas todo processamento é **local**, em Python stdlib, **zero telemetria** — nenhum dado seu sai
da sua máquina por causa do Genial Labs.

**É grátis? Quanto custa?**
Por enquanto: **MIT, aberto e gratuito** (beta). Com o site, chegam os **planos comerciais**
definidos por conta cadastrada/token — o plano gratuito deve continuar cobrindo uso
individual. Detalhes quando o token lançar (roadmap).

**Como atualizo?**
`genial update` (git pull quando veio por clone) ou rodar de novo a linha do `curl | bash` —
idempotente, não duplica nada.

**A skill não apareceu no Codex. E agora?**
1) `genial skills` mostra se ela está no lugar certo (deve listar `[ok] cidadela`);
2) reinicie o Codex uma vez (o scan é automático, mas há casos);
3) confira se não desativou via `[[skills.config]]` em `~/.codex/config.toml`.

**Qual a diferença de "só pedir pra IA"?**
Prompt sem processo aceita opinião; a Cidadela exige **evidência** (`arquivo:linha`, resposta
da probe), **checkpoint** antes de escrever, **ADR** com condição de reversibilidade e **gate
no CI** que impede a regressão depois. A IA continua fazendo o trabalho — agora com régua.

**Posso desinstalar limpo?**
`genial uninstall -y` remove exatamente o que o instalador colocou (`~/.genial-labs`,
`~/.local/bin/genial` e as duas cópias da skill). Nada mais.

**Time: cada um instala na sua máquina?**
Sim — instalação por usuário. Para o time inteiro carregar junto com o projeto, use o instalador
com `--repo` (coloca também em `.agents/skills` e `.claude/skills` do repositório). Com o
token, cada membro usa o próprio.

**Serve para outro CI que não GitHub Actions?**
O workflow pronto é GitHub Actions; os gates por trás (secret-scan no histórico, SCA, SAST,
teste do modificado, imagem, CODEOWNERS) equivalem direto em GitLab CI, CircleCI ou Jenkins —
o protocolo está em `references/ci-cd.md`.

**Onde reporto bug?**
Issue em `brunao23/genial-labs` com: comando executado, SO, versão do Python, saída completa e
a área suspeita (CLI / skill / templates / instalador).
