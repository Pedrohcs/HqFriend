# FIX-NN — <Título curto do defeito>

* **Status:** `pendente` | `em andamento` | `concluida` | `bloqueada` | `cancelada`
* **Branch:** `fix/FIX-NN-<slug>`
* **Severidade:** `crítica` (perda de dados / app não abre) | `alta` (função principal quebrada) | `média` | `baixa`
* **Versão afetada:** v1.X · **Corrigido em:** v1.X.Y
* **Responsável:** <nome / papel>
* **Aberto em:** AAAA-MM-DD

## 1. Classificação (preencha antes de qualquer código)
- [ ] **Tipo A — Código diverge da spec.** A spec está correta; só o código muda. Critério violado: `RFxx-CAn`.
- [ ] **Tipo B — Spec errada, ambígua ou incompleta.** O comportamento esperado não estava (bem) especificado; a spec muda junto (seção 5).
- [ ] **Não é FIX:** o comportamento está de acordo com a spec e o pedido é por outro comportamento → abrir uma **FEAT**.

## 2. Comportamento
* **Esperado:** <o que deveria acontecer, citando o requisito/critério>
* **Observado:** <o que acontece de fato>
* **Passos para reproduzir:**
  1. <...>
  2. <...>
* **Ambiente:** <código-fonte ou `.exe`; versão; tipo de arquivo (CBZ / RAR4 / RAR5 / solid); tamanho da biblioteca>
* **Evidência:** <trecho do `hqfriend.log`, captura de tela, arquivo de exemplo>

## 3. Causa Raiz
<Por que aconteceu (não apenas onde). Arquivo e função. Por que os testes existentes não pegaram.>

## 4. Correção
* **Arquivos alterados:** <...>
* **Abordagem:** <...>
* **Impacto no `state.json`:** <nenhum / corrige dados gravados incorretamente — como os estados existentes são tratados (ver `ARQUITETURA.md` §3.3)>

## 5. Delta de Spec (somente Tipo B)
<!-- Mesmo formato do spec.md de FEAT: requisito inteiro com o texto novo, pronto para colar. -->
#### RFxx — <Título>
<Texto corrigido>
* **RFxx-CAn:** <critério novo ou corrigido que teria detectado o defeito>

> **O que mudou:** <...>

## 6. Teste de Regressão
* **Teste:** `tests/<...>::test_<...>` — comentário `# FIX-NN / RFxx-CAn`
- [ ] O teste **falha** sem a correção e **passa** com ela (confirmado)

## 7. Definição de Pronto
- [ ] Teste de regressão adicionado e `pytest` passando por completo
- [ ] Tipo B: delta da seção 5 aplicado em `specs/`
- [ ] `STATUS_PROJETO.md`: quadro atualizado e novo registro no histórico
- [ ] Pasta do pacote movida para `docs/archive/<versão>/`
