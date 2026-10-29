# FIX-01 — Sincronização da Spec com o Código da v1.0 e Botão de Fechar do Leitor

* **Status:** `em andamento`
* **Branch:** `fix/FIX-01-sincronizacao-spec-v1.0`
* **Severidade:** `média` — nenhum defeito de dados ou de função principal; a spec vigente não descreve fielmente o sistema entregue, o que invalida o SDD como base para as próximas mudanças.
* **Versão afetada:** v1.0 · **Corrigido em:** v1.0.1
* **Responsável:** Tech Lead / Analista de Requisitos Sênior
* **Aberto em:** 2026-10-29
* **Origem:** auditoria spec × código de 2026-10-29 (achados A1–A4, B, C1–C3 e D).

## 1. Classificação

Pacote **misto**, com uma parte de código e uma de spec:

- [x] **Tipo A — Código diverge da spec.** O RF14 especifica "botão de fechar" no leitor, que não foi implementado (achado A1). Decisão **QA-05**: implementar.
- [x] **Tipo B — Spec errada, ambígua ou incompleta.** Diagramas e nomes de componentes desatualizados, regra de bookmark descrita de forma diferente da implementada, comportamentos visíveis sem requisito, estratégia de testes perdida no arquivamento e decisões registradas só no histórico do STATUS (achados A2–A4, B, C, D). Decisão **QA-06**: manter o comportamento atual do bookmark.
- [ ] Não é FIX.

## 2. Comportamento

* **Esperado:** `docs/specs/` e `docs/adr/` descrevem exatamente o que o código da v1.0 faz, cada critério de aceite tem verificação identificada, e toda decisão relevante tem registro com motivo e alternativas.
* **Observado:**
  * **A1:** o leitor só fecha com `ESC`; não existe botão (o ✕ da janela fecha o aplicativo inteiro).
  * **A2:** `TECNICO.md` §3.2 diz que o bookmark é gravado "no máximo a cada 500 ms" (*throttle*). O código (`src/ui/views/reader_view.py:80-82` e `:184`) reinicia um `QTimer` *single-shot* a cada virada, ou seja, grava 500 ms após a **última** virada (*debounce*). O comentário do código repete a descrição incorreta.
  * **A3:** diagramas e textos citam componentes e chamadas inexistentes (tabela na seção 5.3).
  * **A4:** detalhes técnicos divergentes ou ausentes (seção 5.3).
  * **B:** comportamentos visíveis ao usuário sem requisito (seção 5.1).
  * **C1/C2:** testes citam apenas `RFxx`; não há matriz critério → teste nem indicação de critérios verificados só manualmente; a parte "trava de processo morto" do RNF07-CA1 não tem teste.
  * **C3:** a estratégia de testes ficou só no arquivo (`archive/v1.0/PLANO_DESENVOLVIMENTO.md` §1.1) e já estava desatualizada: dizia que a UI seria validada manualmente, mas existem testes de UI automatizados (`tests/ui/`).
  * **D:** decisões de stack, de empacotamento, de distribuição do `UnRAR.exe` e de implementação registradas só no histórico do STATUS ou em texto solto.
* **Ambiente:** código-fonte da branch `main` + `feature-hq-cover` (commit `c5749ff`), docs reorganizados no Registro #020.

## 3. Causa Raiz

1. **Sem etapa obrigatória de sincronização na v1.0.** Os desvios encontrados durante a implementação foram registrados apenas no `STATUS_PROJETO.md` (Registros #012, #013, #015, #016 e #017) e nunca levados à spec. O processo atual (`docs/README.md`, etapa 4) já corrige isso para os próximos pacotes.
2. **Diagramas escritos antes do código** e não revisados: nomes como `ArchiveReaderAdapter`, `FileSystemScanner` e `initialize_library()` eram intenções de design que a implementação substituiu.
3. **Critérios de aceite por FEAT, não por requisito**, sem vínculo com testes. Comportamentos testados mas não especificados (ex: releitura) não tinham onde morar.
4. **A1:** o critério de aceite da FEAT-11 cobria apenas o `ESC`, então a menção a "botão de fechar" no RF14 nunca foi verificada.
5. **C3:** introduzido no Registro #020 ao arquivar o `PLANO_DESENVOLVIMENTO.md` sem migrar a seção 1.1.

## 4. Correção

### 4.1. Código (Tipo A + ajustes)
* **Arquivos alterados:** `src/ui/views/reader_view.py`, `assets/styles/dark_theme.qss`, `tests/ui/test_reader_view.py`, `tests/ui/test_home_view.py`, `tests/ui/test_cover_picker_dialog.py`, `HqFriend.spec`, `bin/UnRAR.exe` (6.11 → 7.23) e `bin/license.txt` (tarefa T10b).
* **Abordagem:**
  1. **Botão Fechar no leitor (RF14-CA3):** `QPushButton` filho do `ReaderView`, sobreposto no canto superior direito (mesmo padrão de posicionamento do `page_indicator`, reposicionado no `resizeEvent`), texto `✕`, tooltip `Fechar (Esc)`, `objectName="readerCloseButton"`, `focusPolicy = Qt.NoFocus` (para não roubar o foco do teclado do leitor). O clique emite o mesmo `close_requested` do `ESC`, de modo que a `MainWindow` segue o fluxo existente de `close_reader()` (grava bookmark, libera o arquivo, volta à Tela da Série atualizada). Estilo no `dark_theme.qss`: fundo translúcido, destaque âmbar no *hover*.
  2. **Comentário do bookmark (QA-06):** corrigir o comentário de `reader_view.py:80` para "grava 500 ms após a última mudança de página (*debounce*)". Sem mudança de comportamento.
  3. **Teste da trava obsoleta (RNF07-CA1):** cobrir que uma trava deixada por processo inexistente não impede a abertura (`acquire_instance_lock` em `src/main.py`). Se o formato de arquivo do `QLockFile` não permitir simular isso de forma confiável, o critério é marcado como verificação **manual** na matriz e o motivo é registrado nas Tarefas.
* **Impacto no `state.json`:** nenhum.

### 4.2. Documentação (Tipo B)
Aplicar integralmente o delta da seção 5 em `docs/specs/`, criar as ADRs da seção 5.4, registrar as questões da seção 5.5 e incluir a matriz de rastreabilidade (seção 5.6).

## 5. Delta de Spec

> Os blocos abaixo trazem o **texto completo** a colar na spec vigente. Os critérios inalterados de requisitos modificados não são repetidos: o texto informa onde inserir.

### 5.1. `specs/REQUISITOS.md`

#### MODIFICADO — RF14 — Navegação de Páginas
`Ativo` · Origem: v1.0 (FEAT-11), FIX-01

Substituir o 3º item da lista por:
* **Tecla `ESC` ou botão "Fechar" (`✕`) do leitor:** Encerrar a visualização da HQ e retornar à listagem da série.

Manter RF14-CA1 e RF14-CA2 e acrescentar:
* **RF14-CA3:** O leitor exibe um botão "Fechar" (`✕`, tooltip `Fechar (Esc)`) no canto superior direito; clicar nele tem o mesmo efeito do `ESC` (grava o bookmark, fecha a HQ e volta à Tela da Série atualizada), e depois do clique o teclado continua controlando o leitor até ele fechar.
* **RF14-CA4:** Durante a leitura, um indicador sobreposto mostra a posição atual: `Pág. N / Total` no modo único e `Págs. N–M / Total` no modo duplo.

> **O que mudou:** o botão passa a ser exigido por um critério verificável (antes só era citado no texto, sem critério, e não foi implementado); o indicador de página, já implementado, ganha requisito.

#### MODIFICADO — RF06 — Persistência de Página Atual (Bookmark)
`Ativo` · Origem: v1.0 (FEAT-11), FIX-01

Acrescentar após RF06-CA3:
* **RF06-CA4:** Durante a releitura de uma HQ "Lida", ela permanece "Lida" e o contador da série não muda; reabri-la novamente recomeça na página 1.
* **RF06-CA5:** Durante a leitura, o bookmark é gravado 500 ms após a última mudança de página e, de imediato, ao fechar a HQ, ao concluí-la e ao encerrar o aplicativo (QA-06).

> **O que mudou:** regra de releitura (já implementada e testada em `test_releitura_nao_desmarca_hq_lida`) e momento de gravação do bookmark passam a ser requisito.

#### MODIFICADO — RF02 — Inicialização na Tela Principal
`Ativo` · Origem: v1.0 (FEAT-08), FIX-01

Acrescentar após RF02-CA2:
* **RF02-CA3:** Os estados vazios da Tela Inicial exibem orientação e o botão "Selecionar pasta": sem pasta configurada ("Selecione a pasta onde estão suas HQs para começar."), pasta não encontrada (exibe o caminho e "Reconecte a unidade ou selecione outra pasta.") e pasta sem séries (exibe o caminho e "Cada subpasta com arquivos .cbr ou .cbz é uma série.").
* **RF02-CA4:** O cabeçalho da Tela Inicial exibe a pasta raiz atual (caminho completo no *tooltip*, sem impor largura mínima à janela) e o aplicativo abre maximizado.

#### MODIFICADO — RF19 — Atualização da Biblioteca
`Ativo` · Origem: v1.0 (FEAT-06, FEAT-08, FEAT-10), FIX-01

Acrescentar após RF19-CA3:
* **RF19-CA4:** Enquanto a varredura está em andamento, a Tela Inicial exibe "Atualizando biblioteca…".

#### MODIFICADO — RF12 — Fluxo de Escolha de Capa em 2 Etapas
`Ativo` · Origem: v1.0 (FEAT-07, FEAT-09), FIX-01

Acrescentar após RF12-CA3:
* **RF12-CA4:** O passo 1 abre com a HQ da capa atual já selecionada (ou a primeira HQ, se a capa for a padrão); no passo 2, "Definir como capa" só fica habilitado com uma página selecionada, e o duplo clique numa miniatura confirma.

#### MODIFICADO — RF13 — Abertura por Duplo Clique
`Ativo` · Origem: v1.0 (FEAT-10, FEAT-11), FIX-01

Acrescentar após RF13-CA1:
* **RF13-CA2:** Durante a leitura, o título da janela exibe `<nome do arquivo> — HqFriend`; ao fechar o leitor, volta a `HqFriend`.

#### ADICIONADO — RF21 — Tratamento de Página Ilegível
`Ativo` · Origem: FIX-01 (comportamento entregue na v1.0, FEAT-11)

Inserir na seção 2.4, após o RF20.

Se uma página de uma HQ válida não puder ser decodificada, o leitor deve exibir um quadro substituto com o texto "Página ilegível" no lugar dela, registrar o problema em log e continuar permitindo a navegação. A HQ não é considerada inválida (RF20) por causa de uma página isolada.
* **RF21-CA1:** Uma página com bytes de imagem corrompidos é exibida como o quadro "Página ilegível", e as demais páginas continuam navegáveis.
* **RF21-CA2:** A falha é registrada em `hqfriend.log` como aviso, sem mensagem modal ao usuário.
* **RF21-CA3:** Chegar à última página continua marcando a HQ como "Lida" (RF07), mesmo que alguma página tenha sido ilegível.

> **Verificar na implementação:** RF21-CA3 descreve o comportamento esperado a partir do código (a conclusão depende só do índice visível). Se o teste mostrar outro comportamento, registre como desvio nas Tarefas e decida antes de sincronizar.

#### ADICIONADO — RNF08 — Identidade Visual em Tema Escuro
`Ativo` · Origem: FIX-01 (comportamento entregue na v1.0, FEAT-08)

Inserir na seção 3, após o RNF07.

A interface deve usar um tema escuro único, definido em uma folha de estilos embarcada (`assets/styles/dark_theme.qss`) sobre o estilo Qt `Fusion`: fundo da aplicação `#121212`, fundo do leitor `#000000`, superfícies `#1e1e1e`/`#2a2a2a` e cor de destaque âmbar `#e5a00d` para ações primárias e seleção.
* **RNF08-CA1:** Telas, diálogos e menus usam o tema escuro tanto no código-fonte quanto no executável (a folha de estilos é resolvida via `get_resource_path`).
* **RNF08-CA2:** Os status usam cores consistentes em toda a interface: "Lida" em verde, "Em andamento" em âmbar e "Não lida" em cinza.

#### MODIFICADO — Convenção dos critérios (cabeçalho do documento)
Acrescentar ao bloco de convenções do topo:
> * **Verificação:** cada critério é verificado de forma **automática** (teste pytest) ou **manual** (roteiro no executável). A seção 7 (Matriz de Rastreabilidade) liga cada critério à sua verificação. Testes novos citam o critério (`# RF14-CA3`).

### 5.2. `specs/REQUISITOS.md` §6 — Questões Decididas

Acrescentar à tabela (as QA-02 a QA-04 são **retroativas**: decisões do usuário de 2026-10-24, registradas no Registro #002, cujo motivo só estava no histórico):

| ID | Questão | Decisão | Alternativas Descartadas |
| :--- | :--- | :--- | :--- |
| **QA-02** | Formato do contador quando nenhuma obra foi lida. | **Decidida em 2026-10-24 (retroativa):** sempre `0 / Y obras` (RF04). | Não registradas na época. |
| **QA-03** | Montagem da imagem de página dupla no `Ctrl + P` quando as páginas têm alturas diferentes. | **Decidida em 2026-10-24 (retroativa):** unir sem redimensionar, centralizando verticalmente a menor sobre fundo preto (RF17). | Não registradas na época. |
| **QA-04** | Caminhos de dados e de exportação. | **Decidida em 2026-10-24 (retroativa):** pastas conhecidas do Windows `%DOCUMENTOS%` / `%IMAGENS%`, respeitando OneDrive (ADR-05). | Caminhos fixos com o nome do usuário (quebram em outra máquina e com o OneDrive). |
| **QA-05** | O leitor deve ter botão de fechar, como cita o RF14? | **Decidida em 2026-10-29:** sim — botão `✕` sobreposto, com o mesmo efeito do `ESC` (RF14-CA3). | Remover o botão da spec e manter só o `ESC` (pior para quem usa só o mouse). |
| **QA-06** | Momento de gravação do bookmark durante a leitura. | **Decidida em 2026-10-29:** manter o implementado — grava 500 ms após a última virada (*debounce*), e de imediato ao fechar, concluir ou sair (RF06-CA5). | Gravação periódica garantida a cada 500 ms mesmo com viradas contínuas (*throttle*): mais escritas no disco para ganhar, no pior caso, as viradas do último meio segundo antes de uma queda do app. |

### 5.3. `specs/ARQUITETURA.md` e `specs/TECNICO.md`

| # | Documento / Seção | Texto atual | Corrigir para |
| :---: | :--- | :--- | :--- |
| 1 | ARQ §2 (diagrama de camadas) | `DomainModels["Domain Models (Series, ComicBook, ReadingState)"]` | `AppState, SeriesState, ComicState, DTOs` |
| 2 | ARQ §2 / §2.3 / §4.2 / §4.3 | `ArchiveReaderAdapter` | `archive_reader` (`open_archive()` + interface `IComicArchive` com `ZipArchiveStrategy` / `RarArchiveStrategy`) |
| 3 | ARQ §2 / §2.3 / §4.1; TECNICO §3.4 | Classe `FileSystemScanner` / `FileSystemScanner.scan_series_folders` | Módulo `fs_scanner` com as funções `ensure_system_directories()` e `scan_series_folders()` |
| 4 | ARQ §2.1 (`MainWindow`) | "Garante instância única do aplicativo (RNF07)" | A instância única é garantida pelo `main.py` antes de criar a janela (ADR-08); a `MainWindow` é o shell de navegação e encerra leitor e workers ao fechar |
| 5 | ARQ §4.1 | `UI->>Lib: initialize_library()`; `Lib->>FS: ensure_system_directories()`; `Lib->>Repo: load_state()` | Sequência real: `main.py` → `ensure_system_directories()`, `logging_setup.configure()`, trava, `LibraryService.load_state()` → `JsonStateRepository.load()`; depois `HomeView.refresh_library()` |
| 6 | ARQ §4.1; TECNICO §3.4 | `save_state()` | `JsonStateRepository.save()` (chamado pelo `LibraryService`) |
| 7 | ARQ §4.1; TECNICO §3.4 | `cover_ready(series_name)` | `cover_ready(series_name, cover_path)` |
| 8 | ARQ §2.1 / §4.2; TECNICO §6.2 | `page_thumbnail_ready(page_index, QImage)` | `page_thumbnail_ready(generation, page_index, QImage)`; `generation` identifica a HQ selecionada e permite descartar miniaturas de uma seleção anterior |
| 9 | ARQ §4.2 | `Cov->>Repo: Atualiza custom_cover_image e cover_source` | `Cov->>Lib: set_cover_reference(series, CoverSource)` → `Lib->>Repo: save()` |
| 10 | TECNICO §3.2 (debounce) | "agrupadas e gravadas no máximo a cada 500ms" | "gravadas 500 ms após a última mudança de página (*debounce*, `FLUSH_DELAY_MS`)", com gravação imediata nos casos já listados (QA-06) |
| 11 | TECNICO §3.2 (carregamento, item 1) | "retorna `AppState()` limpo" | "cria o `state.json` com um `AppState()` limpo e o retorna" |
| 12 | TECNICO §3.3 (filtro) | "não pertençam a metadados ocultos (como `__MACOSX`)" | Incluir arquivos ocultos `._*`; diretórios são ignorados; ZIP com página criptografada é rejeitado |
| 13 | TECNICO §4.2 (fit-to-view) | `fitInView(self.scene.itemsBoundingRect(), ...)` e `self._zoom_level = 0` | `fitInView(sceneRect, KeepAspectRatio)`; o zoom é relativo ao ajuste (`_zoom = 1.0`); o arraste (`ScrollHandDrag`) só fica ativo com zoom > 1x; as barras de rolagem ficam ocultas |
| 14 | TECNICO §4.2 / §4.3 | — | Botão "Fechar" do leitor (RF14-CA3) no mapa de atalhos e na descrição do `ReaderView` |
| 15 | TECNICO §3 (capas) | — | Capa: largura máx. 400 px (`COVER_MAX_WIDTH`), proporção mantida, sem ampliar, PNG otimizado, gravação atômica `.png.tmp` → `os.replace`. Miniaturas: 250 px (`THUMBNAIL_WIDTH`), exibidas em ícones de 150×225 |
| 16 | TECNICO §1.3 / §3 (logs) | Só "log rotativo" | `RotatingFileHandler` com 1 MB e 3 arquivos de backup (`hqfriend.log`), formato com data, nível, thread e logger |
| 17 | TECNICO §4.1 | — | `QApplication` com estilo `Fusion`, ícone e `dark_theme.qss`; `QLockFile.setStaleLockTime(0)` + `tryLock(100)`; `logging_setup.configure` é chamado de novo depois de criar o `UnhandledErrorReporter` para ligar a exibição de erros na UI |
| 18 | TECNICO §6 (concorrência) — novo item 6 | — | Regras de ciclo de vida: (a) varredura pedida durante outra é enfileirada uma única vez, e o resultado de uma raiz que mudou durante a varredura é descartado e refeito; (b) miniaturas de uma seleção anterior são descartadas pelo contador de geração; (c) `HomeView.shutdown()` e `ReaderView.shutdown()` bloqueiam trabalho novo e aguardam as threads antes de a janela ser destruída; (d) exportações pendentes são aguardadas ao fechar |
| 19 | TECNICO — nova §7 "Estratégia de Testes" | (estava só em `archive/v1.0/PLANO_DESENVOLVIMENTO.md` §1.1) | Migrar e atualizar: pytest para todas as camadas, inclusive UI; `tests/ui/` em modo `offscreen` com `QT_QPA_FONTDIR` apontando para as fontes do Windows (`conftest.py`); `SignalRecorder` no lugar de `QSignalSpy.wait()`, que no PySide6 mantém o GIL e impede a execução dos workers; fixtures gerados por `tests/fixtures/build_fixtures.py` (requer o `Rar.exe` do WinRAR para as fixtures RAR); testes nunca gravam nas pastas reais (`tmp_path`); critérios não automatizáveis seguem roteiro manual no executável |
| 20 | TECNICO §7 — armadilhas do PySide6 | (Registro #015) | Passar um **sinal** como `clicked=` / `activated=` no construtor não o conecta (conectar com `.connect`); `clicked` envia `checked` e um sinal sem parâmetros o rejeita (usar `lambda`) |

### 5.4. Novas ADRs (`docs/adr/`)

Criar a partir de `adr/_TEMPLATE.md`, com status `Aceita`, data 2026-10-24 (decisões da v1.0, registradas retroativamente pelo FIX-01), e incluir no índice da ARQ §5:

| ID | Decisão | Conteúdo mínimo |
| :--- | :--- | :--- |
| **ADR-09** | Interface com PySide6 (Qt 6) | Contexto: app desktop Windows com leitor de imagem acelerado e threads. Decisão: PySide6 (`QGraphicsView` para o leitor, `QThread` para workers). Consequências: pacote de ~128 MB; licença LGPL; camadas centrais isoladas do Qt (RNF05-CA3). |
| **ADR-10** | Persistência em JSON validado com Pydantic v2 | Decisão: um único `state.json` validado por schema, escrita atômica e backup. Alternativa descartada: SQLite (mais robusto para volume e concorrência, mas desnecessário com instância única e o volume de uma biblioteca pessoal; a separação em camadas permite migrar depois). Consequências: arquivo legível e fácil de recuperar; regravação inteira a cada mudança; mudanças de schema seguem ARQ §3.3. |
| **ADR-11** | Empacotamento PyInstaller onedir sem UPX | Alternativas descartadas: onefile (extrai o PySide6 em pasta temporária a cada execução, com inicialização lenta); UPX (corrompe DLLs do Qt e aumenta falsos positivos de antivírus). Consequência: distribuição como pasta (`dist\HqFriend\`) compactada. |
| **ADR-12** | `UnRAR.exe` embarcado e versionado no repositório | Decisão: UNRAR 6.11 x64 *freeware* em `bin/`, versionado no git e embarcado no executável. Licença: redistribuição permitida para extração, desde que o binário não seja modificado; o texto da licença deve acompanhar o binário. **Hoje não acompanha** (`bin/` contém só o `UnRAR.exe`): ver tarefa T10b. Atualização: substituir o binário, revalidar RNF04-CA3/CA5 com as fixtures RAR4/RAR5/*solid* e reconfirmar o `CREATE_NO_WINDOW` do `rarfile`. Alternativas descartadas: exigir WinRAR instalado (viola RNF01); bibliotecas RAR em Python puro (sem suporte confiável a RAR5 / *solid*). |
| **ADR-13** | Miniaturas por gerador único (`iter_thumbnails`) | Contexto: a spec inicial previa `build_thumbnail(comic_path, page_index)`, que reabriria a HQ a cada miniatura e, em CBR, reextrairia o arquivo inteiro (custo O(n²), contrariando a ADR-06). Decisão: um gerador abre a HQ uma vez, produz `(índice, miniatura)` e libera o arquivo ao ser fechado, permitindo interrupção entre páginas (RF12-CA2). |

### 5.5. `docs/README.md` — Próximos IDs Livres
Depois deste pacote: `FEAT-14`, `FIX-02`, `RF22`, `RNF09`, `US14`, `QA-07`, `ADR-14`. (Os IDs RF21, RNF08, QA-02 a QA-06 e ADR-09 a ADR-13 ficam **reservados** pelo FIX-01 a partir da abertura deste documento.)

### 5.6. `specs/REQUISITOS.md` — nova §7 Matriz de Rastreabilidade
Tabela com **todos** os critérios `RFxx-CAn` / `RNFxx-CAn`: `Critério | Verificação (Automática / Manual) | Teste ou roteiro`. Preencher a partir dos testes existentes (os nomes em português dos testes permitem o mapeamento). Já identificados como **manuais**: RNF01-CA1, RNF01-CA2, RNF04-CA5 (parte do executável), RNF05-CA1 e RNF05-CA2 (medições de desempenho), RNF08-CA1 (no executável). Critério sem teste e sem roteiro = **lacuna**, listada nas Tarefas para decisão (criar teste ou aceitar como manual).

## 6. Teste de Regressão
* **Parte de código:** `tests/ui/test_reader_view.py::test_botao_fechar_volta_para_a_serie` — comentário `# FIX-01 / RF14-CA3`. Verifica que o botão existe, está visível com uma HQ aberta, que o clique emite `close_requested` e que, na `MainWindow`, a Tela da Série volta a ser exibida com o bookmark gravado.
- [ ] O teste **falha** sem a correção (o botão não existe) e **passa** com ela.
* **Trava obsoleta:** `test_trava_de_processo_encerrado_nao_bloqueia_abertura` — `# FIX-01 / RNF07-CA1` (ou registro como manual, ver 4.1-3).
* **Parte de spec:** a matriz da seção 5.6 é a verificação. Nenhum critério pode ficar sem linha.

## 7. Tarefas
Execução em 4 blocos, com revisão do usuário ao fim de cada um: **Bloco 1** (T1–T6), **Bloco 2** (T7, T8, T13), **Bloco 3** (T9, T10, T10b), **Bloco 4** (T11, T12 + Definição de Pronto). Ordem: primeiro o código (fecha o Tipo A e valida RF21-CA3 antes de sincronizar), depois a documentação.

### Código
- [x] **T1** — Teste do botão "Fechar" (falhando) — `RF14-CA3` · `test_botao_fechar_volta_para_a_serie` e `test_botao_fechar_acompanha_o_redimensionamento` falharam com `AttributeError: 'ReaderView' object has no attribute 'close_button'`
- [x] **T2** — Botão "Fechar" no `ReaderView` + estilo no `dark_theme.qss` — `RF14-CA3` · `close_button` (`QPushButton#readerCloseButton`, 32×32, margem `OVERLAY_MARGIN` = 16 px, âmbar no *hover*), reposicionado no `resizeEvent`
- [x] **T3** — Corrigir o comentário do *debounce* em `reader_view.py` — `QA-06`
- [x] **T4** — Teste da trava obsoleta (ou justificar como manual) — `RNF07-CA1` · automatizado: `test_trava_de_processo_encerrado_nao_bloqueia_abertura` (subprocesso adquire a trava e é encerrado com `kill()`, sem liberá-la)
- [x] **T5** — Testes que faltarem para os critérios novos que descrevem comportamento existente: `RF06-CA4` (já coberto), `RF21-CA1..3`, `RF02-CA3`, `RF19-CA4`, `RF12-CA4`, `RF13-CA2`, `RF14-CA4` — reaproveitar testes existentes quando já cobrirem
  * Já cobertos por testes existentes: `RF06-CA4` (`test_releitura_nao_desmarca_hq_lida`), `RF02-CA3` (`test_sem_raiz_configurada_convida_a_selecionar_pasta`, `test_raiz_inexistente_convida_a_selecionar_pasta_sem_apagar_estado`, `test_raiz_sem_series_mostra_mensagem`), `RF12-CA4` — pré-seleção e botão (`test_reabrir_seletor_parte_da_hq_da_capa_atual`, `test_botao_de_confirmar_exige_pagina_selecionada`), `RF13-CA2` (`test_duplo_clique_em_hq_valida_abre_o_leitor` + volta do título em `test_botao_fechar_volta_para_a_serie`), `RF14-CA4` (testes do leitor que verificam `page_indicator`)
  * Novos: `test_viradas_seguidas_adiam_a_gravacao_do_bookmark` (`RF06-CA5`), `test_pagina_ilegivel_mostra_quadro_substituto_e_leitura_continua` (`RF21-CA1..3`, **RF21-CA3 confirmado**), `test_varredura_em_andamento_e_indicada_no_cabecalho` (`RF19-CA4`), `test_cabecalho_exibe_a_raiz_com_caminho_completo_no_tooltip` (`RF02-CA4`, parte do cabeçalho), `test_duplo_clique_na_miniatura_confirma_a_capa` (`RF12-CA4`, duplo clique)
- [x] **T6** — `pytest` completo passando (registrar o total) · **240 testes** (232 + 8 novos); `tests/ui` repetido 5 vezes sem falhas

### Documentação
- [x] **T7** — Aplicar a seção 5.1 em `specs/REQUISITOS.md` (RF02, RF06, RF12, RF13, RF14, RF19 modificados; RF21 e RNF08 adicionados; convenção de verificação)
- [x] **T8** — Aplicar a seção 5.2 (QA-02 a QA-06)
- [x] **T9** — Aplicar os itens 1 a 20 da seção 5.3 em `ARQUITETURA.md` e `TECNICO.md`
- [x] **T10** — Criar ADR-09 a ADR-13 e atualizar o índice da ARQ §5
- [x] **T10b** — Decisão do usuário (2026-10-29): opção 1, usar o UnRAR oficial da RARLAB. Resultado: `bin/UnRAR.exe` **7.23** estável + `bin/license.txt` (licença freeware), embarcados no `HqFriend.spec`; ADR-12, TECNICO §1.4/§5 e README atualizados; 240 testes passando e build conferido. Plano original: copiar o texto da licença do UnRAR (`license.txt` da instalação local do WinRAR, mesma origem do binário — Registro #009) para `bin/license.txt`, embarcá-lo no `HqFriend.spec` (`datas`) e registrar em TECNICO §1.4 e na ADR-12
- [ ] **T11** — Montar a matriz de rastreabilidade (seção 5.6) e listar as lacunas encontradas
- [ ] **T12** — Atualizar o `README.md` da raiz (atalhos: botão "Fechar" do leitor)
- [x] **T13** — Atualizar a versão da spec no topo do `REQUISITOS.md` para `1.0.1` e os próximos IDs livres em `docs/README.md` (seção 5.5) · próximos IDs já estavam atualizados desde a abertura do pacote; a linha de reservas passou a listar só ADR-09 a ADR-13, ainda pendentes do Bloco 3

### Desvios em Relação a Este Plano
| Planejado | Implementado | Motivo | Doc a atualizar |
| :--- | :--- | :--- | :--- |
| RF14-CA3: "depois do clique o teclado continua controlando o leitor até ele fechar" | O botão não recebe foco (`Qt.NoFocus`): as teclas nunca saem do leitor, inclusive após passar o mouse ou clicar perto do botão | A redação original não era verificável (o clique fecha o leitor) | `specs/REQUISITOS.md` RF14-CA3 (Bloco 2): "o botão não recebe foco do teclado; as teclas de navegação continuam indo para o leitor" |
| RF02-CA4: verificação automática | Cabeçalho coberto por teste; "abre maximizado" (`main.py`, `showMaximized()`) fica como verificação **manual** | `main()` não é exercitado pelos testes de UI | Matriz de rastreabilidade (Bloco 4) |
| RF14-CA3 (Bloco 2): texto do delta | Aplicado com a redação corrigida do desvio acima e com "acompanha o redimensionamento da janela", já verificado por `test_botao_fechar_acompanha_o_redimensionamento` | Deixar no critério tudo o que o teste verifica | — (já aplicado) |
| Seção 7 (Matriz) criada no Bloco 4 | Título e aviso "em construção" criados no Bloco 2; conteúdo continua no Bloco 4 (T11) | A convenção de verificação do cabeçalho, aplicada na T7, já aponta para a seção 7 | — (T11) |
| T9: corrigir pontos específicos dos diagramas da ARQ §4 (itens 5 a 9) | Os três diagramas de sequência foram **reescritos** a partir do código; a §4.3 também mostra o caminho real do bookmark (memória → *debounce* → `flush()`), o `ExportWorker` e o botão "Fechar", e o §2 ganhou o nó `main.py` | Os diagramas tinham mais divergências do que as listadas (ex: `RServ->>Repo` direto, `export_current_view` chamado no `ExportService`) | — (já aplicado) |
| T9, item 15: capas "em TECNICO §3" | Nova seção **TECNICO §3.7 Capas e Miniaturas** | As regras de capa estavam espalhadas e incompletas | — (já aplicado) |
| T9: TECNICO §6.2 não estava na lista | Corrigido: trocar de HQ no seletor **não** chama `wait()` (interrompe sem bloquear e descarta as miniaturas pela geração); só fechar ou cancelar o diálogo aguarda os workers | Divergência encontrada ao revisar o código durante a T9 | — (já aplicado) |
| T10b: copiar `License.txt` da instalação do WinRAR | **Não executado** | O arquivo é o EULA do WinRAR (avaliação, 40 dias), não a licença freeware do UnRAR. A cláusula 3a permite distribuir separadamente os componentes do UnRAR, mas distribuir o EULA do WinRAR como "licença do UnRAR" seria impreciso | Decisão do usuário; depois, ADR-12 (Consequências), TECNICO §1.4 e `HqFriend.spec` |
| T10b, opção 1: binário e licença do pacote *UnRAR for Windows* | Binário **7.23 estável** extraído do instalador oficial do WinRAR 7.23; `license.txt` do pacote *UnRAR for Windows* | O pacote avulso traz hoje o **7.30 beta 2** e a RARLAB não oferece versões anteriores dele; para não distribuir uma beta numa correção, o binário veio da versão estável. Pacotes verificados pela assinatura da win.rar GmbH e extraídos sem executar | — (ADR-12 atualizada) |
| T10b: só licença (sem trocar o binário) | Binário atualizado de **6.11 para 7.23** | Consequência da opção 1; risco de regressão coberto pelos testes de RAR e pela validação do executável no Bloco 4 | Bloco 4: validar `.cbr` no `.exe` |
| RF12-CA4: duplo clique via `QTest.mouseDClick` | Teste usa `mouseClick` + `mouseDClick` | No Qt 6, `mouseDClick` sozinho não gera `itemDoubleClicked` (é como o utilitário de teste funciona; o duplo clique real funciona) | `specs/TECNICO.md` §7, armadilhas de teste (Bloco 3) |

## 8. Definição de Pronto
- [ ] Teste de regressão do botão adicionado (falha sem a correção) e `pytest` passando por completo
- [ ] Delta da seção 5 aplicado em `specs/` e `adr/`, com desvios da seção 7 levados à spec
- [ ] Matriz de rastreabilidade sem critérios órfãos (lacunas decididas)
- [ ] Executável gerado e o botão "Fechar" conferido manualmente (RNF08-CA1 no mesmo roteiro)
- [ ] `STATUS_PROJETO.md`: quadro atualizado e novo registro no histórico
- [ ] Pasta do pacote movida para `docs/archive/v1.0.1/`; tag `v1.0.1`

## 9. Aprovação
- [x] Decisões QA-05 e QA-06 tomadas pelo usuário (2026-10-29)
- [x] Este documento revisado e aprovado para implementação (data: 2026-10-29)
