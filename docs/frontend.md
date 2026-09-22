# Frontend enterprise — pacote de referência Genial Labs

A camada visual do sistema com padrão enterprise e **zero dependências**: HTML + CSS + JS puro,
~34 KB no total, pronto para servir atrás de qualquer web server ou CDN. É o que
`genial ui --copiar` entrega.

## Quando usar

- API interna/administrativo, MVP, página de status, protótipo que precisa parecer produção hoje.
- Base honesta para produto novo em vanilla (sem bundler) — a página incluída demonstra todos os
  componentes em estado vivo: botões e estados, campos com erro, tabela responsiva, formulário
  validado, toasts e status da API.
- **Referência viva**: apps React/Vue/Svelte devem roubar os tokens (`css/tokens.css` é um tema
  pronto — cole as variáveis no seu `:root` ou mapeie para o tema do framework) e as regras de
  comportamento (foco visível, movimento reduzido, alvos de toque, menu que fecha com Esc).

## Quando NÃO usar

- Produto público com design system próprio exigido pelo time — aqui não há component library,
  apenas o padrão visual e as regras de interação.
- SSR, rotas client-side complexas ou i18n multilíngue — recrie esta estrutura dentro do framework.
- Projeto já com Tailwind: mantenha os tokens como `@theme` e as regras de acessibilidade de
  `base.css`; não duplique as duas coisas.

## Estrutura

| Arquivo | Conteúdo |
|---|---|
| `index.html` | Página demonstrativa completa: skip-link, nav colapsável, hero, componentes, tabela responsiva, formulário validado, status da API |
| `css/tokens.css` | **Todos os valores**: cor (temas claro/escuro com pares de contraste AA), espaço (grid de 8 pt), tipografia fluida (`clamp()`), raios, sombras, movimento |
| `css/base.css` | Reset mínimo, foco visível, `prefers-reduced-motion`, impressão, utilitários (`sr-only`, `skip-link`), safe-area insets |
| `css/components.css` | Botões (estados + loading), campos com erro ligado por `aria-describedby`, cartões, tabela que vira cartão no celular, nav colapsável, badges, alertas, toasts, esqueleto de carga |
| `js/app.js` | Menu mobile (fecha com Esc/toque fora), tema persistente em `localStorage`, toasts anunciados por leitor, validação de formulário, widget de status `/healthz` |
| `README.md` | Resumo + decisão rápida |

## Acessibilidade (requisitos embutidos)

- Contraste **WCAG 2.1 AA** em todos os pares texto/fundo, nos dois temas.
- Foco visível em tudo (`:focus-visible` com anel de 2 px) e navegação 100% por teclado.
- Skip-link, landmarks (`header/nav/main/footer`), `aria-expanded`/`aria-controls` no menu.
- Mensagens de erro ligadas ao campo por `aria-describedby`; toasts em região `aria-live`.
- Alvos de toque ≥ 44 px (token `--alvo-tato`) — regra de usabilidade em tela pequena.
- `prefers-reduced-motion` respeitado: todo efeito de transição/animação desliga.
- Tema escuro automático (`prefers-color-scheme`) com override manual persistente.

## Responsividade

- Mobile-first; quebras em **40rem** (tabela vira cartão empilhado via `data-chave`) e **48rem**
  (nav colapsa em menu).
- Grid fluido `repeat(auto-fill, minmax(min(100%, 17rem), 1fr))` — cartões se empilham sem media query.
- Tipografia fluida com `clamp()` (do celular ao desktop sem passos).
- `env(safe-area-inset-*)` para notches e scroll horizontal suave nas rolagens.
- Impressão: chrome desaparece, conteúdo fica limpo.

## Performance

Sem bundle, sem runtime, sem fonte externa: 3 folhas de CSS + 1 JS (~34 KB bruto). O JavaScript só
faz o que a página pede (menu, tema, toasts, status) — nenhum framework carregado para existir.

## Contrato com o resto do sistema

- O widget de status chama `GET /healthz` — o mesmo endpoint que o `genial doctor` exige nos
  vereditos e que o Dockerfile/compose gerados pelo `genial blinda` expõem com healthcheck.
- Os nomes das classes são estáveis e semânticos (`.botao`, `.cartao`, `.tabela-resp`, `.badge`) —
  trate-os como API interna pública do seu produto.

## Limites (honestos)

Sem framework, sem SSR, sem rotas client-side, sem i18n automático e sem suíte de testes incluída
(o pacote é conteúdo de referência, não um app). Para virar produto, encaixe na sua própria suíte
de testes E2E.
