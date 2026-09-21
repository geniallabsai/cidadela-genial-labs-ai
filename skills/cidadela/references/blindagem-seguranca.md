# Blindagem — checklist por camada (OWASP ASVS: mínimo L1 efetivo, alvo L2)

Formato do punch-list: `ID | item | status atual (evidência) | alvo | prioridade | esforço`.
**P0** = sangrando (exploração realista hoje) · **P1** = este trimestre · **P2** = consolidação.
Protocolo de vazamento de dados em `vazamento-dados.md`; ofensiva em `ofensiva.md`; pipeline em `ci-cd.md`.

## S — Secrets & configuração
- [ ] Nenhuma credencial em código nem em repositório (secret-scan no histórico, não só na HEAD)
- [ ] Secrets em vault/env gerenciado; rotação documentada
- [ ] `.env` fora do git (`.env.example` no lugar)
- [ ] Config por ambiente sem `if env == "prod"` espalhado pelo código
- [ ] Segredo ausente = processo NÃO sobe (fail-fast; `secret || 'dev-secret'` é P0 por si só)

## D — Dependências & supply chain
- [ ] Lockfile versionado e usado no build/CI (npm ci / uv sync / go mod vendor …)
- [ ] SCA em CI com política de severidade; CRITICAL conhecido = P0
- [ ] Versões pinadas; imagens com base mantida, assinatura quando disponível
- [ ] SBOM por release (CycloneDX/SPDX)
- [ ] Jobs de CI com token de menor escopo possível (read-only quando der); OIDC em vez de chave longa

## A — Identidade & autorização
- [ ] Autenticação na borda; sessão curta; MFA em conta privilegiada
- [ ] Autorização de menor privilégio (RBAC por função); admin temporário, não permanente
- [ ] Tokens com rotação; refresh revogável; nada sensível em client-side
- [ ] Prova de posse (OTP/link único) em operação crítica
- [ ] Teste "rota sem token = 401" no CI para TODA rota pública-interna

## I — Input & injeção
- [ ] SQL sempre parametrizado/ORM; nenhuma concatenação com input
- [ ] Validação declarativa na fronteira (schema), não espalhada
- [ ] Saída encodificada por contexto (HTML, JS, CSS, query); CSP presente
- [ ] Headers de segurança: HSTS, X-Content-Type-Options, Referrer-Policy, frame-ancestors
- [ ] Upload: tipo + tamanho + nome normalizado; fora de caminho executável; servido com Content-Disposition
- [ ] Limites de tamanho em corpo de request, profundidade de objeto e duração de parse (zip bomb/ReDoS)

## C — Criptografia & transporte
- [ ] TLS 1.2+ em toda comunicação (incl. serviço a serviço em rede não isolada)
- [ ] Senhas: Argon2/bcrypt (MD5/SHA1 puro = P0)
- [ ] Chaves gerenciadas centralmente; rotação sem downtime; KMS/HSM onde há dado sensível
- [ ] Aleatoriedade criptográfica do stdlib (crypto/secrets), nunca Math.random()/rand comum
- [ ] JWT: alg esperado FIXADO (jamais aceitar `none`), iss/aud/exp validados, kid restrito

## B — Borda & API
- [ ] Rate limit + quota + timeout + limite de payload
- [ ] CORS restrito por origem (NUNCA `*` em rota autenticada)
- [ ] WAF ou equivalente em superfície pública
- [ ] Breaking change de API só com nova versão + janela de overlap
- [ ] Webhook: origem assinada (HMAC + timestamp + proteção de replay), não só "o IP é seu"
- [ ] Host header: normalizado na borda; fluxos com link (reset, convite) usam URL canônica

## F — Infraestrutura
- [ ] Menor privilégio de IAM: identidade própria por workload, escopo enxuto
- [ ] Segmentação de rede; banco nunca exposto
- [ ] Containers: non-root, imagem mínima, FS read-only quando possível, sem docker.sock
- [ ] Healthchecks reais (liveness/readiness), circuit breaker, kill-switch por feature
- [ ] Host imutável (imagem/IaC); nenhum fix a mão em produção
- [ ] Superfícies de dev DESLIGADAS em produção (/debug, /actuator, playground, source maps, .git/.env)

## O — Observabilidade de segurança
- [ ] Log estruturado centralizado, com request-id de correlação
- [ ] Audit log imutável para ação sensível (auth, dinheiro, permissão)
- [ ] Alertas de anomalia: login falho, 5xx, p99, fila, erro de conexão
- [ ] Zero secret em log e stack trace (scrubber central — vazamento-dados.md §4)

## P — Processo
- [ ] CODEOWNERS + review obrigatória em core path
- [ ] Branch protection: PR + gates (lint, tipos, SAST, secret-scan, SCA, testes) bloqueiam merge — gates completos em `ci-cd.md` e workflow pronto em `assets/workflow-ci-gates.yml`
- [ ] Deploy por tag com canary + rollback < 5 min documentado
- [ ] Playbook de incidente (quem faz o quê em 30 min) e post-mortem sem culpa
- [ ] Dependência crítica patcheada em ≤ 7 dias (política escrita)
- [ ] Fase ofensiva repetida a cada release que tocar auth/dinheiro/tenancy

## V — Vazamento de dados (protocolo completo)
Este arquivo cobre "segredo e acesso"; o canal de fuga de dado vive em `vazamento-dados.md`:
inventário de classes de dado → auditoria dos **12 canais** (logs, erro, URL, header, cookie, cache,
analytics, terceiros, backup, superfície de dev, mensagens, DNS/cliente local) → testes negativos no CI
→ máscara PII brasileira → entradas para o jurídico/LGPD. Executar sempre que houver dado pessoal,
credencial, pagamento ou segredo de negócio.

## X — Código fortemente gerado por IA (passo obrigatório da blindagem)
Tratar DEFAULTS COMO HOSTIS. Antes de fechar a blindagem, varrer o resultado da Fase 0 ("cheiro de
código gerado por IA") linha a linha pela tabela de `ofensiva.md` §4: stub de auth, segredo com fallback,
CORS `*`, rota fora do middleware, debug flag, endpoint temporário, teste que mocka a segurança,
`latest` em imagem. Cada categoria > 0 gera 1 check de 60s registrado no relatório.

## STRIDE rápido (por superfície pública)
Para cada rota/webhook/worker: **S**poofing (quem autentica?), **T**ampering (input mutável onde?),
**R**epudiation (há trilha?), **I**nformation disclosure (stack trace fala demais?), **D**oS
(limite/timeout/parse bounded?), **E**levation (que privilégio o input compra?).
Saída: 1 linha por superfície × vetor, apontando a mitigação para um item deste checklist.
