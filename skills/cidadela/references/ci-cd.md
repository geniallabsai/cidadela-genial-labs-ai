# CI/CD — gates que fazem o projeto ser levado a sério

Para quem não é engenheiro de software, o pipeline é o argumento que cala a zoeira: "isso roda em CI com
gate de segurança OBRIGATÓRIO". Sem pipeline, nenhuma blindagem manual sobrevive à segunda pessoa que mexe
no código.

## 1. Pipeline mínimo (estágios na ordem)
build → testes (unit + integração) → qualidade (lint + type-check) → segurança (secrets, SCA, SAST, imagem)
→ empacotar (tag imutável + SBOM + assinatura) → promover (dev → staging → prod) → smoke pós-deploy → rollback automático.
Regra: estágio de segurança **bloqueia**, não avisa. Aviso é coisa de chat.

## 2. Gates obrigatórios
| Gate | Ferramenta (exemplo) | O que bloqueia o merge |
|------|----------------------|------------------------|
| Secrets no código E no histórico | gitleaks, trufflehog | qualquer match em HEAD ou no histórico |
| Dependência vulnerável | trivy fs, osv-scanner, npm audit, govulncheck | CRITICAL/HIGH com fix disponível em caminho de runtime |
| SAST | semgrep, eslint-plugin-security, bandit, gosec, rubocop-security | regra P0/P1 nova ou em caminho modificado |
| Teste do arquivo modificado | runner nativo + cobertura de delta | arquivo tocado sem teste verde que o cobre |
| Imagem de container | trivy image, grype | CRITICAL sem fix; tag `latest`; processo root |
| Aprovação de dependência | renovate/dependabot + review humano | merge de update sem review |
| Review | branch protection + CODEOWNERS | merge sem review no core (auth, money, tenancy) |
| Build reproduzível | lockfile commitado + comando `ci`/lock + imagem de build fixa | `npm install` solto, `pip install` sem pin |

## 3. Práticas de deploy (o que separa amador de profissional)
1. **Tag é o artefato:** ambientes promovem tag (`v1.4.2`), nunca ponta de branch flutuante.
2. **Canary:** 1% → 10% → 100% com SLI de erro (5xx + p99) em cada patamar; estourou ⇒ volta sozinho.
3. **Rollback < 5 min:** o alvo anterior fica pronto para 1 clique (ou é automático por métrica) durante toda a janela.
4. **Freeze:** janela documentada antes de feriado/faturamento/release grande — escrita, não cultural.
5. **Imutabilidade:** nada de SSH para "consertar" produção; conserto é commit novo + redeploy.
6. **Secrets no CI:** OIDC federation (CI → cloud) — zero chave longa morando em variável de ambiente do pipeline.
7. **Smoke pós-deploy:** 3–5 requests sintéticos (login, 1 leitura, 1 escrita descartável) nas primeiras 2 min.

## 4. Observabilidade pós-deploy (o gate continua vivo depois do merge)
- Alerta de burn-rate do error budget (não só "subiu 5xx").
- Métricas de segurança: segredo novo detectado, dependência nova sem review, rota nova sem teste (detectar no diff).
- Dashboards: 1 por SLO + 1 por tenant (quando multi-tenant) + 1 financeiro (quando toca dinheiro).

## 5. Configuração mínima
- Workflow de referência: `assets/workflow-ci-gates.yml` → copiar para `.github/workflows/` e adaptar os blocos por linguagem.
- Branch protection na `main`: exigir PR + status checks (toda a tabela §2) + CODEOWNERS.
- Tags protegidas (prefixo `v` só criada pela CI que passou em tudo).
- GitLab CI / CircleCI / Jenkins: mesmo mapa de gates — o gate é o conceito, não a ferramenta.

## 6. Os 10 checkboxes do "projeto levado a sério"
1. Lockfile commitado e CI usando o comando `ci`/lock
2. CI verde obrigatório para merge (badge no README)
3. Secret-scan no histórico, não só na HEAD
4. SCA com política escrita (CRITICAL bloqueia)
5. Teste de integração na fronteira de auth e de tenancy
6. Deploy por tag, com canary e rollback < 5 min
7. CODEOWNERS em auth/dinheiro/tenancy
8. SBOM por release (CycloneDX/SPDX)
9. Runbook de incidente escrito (quem faz o quê em 30 min)
10. Revisão trimestral de segurança = rodar a fase ofensiva desta skill de novo
