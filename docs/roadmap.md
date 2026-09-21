# Roadmap público

Roadmap público: o que já saiu, o que vem e por quê. Sujeito a mudança — esta página existe para
a comunidade saber onde o trem vai.

## Liberado — v1.0.0 / v1.0.1 (set/2026)

- Instalador de terminal com banner **GENIAL LABS** em azul tech + self-test automático;
- CLI `genial`: `init` (projeto guiado por arquitetura de dados), `doctor` (auditoria),
  `deploy` (escada 0–5 de infra), `skills`, `update`, `uninstall`;
- Skill **Cidadela** com 8 fases: diagnóstico com evidência, veredito com checkpoint humano,
  cirurgia reversível, **ofensiva red-team**, blindagem (12 canais de vazamento, PII brasileira,
  LGPD), gates de CI/CD e **plataforma** (VPS/Docker/K8s/AWS + IA no produto);
- Reversão de **legado** e **migração gradual de linguagem** como protocolos próprios;
- Templates: Arquitetura de Dados, Dockerfiles (py/node/go), Compose, Kubernetes mínimo
  saudável, skeletons com testes, gates de CI;
- **Documentação completa** (12 páginas) e licença **MIT**.

## Próxima etapa — Site oficial + acesso por token

A instalação deixa de ser "aberta para quem acha o repositório" e passa a ser **"cadastrou,
recebeu chave, instalou"**:

1. Site com cadastro (nome + e-mail) e login;
2. **Token pessoal** `GL-…` gerado na conta;
3. Instalação: `curl ... | bash -s -- --token …` (forma já documentada em
   [Acesso e token](acesso-e-token.md));
4. `genial update` passa a validar a conta — versão instalada visível para suporte.

Até lá: **beta aberto**. Nada do que você instalar hoje fica órfão.

## Depois — lapidação para o lançamento comercial

- **Planos** definidos por conta (gratuito individual / pro / time) — o que muda em cada;
- Branding e domínio oficiais; o site vira a vitrine (demonstração do banner, exemplos de
  relatório, depoimentos);
- Mais stacks no `init` (Rust, Java/Spring, PHP, Kotlin — por ordem de pedidos);
- Mais agentes de IA além de Codex/Claude Code (formato aberto ajuda);
- Painel opcional por conta: histórico de versões e projetos auditados.

## Como influenciar

Issue com o label `roadmap` — pedido com contexto (o que, por quê, urgência) sobe na fila.
