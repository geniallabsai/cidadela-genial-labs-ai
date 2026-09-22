# saas-multitenant

SaaS de exemplo em **um único processo**: isolamento por tenant (shared schema +
identificação por subdomínio/header/chave), zero dependência.

## Estratégias de isolamento (escolha consciente — ADR!)
| Estratégia | Isolamento | Custo | Complexidade | Uso |
|---|---|---|---|---|
| **Shared schema + coluna tenant_id** ✅ (este pack) | lógico | baixo | baixa | 0 → ~50 tenants, produto early |
| Schema por tenant | físico parcial | médio | média | tenant exige separação de schema |
| Banco por tenant | físico total | alto | alta | enterprise/compliance (LGPD setorizada) |

Escolha a **menos isolante que sua política de dados permita** e escreva ADR documentando.
Guia completo: `skills/cidadela/references/multitenancy.md`.

## Resolução de tenant (ordem)
1. **Subdomínio**: `acme.suaapp.com` → tenant `acme` (o que um SaaS sério expõe).
2. **Header** `X-Tenant: acme` (API/mobile).
3. **Query** `?tenant=acme` (último recurso, só dev).

Depois: **autenticação por chave** — cada tenant tem `X-API-Key` própria; chave errada ou
de outro tenant → 401. Neste pack as chaves são derivadas demo (`demo-` + sha256(curto));
em produção: banco + hash da chave + rotação.

## Rodar / testar
```bash
python app.py                     # http://localhost:8010
python test_app.py                # smoke test sem rede (WSGI direto)
# uso:
curl -H "X-Tenant: acme" -H "X-API-Key: $(python -c 'import hashlib;print("demo-"+hashlib.sha256(b"acme").hexdigest()[:12])')" \
     -X POST localhost:8010/recursos -d '{"nome":"plano-pro"}'
```

## Endurecer antes de cobrar dinheiro
- [ ] Chaves com sha256 no banco (nunca plaintext) + rotação dupla
- [ ] Quota por tenant (requisições/min, volume) — rejeitar com 429 + `Retry-After`
- [ ] Audit log imutável (quem fez o quê, em qual tenant)
- [ ] Tenant off: soft delete + prazo legal de exclusão (LGPD: exclusão efetiva documentada)
- [ ] Rate limit no edge (Cloudflare/WAF) antes do app
