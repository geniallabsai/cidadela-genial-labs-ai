# 🏛️ Arquiteturas prontas — guia de decisão

Cinco formas de empacotar e operar o mesmo tipo de software, todas copiáveis com
**`genial arq <nome>`** e todas com README próprio de decisão + limites + deploy.
Este guia responde a pergunta certa **antes** de copiar: *qual forma o seu problema pede?*

## Escolha pela situação (tabela única de decisão)

| Sua situação | Arquitetura | Pack | Por quê |
|---|---|---|---|
| "Sobe uma API fina / webhook em minutos" | Serverless Vercel | `serverless-vercel` | Deploy em 2 comandos, custo por execução |
| "Já vivo no mundo AWS (S3/SQS/Cognito)" | Serverless Lambda | `serverless-lambda` | Trigger nativo + IAM, template SAM incluso |
| "Latência global + plano grátis generoso" | Cloudflare Workers | `serverless-cloudflare` | Execução na borda, cold start quase nulo |
| "Partes do sistema escalam/deployam em ritmo不同" | Microserviços | `microservicos` | Só quando o sinal foi medido (regra abaixo) |
| "Vendo para N organizações" | SaaS multi-tenant | `saas-multitenant` | Isolamento por tenant com a estratégia menos cara que sua política aceita |

**Monólito baseline** continua sendo o ponto de partida do `genial init` — essas opções são
**formas de operação**, não substitutas da disciplina de dados/segurança/CI do pacote.

## A regra que evita 80% das dores

1. **Monólito primeiro.** Comece no `genial init` (Dockerfile + compose + k8s + gates).
2. **Serverless antes de micro.** Se a dor é "máquina ligada custando caro" ou "tráfego
   imprevisível", serverless resolve **sem** quebrar o sistema em vários.
3. **Micro só com sinal medido.** Duas equipes pisando na mesma pasta, escala 10× diferente
   por parte, deploy acoplado travando release — *mediu*? Vai de `microservicos`. Senão, não.
   Critérios completos: `skills/cidadela/references/monolito-vs-microservicos.md`.
4. **Multi-tenant muda produto, não só infra.** Chave por tenant, quota, LGPD (exclusão efetiva),
   pricing. Guia: `skills/cidadela/references/multitenancy.md`.

## Como se encaixam na escada do `genial deploy`

A escada (`0 nada → 1 Dockerfile → 2 compose → 3 gates CI → 4 K8s → 5 IaC/cloud`) mede
**maturidade operacional**, não forma. Os packs mudam o *onde roda*:

- **Vercel/Lambda/Workers**: atiram você direto no degrau 5 de facto (plataforma gerencia
  escalo, rede, certificações) — mas o gate de CI (degrau 3) **continua obrigatório**: o
  `workflow-ci-gates.yml` do pacote funciona igual no pipeline da plataforma (GitHub Actions).
- **Microserviços**: sobem a partir do degrau 3 (gates por serviço) e usam os manifests
  `templates/k8s/` no degrau 4 (namespace por serviço) — ou um cluster gerenciado no 5.
- **SaaS multi-tenant**: ortogonal — roda em qualquer degrau/forma; o que ele impõe é a
  disciplina de isolamento (ADR escrito) e o checklist de enduro do README do pack.

## Limites que já doem em produção (leia ANTES de copiar)

| Pack | Armadilha comum | Mitigação no pack |
|---|---|---|
| vercel | Execução longa estoura maxDuration | `maxDuration` explícito em `vercel.json`; trabalho longo → fila |
| lambda | Estado em `/tmp` sumindo + cold start | handler stateless por design; cache em DynamoDB/ElastiCache |
| cloudflare | CPU ms por invocação no plano grátis | worker = borda leve; processamento pesado sai do worker |
| microservicos | 3 serviços no dia 1 e ninguém debuga | healthchecks agregados no gateway + regra "tracing antes do 4º serviço" |
| saas | Tenant A vê dado do tenant B (o bug que derruba SaaS) | resolução única de tenant + teste de isolamento incluído (`test_app.py`) |

## Depois de copiar

```bash
genial arq                        # lista o que existe no seu pacote
genial arq <nome> --copiar DIR    # copia sem sobrepor o que já existe
cd <dir> && cat README.md         # decisão, limites, comando de deploy — por escrito
```
Todo pack segue o padrão Genial Labs: **zero dependência**, `/healthz` JSON, erros JSON,
README que explica *quando não usar* (a parte que todo template finge que não existe).
