# 📚 Documentação — Genial Labs

O manual completo do Genial Labs: instalar, usar, entender e estender. Cada página deste diretório
foi escrita para funcionar **tanto aqui no GitHub quanto como página do site oficial** (título,
descrição e navegação próprios — a virada para site é mecânica, conteúdo pronto).

## O que é o Genial Labs

O instalador de terminal que faz produto construído com IA render como engenharia de software
profissional. Uma linha no terminal instala:

- a skill **Cidadela** — o cérebro: audita a arquitetura (monolito × micro × dados), decide o melhor
  destino, ataca o sistema antes do atacante, blinda em camadas e planeja o deploy — tudo com
  evidência `arquivo:linha` e mudança reversível;
- o comando **`genial`** — scaffold guiado por arquitetura de dados, auditoria com veredito e
  blindagem automática, frontend enterprise e escada de infraestrutura (VPS → Docker → K8s → AWS);
- **templates** — Arquitetura de Dados, Dockerfiles, Compose, Kubernetes, gates de CI e frontend enterprise.

Em qualquer linguagem. Feita para quem não é engenheiro de software e precisa entregar como um.

## Comece em 5 minutos

```bash
# 1. Instalar (Linux/macOS; Python 3.7+ apenas stdlib)
curl -fsSL https://raw.githubusercontent.com/geniallabsai/genial-labs/main/install.sh | bash

# 2. Criar um projeto novo já guiado (escolha seu stack)
genial init meu-app --stack py      # py | node | go | auto

# 3. Auditar um projeto existente
cd meu-outro-projeto && genial doctor

# 4. Saber onde você está na escada de infra
genial deploy
```

Depois é abrir o projeto no Codex ou Claude Code e falar: **"cidadela: audite este repositório"**.

## Sumário

| Página | O que você vai aprender |
|--------|--------------------------|
| [Iniciação rápida](iniciacao-rapida.md) | Requisitos, instalação, primeiro projeto, primeiro diagnóstico, checklist do "funcionou" |
| [Comando `genial`](comandos-genial.md) | Referência completa: todos os comandos, flags, exemplos e códigos de saída |
| [A skill Cidadela](skill-cidadela.md) | As 8 fases, o checkpoint humano, as entregas e como invocar no Codex/Claude Code |
| [Arquitetura de dados](arquitetura-de-dados.md) | Por que os dados guiam a programação: donos, contratos, gates, dinheiro em centavos |
| [Segurança ofensiva e defensiva](seguranca-ofensiva-defensiva.md) | A primeira hora do atacante, os 12 canais de vazamento, PII brasileira, gates de CI |
| [Plataforma e cloud](plataforma-e-cloud.md) | A escada VPS→Docker→K8s→AWS, deploy zero-downtime e IA no produto |
| [Arquiteturas prontas](arquiteturas.md) | Guia de decisão: serverless (Vercel/Lambda/Workers), microserviços e SaaS multi-tenant — com packs copiáveis |
| [Frontend enterprise](frontend.md) | Tokens, temas claro/escuro, acessibilidade WCAG 2.1 AA, responsivo mobile-first — e quando NÃO usar o vanilla pack |
| [Legado e migração](legado-e-migracao.md) | Reverter engenharia em código antigo e migrar de linguagem sem parar o sistema |
| [Acesso e token](acesso-e-token.md) | O modelo de registro + token pessoal (com o site oficial) — e o estado atual do beta |
| [FAQ](faq.md) | Windows? Atualização? Seguros? Licença? Tudo que perguntam primeiro |
| [Roadmap](roadmap.md) | O que já saiu, o que vem: site, token e a versão comercial |
| [Contribuindo](contribuindo.md) | Como reportar bug e mandar PR — onde cada coisa mora no repositório |

## Estado atual

- **v1.3.1 — beta público.** Banner corrigido: a arte era em glifos de bloco (`█▀║`) e virava
  quadrados em fontes sem suporte; agora é **ASCII puro** e carrega os nomes **Cidadela**
  e **Genial Labs AI**. Base v1.3.0: `genial blinda` (correções mecânicas do veredito,
  idempotente, auditoria ANTES→DEPOIS) e `genial ui` (frontend enterprise zero-dependência).
- Anterior: v1.2.0 (veredito por componente na auditoria). A instalação está **aberta** para a comunidade (sem cadastro).
- Com o lançamento do **site oficial**, a instalação passa a ser feita com **token pessoal**:
  cada pessoa se cadastra e recebe a chave própria (ver [Acesso e token](acesso-e-token.md)).
- Suporte e sugestões: abra uma issue no repositório `geniallabsai/genial-labs`.
