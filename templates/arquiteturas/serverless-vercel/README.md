# serverless-vercel

Funções Python WSGI na Vercel — zero dependência, deploy arrastando a pasta ou com `npx vercel`.

## Quando usar
- Rota/stateless de baixa latência: webhook, endpoint de análise, API fina sobre LLM externo.
- Tráfego intermitente ou imprevisível — paga-se por execução, não por máquina ligada.
- Time pequeno que quer produção em minutos, sem gerenciar servidor nem container.

## Quando NÃO usar
- Carga longa (> maxDuration do plano; padrão ~10 s no plano gratuito — aumente em `vercel.json`).
- Estado entre requisições: filesystem é **efêmero** — use KV/banco externo.
- Cold start sensível (Python paga ~250 ms na primeira execução do processo).

## Rotas deste pack
| Arquivo | Rota | Método | O que faz |
|---|---|---|---|
| `api/saude.py` | `/saude` | GET | health probe JSON |
| `api/processar.py` | `/processar` | POST | métricas de texto (palavras, leitura, top termos) |

## Deploy
```bash
npm i -g vercel        # uma vez
cd <este-dir> && vercel
# ou com git: conecte o repositório no dashboard → framework "Other"
```
Variáveis: `Project Settings → Environment Variables` (veja `.env.example` local).

## Limites que importam (confira o plano: vercel.com/docs/functions#function-limits)
- Duração máxima por função: configurável em `vercel.json` → `functions.*.maxDuration`.
- Memória por execução limitada (default ~1 GB no plano pago).
- Regiões: funções rodam na região do projeto; latência importa → escolha perto dos usuários.
