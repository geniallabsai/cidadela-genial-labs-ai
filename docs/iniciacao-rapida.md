# Iniciação rápida

Do zero ao primeiro projeto guiado em menos de 5 minutos.

## Requisitos

| Requisito | Por quê |
|-----------|---------|
| Linux ou macOS (Windows: use **WSL2**) | instalador em `bash` |
| `bash` (qualquer versão recente) | executa o instalador |
| `python3` ≥ 3.7 — **apenas stdlib** | o CLI `genial` e os scripts da skill não usam `pip install` de nada |
| `git` **ou** `curl` (opcional) | o instalador baixa o pacote; se faltar ambos, usa `urllib` do Python |
| Docker e kubectl (opcionais) | só quando você for subir containers/cluster — o scaffold nasce pronto para isso |

Nenhum compilador, nenhum ambiente virtual, nenhum serviço de fundo.

## Instalação

```bash
curl -fsSL https://raw.githubusercontent.com/brunao23/genial-labs/main/install.sh | bash
```

No terminal aparece o bloco **GENIAL LABS** em azul tech e o instalador faz 4 passos:

1. baixa o pacote (git → zip → urllib, na ordem de disponibilidade);
2. instala em `~/.genial-labs/`;
3. instala a skill **cidadela** em `~/.agents/skills` (Codex) e `~/.claude/skills` (Claude Code);
4. instala o comando `genial` em `~/.local/bin` — e roda um self-test criando um projeto de teste.

Se aparecer "aviso: adicione ao PATH", faça uma vez só no seu perfil:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

> **Nota:** a instalação atual é **beta aberto**. Com o site oficial, ela passará a receber seu
> token pessoal: `curl ... | bash -s -- --token SEU_TOKEN` — detalhes em [Acesso e token](acesso-e-token.md).

## Primeiro projeto guiado

```bash
genial init meu-app --stack py     # ou: node | go | auto (detecta o que existir)
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

Isso roda a **Fase 0 (Acervo)** da skill Cidadela no terminal: linguagens/LOC, topologia de
deploy, segredos expostos, sinais de multi-tenancy e **cheiro de código gerado por IA**.

A interpretação profunda (o veredito, a cirurgia, a ofensiva) acontece dentro do agente de IA:
abra o projeto no Codex ou Claude Code e diga:

```
cidadela: audite este repositório de ponta a ponta
```

No Codex você também encontra a skill em `/skills` → `cidadela`. Ela **para num checkpoint** e só
escreve código depois de você aprovar o relatório.

## Checklist do "funcionou"

- [ ] `genial skills` mostra `[ok] cidadela` nas duas linhas (Codex e Claude Code);
- [ ] `genial init` criou `ARCHITETURA-DADOS.md` e 17 arquivos sem queixas;
- [ ] `make test` verde no projeto novo;
- [ ] `genial deploy` respondeu com um degrau 0–5 e um próximo passo;
- [ ] no Codex, "cidadela:" dispara a skill (se não aparecer, reinicie o Codex uma vez).

## Atualizar e desinstalar

```bash
genial update       # git pull se o pacote veio por clone; senão, mostra o comando de reinstalar
genial uninstall -y # remove ~/.genial-labs, ~/.local/bin/genial e as cópias da skill
```
