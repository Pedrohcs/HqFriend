# FEAT-14 — Manter o zoom ao trocar de página

* **Status:** `concluida`
* **Versão alvo:** v1.1
* **Branch:** `feat/FEAT-14-manter-zoom-entre-paginas`
* **Responsável:** Tech Lead / Analista de Requisitos Sênior
* **Criada em:** 2026-10-29

> **O que é este arquivo:** o **delta** dos requisitos — só o que muda em relação a `docs/specs/REQUISITOS.md`. Não copie requisitos que não mudam. Na etapa de Sincronização, este conteúdo é aplicado na spec vigente.

## 1. Motivação

Hoje, ao virar a página (`→`, `Espaço`, `←`), o leitor descarta o zoom e volta ao ajuste à tela (*Fit-to-View*). É o comportamento que a spec exige (RF15-CA2) e que o código implementa (`ReaderView.render_pages()` chama `reset_zoom_fit_to_view()`). Por isso esta mudança é uma **FEAT**, não um FIX: o código segue a spec, mas o usuário quer outro comportamento.

Quem lê com zoom (páginas com texto pequeno, telas menores, leitura quadro a quadro) precisa refazer `Ctrl + Scroll` **a cada página**. É um atrito repetido dezenas de vezes por HQ. Se nada mudar, esse uso continua cansativo e o zoom fica pouco útil na prática.

## 2. Escopo

* **Dentro:**
  * Ao virar a página dentro da HQ aberta, o **nível de zoom** escolhido pelo usuário é mantido.
  * Regra de **posição** da nova página quando ela é exibida ampliada (QA-08).
  * Regra para a alternância de modo `Ctrl + S` com zoom ativo (QA-09).
  * Forma explícita de **voltar ao ajuste à tela**, já que o zoom deixa de ser desfeito sozinho (QA-10).
  * Atualização dos testes de UI que hoje verificam o reset do zoom (RF15-CA2).
* **Fora:**
  * Alterar os limites (0,5x–5x) ou o passo (1,15) do zoom (RF15-CA1 continua igual).
  * Persistir o zoom no `state.json` ou entre HQs/reinícios do app (QA-07).
  * Zoom por teclado (`Ctrl + +` / `Ctrl + -`), modos "ajustar à largura"/"ajustar à altura" e leitura com rolagem contínua.
  * Mudanças no `Ctrl + P`: a exportação continua ignorando o zoom (RF17).

## 3. Delta de Requisitos

### 3.1. ADICIONADO

Nenhum requisito novo: o comportamento é uma extensão do controle de zoom e entra como critérios do **RF15**.

### 3.2. MODIFICADO

> O texto abaixo segue as decisões da seção 4 (todas na opção recomendada, A).

#### RF15 — Controle de Zoom (`Ctrl + Scroll`)
`Ativo` · Origem: v1.0 (FEAT-11), FIX-01, FEAT-14

O usuário deve poder ampliar (zoom in) ou reduzir (zoom out) o tamanho da página atual utilizando o atalho `Ctrl + Scroll do mouse`. O nível de zoom escolhido é **mantido ao trocar de página** durante a leitura da HQ, para que o usuário não precise refazê-lo a cada página. O zoom é relativo ao ajuste à tela (*Fit-to-View*) de cada página: 1x é a página inteira visível; 2x é o dobro desse tamanho, qualquer que seja a resolução da página.

* **RF15-CA1:** *(inalterado)* `Ctrl + Scroll` aplica zoom ancorado no cursor, limitado entre 0,5x e 5x; com zoom acima de 1x, a página pode ser arrastada com o mouse.
* **RF15-CA2:** *(alterado)* Virar a página (`→`, `Espaço`, `←`) **mantém o nível de zoom** atual, aplicado sobre o ajuste à tela da nova página (ou do novo par). Alternar o modo (`Ctrl + S`) restaura o ajuste à tela (QA-09). Ao redimensionar a janela, a página acompanha o novo tamanho se estiver ajustada à tela (zoom 1x); com outro zoom, o zoom escolhido é preservado.
* **RF15-CA3:** *(novo)* Ao virar a página com zoom acima de 1x, a nova página é exibida a partir do **canto superior esquerdo** (início da leitura), tanto ao avançar quanto ao voltar (QA-08). Com zoom de até 1x, a página fica centralizada, como hoje.
* **RF15-CA4:** *(novo)* O zoom vale para a HQ aberta: ao fechar a HQ e abrir esta ou outra, a leitura começa com o ajuste à tela (QA-07). O zoom não é gravado no `state.json`.
* **RF15-CA5:** *(novo)* `Ctrl + 0` restaura o ajuste à tela (zoom 1x) a qualquer momento da leitura (QA-10).

> **O que mudou:** antes, toda virada de página desfazia o zoom; agora o zoom acompanha a leitura até o usuário fechar a HQ, alternar o modo ou pressionar `Ctrl + 0`. Foram acrescentadas a regra de posição da página ampliada (CA3), o escopo do zoom (CA4) e o atalho para restaurar o ajuste à tela (CA5).
> **Impacto em critérios existentes:** RF15-CA2 alterado. O teste `ui/test_reader_view.py::test_ctrl_scroll_aplica_zoom_e_virar_pagina_reseta` deixa de valer como está (verifica o reset ao virar a página) e será reescrito; `ui/test_reader_view.py::test_ctrl_s_e_redimensionar_reajustam_a_pagina_a_tela` continua válido com a QA-09 na opção A. A matriz de rastreabilidade (`REQUISITOS.md` §7) ganha as linhas RF15-CA3 a CA5.

#### US09 — Controle de Zoom na Leitura
Como leitor, quero usar `Ctrl + Scroll do mouse` para ajustar o zoom da página durante a leitura **e que esse zoom seja mantido quando eu virar a página**, para não precisar ajustá-lo de novo a cada página.

> **O que mudou:** a história passa a incluir a manutenção do zoom entre páginas.

#### Outros documentos afetados na Sincronização (sem mudança de requisito)
* `specs/REQUISITOS.md` §6: QA-07 a QA-10 registradas como decididas; §7: linhas RF15-CA2 a CA5 da matriz.
* `specs/TECNICO.md` §4.2 ("Regra validada" do reset de zoom) e §4.3 (mapa de atalhos: `→`/`Espaço`/`←` deixam de resetar o zoom; nova linha `Ctrl + 0`).
* `specs/ARQUITETURA.md` §4.3 (diagrama de leitura: "Nova(s) página(s), zoom ajustado à tela" → "zoom mantido").
* `README.md` (raiz): funcionalidades e tabela de atalhos do leitor.

### 3.3. REMOVIDO

Nada.

## 4. Questões Decididas

| ID | Questão | Opções | Decisão |
| :--- | :--- | :--- | :--- |
| **QA-07** | Por quanto tempo o zoom é mantido? | **A. (recomendada)** Enquanto a HQ estiver aberta; abrir uma HQ começa no ajuste à tela. Sem mudança no `state.json`. **B.** Durante toda a execução do app, valendo também para a próxima HQ aberta. Sem mudança no `state.json`. **C.** Persistido no `state.json` como preferência global, como o modo de página (RF16-CA4). Exige nova versão do schema e migração (`ARQUITETURA.md` §3.3). | decidida em 2026-10-29: opção A |
| **QA-08** | Com a página ampliada, que parte da nova página aparece ao virar? | **A. (recomendada)** Canto superior esquerdo (início da leitura ocidental), ao avançar e ao voltar. **B.** Topo da página, centralizado na horizontal. **C.** A mesma posição relativa da página anterior (útil para comparar quadros, ruim para ler a página do início). **D.** Avançar abre no canto superior esquerdo; voltar abre no canto inferior direito (continua de onde a leitura parou). | decidida em 2026-10-29: opção A |
| **QA-09** | O que acontece com o zoom ao alternar o modo único/duplo (`Ctrl + S`)? | **A. (recomendada)** Restaura o ajuste à tela, como hoje: a troca de layout muda o tamanho do conteúdo, e manter o fator gera um enquadramento inesperado. **B.** Mantém o fator de zoom também nesse caso. | decidida em 2026-10-29: opção A |
| **QA-10** | Como o usuário volta ao ajuste à tela, já que virar a página deixa de fazer isso? | **A. (recomendada)** Atalho `Ctrl + 0` (convenção de navegadores e leitores de imagem). **B.** Sem atalho novo: reduzir com `Ctrl + Scroll` ou alternar o modo duas vezes. **C.** `Ctrl + 0` e também duplo clique na página. | decidida em 2026-10-29: opção A |

## 5. Aprovação
- [x] Delta revisado e aprovado pelo responsável pelo produto (data: 2026-10-29), com as opções recomendadas nas QA-07 a QA-10
