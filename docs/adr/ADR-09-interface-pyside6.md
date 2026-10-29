# ADR-09 — Interface Gráfica com PySide6 (Qt 6)

* **Status:** `Aceita`
* **Data:** 2026-10-24 (registrada retroativamente pelo FIX-01 em 2026-10-29)
* **Origem:** v1.0 (FEAT-08 a FEAT-11)
* **Requisitos relacionados:** RNF01, RNF05, RNF08, RF14 a RF17

## Contexto
O HqFriend é um aplicativo desktop para Windows 11 que precisa de: um leitor de imagens grandes com zoom ancorado no cursor e arraste; grids responsivos de capas; menus de contexto e atalhos de teclado; e trabalho pesado (varredura, extração, capas, exportação) em segundo plano sem travar a interface (RNF05). O restante do sistema é escrito em Python.

## Decisão
Usar **PySide6** (binding oficial do Qt 6) na camada de apresentação:
* leitor sobre `QGraphicsView` / `QGraphicsScene` (renderização acelerada, transformações de zoom e `ScrollHandDrag`);
* navegação em janela única com `QStackedWidget`;
* trabalho em segundo plano com `QThread` (workers) entregando resultados por sinais;
* tema visual por folha de estilos `.qss` sobre o estilo `Fusion` (RNF08).

As camadas de domínio, serviços e infraestrutura **não importam PySide6** (RNF05-CA3): toda integração com Qt fica em `src/ui/`.

## Alternativas descartadas
* **Tkinter:** sem canvas de imagem com zoom/transformações de qualidade e sem um modelo de threads com sinais; visual difícil de adequar ao tema escuro.
* **Aplicação web local / Electron:** exigiria um runtime de navegador e uma ponte com o Python para ler os arquivos, contrariando a execução local simples (RNF01) e aumentando o pacote.
* **PyQt6:** API equivalente, mas licença GPL/comercial; o PySide6 é LGPL e mantido pela Qt Company.

## Consequências
* Pacote distribuído de ~128 MB (as DLLs do Qt dominam o tamanho — ver ADR-11).
* Licença LGPL: o PySide6 é usado como biblioteca dinâmica, sem modificação.
* Armadilhas específicas do binding documentadas em `TECNICO.md` §7.5 (sinais no construtor, `QSignalSpy.wait()` e o GIL).
* Verificação: testes de UI em modo offscreen (`tests/ui/`) e teste que garante que as camadas centrais não importam PySide6 (`tests/services/test_cover_service.py`).
