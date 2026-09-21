# Plataforma — Docker, Compose, Kubernetes, VPS e AWS (a escada do deploy)

Princípio: **o menor degrau que segura**. Infra mais complexa que o problema é pagar catedral para o
que o galinheiro resolve — mas sistema que sobe a escada sem saber como chega no topo quebrado.

## 1. A escada (subir só com sinal medido)
| Degrau | Quando sustenta |
|--------|-----------------|
| Processo em VPS (systemd + Caddy + Postgres) | até ~2 serviços, tráfego modesto, 1 pessoa dona |
| Docker + Compose (VPS ou gerenciada) | time pequeno multi-serviço, paridade local |
| Containers gerenciados (ECS Fargate / App Runner / Cloud Run) | multi-ambiente real sem cluster K8s próprio |
| K8s (EKS/GKE/AKS) | muitos serviços + time de plataforma (pessoas, não só YAML) |
| Serverless à parte (Lambda/Functions) | jobs bursty/assíncronos — complementa qualquer degrau acima |
Sinal para subir: custo operacional do degrau atual (incidentes, tempo de deploy, pessoas) passa a
custar mais que o próximo degrau. Subir por "padrão" é dívida, não evolução.

## 2. Baseline por serviço (vale em qualquer degrau)
Imagem non-root com digest fixo (nunca `:latest`); healthchecks (liveness/readiness); configuração
separada de código (env/configmap); segredos em vault/KMS (jamais em compose em produção); recursos
limitados (CPU/RAM); log estruturado JSON em stdout; imagem varrida (trivy) no CI.

## 3. VPS (degrau sábio)
Unidade systemd: `Restart=always`, `User=app`, `ProtectSystem=strict`, `NoNewPrivileges=true`;
Caddy ou Traefik para TLS automático; uFW + fail2ban; backup diário (pg_dump) + cópia offsite +
**restore testado**; uptime + node_exporter/prometheus; janela de atualização escrita.

## 4. Docker/Compose (time pequeno)
Dockerfile multi-stage + `.dockerignore`; profiles dev/prod no compose; banco com named volume +
healthcheck; rede interna separada da pública (frontend/backend); sem segredo duro (env +
`.env.example`); script de backup (pg_dump) agendado no CI ou cron da VPS.

## 5. Kubernetes mínimo saudável (quando a escada exigir)
Namespace por ambiente + **pod security restricted** (non-root, drop ALL caps, ROFS quando possível);
requests/limits em tudo; HPA por métrica medida; PDB nos serviços críticos; NetworkPolicy default
deny entre namespaces e depois allow só o necessário; secrets via ExternalSecrets/KMS; ingress com
TLS + rate limit; rollout canary/peso; GitOps (ArgoCD) quando passar de dois ambientes.
Anti-padrões: K8s para 3 serviços e 1 pessoa; operador caseiro antes da necessidade; Helm fora do CI.

## 6. AWS (caminho prático)
Começo: **App Runner ou ECS Fargate** (primeiro container) + RDS PostgreSQL (Multi-AZ só com
requisito real) + ElastiCache + S3 (versioning + lifecycle) + SQS/SNS para assíncrono + CloudFront/WAF
na frente. **IAM via OIDC federation para o CI (zero chave longa);** Terraform desde o dia 1 (mesmo
5 recursos); Cost Explorer com alerta; região planejada para residência de dados (LGPD — vazamento-
dados.md §1); backup RDS (snapshots + PITR); **failover exercitado uma vez antes de precisar**.
Cláusula de saída (portabilidade): PostgreSQL em SQL padrão, S3 em protocolo compatível, SQS em
protocolo padrão — portabilidade é cláusula contratual (multitenancy.md §5).

## 7. Deploy zero-downtime (padrão da casa)
Rolling com readiness (pod novo só recebe tráfego saudável); banco em **expand → contract**
(plano-cirurgia.md); canary 1→10→100% por SLI (erro 5xx + p99); **smoke sintético pós-deploy**
(login, leitura, escrita descartável) nas primeiras 2 min; freeze windows documentado; rollback
< 5 min por 1 clique (tag anterior pronta).

## 8. Observabilidade da plataforma
SLO por serviço (disponibilidade, latência); alerta de burn-rate; métricas de canary; dashboard de
custo (finops) por serviço/ambiente; trilha de deploy (quem subiu qual tag quando — registro do CI).

## 9. IA no produto (padrões avançados)
- **Abstração**: uma interface LLM na aplicação (prompt, modelo, timeout, fallback) — trocar de
  fornecedor não toca no domínio.
- **Resiliência**: timeout + retry com backoff + fallback de modelo secundário; cache só para
  pergunta que permite.
- **Custo**: teto de tokens por usuário/dia + alerta; prompt e resposta logados truncados e mascarados
  (PII — vazamento-dados.md §7).
- **Regressão**: conjunto de **evals golden no CI** (resposta piorou = CI vermelho); prompt é código:
  versionado com changelog.
- **Human-in-the-loop**: IA sugere, humano confirma em ação de alto risco (dinheiro, exclusão, envio).
- **Privacidade**: contrato definindo se PII sai do ambiente (DPA, região); opção de modelo local
  quando a classe de dado pedir.
