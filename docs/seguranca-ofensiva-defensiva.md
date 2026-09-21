# Segurança: atacar antes do atacante

A reclamação mais comum contra produto feito com IA é a mesma: "vai vazar dado, a arquitetura
quebra, o pipeline não segura". A resposta do Genial Labs não é argumento — é processo executado
e registrado: **fase ofensiva** (probes rodadas em staging), **12 canais de vazamento
auditados um a um** e **gates no CI que bloqueiam merge**.

## Ofensiva (Fase 5 da Cidadela)

1. **Árvore de ataque** nas 3 superfícies mais sensíveis (auth, dinheiro, dados por ID):
   objetivo explícito ("com a conta de teste T1, conseguir dado de T2 ou virar admin"),
   timebox de 2h por superfície.
2. **Primeira hora do atacante** — probes prontas: superfícies ocultas (`.env`, `.git/config`,
   `/actuator`, swagger, source maps expondo fonte), CORS de origem maliciosa, IDOR por
   incremento/troca de tenant, JWT (`alg:none`, HS256 com secreto fraco, exp longo),
   host-header injection no link de reset de senha, SSRF na metadata da cloud
   (`169.254.169.254`), race condition em saque/desconto, webhook forjado sem assinatura,
   mass assignment (`"role":"admin"` no body), zip bomb, ReDoS, enumeração por timing.
3. **Triagem do cheiro de código-IA** — o inventário detecta 12 categorias (eval/pickle,
   CORS `*`, debug ligado, JWT fraco/padrão, SQL por concatenação, innerHTML, segredo em log,
   catch vazio, `any`, TODO pendente, webhook sem assinatura, `.map` servido); cada categoria
   > 0 exige o check de 60s correspondente.
4. **Severidade por regra única** — P0 (explorável agora, sem acesso especial, impacto em
   dado/credencial/execução) **congela tudo até corrigir**; P1 (conta comum + impacto contido);
   P2 (endurecimento). Toda descoberta vira linha do relatório: vetor + entrada + saída + mitigação.

## Defesa em camadas (Fase 6)

Camadas S/D/A/I/C/B/F/O/P (rede/borda, segredos, identidade/autenticação, autorização, dados,
integrações, frontend, observabilidade, processo) no framework **OWASP ASVS** (mínimo L1,
alvo L2), com **STRIDE curto** por superfície pública. Multi-tenant ganha as dimensões
**T1–T6** (isolamento de esquema, RLS, chaves compostas, backup granular, purge, cláusula de
saída); T2 ≤ 4 ⇒ risco nº 1 é vazamento entre tenants.

## Os 12 canais de vazamento (todos auditados, status limpo/achado/não avaliado)

1. logs e stack trace · 2. páginas de erro · 3. URL/query string · 4. headers de resposta ·
5. cookies · 6. cache (browser/CDN/API) · 7. analytics/telemetria/tracker de erro ·
8. terceiros (SDK, pagamento, e-mail) · 9. backup/dump/export · 10. superfícies de dev em
produção (debug, actuator, playground, source maps, `.env`/`.git` servidos) ·
11. mensagens (e-mail/SMS/push com token/TTL/link) · 12. DNS/subdomínio e cliente local
(localStorage, http misturado em WebView).

Cada canal tem: como detectar (grep + probe + teste manual) e a correção padrão. E cada classe
de dado exige **teste negativo no CI** — ex.: "usuário A lê a resposta sem dados de B",
"log de /relatorio não contém CPF de B", "sem token ⇒ 401 sem campo de perfil no body".

## PII brasileira e LGPD

Máscara padrão (scrubber central único, nunca máscara espalhada): CPF `***.***.***-**12`,
CNPJ `****.***.***/****-**34`, telefone `(##) *****-****`, e-mail `j***@dominio.com`,
cartão `**** **** **** 1234`. Entradas para o jurídico (não substitui parecer): base legal do
tratamento por classe (art. 7), eliminação coberta pelo teardown testado, minimização coberta
pelo inventário, incidente com risco ⇒ avaliação de comunicação dentro dos prazos.

## Gates de CI que bloqueiam merge (não avisam)

| Gate | Ferramenta exemplo |
|------|--------------------|
| Secrets no código **e no histórico** | gitleaks / trufflehog |
| Dependências vulneráveis (CRITICAL/HIGH runtime) | trivy fs / osv-scanner / npm audit |
| SAST (regras novas ou em caminho modificado) | semgrep / bandit / gosec / eslint-plugin-security |
| Teste do arquivo modificado (cobertura delta) | runner nativo |
| Imagem de container (non-root, sem `:latest`, CRITICAL fix) | trivy image / grype |
| Update sem aprovação humana | renovate / dependabot + review |
| Review no core | branch protection + CODEOWNERS |
| Build reproduzível | lockfile commitado, comando `ci`/lock |

Workflow pronto: `assets/workflow-ci-gates.yml` (o `genial init` já coloca em
`.github/workflows/gates.yml`). Práticas de deploy: tag imutável, canary 1→10→100% por SLI,
rollback automático < 5 min, freeze documentado, **OIDC no CI** (zero chave longa morando em
variável de ambiente), smoke sintético pós-deploy.

## Como saber que está blindado

Três provas concretas, não promessa: (1) seção ofensiva do relatório com evidências
(requisição + resposta); (2) os 12 canais marcados limpo/achado com o achado corrigido ou
planejado; (3) CI vermelho de verdade quando você quebra algo (tente commitar um `token =
"..."` com gitleaks ligado). E o rollback foi exercitado pelo menos uma vez antes de precisar.
