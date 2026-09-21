# Plataforma: da VPS à AWS sem parar produção

Princípio da casa: **o menor degrau que segura**. Infra mais complexa que o problema é pagar
catedral para o que o galinheiro resolve — mas sistema que sobe a escada sem saber como chega
no topo quebrado.

## A escada (subir só com sinal medido)

| Degrau | Quando sustenta | Sinal para subir |
|--------|-----------------|------------------|
| Processo em VPS (systemd + Caddy + Postgres) | até ~2 serviços, tráfego modesto | incidentes/tempo de deploy passam a custar mais que o próximo degrau |
| Docker + Compose (VPS ou gerenciada) | time pequeno multi-serviço, paridade local | ambientes reais exigindo mais que "1 VPS" |
| Containers gerenciados (ECS Fargate / App Runner / Cloud Run) | multi-ambiente sem cluster K8s próprio | muitos serviços + necessidade de plataforma |
| K8s (EKS/GKE/AKS) | muitos serviços + time de plataforma (pessoas, não só YAML) | custo operacional do cluster < custo da dor atual |
| Serverless à parte (Lambda/Functions) | jobs bursty/assíncronos | complementa qualquer degrau acima |

`genial deploy` mede automaticamente em qual degrau seu projeto está (0–5) e indica o próximo
passo com a seção exata desta referência.

## Baseline por serviço (vale em qualquer degrau)

Imagem non-root com digest fixo (nunca `:latest`) · healthchecks liveness/readiness ·
configuração separada de código (env/configmap) · segredos em vault/KMS (jamais no compose de
produção) · recursos limitados (CPU/RAM) · log estruturado JSON em stdout · imagem varrida
(trivy) no CI.

## VPS (o degrau sábio)

Unidade systemd com `Restart=always`, `User=app`, `ProtectSystem=strict`, `NoNewPrivileges`;
Caddy ou Traefik para TLS automático; uFW + fail2ban; backup diário (`pg_dump`) + cópia offsite
+ **restore testado**; uptime + prometheus/node_exporter; janela de atualização escrita.

## Docker/Compose (o degrau do time pequeno)

Dockerfile multi-stage + `.dockerignore`; profiles dev/prod; banco com named volume +
healthcheck; rede interna separada da pública; sem segredo duro (`.env.example` versionado);
script de backup agendado. O `genial init` entrega tudo isso pronto.

## Kubernetes mínimo saudável (quando a escada exigir)

Namespace por ambiente + **pod security restricted** (non-root, drop ALL caps, ROFS quando
possível) · requests/limits em tudo · HPA por métrica medida · PDB nos serviços críticos ·
NetworkPolicy default deny entre namespaces e allow só o necessário · secrets via
ExternalSecrets/KMS · ingress com TLS + rate limit · rollout canary por peso · GitOps (ArgoCD)
quando passar de dois ambientes.

**Anti-padrões:** K8s para 3 serviços e 1 pessoa; operador caseiro antes da necessidade;
Helm chart que não roda no CI.

## AWS (o caminho prático)

Começo recomendado: **App Runner ou ECS Fargate** (primeiro container) + **RDS PostgreSQL**
(Multi-AZ só com requisito real) + ElastiCache + S3 (versioning + lifecycle) + SQS/SNS para o
assíncrono + CloudFront/WAF na frente. Regras: **IAM via OIDC federation para o CI (zero chave
longa)**; **Terraform desde o dia 1** (mesmo que sejam 5 recursos); Cost Explorer com alerta;
região planejada para residência de dados (LGPD); backup RDS (snapshots + PITR); **failover
exercitado uma vez antes de precisar**. Cláusula de saída (portabilidade): PostgreSQL em SQL
padrão, S3 em protocolo compatível, fila em protocolo padrão — portabilidade é cláusula
contratual, não torcida.

## Deploy zero-downtime (padrão)

Rolling com readiness (pod novo só recebe tráfego saudável) · banco em **expand → contract** ·
canary 1→10→100% por SLI (5xx + p99) · smoke sintético pós-deploy (login, leitura, escrita
descartável) nas primeiras 2 min · freeze windows documentados · rollback < 5 min com 1 clique
(tag anterior sempre pronta).

## Observabilidade e finops

SLO por serviço (disponibilidade + latência) · alerta de burn-rate (não só "subiu 5xx") ·
métricas de canary · dashboard de **custo por serviço/ambiente** · trilha de deploy registrada
pelo CI (quem subiu qual tag quando).

## IA no produto (padrões avançados)

- **Abstração:** uma interface LLM na aplicação (prompt, modelo, timeout, fallback) — trocar de
  fornecedor não toca o domínio.
- **Resiliência:** timeout + retry com backoff + fallback para modelo secundário; cache só para
  pergunta que permite.
- **Custo:** teto de tokens por usuário/dia + alerta; prompt e resposta logados truncados e
  mascarados (PII).
- **Regressão:** conjunto de **evals golden no CI** (resposta piorou = CI vermelho); prompt é
  código: versionado com changelog.
- **Human-in-the-loop:** IA sugere, humano confirma em ação de alto risco (dinheiro, exclusão, envio).
- **Privacidade:** contrato definindo se PII sai do ambiente (DPA, região); opção de modelo
  local quando a classe de dado pedir.
