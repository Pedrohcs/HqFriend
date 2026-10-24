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

### [Registro #002] — 2026-10-24 — Revisão e Validação das Especificações
* **Responsável:** Analista de Requisitos Sênior / Tech Lead
* **Etapa Atual:** Specs revisadas e corrigidas (`REQUISITOS.md`, `PLANO_ARQUITETURA.md`, `PLANO_TECNICO.md`, `PLANO_DESENVOLVIMENTO.md`). Pronto para iniciar a **Fase 1 (`FEAT-01`)**.
* **Resumo das Mudanças:**
    * **Decisões do usuário:** contador sempre no formato `0 / Y obras` (RF04); página dupla no `Ctrl + P` centralizada sobre fundo preto, sem redimensionar (RF17); caminhos fixos substituídos por pastas conhecidas do Windows `%DOCUMENTOS%` / `%IMAGENS%` (RNF02, RNF03, ADR-05).
    * **Bugs de spec corrigidos:** HQ com 0 páginas não é mais marcada como lida (RF20); releitura de HQ concluída em modo duplo reabre na página 1 (critério `is_read`); "Marcar como não lida" zera o bookmark (RF08/RF10); conclusão verificada a cada mudança de páginas visíveis, inclusive `Ctrl + S` e abertura (RF07); exemplo do `state.json` corrigido para índice base-0.
    * **Novos requisitos:** RF18 (ordenação natural), RF19 (atualização da biblioteca / `F5`), RF20 (arquivo inválido), RNF06 (logs), RNF07 (instância única), US13; "Marcar série como não lida" e "Restaurar capa padrão"; `Ctrl + P` não sobrescreve arquivos.
    * **Técnico:** backup/recuperação do `state.json` com novas tentativas de escrita; extração RAR em passada única (ADR-06); camada de domínio sem PySide6 (sinais movidos para Workers); varredura e capas assíncronas; regras de concorrência entre threads; conversão RGB no export; `HqFriend.spec` reescrito para PyInstaller 6 (onedir, sem UPX); estratégia de testes com pytest.
    * **Pendência:** **QA-01** — identificação do progresso ao trocar de diretório raiz (comportamento provisório: estado único, sem reset). Impacta FEAT-02 e FEAT-06.

| ID | Fase | Feature | Requisitos / US | Status | Observações / Bloqueios |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **FEAT-01** | Fase 1 | Setup do Projeto, Configuração de Caminhos, Logs e Bootstrap de Pastas | RNF01, RNF02, RNF03, RNF06 | `pendente` | Ponto de partida da implementação |
| **FEAT-02** | Fase 1 | Modelagem de Domínio e Schemas com Pydantic v2 | RNF02, RF18, US12 | `pendente` | Depende de FEAT-01. Modelo sujeito à decisão da QA-01 |
| **FEAT-03** | Fase 1 | Repositório de Estado JSON com Escrita Atômica, Backup e Recuperação | RNF02, US12 | `pendente` | Depende de FEAT-02 |
| **FEAT-04** | Fase 2 | Scanner de Diretórios de Nível Único (`.cbr`/`.cbz`) | RF01, RF03 | `pendente` | Depende de FEAT-01 |
| **FEAT-05** | Fase 2 | Motor de Leitura `.cbz`/`.cbr` em RAM (RAR em passada única) + Ordenação Natural | RNF04, RNF05, RF20, ADR-01, ADR-06 | `pendente` | Depende de FEAT-01 e FEAT-02 |
| **FEAT-06** | Fase 3 | Serviço de Biblioteca, Contadores `X / Y`, Status Dinâmico e Marcações | RF04, RF05, RF08, RF09, RF10, RF18, RF19 | `pendente` | Depende de FEAT-03 e FEAT-04. Sujeito à decisão da QA-01 |
| **FEAT-07** | Fase 3 | Serviço de Gerenciamento e Cache de Capas (`%DOCUMENTOS%\HqFriend\covers`) | RF11, RF12, RNF02, RNF05 | `pendente` | Depende de FEAT-03 e FEAT-05 |
| **FEAT-08** | Fase 4 | `MainWindow` (Dark Mode, Instância Única) e Tela Inicial de Séries (`HomeView`) | RF01, RF02, RF04, RF10, RF11, RF18, RF19, RNF06, RNF07 | `pendente` | Depende de FEAT-06 e FEAT-07 |
| **FEAT-09** | Fase 4 | Modal de Seleção de Capa em 2 Etapas com Worker Assíncrono | RF11, RF12, RNF05, US04 | `pendente` | Depende de FEAT-07 e FEAT-08 |
| **FEAT-10** | Fase 4 | Tela de Detalhes da Série e Listagem de HQs (`SeriesView`) | RF05, RF08, RF13, RF18, RF19, RF20, US06 | `pendente` | Depende de FEAT-08 |
| **FEAT-11** | Fase 5 | Serviço e Canvas de Leitura (`ReaderView`: Zoom, Pan, `Ctrl+S`, Bookmark) | RF06, RF07, RF13 a RF16, RF20 | `pendente` | Depende de FEAT-05, FEAT-06 e FEAT-10 |
| **FEAT-12** | Fase 5 | Serviço de Captura e Exportação de Página `Ctrl + P` (`%IMAGENS%\HQs`) | RF17, RNF03, US11 | `pendente` | Depende de FEAT-11 |
| **FEAT-13** | Fase 5 | Empacotamento e Build do Executável Windows (`HqFriend.exe`, onedir) | RNF01, RNF04 | `pendente` | Depende de todas as anteriores |

---
<!-- ADICIONE NOVOS REGISTROS ABAIXO DESTA LINHA (NÃO EDITE OS REGISTROS ACIMA) -->

### [Registro #003] — 2026-10-24 — Decisão da QA-01
* **Responsável:** Analista de Requisitos Sênior / Tech Lead
* **Etapa Atual:** Nenhuma pendência de especificação. Pronto para iniciar a **Fase 1 (`FEAT-01`)**.
* **Resumo das Mudanças:**
    * **QA-01 decidida — opção C:** estado único chaveado por nome da pasta da série + nome do arquivo, sem reset ao trocar de diretório raiz. Limitações aceitas: bibliotecas diferentes com nomes iguais compartilham progresso; renomear pasta/arquivo perde o progresso.
    * Documentos atualizados: `REQUISITOS.md` (RF01 e seção 6), `PLANO_ARQUITETURA.md` (3.2), `PLANO_TECNICO.md` (3.2), `PLANO_DESENVOLVIMENTO.md` (1.1 e critério 7 da FEAT-06).

| ID | Fase | Feature | Requisitos / US | Status | Observações / Bloqueios |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **FEAT-01** | Fase 1 | Setup do Projeto, Configuração de Caminhos, Logs e Bootstrap de Pastas | RNF01, RNF02, RNF03, RNF06 | `pendente` | Ponto de partida da implementação |
| **FEAT-02** | Fase 1 | Modelagem de Domínio e Schemas com Pydantic v2 | RNF02, RF18, US12 | `pendente` | Depende de FEAT-01 |
| **FEAT-03** | Fase 1 | Repositório de Estado JSON com Escrita Atômica, Backup e Recuperação | RNF02, US12 | `pendente` | Depende de FEAT-02 |
| **FEAT-04** | Fase 2 | Scanner de Diretórios de Nível Único (`.cbr`/`.cbz`) | RF01, RF03 | `pendente` | Depende de FEAT-01 |
| **FEAT-05** | Fase 2 | Motor de Leitura `.cbz`/`.cbr` em RAM (RAR em passada única) + Ordenação Natural | RNF04, RNF05, RF20, ADR-01, ADR-06 | `pendente` | Depende de FEAT-01 e FEAT-02 |
| **FEAT-06** | Fase 3 | Serviço de Biblioteca, Contadores `X / Y`, Status Dinâmico e Marcações | RF04, RF05, RF08, RF09, RF10, RF18, RF19 | `pendente` | Depende de FEAT-03 e FEAT-04 |
| **FEAT-07** | Fase 3 | Serviço de Gerenciamento e Cache de Capas (`%DOCUMENTOS%\HqFriend\covers`) | RF11, RF12, RNF02, RNF05 | `pendente` | Depende de FEAT-03 e FEAT-05 |
| **FEAT-08** | Fase 4 | `MainWindow` (Dark Mode, Instância Única) e Tela Inicial de Séries (`HomeView`) | RF01, RF02, RF04, RF10, RF11, RF18, RF19, RNF06, RNF07 | `pendente` | Depende de FEAT-06 e FEAT-07 |
| **FEAT-09** | Fase 4 | Modal de Seleção de Capa em 2 Etapas com Worker Assíncrono | RF11, RF12, RNF05, US04 | `pendente` | Depende de FEAT-07 e FEAT-08 |
| **FEAT-10** | Fase 4 | Tela de Detalhes da Série e Listagem de HQs (`SeriesView`) | RF05, RF08, RF13, RF18, RF19, RF20, US06 | `pendente` | Depende de FEAT-08 |
| **FEAT-11** | Fase 5 | Serviço e Canvas de Leitura (`ReaderView`: Zoom, Pan, `Ctrl+S`, Bookmark) | RF06, RF07, RF13 a RF16, RF20 | `pendente` | Depende de FEAT-05, FEAT-06 e FEAT-10 |
| **FEAT-12** | Fase 5 | Serviço de Captura e Exportação de Página `Ctrl + P` (`%IMAGENS%\HQs`) | RF17, RNF03, US11 | `pendente` | Depende de FEAT-11 |
| **FEAT-13** | Fase 5 | Empacotamento e Build do Executável Windows (`HqFriend.exe`, onedir) | RNF01, RNF04 | `pendente` | Depende de todas as anteriores |

---
<!-- ADICIONE NOVOS REGISTROS ABAIXO DESTA LINHA (NÃO EDITE OS REGISTROS ACIMA) -->