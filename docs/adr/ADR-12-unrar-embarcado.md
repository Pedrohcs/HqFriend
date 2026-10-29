# ADR-12 — `UnRAR.exe` Embarcado e Versionado no Repositório

* **Status:** `Aceita`
* **Data:** 2026-10-24 (registrada retroativamente pelo FIX-01 em 2026-10-29; binário atualizado para 7.23 e licença incluída pelo FIX-01)
* **Origem:** v1.0 (FEAT-05, FEAT-13 — Registro #009); FIX-01 (T10b)
* **Requisitos relacionados:** RNF01, RNF04

## Contexto
Arquivos `.cbr` usam o formato RAR, cuja descompactação não existe na biblioteca padrão do Python. O `rarfile` lista as entradas, mas depende de um executável externo para extrair. O usuário não deve precisar instalar o WinRAR (RNF01), e a extração precisa suportar RAR4, RAR5 e RAR5 *solid* (RNF04).

## Decisão
* Usar o **`UnRAR.exe` x64 freeware** da RARLAB (win.rar GmbH), sempre em versão **estável**, em `bin/UnRAR.exe`, acompanhado do texto oficial da **licença freeware do UnRAR** em `bin/license.txt`.
* Os dois arquivos são **versionados no git** e embarcados no executável (`HqFriend.spec`: `binaries` e `datas`, ambos em `_internal\bin\`). O binário é resolvido por `config.UNRAR_BINARY_PATH` / `get_resource_path`.
* O `rarfile` usa esse binário para listar as entradas; a extração é feita em passada única (ADR-06), sempre com `CREATE_NO_WINDOW`.

### Versão e procedência atuais

| Arquivo | Versão | Origem | SHA-256 |
| :--- | :--- | :--- | :--- |
| `bin/UnRAR.exe` | **UNRAR 7.23 x64 freeware** (`7.23.0`) | Extraído do instalador oficial `winrar-x64-723.exe` (rarlab.com/rar/winrar-x64-723.exe, assinatura Authenticode válida de **win.rar GmbH**); o próprio `UnRAR.exe` também é assinado pela win.rar GmbH | `0d3715001790f0fd18d3e850f947b540530b2d2deb9a2e6a9e84f2ed7b234235` |
| `bin/license.txt` | "UnRAR — License for use and distribution of FREEWARE version" | Pacote oficial *UnRAR for Windows* (rarlab.com/rar/unrarw64.exe, assinatura válida de **win.rar GmbH**) | `48c3ebe5e74e4b9312cdf6b337b04f87f220416cb54ca4f4df01a1f504859d09` |

A licença freeware permite distribuir o UnRAR livremente, inclusive dentro de outros pacotes de software (item 2), sem garantia (item 3) e proibindo o uso do código para recriar o algoritmo de compressão RAR (item 4).

**Por que o binário não veio do pacote *UnRAR for Windows*:** em 2026-10-29 o pacote avulso (`unrarw64.exe`) da RARLAB trazia o **UnRAR 7.30 beta 2**; a RARLAB só oferece esse pacote na versão mais recente, sem links por versão. Para não distribuir uma versão beta, o binário estável (7.23, mesma versão do WinRAR estável) foi extraído do instalador oficial do WinRAR 7.23, e a licença, do pacote avulso — ambos verificados pela assinatura digital e extraídos sem executar os instaladores.

**Histórico:** v1.0 — UNRAR 6.11 x64 (copiado da instalação local do WinRAR, Registro #009, sem texto de licença). FIX-01 — UNRAR 7.23 x64 + `license.txt`.

## Alternativas descartadas
* **Exigir o WinRAR instalado:** viola o RNF01.
* **Bibliotecas RAR em Python puro ou bindings de terceiros:** sem suporte confiável a RAR5 / *solid*, ou com distribuição de binários mais complexa.
* **Baixar o UnRAR na primeira execução:** exige internet (viola o RNF01).

## Procedimento de atualização do binário
1. Obter a nova versão **estável** (x64) de origem oficial da RARLAB — o pacote *UnRAR for Windows* se ele estiver numa versão estável, ou o `UnRAR.exe` do instalador oficial do WinRAR da mesma versão. Conferir a assinatura Authenticode (win.rar GmbH) do pacote e do binário, extrair sem executar o instalador e substituir `bin/UnRAR.exe`; atualizar `bin/license.txt` se o texto da licença freeware mudar.
2. Rodar os testes de `tests/infrastructure/test_archive_reader.py` (RAR4, RAR5, *solid*, senha, truncado) — RNF04-CA1 a CA4.
3. Reconfirmar que o `rarfile` aplica `CREATE_NO_WINDOW` (`rarfile.custom_popen`) e validar no executável que nenhuma janela de console aparece (RNF04-CA5).
4. Atualizar a tabela "Versão e procedência atuais" (versão, origem e SHA-256) e o histórico desta ADR, e registrar no STATUS.

## Consequências
* Nenhuma dependência externa para ler `.cbr`; comportamento idêntico em qualquer máquina.
* Um binário de terceiros fica no repositório (~550 KB) e precisa ser atualizado manualmente.
* O texto da licença freeware acompanha o binário no repositório e no executável (`dist\HqFriend\_internal\bin\license.txt`).
* O `License.txt` da instalação do WinRAR **não** é usado: é o contrato do WinRAR (versão de avaliação), não a licença do UnRAR.
* Verificação da troca 6.11 → 7.23: os 43 testes de `test_archive_reader.py` (RAR4, RAR5, *solid*, senha, truncado, formato pelo conteúdo) e a suíte completa (240) passaram; a validação no executável (RNF04-CA5) é feita no Bloco 4 do FIX-01.
