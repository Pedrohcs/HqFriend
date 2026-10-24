# STATUS_PROJETO.md — Rastreamento de Progresso do Sistema (HqFriend)

> **REGRA DE GOVERNANÇA DESTE DOCUMENTO:**
> 1. A seção **`Quadro de Features`** contém a **única** tabela de features do projeto e deve ser **atualizada no próprio lugar** sempre que o status de uma ou mais features mudar.
> 2. A seção **`Histórico de Atualizações`** é **append-only (somente adição)**: **NUNCA apague ou sobrescreva** registros anteriores. A cada mudança, adicione ao final um novo registro cronológico com data, responsável, etapa atual e resumo da mudança — **sem** repetir a tabela de features.
> 3. **Status Permitidos:** `pendente` | `em andamento` | `concluida` | `bloqueada` | `cancelada`.

---

## Quadro de Features

**Etapa Atual:** Fase 1 em andamento. Próxima feature: **`FEAT-03`**.

| ID | Fase | Feature | Requisitos / US | Status | Observações / Bloqueios |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **FEAT-01** | Fase 1 | Setup do Projeto, Configuração de Caminhos, Logs e Bootstrap de Pastas | RNF01, RNF02, RNF03, RNF06 | `concluida` | Validada em Python 3.12.10 |
| **FEAT-02** | Fase 1 | Modelagem de Domínio e Schemas com Pydantic v2 | RNF02, RF18, US12 | `concluida` | — |
| **FEAT-03** | Fase 1 | Repositório de Estado JSON com Escrita Atômica, Backup e Recuperação | RNF02, US12 | `pendente` | Próxima feature (dependências concluídas) |
| **FEAT-04** | Fase 2 | Scanner de Diretórios de Nível Único (`.cbr`/`.cbz`) | RF01, RF03 | `pendente` | Dependências concluídas |
| **FEAT-05** | Fase 2 | Motor de Leitura `.cbz`/`.cbr` em RAM (RAR em passada única) + Ordenação Natural | RNF04, RNF05, RF20, ADR-01, ADR-06 | `pendente` | Requer `bin/UnRAR.exe` |
| **FEAT-06** | Fase 3 | Serviço de Biblioteca, Contadores `X / Y`, Status Dinâmico e Marcações | RF04, RF05, RF08, RF09, RF10, RF18, RF19 | `pendente` | Depende de FEAT-03 e FEAT-04 |
| **FEAT-07** | Fase 3 | Serviço de Gerenciamento e Cache de Capas (`%DOCUMENTOS%\HqFriend\covers`) | RF11, RF12, RNF02, RNF05 | `pendente` | Depende de FEAT-03 e FEAT-05 |
| **FEAT-08** | Fase 4 | `MainWindow` (Dark Mode, Instância Única) e Tela Inicial de Séries (`HomeView`) | RF01, RF02, RF04, RF10, RF11, RF18, RF19, RNF06, RNF07 | `pendente` | Depende de FEAT-06 e FEAT-07 |
| **FEAT-09** | Fase 4 | Modal de Seleção de Capa em 2 Etapas com Worker Assíncrono | RF11, RF12, RNF05, US04 | `pendente` | Depende de FEAT-07 e FEAT-08 |
| **FEAT-10** | Fase 4 | Tela de Detalhes da Série e Listagem de HQs (`SeriesView`) | RF05, RF08, RF13, RF18, RF19, RF20, US06 | `pendente` | Depende de FEAT-08 |
| **FEAT-11** | Fase 5 | Serviço e Canvas de Leitura (`ReaderView`: Zoom, Pan, `Ctrl+S`, Bookmark) | RF06, RF07, RF13 a RF16, RF20 | `pendente` | Depende de FEAT-05, FEAT-06 e FEAT-10 |
| **FEAT-12** | Fase 5 | Serviço de Captura e Exportação de Página `Ctrl + P` (`%IMAGENS%\HQs`) | RF17, RNF03, US11 | `pendente` | Depende de FEAT-11 |
| **FEAT-13** | Fase 5 | Empacotamento e Build do Executável Windows (`HqFriend.exe`, onedir) | RNF01, RNF04 | `pendente` | Depende de todas as anteriores |

---

## Histórico de Atualizações (Append-Only)

### [Registro #001] — 2026-10-24 — Inicialização do Backlog e Especificação SDD Concluída
* **Responsável:** Arquiteto de Software / Tech Lead
* **Etapa Atual:** Especificação concluída (`REQUISITOS.md`, `PLANO_ARQUITETURA.md`, `PLANO_TECNICO.md`, `PLANO_DESENVOLVIMENTO.md`). Pronto para iniciar a **Fase 1 (`FEAT-01`)**.
* **Resumo das Mudanças:** backlog inicial com as 13 features (`FEAT-01` a `FEAT-13`) criado, todas com status `pendente`.

### [Registro #002] — 2026-10-24 — Revisão e Validação das Especificações
* **Responsável:** Analista de Requisitos Sênior / Tech Lead
* **Etapa Atual:** Specs revisadas e corrigidas (`REQUISITOS.md`, `PLANO_ARQUITETURA.md`, `PLANO_TECNICO.md`, `PLANO_DESENVOLVIMENTO.md`). Pronto para iniciar a **Fase 1 (`FEAT-01`)**.
* **Resumo das Mudanças:**
    * **Decisões do usuário:** contador sempre no formato `0 / Y obras` (RF04); página dupla no `Ctrl + P` centralizada sobre fundo preto, sem redimensionar (RF17); caminhos fixos substituídos por pastas conhecidas do Windows `%DOCUMENTOS%` / `%IMAGENS%` (RNF02, RNF03, ADR-05).
    * **Bugs de spec corrigidos:** HQ com 0 páginas não é mais marcada como lida (RF20); releitura de HQ concluída em modo duplo reabre na página 1 (critério `is_read`); "Marcar como não lida" zera o bookmark (RF08/RF10); conclusão verificada a cada mudança de páginas visíveis, inclusive `Ctrl + S` e abertura (RF07); exemplo do `state.json` corrigido para índice base-0.
    * **Novos requisitos:** RF18 (ordenação natural), RF19 (atualização da biblioteca / `F5`), RF20 (arquivo inválido), RNF06 (logs), RNF07 (instância única), US13; "Marcar série como não lida" e "Restaurar capa padrão"; `Ctrl + P` não sobrescreve arquivos.
    * **Técnico:** backup/recuperação do `state.json` com novas tentativas de escrita; extração RAR em passada única (ADR-06); camada de domínio sem PySide6 (sinais movidos para Workers); varredura e capas assíncronas; regras de concorrência entre threads; conversão RGB no export; `HqFriend.spec` reescrito para PyInstaller 6 (onedir, sem UPX); estratégia de testes com pytest.
    * **Pendência:** **QA-01** — identificação do progresso ao trocar de diretório raiz (comportamento provisório: estado único, sem reset). Impacta FEAT-02 e FEAT-06.

### [Registro #003] — 2026-10-24 — Decisão da QA-01
* **Responsável:** Analista de Requisitos Sênior / Tech Lead
* **Etapa Atual:** Nenhuma pendência de especificação. Pronto para iniciar a **Fase 1 (`FEAT-01`)**.
* **Resumo das Mudanças:**
    * **QA-01 decidida — opção C:** estado único chaveado por nome da pasta da série + nome do arquivo, sem reset ao trocar de diretório raiz. Limitações aceitas: bibliotecas diferentes com nomes iguais compartilham progresso; renomear pasta/arquivo perde o progresso.
    * Documentos atualizados: `REQUISITOS.md` (RF01 e seção 6), `PLANO_ARQUITETURA.md` (3.2), `PLANO_TECNICO.md` (3.2), `PLANO_DESENVOLVIMENTO.md` (1.1 e critério 7 da FEAT-06).

### [Registro #004] — 2026-10-24 — Início da Implementação (FEAT-01)
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 1 iniciada. `FEAT-01` implementada; aguardando a instalação do Python 3.12 para validação final no ambiente virtual oficial (`.venv`).
* **Resumo das Mudanças:**
    * Criada a árvore de diretórios do projeto (`src/`, `tests/`, `bin/`), `requirements.txt`, `requirements-dev.txt`, `pytest.ini` e `.gitignore` atualizado.
    * `src/config.py`: resolução de `%DOCUMENTOS%` / `%IMAGENS%` via `SHGetKnownFolderPath` e resolvedor `_MEIPASS`.
    * `src/infrastructure/fs_scanner.py`: `ensure_system_directories()` (bootstrap das 4 pastas do sistema).
    * `src/infrastructure/logging_setup.py`: log rotativo + `sys.excepthook` / `threading.excepthook`.
    * 14 testes pytest cobrindo os 4 critérios de aceite — todos passando (validação preliminar em Python 3.11.4).
    * **Pré-requisitos pendentes do ambiente:** instalação do Python 3.12 (FEAT-01) e obtenção do `bin/UnRAR.exe` (necessário a partir da FEAT-05).
    * `FEAT-01` $\rightarrow$ `em andamento`.

### [Registro #005] — 2026-10-24 — FEAT-01 e FEAT-02 Concluídas
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 1 em andamento. Próxima feature: **`FEAT-03`**.
* **Resumo das Mudanças:**
    * **FEAT-01:** validada no ambiente virtual oficial (`.venv`, Python 3.12.10) com todas as dependências de `requirements-dev.txt` instaladas (`pip check` sem conflitos).
    * **FEAT-02:** implementados `src/domain/enums.py` (`SeriesStatus`), `src/domain/errors.py` (`InvalidComicError`, `StateRecoveredWarning`), `src/domain/sorting.py` (`natural_sort_key`) e `src/domain/models.py` (schemas Pydantic e DTOs `SeriesDTO` / `ComicDTO`, com o contador `X / Y obras` do RF04).
    * Suíte de testes: **32 testes passando** (FEAT-01: 14; FEAT-02: 18), cobrindo os 3 critérios de aceite da FEAT-02.
    * `FEAT-01` $\rightarrow$ `concluida`; `FEAT-02` $\rightarrow$ `concluida`.

### [Registro #006] — 2026-10-24 — Reestruturação do Documento de Status
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 1 em andamento. Próxima feature: **`FEAT-03`**.
* **Resumo das Mudanças:** por decisão do usuário (exceção pontual à regra append-only), o documento passou a ter **uma única tabela de features** (`Quadro de Features`), atualizada no próprio lugar. As tabelas repetidas dos registros #001 a #005 foram removidas; o conteúdo textual dos registros foi preservado. A regra de governança foi ajustada para refletir o novo formato.

<!-- ADICIONE NOVOS REGISTROS ABAIXO DESTA LINHA (NÃO EDITE OS REGISTROS ACIMA) -->
