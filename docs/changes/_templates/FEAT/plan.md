# FEAT-NN — Plano Técnico

> Escrito **depois** que o `spec.md` foi aprovado. Descreve como implementar o delta sem contrariar `docs/specs/ARQUITETURA.md` e `docs/specs/TECNICO.md`; o que mudar nesses documentos fica listado na seção 6.

## 1. Resumo da Abordagem
<Dois ou três parágrafos: a solução e por que ela foi escolhida.>

## 2. Impacto por Camada

| Camada | Arquivos | Mudança |
| :--- | :--- | :--- |
| Domínio (`src/domain/`) | <...> | <...> |
| Serviços (`src/services/`) | <...> | <...> |
| Infraestrutura (`src/infrastructure/`) | <...> | <...> |
| Apresentação (`src/ui/`) | <...> | <...> |

Restrições que continuam valendo: domínio, serviços e infraestrutura **não importam PySide6** (RNF05-CA3); o `AppState` só é alterado na thread principal.

## 3. Contrato do `state.json`
- [ ] **Sem mudança de schema.**
- [ ] **Mudança compatível:** novo campo opcional `<campo>` (padrão `<valor>`); versão `1.X` → `1.Y`.
- [ ] **Mudança incompatível:** <descrição>; versão `X.0` → `Y.0`; migração `<função>` com teste a partir de um JSON da versão anterior.

Ver `ARQUITETURA.md` §3.3.

## 4. Decisões Arquiteturais
- [ ] Nenhuma decisão nova.
- [ ] Nova ADR: `docs/adr/ADR-NN-<slug>.md` — <título>.
- [ ] ADR substituída: ADR-NN → `Substituída por ADR-MM`.

## 5. Estratégia de Testes
* **Unitários:** <o que cobre cada critério `RFxx-CAn`>.
* **UI (offscreen):** <...>.
* **Fixtures novas:** <se houver; gerar via `tests/fixtures/build_fixtures.py`>.
* **Manual / executável:** <roteiro, quando o critério só pode ser verificado no `.exe`>.
* **Desempenho:** <medição exigida, se tocar em RNF05>.

## 6. Atualizações de Spec Previstas (checklist da Sincronização)
- [ ] `specs/REQUISITOS.md`: <RFs adicionados / modificados / obsoletos>
- [ ] `specs/ARQUITETURA.md`: <seções>
- [ ] `specs/TECNICO.md`: <seções>
- [ ] `adr/`: <ADRs>
- [ ] `README.md` (raiz): <funcionalidades / atalhos, se visíveis ao usuário>

## 7. Riscos e Mitigações
| Risco | Mitigação |
| :--- | :--- |
| <...> | <...> |
