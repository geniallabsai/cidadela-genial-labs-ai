# serverless-lambda

AWS Lambda + API Gateway via SAM — zero dependência, faturamento por fração de segundo.

## Quando usar
- Ecossistema AWS já presente (S3, SQS, DynamoDB, Cognito) — Lambda é a cola nativa.
- Eventos: upload de arquivo, fila, cron (EventBridge), trigger em outro serviço.
- Custo por uso importa mais que latência mínima (cold start Python ~300–800 ms).

## Quando NÃO usar
- Requisições longas (> 15 min, teto absoluto da Lambda) ou streaming contínuo.
- Estado entre chamadas: efêmero `/tmp` tem ~512 MB e morre com o container.
- Times sem CI na AWS: IAM/permissions são o coração do deploy (template incluso).

## Rotas deste pack
| Rota | Método | O que faz |
|---|---|---|
| `/saude`, `/` | GET | health probe |
| `/eco` | GET/POST | devolve o que recebeu (valida contrato) |
| — | OPTIONS | CORS automático |

Chave opcional: defina `API_KEY` na função e envie `x-api-key` (401 senão).

## Deploy
```bash
# opção A — SAM (recomendado; valida o template no deploy)
sam build && sam deploy --guided
# opção B — manual
zip -r app.zip handler.py
aws lambda create-function --function-name genial-exemplo --runtime python3.12 \
  --handler handler.lambda_handler --zip-file fileb://app.zip --timeout 10
```
Teste local sem AWS: `python -c "import handler; print(handler.lambda_handler({'path':'/saude','httpMethod':'GET'}, None))"`
