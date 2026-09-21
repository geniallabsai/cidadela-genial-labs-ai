# Fase Ofensiva — atacar antes do atacante

Não basta blindar: a skill executa em staging os ataques que um red team faria na primeira semana e
registra o resultado. Regra de ouro: **todo achado vira evidência** (requisição + resposta ou arquivo:linha).
Achado sem evidência não entra no relatório — zoeira sem evidência também não convence ninguém.

## 1. Método (árvore de ataque)
Para as 3 superfícies públicas mais sensíveis (auth, dinheiro, dados por ID):
1. Objetivo explícito: "com a conta de teste T1, obter dado de T2, virar admin, ou fazer o sistema executar algo".
2. Descompor: entrada → transformação → saída; em cada nó perguntar "e se esta entrada for maligna?".
3. Um vetor por nó, executar, registrar. Se falhar, descer um nível. Parar quando: P0 encontrado OU 2h por superfície.

## 2. Primeira hora do atacante (probes prontas)
Executar ANÔNIMO e AUTENTICADO; registrar status + corpo da resposta:
```bash
B="https://staging.seudominio.com"
# superfícies ocultas
for p in .env .git/config .git/HEAD docker-compose.yml wp-login.php actuator actuator/env \
         actuator/health debug __admin api swagger.json api-docs graphql robots.txt \
         sitemap.xml .DS_Store favicon.ico; do
  printf "%-24s %s\n" "/$p" "$(curl -s -o /dev/null -w '%{http_code}' $B/$p)"
done
# CORS aberto em API autenticada?
curl -si -X OPTIONS $B/api/dados -H "Origin: https://evil.com" -H "Access-Control-Request-Method: GET" \
  | grep -i access-control
# source map expõe o código-fonte?
JS=$(curl -s $B/login.html | grep -oE '/[^"]+\.js' | head -1)
curl -s -o /dev/null -w '%{http_code}\n' "${B%/}$JS.map"
# IDOR: incrementar id / trocar id de outra conta / trocar tenant em cada rota /:id
# JWT: decodificar payload; forçar alg:none; trocar exp/atualizar kid; se HS256 e secret curto, hashcat -m 16500
# host-header injection: curl -H "Host: attacker.tld" no fluxo de reset de senha — para onde o link aponta?
# SSRF em campo que aceita URL: http://169.254.169.254/latest/meta-data/ e file:///etc/passwd
# race: 10 POSTs simultâneos de saque/desconto/cupom — somou o dobro?
# webhook: POST de evento forjado SEM assinatura — foi processado?
# mass assignment: adicionar "role":"admin" / "tenant_id":"outro" / "balance":1e9 no body de update
# zip bomb: upload de ~50KB com Content-Encoding gzip descompactando GB
# ReDoS: e-mail/string de 10k chars em campo validado por regex
# enumeração: timing de "usuário não existe" vs "senha errada"; 200 vs 404 em /usuario/:id
```
Cada probe → 1 linha no relatório ofensivo (vetor, entrada, saída, severidade, mitigação).

## 3. Severidade (regra única)
- **P0**: explorável AGORA, sem acesso especial, com impacto em dado/credencial/execução
  (.env legível, CORS `*` em API autenticada, IDOR entre tenants, `alg:none` aceito, webhook sem assinatura).
- **P1**: exige conta comum ou pouco esforço; impacto contido ou em sub-funcionalidade.
- **P2**: endurecimento (rate limit ausente em login, header faltando, SCA médio, doc interna exposta).
Score = impacto (alcance: 1 conta / 1 tenant / plataforma × tipo: ler / escrever / executar)
× viabilidade (anônimo < autenticado < admin). Duas incertezas ⇒ subir UMA categoria.

## 4. Cheiro de código gerado por IA (triagem de 60s por linha)
Onde a IA erra mais em segurança:
| Cheiro no código | Vulnerabilidade típica | Check em 60s |
|------------------|------------------------|--------------|
| `if (user?.isAdmin \|\| process.env.DEBUG)` | autorização a puxa-a-zipão | grep `\|\|.*DEBUG` perto de checagem de permissão |
| rota registrada FORA do middleware de auth (ordem) | endpoint privado que ficou público | listar rotas × middlewares aplicados, um a um |
| `secret \|\| 'dev-secret'` / JWT secret fixo | token forjável por qualquer um | grep default perto de secret; forjar 1 token e bater em rota protegida |
| `fetch(url)` com `url` vindo do usuário | SSRF (inclusive metadata da cloud) | seguir o parâmetro de URL até a chamada de rede |
| `innerHTML` / template com input crú | XSS armazenado/refletido | injetar `<img src=x onerror=alert(1)>` em campo livre |
| query do ORM após refator sem o filtro antigo | IDOR / leak entre tenants | rodar o teste negativo A×B |
| `TODO: validar depois` em auth/pagamento | stub virou produção | grep TODO em arquivos que tocam auth/money |
| middleware duplicado com 1 linha de diferença | uma das cópias esqueceu o check | diff dos middlewares irmãos |
| endpoint de debug com flag "desligada" | backdoor que vive de um typo de config | grep debug/tmp/fix em rotas; forçar a flag e chamar |
| teste que MOCKA a camada de segurança | suíte verde sobre buraco aberto | rodar 1 fluxo de auth sem mocks |
| `latest` nas imagens / sem lockfile | supply chain muda sob os pés | `grep latest` em Dockerfile + lockfile presente? |
| CORS `*` copiado do Stack Overflow | credencial/cookie lidos por página maliciosa | probe de OPTIONS da §2 |

## 5. Regras de engajamento
- Ambiente: staging com dados sintéticos (2 tenants + 1 admin). Nunca probe destrutiva em produção.
- Registro: cada probe = 1 linha (vetor, entrada, saída, severidade, mitigação). O relatório OFENSIVO é esse registro.
- Ordem: anônimo → autenticado → admin. P0 encontrado ⇒ **parar e corrigir antes de continuar** (timebox perde de buraco aberto).
- Repetir a ofensiva a cada release que tocar em auth, dinheiro ou tenancy — não só no lançamento.
