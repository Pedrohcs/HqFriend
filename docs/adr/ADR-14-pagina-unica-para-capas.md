# ADR-14 — Leitura de Página Única para Gerar Capas (`read_page`)

* **Status:** `Aceita`
* **Data:** 2026-10-29 (proposta) · 2026-10-30 (aceita)
* **Origem:** FEAT-15
* **Requisitos relacionados:** RF11, RF22, RF23, RNF04, RNF05

## Contexto
Toda leitura de HQ passa por `open_archive()`. Num `.cbr`, a abertura extrai o arquivo **inteiro** para a RAM em uma única execução do `UnRAR.exe` (ADR-06) — a escolha certa para o leitor, que vai percorrer todas as páginas, e para o seletor de capa, que exibe todas as miniaturas (ADR-13).

Para gerar uma capa, porém, só uma página interessa. Na v1.1 isso já acontece uma vez por série (capa padrão da série). Com a FEAT-15, cada HQ ganha capa própria (RF22): abrir uma série de 100 HQs `.cbr` de ~100 MB faria o aplicativo descompactar ~10 GB e alocar cada arquivo inteiro na RAM, só para exibir 100 imagens de 400 px.

## Decisão
Criar em `src/infrastructure/archive_reader.py` a função **`read_page(path, page_index) -> bytes`**, usada pelo `CoverService` sempre que precisa de **uma** página (capa padrão e capa customizada, de séries e de HQs):

* Detecta o formato pelos *Magic Bytes* e aplica o mesmo filtro de imagens e a mesma ordenação natural de `open_archive()`, de modo que o índice `n` aponta para a mesma página nos dois caminhos.
* **ZIP:** abre o `ZipFile`, lê só a entrada da página e fecha.
* **RAR:** lista as entradas com `rarfile`, rejeita página protegida por senha e executa **um único** processo `UnRAR.exe p -inul -p- -@ -- <arquivo> <entrada>` com `CREATE_NO_WINDOW`, que escreve no `stdout` apenas aquela entrada. O total recebido precisa ser igual ao `file_size` da entrada; caso contrário, ou com código de saída diferente de `0`, lança `InvalidComicError`.
* **Como o `UnRAR.exe` casa a entrada** (verificado com o UnRAR 7.23 embarcado durante a implementação, 2026-10-29):
    * só aceita o caminho com `\` (`cap1\01.jpg`); com `/`, como o `rarfile` devolve, nada é extraído — o nome é convertido antes da chamada;
    * um nome sem pasta casa apenas a entrada da raiz, então páginas de mesmo nome em pastas diferentes não se confundem;
    * um argumento iniciado por `@` é lido como arquivo-lista; `-@` desliga esse comportamento.
* Índice inexistente lança `IndexError`, como `get_page_bytes()`, para o chamador distinguir página inexistente de HQ inválida (RF23-CA5).
* O leitor (`ReaderService`) e o seletor de capa (`iter_thumbnails`) continuam usando `open_archive()`.

## Alternativas descartadas
* **Continuar com `open_archive()` para as capas:** custo proporcional ao tamanho total dos arquivos, não ao número de capas; inviável para séries grandes (RNF05-CA4).
* **`rarfile.RarFile.read(entry)`:** também chama o `UnRAR.exe`, mas deixa a forma da chamada a cargo da biblioteca, cuja supressão de janela precisa ser reconfirmada a cada versão (`TECNICO.md` §6, item 1); a chamada direta mantém o mesmo controle de processo, código de saída e tamanho já usado na ADR-06.
* **Gerar as capas das HQs com `iter_thumbnails`:** abre o arquivo inteiro da mesma forma; só resolve o problema das miniaturas, não o das capas.

## Consequências
* O custo de gerar uma capa passa a depender do tamanho da página, não do arquivo. Em RAR *solid*, o `UnRAR.exe` ainda descompacta os dados que antecedem a entrada no fluxo *solid*; como a primeira página costuma ser a primeira entrada, o caso comum é rápido.
* A capa padrão da série (RF11) muda de caminho interno sem mudar de comportamento.
* Existem dois caminhos de extração RAR; ambos ficam em `archive_reader.py` e compartilham a listagem, o filtro e a ordenação.
* Um nome de entrada que o `UnRAR.exe` trate como máscara (`*`, `?`, só possíveis em arquivos criados fora do Windows) extrai mais de uma entrada; a verificação de tamanho converte isso em capa indisponível, nunca em página errada.
* **Verificação:** RNF04-CA6 — bytes idênticos aos de `open_archive().get_page_bytes()` (que a ADR-06 já compara com `rarfile`) em ZIP, RAR4, RAR5, RAR5 *solid* e na fixture `subpastas` (mesmo nome em subpastas e nome iniciado por `@`), e um único processo por chamada (`tests/infrastructure/test_archive_reader.py`). Retirar a conversão de `/` ou o `-@` faz os testes falharem. **Validação no executável (2026-10-30):** roteiros M2 (passo 7, capas de `.cbr` e `.cbz` reais, sem janela de console) e M3 (passo 3, série com 100+ HQs `.cbr` sem capas em cache, com a Tela da Série abrindo de imediato e respondendo durante a geração) confirmados pelo usuário. O tempo por capa não foi informado na validação, então não há medição numérica registrada; a aceitação se apoia na verificação automática acima e na responsividade confirmada no M3.
