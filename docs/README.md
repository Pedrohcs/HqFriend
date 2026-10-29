# Documentação do HqFriend — Processo SDD

O HqFriend é desenvolvido com **Spec-Driven Development (SDD)**: nenhuma mudança de comportamento entra no código sem antes estar na spec, e a spec vigente sempre descreve o código da branch `main`.

A documentação separa **o que o sistema é** (spec vigente, atualizada a cada entrega) de **o que está mudando** (um pacote por FEAT ou FIX, arquivado ao final).

## Estrutura

```
docs/
├── README.md               # este guia
├── STATUS_PROJETO.md       # quadro de FEATs/FIXes + histórico (só acréscimos)
├── specs/                  # SPEC VIGENTE — sempre igual ao código da main
│   ├── REQUISITOS.md       # RF/RNF/US com critérios de aceite próprios (RFxx-CAn)
│   ├── ARQUITETURA.md      # camadas, contrato e migração do state.json, fluxos
│   └── TECNICO.md          # stack, algoritmos, UI, empacotamento (regras, não cópia de código)
├── adr/                    # uma decisão arquitetural por arquivo (+ _TEMPLATE.md)
├── changes/                # PACOTES EM ANDAMENTO
│   ├── _templates/
│   │   ├── FEAT/           # spec.md, plan.md, tasks.md
│   │   └── FIX/            # fix.md
│   └── FEAT-NN-<slug>/     # um pacote por mudança
└── archive/                # pacotes concluídos, por versão (somente leitura)
    └── v1.0/               # backlog original FEAT-01..13
```

## Próximos IDs Livres

Atualize esta tabela ao reservar um ID (IDs **nunca** são reaproveitados, nem de itens cancelados ou obsoletos).

| Tipo | Próximo | Onde fica |
| :--- | :--- | :--- |
| Feature | `FEAT-14` | `changes/FEAT-14-<slug>/` |
| Correção | `FIX-01` | `changes/FIX-01-<slug>/` |
| Requisito funcional | `RF21` | `specs/REQUISITOS.md` §2 |
| Requisito não funcional | `RNF08` | `specs/REQUISITOS.md` §3 |
| História de usuário | `US14` | `specs/REQUISITOS.md` §4 |
| Questão de decisão | `QA-02` | `spec.md` do pacote → `specs/REQUISITOS.md` §6 |
| Decisão arquitetural | `ADR-09` | `adr/ADR-09-<slug>.md` |

## Ciclo de uma FEAT

| # | Etapa | Saída | Portão para avançar |
| :---: | :--- | :--- | :--- |
| 1 | **Especificar** | `changes/FEAT-NN-<slug>/spec.md` (copiado de `_templates/FEAT/`) com o **delta**: ADICIONADO / MODIFICADO / REMOVIDO | Todas as `QA-NN` decididas; delta aprovado |
| 2 | **Planejar** | `plan.md` (impacto por camada, `state.json`, ADRs, testes, specs a atualizar) e `tasks.md` | Plano revisado |
| 3 | **Implementar** | Código + testes na branch `feat/FEAT-NN-<slug>`; testes citam `RFxx-CAn`; desvios anotados em `tasks.md` | `pytest` passando por completo |
| 4 | **Sincronizar** | Delta aplicado em `specs/`, desvios levados à spec, ADRs criadas ou substituídas, `STATUS_PROJETO.md` atualizado | Spec vigente descreve o código da branch |
| 5 | **Arquivar** | Pacote movido para `archive/<versão>/`; merge na `main`; tag `v1.X` | — |

A etapa 4 faz parte da **Definição de Pronto**: uma FEAT com código pronto e spec desatualizada ainda está `em andamento`.

## Correções (FIX): classificar primeiro

| Situação | Tipo | O que fazer |
| :--- | :--- | :--- |
| A spec está correta e o código diverge dela | **FIX Tipo A** | `fix.md` + teste de regressão citando o `RFxx-CAn` violado. A spec não muda. |
| A spec está errada, ambígua ou incompleta | **FIX Tipo B** | `fix.md` + delta na spec, incluindo um critério novo que teria detectado o defeito |
| O comportamento segue a spec, mas o usuário quer outro | **Não é FIX** | Abrir uma **FEAT** |

Todo FIX exige um teste de regressão que **falha sem a correção** e passa com ela. Branch: `fix/FIX-NN-<slug>`.

## Regras da Spec Vigente

1. **Uma fonte por informação.** Requisito e critério de aceite ficam em `REQUISITOS.md`; decisão em `adr/`; contrato de dados em `ARQUITETURA.md` §3.2; regra técnica em `TECNICO.md`. Os demais documentos (e o `README.md` da raiz) apenas referenciam.
2. **Nada de código copiado em `TECNICO.md`.** Aponte para o arquivo; trechos curtos só quando o algoritmo é a própria regra.
3. **Requisitos não são apagados.** Ao remover um requisito, ele passa a `Obsoleto (FEAT-NN)`, mantendo o texto.
4. **ADRs não são reescritas.** Uma decisão revista gera uma nova ADR, e a antiga passa a `Substituída por ADR-NN`.
5. **Mudança no `state.json` segue `ARQUITETURA.md` §3.3** (versão + migração testada).
6. **Rastreabilidade nos testes.** Testes novos citam o critério que cobrem (`# RF07-CA2`, `# FIX-03 / RF16-CA2`).

## Versionamento

* **`v1.Y`** — uma ou mais FEATs entregues. **`v1.Y.Z`** — somente FIXes.
* A versão da spec, no topo de `specs/REQUISITOS.md`, acompanha a versão do aplicativo.
* Cada versão entregue recebe uma tag git e uma pasta em `archive/`.
