# Vazamento de dados — auditoria em 12 canais

O argumento contra "projeto de IA" quase sempre é o mesmo: vazamento. Este protocolo existe para que, antes
de qualquer entrega, TODO canal por onde dado escapa seja auditado, evidenciado e corrigido. Executar sempre
que o produto tocar dado pessoal (LGPD), credencial, pagamento, saúde ou segredo de negócio.

## 1. Inventário de dados (antes de caçar canal)
| Classe | Exemplos | Regra de tratamento |
|--------|----------|---------------------|
| PII | nome, e-mail, CPF/CNPJ, telefone, endereço, IP | máscara por padrão em log/resposta; minimizar coleta |
| Credencial | senha, hash, token, sessão, refresh, API key | nunca fora de storage cifrado; rotação documentada |
| Financeiro | cartão, Pix, boleto, fatura, saldo | não guardar mais dígitos do que o necessário (tokenizador para PAN) |
| Saúde/jurídico | prontuário, contrato, processo, confessionário | isolamento próprio (schema/banco) — ver multitenancy.md |
| Negócio | preço, margem, roadmap, base de clientes | mesmo rigor que PII |

Para cada tabela/modelo relevante responder: quem cria, quem lê, quem apaga (teardown), onde replica
(backup, analytics, 3º). O que não apareça em lugar nenhum do inventário é achado por definição.

## 2. Os 12 canais de fuga (auditar um a um; status = limpo | achado | não avaliado)
1. **Logs e stack trace** — grep de PII/credencial em statements de log; induzir erro 500 real e ler a resposta + o log. Correção: allowlist de campos por logger; scrubber central (regex de CPF/CNPJ/e-mail/tel/`AKIA`/`sk_`); nunca logar body de requisição autenticada.
2. **Páginas de erro** — 500 não pode exibir trace, nome de serviço interno, versão, SQL. Correção: handler global → mensagem genérica + request-id; detalhe vai para o log (canal 1).
3. **URL / query string** — token, e-mail, CPF em GET (vazam em log de proxy, Referer, prints, histórico). Correção: estado sensível em header/cookie/body; link externo → token opaco, de uso único, com TTL.
4. **Headers de resposta** — `Server`, `X-Powered-By`, nome interno, `WWW-Authenticate` reveladora, CORS `*` em rota autenticada. Correção: strip na borda; pacote de headers de segurança por padrão.
5. **Cookies** — PII no valor (base64 NÃO é cifrar), falta de HttpOnly/Secure/SameSite, path amplo. Correção: cookie opaco; flags corretas; path restrito.
6. **Cache (browser/CDN/API)** — resposta autenticada com `Cache-Control: public`; CDN sem `Vary: Cookie`; key de API sem tenant/role. Correção: `private, no-store` em rota autenticada; purge no logout; key de cache composta (tenant+role).
7. **Analytics / telemetria / tracker de erro** — e-mail e ID de usuário nos eventos; breadcrumb com segredo. Correção: whitelist de propriedades, scrubber antes do envio, opt-in LGPD para não essencial.
8. **Terceiros (SDK, pagamento, e-mail)** — o que o SDK envia, retenção deles, sub-processadores, DPA. Correção: inventário provedor × dado; DPA assinado; caminho sem SDK quando possível.
9. **Backup / dump / export / migration** — `.sql`/`.csv` com PII em disco local ou de dev; dump colado em grupo; export sem expiração. Correção: backup cifrado, acesso escopado, retenção, prova de exclusão.
10. **Superfícies de dev em produção** — `/debug`, `/actuator`, playground GraphQL, **source maps (.map)** acessíveis, `.git`/`.env` servidos, pino de deploys. Correção: desligar em produção (não esconder); prova com probe anônima.
11. **Mensagens (e-mail/SMS/push)** — link de reset sem assinatura/TTL/single-use; CPF no assunto; cartão no corpo; deep link revelando ID interno. Correção: token assinado + TTL + uso único; template sem dado bruto.
12. **DNS/subdomínio e cliente local** — subdomínio por tenant (catálogo de clientes vaza por DNS); token em `localStorage` de app híbrido; http misto em WebView. Correção: tenant por claim validada (não por hostname público); storage seguro; https-only + HSTS.

## 3. Testes negativos obrigatórios no CI
Regra: se existe autenticação OU tenancy, existe teste que FALHA O BUILD quando dado cruza.
```
- usuário A logado → GET /dados → resposta contém dados A e NÃO contém dados B
- leitura de /relatório → log capturado não contém CPF de B
- request sem token → 401 e body não contém nenhum campo de perfil
- tenant 1 acessa /api/x?id=<id-do-tenant-2> → 404 (não 200, não 403 que revela existência)
- webhook forjado sem assinatura → rejeitado (4xx), não processado
```
Mínimo por produto: 1 teste por classe de dado × superfície pública. Nome do teste citando o canal (ex.: `test_log_nao_contem_cpf_outro_tenant`).

## 4. Máscara de PII (padrão BR) — scrubber ÚNICO central
| Dado | Padrão (indicativo) | Máscara |
|------|--------------------|---------|
| CPF | `\d{3}\.\d{3}\.\d{3}-\d{2}` | `***.***.***-**12` |
| CNPJ | `\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}` | `****.***.***/****-**34` |
| Telefone BR | `(?:\+?55)?\s?\(?\d{2}\)?\s?9\d{3}-\d{4}` | `(##) *****-****` |
| E-mail | `\w+@\w+\.\w+` | `j***@dominio.com` |
| Cartão | `\d{16,19}` | `**** **** **** 1234` |
Uma função de máscara, todos os loggers/respostas passam por ela — nunca máscara espalhada por função.

## 5. Enquadramento (entradas para o jurídico/LGPD)
- Base legal do tratamento por classe (art. 7º) — o inventário §1 é a matéria-prima.
- Direito de eliminação ⇒ o teardown (multitenancy.md §6.10) precisa cobrir backup e export, não só a tabela.
- Minimização ⇒ tudo que entra no inventário precisa de justificativa de uso escrita.
- Incidente com risco ⇒ a engenharia entrega linha do tempo técnica (quando entrou, quando saiu, quem viu)
  — o resto é papelada; a linha do tempo só existe se o audit log (blindagem §O) estiver ativo.
Esta seção lista o que a engenharia garante para o jurídico ter material; não substitui parecer.
