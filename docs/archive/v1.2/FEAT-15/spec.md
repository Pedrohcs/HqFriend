# FEAT-15 — Capa das HQs e grade de capas na Tela da Série

* **Status:** `concluida`
* **Versão alvo:** v1.2
* **Branch:** `feat/FEAT-15-capa-das-hqs`
* **Responsável:** Tech Lead / Analista de Requisitos Sênior
* **Criada em:** 2026-10-29

> **O que é este arquivo:** o **delta** dos requisitos — só o que muda em relação a `docs/specs/REQUISITOS.md`. Não copie requisitos que não mudam. Na etapa de Sincronização, este conteúdo é aplicado na spec vigente.
>
> **Aplicação antecipada:** a pedido do responsável pelo produto, o delta abaixo **já foi aplicado** em `docs/specs/` e `docs/adr/` **nesta branch**, antes da implementação. A branch só vai para a `main` com o código pronto; a etapa de Sincronização passa a ser a conferência da spec contra o código, levando a ela os desvios anotados em `tasks.md`.

## 1. Motivação

Hoje a Tela da Série é uma lista de texto com duas colunas (nome do arquivo e status). Numa série com dezenas de edições, nomes como `Batman_037.cbz` e `Batman_038.cbz` são difíceis de distinguir, e o usuário não tem pista visual de qual edição é qual. A Tela Inicial já resolve isso para as séries com capas (RF11, RF12); a Tela da Série não.

O pedido é levar o mesmo modelo para dentro da série: **cada HQ tem uma capa**, a Tela da Série vira uma **grade de capas com 5 colunas**, a capa padrão é a **primeira imagem do arquivo** e o usuário pode **trocá-la pelo botão direito**, como já faz com a série. Não é um FIX: o comportamento atual segue a spec (RF05-CA1 pede uma lista).

## 2. Escopo

* **Dentro:**
  * Grade de capas com 5 colunas fixas e rolagem vertical na Tela da Série, no lugar da lista (QA-11).
  * Capa padrão de cada HQ (primeira página, em ordem natural), gerada em segundo plano e guardada em cache.
  * Menu de contexto da HQ com "Selecionar imagem de capa" e "Restaurar capa padrão", além de "Marcar como lida/não lida" (RF08).
  * Seletor de capa da HQ: galeria das páginas da própria HQ (passo 2 do RF12, sem o passo 1) (QA-13).
  * Novo campo opcional no `state.json` (`custom_cover_page` na HQ): versão do schema `1.0` → `1.1`, com a implementação do mecanismo de migração previsto em `ARQUITETURA.md` §3.3 (é a primeira mudança de schema).
  * Leitura de uma única página do `.cbr` para gerar capas, sem extrair o arquivo inteiro (ADR-14).
* **Fora:**
  * Usar imagem externa (arquivo do computador) como capa — nem da série, nem da HQ.
  * Mudar a capa da série: ela continua independente das capas das HQs (QA-12, RF11 inalterado).
  * Gerar as capas das HQs de todas as séries na varredura da biblioteca (QA-14).
  * Detectar que um arquivo foi substituído por outro de mesmo nome para regerar a capa (mesma limitação da capa da série).
  * Atalhos novos na grade (ex: `Enter` para abrir a HQ), ordenação alternativa, filtros ou busca.
  * Limpeza automática do cache de capas de HQs removidas do disco (seguem a ADR-03: ficam como órfãs).

## 3. Delta de Requisitos

> Texto escrito com as decisões da seção 4 (QA-11 a QA-14, todas na opção recomendada).

### 3.1. ADICIONADO

#### RF22 — Capa Padrão da HQ
`Ativo` · Origem: FEAT-15

Toda HQ (`.cbr`/`.cbz`) válida possui uma capa, exibida no seu card na Tela da Série (RF05). Enquanto o usuário não escolher outra (RF23), a capa é a **primeira página do arquivo**, isto é, a primeira imagem na ordenação natural das páginas (RNF04, RF18). As capas são geradas em segundo plano ao abrir a série, apenas para as HQs que ainda não têm capa em cache (QA-14), e ficam guardadas para as próximas aberturas.

* **RF22-CA1:** Ao abrir a Tela da Série, cada HQ sem capa em cache exibe o *placeholder* "Carregando capa…" e as capas são geradas em segundo plano, na ordem da grade, aparecendo uma a uma sem travar a interface.
* **RF22-CA2:** A capa padrão é a primeira página do arquivo em ordem natural, gravada em `%DOCUMENTOS%\HqFriend\covers\<Série>\<arquivo>.png` (ex: `covers\Batman\Batman_01.cbz.png`), com no máximo 400 px de largura, mantendo a proporção e sem ampliar.
* **RF22-CA3:** HQ cuja capa já está em cache exibe a capa sem reabrir o arquivo compactado, inclusive depois de reiniciar o aplicativo.
* **RF22-CA4:** HQ inválida (RF20) ou com a primeira página ilegível exibe o *placeholder* "Sem capa"; a falha é registrada em log e não impede a geração das demais capas.
* **RF22-CA5:** Sair da Tela da Série (`Esc`, "Voltar") ou abrir uma HQ no leitor interrompe a geração após a capa em andamento, liberando o arquivo; ao voltar à Tela da Série, a geração continua pelas capas que faltam.

#### RF23 — Seleção da Capa da HQ (Menu de Contexto)
`Ativo` · Origem: FEAT-15

Na Tela da Série, ao clicar com o botão direito sobre uma HQ, o menu exibe **"Selecionar imagem de capa"** e, quando a HQ tiver capa customizada, **"Restaurar capa padrão"**, além da opção de marcar como lida ou não lida (RF08). "Selecionar imagem de capa" abre a galeria de miniaturas das páginas **da própria HQ**, onde o usuário clica numa página para defini-la como capa (QA-13). A capa da HQ é independente da capa da série (QA-12).

* **RF23-CA1:** O menu de contexto da HQ exibe "Selecionar imagem de capa" e, apenas quando há capa customizada, "Restaurar capa padrão"; as opções de RF08 continuam no menu.
* **RF23-CA2:** A galeria exibe apenas as páginas da HQ escolhida, carregadas em segundo plano; fechar o diálogo antes do fim interrompe o carregamento e libera o arquivo. A página da capa atual já vem selecionada (a página 1, se a capa for a padrão); "Definir como capa" só fica habilitado com uma página selecionada, e o duplo clique numa miniatura confirma. Numa HQ inválida, o diálogo exibe a mensagem de erro e nada é alterado.
* **RF23-CA3:** Ao confirmar a página, o arquivo da capa em `covers\<Série>\` e o `state.json` (`custom_cover_page` da HQ) são atualizados imediatamente e o card da HQ exibe a nova capa. O card da série na Tela Inicial não muda.
* **RF23-CA4:** "Restaurar capa padrão" regera a capa a partir da primeira página e remove a referência customizada do `state.json`.
* **RF23-CA5:** Se a capa customizada precisar ser regerada (arquivo do cache apagado) e a página registrada não existir mais no arquivo (ex: HQ substituída por versão menor), é usada a capa padrão e o problema é registrado em log.

#### US14 — Capas das HQs na Tela da Série
Como leitor, quero ver as HQs de uma série como uma grade de capas e poder escolher, pelo botão direito, qual página é a capa de cada HQ, para reconhecer cada edição de relance.

### 3.2. MODIFICADO

#### RF05 — Listagem de Obras da Série em Grade de Capas
`Ativo` · Origem: v1.0 (FEAT-10), FEAT-15

Ao acessar uma série, o sistema deve exibir todos os arquivos `.cbr` e `.cbz` pertencentes a ela em uma **grade de capas com 5 colunas**, em ordem natural (RF18), da esquerda para a direita e de cima para baixo. Cada card exibe a capa da HQ (RF22), o nome do arquivo e o status individual de leitura (Não lida, Em andamento com página atual, ou Lida).

* **RF05-CA1:** *(alterado)* A Tela da Série exibe as HQs em uma grade de capas em ordem natural (RF18); cada card mostra a capa, o nome do arquivo (abreviado com reticências quando não couber, com o nome completo no *tooltip*) e o status `Não lida`, `Em andamento – Pág. X/Y` ou `Lida`, nas cores do RNF08-CA2.
* **RF05-CA2:** *(novo)* A grade tem sempre 5 colunas: a largura dos cards acompanha a largura da janela, com a capa na proporção 2:3, e as linhas seguintes ficam acessíveis por rolagem vertical, sem rolagem horizontal. Abaixo de 120 px de largura por card, a largura para de diminuir e surge a rolagem horizontal (QA-11).

> **O que mudou:** a lista de duas colunas (HQ / Status) vira uma grade de capas com 5 colunas fixas (CA1 alterado, CA2 novo).
> **Impacto em critérios existentes:** RF05-CA1 alterado. Os testes de `tests/ui/test_series_view.py` que usam o `QTreeWidget` (`comic_list`, `comic_rows()`, `topLevelItem`) serão adaptados à grade, mantendo o que verificam (ordem, status, menu, duplo clique): `test_lista_hqs_da_serie_em_ordem_natural_com_status`, `test_mostra_hq_em_andamento_com_pagina`, `test_menu_marca_hq_como_lida_e_recalcula_serie`, `test_marcar_todas_como_lidas_conclui_a_serie`, `test_marcar_como_nao_lida_remove_indicacao_de_andamento`, `test_duplo_clique_solicita_abertura_da_hq`, `test_hq_invalida_mostra_erro_e_permanece_na_serie` e `test_hq_valida_nao_mostra_erro`. RF08, RF13 e RF20 não mudam de texto: o card da grade substitui a linha da lista.

#### RNF02 — Armazenamento de Memória e Estado
`Ativo` · Origem: v1.0 (FEAT-02, FEAT-03), FEAT-15

Toda a memória do sistema (diretório raiz configurado, progresso de leitura por arquivo, página atual/bookmark, status das séries, capas customizadas de séries e HQs e cache de capas) deve ser armazenada no diretório `%DOCUMENTOS%\HqFriend`, utilizando arquivo estruturado em formato **JSON** (`state.json`) e subpasta de cache de capas (`covers\`).
* *Integridade:* *(inalterado)* A gravação deve ser atômica. O sistema deve manter uma cópia de segurança (`state.json.bak`) da última versão válida carregada. Se o `state.json` estiver corrompido, o sistema deve preservá-lo para análise, restaurar a partir do `.bak` (ou iniciar com estado limpo, caso o backup também seja inválido) e avisar o usuário.
* *Versão do schema:* *(novo)* um `state.json` de versão anterior é migrado na carga, sem perda de dados; um `state.json` de versão mais nova que a suportada nunca é sobrescrito (`ARQUITETURA.md` §3.3).

Critérios de aceite:
* **RNF02-CA1** a **RNF02-CA4:** *(inalterados)*
* **RNF02-CA5:** *(novo)* Um `state.json` da versão `1.0` é carregado e migrado para `1.1` preservando raiz, progresso, preferências e capas das séries; antes da primeira gravação do estado migrado, uma cópia do arquivo original é guardada como `state.v1.0.json`.
* **RNF02-CA6:** *(novo)* Um `state.json` de versão mais nova que a suportada não é sobrescrito nem tratado como corrompido: o sistema avisa o usuário ("O arquivo de estado é de uma versão mais nova do HqFriend…") e encerra.

> **O que mudou:** a lista de dados guardados inclui as capas customizadas das HQs; entram as regras de versão do schema (CA5 e CA6), que a FEAT-15 implementa por ser a primeira mudança de schema. **Impacto em critérios existentes:** nenhum (CA1 a CA4 inalterados; o exemplo do contrato em `ARQUITETURA.md` §3.2 passa a mostrar a versão `1.1`).

#### RNF04 — Suporte a Formatos de Compactação em Memória
`Ativo` · Origem: v1.0 (FEAT-05, FEAT-13), FEAT-15

*(texto inalterado)*

* **RNF04-CA1** a **RNF04-CA5:** *(inalterados)*
* **RNF04-CA6:** *(novo)* Gerar a capa de um `.cbr` (da série ou da HQ) executa um único processo `UnRAR.exe` que extrai apenas a entrada da página necessária, sem extrair o arquivo inteiro para a RAM; os bytes obtidos são idênticos aos de `rarfile` (ADR-14).

> **O que mudou:** novo critério para a leitura de página única usada nas capas. **Impacto:** nenhum critério existente muda; o RNF04-CA3 continua valendo para a abertura no leitor e para o seletor de capa (ADR-06, ADR-13).

#### RNF05 — Desempenho de Renderização
`Ativo` · Origem: v1.0 (FEAT-07, FEAT-08, FEAT-09, FEAT-11), FEAT-15

A transição entre páginas no leitor deve ocorrer de maneira fluida (tempo de resposta inferior a 200ms após o carregamento do arquivo). A varredura da biblioteca, a geração de capas padrão (das séries e das HQs) e o carregamento da galeria de seleção de capas (RF12, RF23) devem ocorrer de forma assíncrona, mantendo a interface responsiva.

* **RNF05-CA1** a **RNF05-CA3:** *(inalterados)*
* **RNF05-CA4:** *(novo)* A Tela da Série de uma série com 100+ HQs abre de imediato e continua respondendo (rolagem, menu de contexto, duplo clique, "Voltar") enquanto as capas das HQs são geradas.

> **O que mudou:** a geração das capas das HQs e a galeria do RF23 entram no requisito de assincronia (CA4 novo). **Impacto:** o roteiro manual M3 ganha a medição com uma série de 100+ HQs.

#### US06 — Listagem e Marcação Manual de HQ
Como leitor, quero abrir uma série para ver seus arquivos `.cbr`/`.cbz` **em uma grade de capas**, em ordem natural, e poder clicar com o botão direito em uma HQ específica para marcá-la manualmente como "Lida" ou "Não lida".

> **O que mudou:** "lista" → "grade de capas". A escolha da capa da HQ fica na nova US14.

#### Outros documentos afetados (sem mudança de requisito)
* `specs/REQUISITOS.md`: versão da spec `1.2`; §2.3 renomeada para "Capas de Séries e HQs"; §5 (grafo: Tela da Série em grade e menu da HQ com capa); §6 (QA-11 a QA-14); §7 (matriz com as linhas novas e roteiros M2/M3).
* `specs/ARQUITETURA.md`: §2 (diagrama, `SeriesView`, `CoverPickerDialog` em modo HQ, `ComicCoverWorker`, `CoverService`, `archive_reader.read_page`, migrações do `JsonStateRepository`); §3.1 (pasta `covers\<Série>\`); §3.2 (contrato `1.1` com `custom_cover_page`); §3.3 (mecanismo de migração implementado); §4.4 (novo fluxo: grade e capas das HQs); §5 (ADR-14).
* `specs/TECNICO.md`: §2 (árvore de fontes); §3.2 (schema e migração); §3.3 (leitura de página única); §3.7 (capas das HQs); §4.1, §4.3 e nova §4.4 (grade da Tela da Série); §6 (riscos); §7 (testes).
* `adr/ADR-14-pagina-unica-para-capas.md` (nova).
* `README.md` (raiz) — na Sincronização: funcionalidades, fluxo e pasta `covers\`.

### 3.3. REMOVIDO

Nada.

## 4. Questões Decididas

| ID | Questão | Opções | Decisão |
| :--- | :--- | :--- | :--- |
| **QA-11** | Como funciona a "grade 5x5" da Tela da Série? | **A. (recomendada)** Sempre 5 colunas; os cards acompanham a largura da janela e as linhas seguem com rolagem vertical (~5 linhas visíveis em 1080p). **B.** Páginas de exatamente 25 HQs (5×5), com botões Anterior/Próxima. **C.** Colunas responsivas, com cards de tamanho fixo, como na Tela Inicial. | decidida em 2026-10-29: opção A |
| **QA-12** | A capa escolhida para uma HQ afeta a capa da série? | **A. (recomendada)** Não: são independentes; a capa padrão da série continua sendo a primeira página da primeira HQ (RF11). **B.** Sem capa customizada, a série herda a capa (padrão ou customizada) da primeira HQ. | decidida em 2026-10-29: opção A |
| **QA-13** | De onde vem a imagem ao escolher a capa de uma HQ? | **A. (recomendada)** Só das páginas da própria HQ: o seletor abre direto na galeria (passo 2 do RF12). **B.** Reaproveitar o fluxo em 2 etapas, permitindo usar a página de outra HQ da série. **C.** Também permitir uma imagem do computador. | decidida em 2026-10-29: opção A |
| **QA-14** | Quando as capas das HQs são geradas? | **A. (recomendada)** Ao abrir a série, só para as HQs dela que não têm capa em cache; as próximas aberturas usam o cache. **B.** Na varredura da biblioteca, para todas as HQs de todas as séries, em segundo plano. Abre milhares de arquivos na primeira execução e disputa disco e CPU com as capas das séries. | decidida em 2026-10-29: opção A |

## 5. Aprovação
- [x] Delta revisado e aprovado pelo responsável pelo produto (data: 2026-10-29), com as opções recomendadas nas QA-11 a QA-14
