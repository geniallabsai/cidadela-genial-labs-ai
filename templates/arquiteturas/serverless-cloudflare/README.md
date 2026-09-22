# serverless-cloudflare

Cloudflare Workers — JS na borda, cold start quase nulo, 100 mil requisições/dia gratuitas.

## Quando usar
- Latência global é requisito (rede da Cloudflare + execução perto do usuário).
- Fronteira: rewrite, A/B, rate limit leve, enriquecer resposta de API upstream.
- Custo predizível zero a baixo — plano gratuito cobre protótipo e projeto pequeno.

## Quando NÃO usar
- Carga pesada por requisição (limite de CPU por invocação no plano grátis: ~10 ms) —
  processe pesado em worker pago ou fora.
- Bibliotecas nativas (napi) ou dependências grandes:Workers empacota tudo (esgotando ~10 MB no grátis).
- Python/Go: possível (Pyodide/compile), mas o pack casa com JS — a linguagem da plataforma.

## Rotas deste pack
| Rota | Método | O que faz |
|---|---|---|
| `/saude`, `/` | GET | health probe |
| `/eco` | POST | devolve JSON recebido (usa KV opcional para guardar) |

KV é opcional: descomente `kv_namespaces` no `wrangler.jsonc` e crie com
`npx wrangler kv namespace create STORAGE` (o id vai no campo `id`).

## Deploy
```bash
npx wrangler dev              # local, com .dev.vars
npx wrangler deploy           # produção
```
Variáveis: `npx wrangler secret put MINE` (production) — local usa `.dev.vars`.
