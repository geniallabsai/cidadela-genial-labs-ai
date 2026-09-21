# Contribuindo

O Genial Labs é código aberto (MIT) enquanto beta. Bug report bom vale mais que PR perfeito:
muita coisa aqui nasce de quem usou em produção.

## Onde cada coisa mora

| Área | Arquivos |
|------|----------|
| CLI `genial` | `genial` (Python stdlib, 1 arquivo) |
| Instalador | `install.sh`, `uninstall.sh` |
| Skill Cidadela | `skills/cidadela/` (SKILL.md orquestra; `references/` = protocolos; `scripts/` = inventário; `assets/` = templates de saída) |
| Templates de projeto | `templates/` (dados, Dockerfiles, compose, k8s, skeletons) |
| Documentação | `docs/` (esta) |

## Reportando bug (mínimo que acelera o fix)

1. O comando exato que você rodou;
2. SO (distro/versão) e `python3 --version`;
3. Saída completa (com `NO_COLOR=1` ajuda a ler);
4. Área suspeita: CLI / skill / templates / instalador / docs;
5. Se reproduzível: o menor projeto possível que reproduz.

## Mandando PR

- CLI: Python stdlib, sem dependência nova sem motivo forte; rode `python3 -m py_compile genial`
  e um ciclo `init` + `doctor` em /tmp antes de mandar.
- Skill: mudança em `references/` mantém o tom (regra + evidência + exceção rotulada); mudar
  fase do `SKILL.md` exige ajuste do `description` do frontmatter (≤ 1024 chars) e do LEIA-ME.
- Templates: placeholder novo ⇒ atualize a substituição no `genial` (busque `{{`).
- Docs: português do Brasil, tom direto, tabela quando comparar, exemplo quando executar.

## Estilo da casa

Evidência antes de opinião; nada quebra (toda mudança com rollback); hipótese rotulada nunca
passa por fato; dinheiro em centavos; segredo fora do repositório — inclusive no seu branch.
