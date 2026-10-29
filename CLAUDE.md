# CLAUDE.md — HqFriend

Aplicativo desktop (Windows 11, Python 3.12, PySide6) para organizar e ler HQs `.cbz`/`.cbr`. O projeto segue **Spec-Driven Development**: o processo completo está em [`docs/README.md`](docs/README.md) — leia-o antes de mudar comportamento.

## Regras do processo
* **Spec antes do código.** Toda mudança de comportamento começa por um pacote em `docs/changes/` copiado de `docs/changes/_templates/` (`FEAT/` → `spec.md`, `plan.md`, `tasks.md`; `FIX/` → `fix.md`). Não implemente sem o `spec.md`/`fix.md` aprovado pelo usuário. A pasta do pacote leva só tipo + número (`docs/changes/FEAT-14/`, `docs/changes/FIX-02/`); o título fica dentro do documento.
* **Classifique todo bug** antes de corrigir: Tipo A (código diverge da spec), Tipo B (spec errada) ou, se o comportamento segue a spec, é uma FEAT.
* **`docs/specs/` é a verdade vigente** e deve descrever o código da `main`. Ao concluir um pacote, aplique o delta e os desvios de implementação em `docs/specs/` e `docs/adr/` — registrar o desvio só no STATUS não basta.
* **IDs nunca são reaproveitados.** Consulte e atualize a tabela "Próximos IDs Livres" em `docs/README.md`. Requisitos removidos viram `Obsoleto (FEAT-NN)`; ADRs revistas viram `Substituída por ADR-NN`.
* **`docs/STATUS_PROJETO.md`:** atualize o quadro no próprio lugar e acrescente um registro ao final do histórico a cada mudança de status de um pacote. Nunca edite registros anteriores.
* **`state.json`:** qualquer mudança de schema segue `docs/specs/ARQUITETURA.md` §3.3 (versão + migração testada).
* Não copie código-fonte para `docs/specs/TECNICO.md`; referencie o arquivo.

## Regras de código
* `src/domain`, `src/services` e `src/infrastructure` **não importam PySide6** (há teste que verifica). Integração com Qt fica em `src/ui/` (workers `QThread`).
* O `AppState` só é alterado na thread principal.
* Testes nunca gravam nas pastas reais do usuário: redirecione `APP_DATA_DIR` / `EXPORT_PICTURES_DIR` para `tmp_path`.
* Testes novos citam o critério que cobrem (`# RF07-CA2`, `# FIX-03 / RF16-CA2`).

## Comandos
* Testes: `.venv\Scripts\python.exe -m pytest`
* App pelo código-fonte: `.venv\Scripts\python.exe -m src.main`
* Executável: `.venv\Scripts\pyinstaller.exe --noconfirm --clean HqFriend.spec` → `dist\HqFriend\HqFriend.exe`

## Git
* **Commits, MRs/PRs, merges, push e tags são feitos sempre pelo usuário.** O agente pode criar branches e consultar o estado do repositório (`status`, `diff`, `log`), deixando as alterações prontas no working tree para o usuário commitar.
* Branches: `feat/FEAT-NN-<slug>` e `fix/FIX-NN-<slug>`, a partir da `main`.
* Cada versão entregue recebe uma tag (`v1.Y` para features, `v1.Y.Z` para correções).
