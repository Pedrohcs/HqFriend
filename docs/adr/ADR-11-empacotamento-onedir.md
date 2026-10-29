# ADR-11 — Empacotamento com PyInstaller em Modo onedir, sem UPX

* **Status:** `Aceita`
* **Data:** 2026-10-24 (registrada retroativamente pelo FIX-01 em 2026-10-29)
* **Origem:** v1.0 (FEAT-13)
* **Requisitos relacionados:** RNF01, RNF04

## Contexto
O usuário final não deve precisar instalar Python, dependências nem o WinRAR (RNF01). O executável roda sem console e precisa embarcar o `UnRAR.exe`, o ícone e a folha de estilos.

## Decisão
Gerar o executável com **PyInstaller 6** a partir do `HqFriend.spec` (na raiz do projeto), em modo **onedir**: a pasta `dist\HqFriend\` contém o `HqFriend.exe` e a pasta `_internal\` com as dependências, o `bin\UnRAR.exe` e os `assets\`. `console=False`, **sem UPX** (`upx=False`). A distribuição é a pasta inteira (ex: compactada em `.zip`). Configuração descrita em `TECNICO.md` §5.

## Alternativas descartadas
* **onefile:** um único `.exe` é mais simples de distribuir, mas extrai o PySide6 (~120 MB) para uma pasta temporária a **cada** execução, deixando a abertura lenta e acumulando lixo em `%TEMP%` quando o processo é encerrado à força.
* **Compressão com UPX:** reduz o tamanho, mas corrompe DLLs do Qt com frequência e aumenta os falsos positivos de antivírus.
* **Instalador (MSI / Inno Setup):** desnecessário para a v1.0; pode ser adicionado sobre a pasta onedir no futuro.

## Consequências
* Abertura rápida (sem extração a cada execução); pacote de ~128 MB e ~222 arquivos.
* O usuário precisa manter a pasta inteira: mover só o `HqFriend.exe` quebra o aplicativo.
* Verificação: build e validação manual do executável (RNF01-CA1/CA2, RNF04-CA5).
