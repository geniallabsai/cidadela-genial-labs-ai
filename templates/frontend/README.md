# Frontend enterprise — pacote de referência Genial Labs

Painel de referência **zero-dependências** (HTML + CSS + JS puro, ~35 KB no total) com padrão
enterprise na camada visual: tokens de design, temas claro/escuro, acessibilidade WCAG 2.1 AA,
responsividade mobile-first e página de status conectada ao `/healthz` da sua API.

Uso rápido:

```bash
genial ui --copiar publico/     # copia index.html, css/ e js/ para dentro de publico/
python3 -m http.server 8080     # sirva a pasta e abra http://localhost:8080
```

## Estrutura

```
index.html       página demonstrativa completa (skip-link, nav, hero, componentes, tabela, form, status)
css/tokens.css   TODOS os valores: cor (2 temas), espaço 8pt, tipografia fluida, raios, sombras, movimento
css/base.css     reset mínimo, foco visível, reduced-motion, impressão, utilitários (skip-link, sr-only)
css/components.css botões, campos, cartões, tabela responsiva, nav colapsável, badges, alertas, toasts
js/app.js        menu mobile (Esc/toque fora), tema persistente, toasts, /healthz, validação de formulário
```

## Quando usar

- API interna/administrativo, MVP, página de status, protótipo que precisa parecer produção hoje.
- **Referência viva**: projetos React/Vue/Svelte devem roubar os tokens (`css/tokens.css` é um tema
  pronto — cole as variáveis no seu `:root`) e as regras de comportamento (foco, movimento, alvos).

## Quando NÃO usar

- Produto público com design system próprio exigido pelo time (aqui não há componente library).
- SSR, rotas client-side complexas ou i18n em várias línguas (recrie esta estrutura dentro do framework).
- Se o projeto já tem Tailwind: use os tokens como `@theme`, mantenha as regras de a11y de `base.css`.

## Acessibilidade (checklist embutido)

Contraste AA nos dois temas (todos os pares texto/fundo) · foco visível em tudo · skip-link ·
landmarks (`header/nav/main/footer`) · `aria-expanded`/`aria-controls` no menu · mensagens de erro
ligadas por `aria-describedby` · `role=status` para badges e toasts · alvos de toque ≥ 44 px ·
`prefers-reduced-motion` respeitado · navegação 100% teclado.

## Responsividade

Mobile-first · quebras em 40rem e 48rem · grid fluido `auto-fill/minmax` · tabela vira cartões
empilhados ≤ 40rem (via `data-chave`) · safe-area insets para notches · tipografia fluida com `clamp()`.

## Performance

Sem bundle, sem runtime, sem fonte externa: 3 folhas CSS + 1 JS. Servir atrás de qualquer CDN;
adicionar `Cache-Control` imutável nos assets com hash se publicar.

## Contrato com o restante do sistema

O widget de status chama `GET /healthz` — o mesmo endpoint que o `genial doctor` exige nos
vereditos e que o Dockerfile/docker-compose gerados pelo `genial blinda` expõem com healthcheck.
