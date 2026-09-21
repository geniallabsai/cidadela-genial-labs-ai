# Iniciação rápida

Do zero ao primeiro projeto guiado em menos de 5 minutos.

## Requisitos

| Requisito | Por quê |
|-----------|---------|
| **Windows 10/11, Linux ou macOS** | instaladores para os três (Windows tem rota nativa em PowerShell) |
| **Python 3.7+** (apenas stdlib, sem `pip install` de nada) | o CLI `genial` e os scripts da skill |
| No Windows: **PowerShell 5.1+** (vem com o SO) **ou** Git Bash / WSL2 | executa o instalador |
| `git` ou `curl` (opcionais) | o instalador baixa o pacote; se faltar ambos, usa `urllib` do Python |
| Docker e kubectl (opcionais) | só quando for subir containers/cluster — o scaffold nasce pronto |

> No Windows, instale o Python marcando **"Add python.exe to PATH"** no instalador oficial
> (python.org). O Genial Labs procura `py`, `python` e `python3`, nessa ordem.

## Instalação

### Windows — PowerShell nativo (recomendado)

Abra o PowerShell (não precisa de administrador):

```powershell
irm https://raw.githubusercontent.com/brunao23/genial-labs/main/install.ps1 | iex
```

Se a política da sua máquina bloquear `iex`:

```powershell
iwr https://raw.githubusercontent.com/brunao23/genial-labs/main/install.ps1 -OutFile $env:TEMP\ig.ps1
powershell -ExecutionPolicy Bypass -File $env:TEMP\ig.ps1
```

O instalador adiciona o comando ao **PATH do seu usuário** — **abra um novo terminal** para ele valer.

### Linux / macOS / WSL2 / Git Bash (Windows)

```bash
curl -fsSL https://raw.githubusercontent.com/brunao23/genial-labs/main/install.sh | bash
```

No terminal aparece o bloco **GENIAL LABS** em azul tech e o instalador faz 4 passos:

1. baixa o pacote (git com `autocrlf=false` → zip → urllib, na ordem de disponibilidade);
2. instala em `~/.genial-labs/` (no Windows nativo: `%USERPROFILE%\.genial-labs`);
3. instala a skill **cidadela** em `~/.agents/skills` (Codex) e `~/.claude/skills` (Claude Code);
4. instala o comando `genial` (wrapper que chama o Python explicitamente) em
   `~/.local/bin` (Unix) ou `%LOCALAPPDATA%\GenialLabs\bin` (Windows) — e roda self-test.

Se aparecer "aviso: adicione ao PATH" (Unix), faça uma vez só no seu perfil:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

> **Nota:** a instalação atual é **beta aberto**. Com o site oficial ela passará a receber seu
> token pessoal: `--token SEU_TOKEN` — detalhes em [Acesso e token](acesso-e-token.md).

## Primeiro projeto guiado

```bash
genial init meu-app --stack py     # py | node | go | auto (detecta o que existir)
cd meu-app
git init && git add -A && git commit -m "chore: scaffold genial labs"
make run        # sobe o app
make test       # suíte de testes
make docker-up  # app + Postgres local (se tiver Docker)
```

O que o `init` já cria (e **nunca sobrescreve** arquivo seu):

- `ARCHITETURA-DADOS.md` — o documento que **guia a programação** (donos por entidade, contratos, gates);
- skeleton com rota `/healthz` + testes;
- `Dockerfile` (non-root + healthcheck), `.dockerignore`, `.env.example`, `.gitignore`;
- `docker-compose.yml` (app + db com healthcheck);
- `k8s/` — deployment (securityContext restrito), service, ingress (TLS + rate limit), hpa;
- `.github/workflows/gates.yml` — gates de segurança que **bloqueiam** merge;
- `Makefile` (run/test/docker/backup-db/k8s-apply);
- `docs/adr/ADR-0000-stack.md` — a primeira decisão registrada, com condição de reversibilidade.

## Primeira auditoria de um projeto existente

```bash
cd meu-projeto
genial doctor
```

Roda a **Fase 0 (Acervo)** da skill Cidadela no terminal: linguagens/LOC, topologia de deploy,
segredos expostos, sinais de multi-tenancy e **cheiro de código gerado por IA**. A interpretação
profunda (veredito, cirurgia, ofensiva) acontece dentro do agente: abra o projeto no Codex ou
Claude Code e diga:

```
cidadela: audite este repositório de ponta a ponta
```

No Codex a skill também aparece em `/skills` → `cidadela`. Ela **para num checkpoint** e só
escreve código depois de você aprovar o relatório.

## Checklist do "funcionou"

- [ ] `genial skills` mostra `[ok] cidadela` nas linhas Codex e Claude Code;
- [ ] `genial init` criou `ARCHITETURA-DADOS.md` e 17 arquivos sem queixas;
- [ ] `make test` verde no projeto novo;
- [ ] `genial deploy` respondeu com um degrau 0–5 e um próximo passo;
- [ ] no Codex, "cidadela:" dispara a skill (se não aparecer, reinicie o Codex uma vez);
- [ ] (Windows) você abriu um **novo terminal** depois de instalar.

## Atualizar e desinstalar

```bash
genial update                 # git pull se veio por clone; senão, comando de reinstalação
genial uninstall -y           # remove pacote, skill e wrapper
```

Windows: também há `uninstall.ps1` (mesma origem do instalador, flag `-y` para não perguntar).

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| `genial` não reconhecido (Windows) | PATH novo não carregado | **abra um novo terminal**; confira `genial skills` via `python %USERPROFILE%\.genial-labs\genial skills` |
| `genial` não reconhecido (Unix) | `~/.local/bin` fora do PATH | `export PATH="$HOME/.local/bin:$PATH"` (coloque no `~/.bashrc`) |
| "Python não encontrado" | Python sem PATH no Windows | reinstale o Python marcando *Add to PATH*; reabra o terminal |
| Skill não aparece no Codex | scan automático atrasado | reiniciar o Codex; conferir `genial skills`; checar `[[skills.config]]` |
