# FEAT-NN — Tarefas

> Checklist executável, na ordem de dependência entre camadas (domínio → infraestrutura → serviços → UI). Cada tarefa cita os critérios que fecha. Marque `[x]` ao concluir, e registre aqui os desvios em relação ao `plan.md`.

## Implementação
- [ ] **T1** — <tarefa> (`src/...`) — fecha `RFxx-CA1`
- [ ] **T2** — <tarefa> — fecha `RFxx-CA2`
- [ ] **T3** — Testes de <...> citando `RFxx-CAn` no nome ou no comentário do teste

## Desvios em Relação ao Plano
<!-- Todo desvio precisa ser levado à spec vigente na Sincronização (não basta registrar no STATUS). -->
| Planejado | Implementado | Motivo | Doc a atualizar |
| :--- | :--- | :--- | :--- |
| <...> | <...> | <...> | <specs/... §x.y> |

## Definição de Pronto
- [ ] Todos os critérios `CA` do `spec.md` cobertos por teste automatizado (ou roteiro manual registrado)
- [ ] `pytest` passando por completo (registrar total de testes)
- [ ] **Sincronização:** delta do `spec.md` aplicado em `specs/REQUISITOS.md`; itens da seção 6 do `plan.md` e desvios acima aplicados em `specs/` e `adr/`
- [ ] `STATUS_PROJETO.md`: quadro atualizado e novo registro no histórico
- [ ] Executável gerado e validado (quando a FEAT afeta build, binários ou comportamento só verificável no `.exe`)
- [ ] Pasta do pacote movida para `docs/archive/<versão>/`
