# Protocolo de Cirurgia (Strangler-Fig) — sem parar o paciente

## 8 regras de ouro
1. **Rede antes da bisturi:** testes de caracterização do comportamento atual da costura ANTES de qualquer mudança.
2. **Flag é lei:** comportamento novo só existe atrás de feature flag; flag desligada = comportamento antigo (ou diff documentado e aceite).
3. **Rollback < 5 min:** escrito, ensaiado, e disponível durante toda a janela de cutover.
4. **Commit = estado entregável:** nenhum PR deixa CI vermelho nem remove o caminho antigo no mesmo merge em que nasce o novo.
5. **Um módulo por PR:** blast radius limitado; revisão cabível.
6. **Observabilidade na costura:** toda fronteira nova ganha log estruturado + métrica + trace ANTES do cutover.
7. **Dados por último, expand → migrate → contract:** nada destrutivo em voo.
8. **Parar custa barato:** erro budget estourando ou rollback necessário ⇒ congela a cirurgia, volta ao checkpoint, diagnostica.

## Os 7 passos (repetir por costura, do menor para o maior risco)
| Passo | Ação | Saída verificável |
|-------|------|-------------------|
| 1 Congelar | Documentar comportamento atual da costura; bloquear nova feature nela | Lista de comportamentos + testes de caracterização verdes |
| 2 Rede | CI verde no módulo; backup/restauração de dados exercitado; infra de flag pronta (se não existir) | Backup restaurado com sucesso; suíte verde |
| 3 Abstração | Criar interface/porta na fronteira; implementação antiga passa a implementar a porta | Compila; testes antigos continuam verdes |
| 4 Sombra | Implementação nova atrás da flag; tráfego sombreado compara saídas | Diff de sombra abaixo do limite acordado |
| 5 Cutover | Flag sobe gradual: 1% → 10% → 100%; SLIs de olho em cada patamar | Erro/latência estáveis |
| 6 Consolidação | 1 ciclo de release completo a 100% sem incidente | Zero rollback na janela |
| 7 Descomissionar | PR separada remove caminho antigo + flag + código morto | Sem código morto; suíte de regressão passa |

## Migration de dados
- **Expand:** coluna/tabela nova tolerante a nulo; escrita dupla onde necessário.
- **Migrate:** backfill assíncrono, idempotente e retomável.
- **Contract:** remover o antigo somente após 1 ciclo completo de leitura pela nova via.
- Entre expand e contract, **nenhuma** migration destrutiva.

## "Não quebra nada" — definição operacional
- Todo commit: CI verde e lançável.
- Flag desligada: comportamento anterior (ou diff documentado e aceito).
- Rollback documentado e < 5 min.
- Error budget do período intacto.
- Consumidor externo (API/chamador) não percebeu — ou a mudança breaking foi versionada e comunicada.

## Ordem dos cortes
Costuras de leitura primeiro → escritas sem valor financeiro → núcleo transacional por último. Cada corte concluído gera seu ADR.
