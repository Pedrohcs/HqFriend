# STATUS_PROJETO.md — Rastreamento de Progresso do Sistema (HqFriend)

> **REGRA DE GOVERNANÇA DESTE DOCUMENTO (APPEND-ONLY):**
> 1. Este documento é **estritamente append-only (somente adição)**.
> 2. **NUNCA apague ou sobrescreva** tabelas ou registros de atualizações anteriores.
> 3. Sempre que o status de uma ou mais features mudar, adicione uma **nova entrada cronológica** ao final da seção `Histórico de Snapshots e Atualizações (Append-Only)` contendo o timestamp, o resumo da mudança e a tabela atualizada das features.
> 4. **Status Permitidos:** `pendente` | `em andamento` | `concluida` | `bloqueada` | `cancelada`.

---

## Histórico de Snapshots e Atualizações (Append-Only)

### [Registro #001] — 2026-10-24 — Inicialização do Backlog e Especificação SDD Concluída
* **Responsável:** Arquiteto de Software / Tech Lead
* **Etapa Atual:** Especificação concluída (`REQUISITOS.md`, `PLANO_ARQUITETURA.md`, `PLANO_TECNICO.md`, `PLANO_DESENVOLVIMENTO.md`). Pronto para iniciar a **Fase 1 (`FEAT-01`)**.

| ID | Fase | Feature | Requisitos / US | Status | Observações / Bloqueios |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **FEAT-01** | Fase 1 | Setup do Projeto, Configuração de Caminhos e Bootstrap de Pastas | RNF01, RNF02, RNF03 | `pendente` | Ponto de partida da implementação |
| **FEAT-02** | Fase 1 | Modelagem de Domínio e Schemas com Pydantic v2 | RNF02, US12 | `pendente` | Depende de FEAT-01 |
| **FEAT-03** | Fase 1 | Repositório de Estado JSON com Escrita Atômica (`state.json`) | RNF02, US12 | `pendente` | Depende de FEAT-02 |
| **FEAT-04** | Fase 2 | Scanner de Diretórios de Nível Único (`.cbr`/`.cbz`) | RF01, RF03, RNF04 | `pendente` | Depende de FEAT-01 |
| **FEAT-05** | Fase 2 | Motor de Leitura `.cbz`/`.cbr` em RAM + Ordenação Natural + `UnRAR.exe` | RNF04, RNF05, ADR-01 | `pendente` | Depende de FEAT-01 |
| **FEAT-06** | Fase 3 | Serviço de Biblioteca, Contadores `X / Y` e Status Dinâmico | RF04, RF05, RF08, RF09, RF10 | `pendente` | Depende de FEAT-03 e FEAT-04 |
| **FEAT-07** | Fase 3 | Serviço de Gerenciamento e Cache de Capas (`Documents\HqFriend\covers`) | RF11, RF12, RNF02, RNF05 | `pendente` | Depende de FEAT-03 e FEAT-05 |
| **FEAT-08** | Fase 4 | `MainWindow` (Dark Mode) e Tela Inicial de Séries (`HomeView`) | RF01, RF02, RF04, RF10, RF11 | `pendente` | Depende de FEAT-06 e FEAT-07 |
| **FEAT-09** | Fase 4 | Modal de Seleção de Capa em 2 Etapas com Worker Assíncrono | RF11, RF12, RNF05, US04 | `pendente` | Depende de FEAT-07 e FEAT-08 |
| **FEAT-10** | Fase 4 | Tela de Detalhes da Série e Listagem de HQs (`SeriesView`) | RF05, RF08, RF13, US06 | `pendente` | Depende de FEAT-08 |
| **FEAT-11** | Fase 5 | Serviço e Canvas de Leitura (`ReaderView`: Zoom, Pan, `Ctrl+S`, Bookmark) | RF06, RF07, RF13 a RF16 | `pendente` | Depende de FEAT-05, FEAT-06 e FEAT-10 |
| **FEAT-12** | Fase 5 | Serviço de Captura e Exportação de Página `Ctrl + P` (`Pictures\HQs`) | RF17, RNF03, US11 | `pendente` | Depende de FEAT-11 |
| **FEAT-13** | Fase 5 | Empacotamento e Build do Executável Windows (`HqFriend.exe`) | RNF01, RNF04 | `pendente` | Depende de todas as anteriores |

---
<!-- ADICIONE NOVOS REGISTROS ABAIXO DESTA LINHA (NÃO EDITE OS REGISTROS ACIMA) -->