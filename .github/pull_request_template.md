## Pacote
<!-- FEAT-NN ou FIX-NN, com link para a pasta do pacote -->
* **Pacote:** `FEAT-NN` / `FIX-NN` — `docs/changes/FEAT-NN/` ou `docs/changes/FIX-NN/`
* **Tipo de FIX (se aplicável):** A (código diverge da spec) / B (spec corrigida)

## Resumo
<!-- O que muda para o usuário e por quê. -->

## Critérios cobertos
<!-- Liste os RFxx-CAn / RNFxx-CAn fechados e onde estão os testes. -->
- `RFxx-CAn` — `tests/...::test_...`

## Checklist SDD (Definição de Pronto)
- [ ] `spec.md` (ou `fix.md`) aprovado antes do código
- [ ] Testes novos citam o critério que cobrem; FIX tem teste de regressão que falha sem a correção
- [ ] `pytest` passando por completo — total: ___ testes
- [ ] **Sincronização:** delta aplicado em `docs/specs/`; desvios do plano levados à spec
- [ ] ADR criada ou substituída (se houve decisão arquitetural)
- [ ] `state.json`: sem mudança de schema **ou** versão incrementada + migração testada (`ARQUITETURA.md` §3.3)
- [ ] `docs/STATUS_PROJETO.md`: quadro atualizado + novo registro no histórico
- [ ] Próximos IDs livres atualizados em `docs/README.md`
- [ ] Pacote movido para `docs/archive/<versão>/`
