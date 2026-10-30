"""Persistência do state.json: escrita atômica, backup, recuperação e migração (RNF02)."""
import json
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Optional, Tuple

from src import config
from src.domain.errors import StateRecoveredWarning
from src.domain.models import AppState
from src.infrastructure.state_migrations import migrate

logger = logging.getLogger(__name__)

_REPLACE_ATTEMPTS = 5
_REPLACE_RETRY_DELAY = 0.1


class LoadResult(NamedTuple):
    state: AppState
    recovery_warning: Optional[StateRecoveredWarning] = None
    migrated_from: Optional[str] = None  # versão original do schema, se o estado foi migrado


class JsonStateRepository:
    def __init__(self, state_path: Path = config.STATE_JSON_PATH,
                 backup_path: Path = config.STATE_BACKUP_PATH,
                 retry_delay: float = _REPLACE_RETRY_DELAY):
        self._state_path = state_path
        self._backup_path = backup_path
        self._tmp_path = state_path.with_name(state_path.name + ".tmp")
        self._retry_delay = retry_delay

    def load(self) -> LoadResult:
        """Carrega o estado, recuperando do backup se o state.json estiver corrompido.

        Um state.json de versão futura lança FutureStateVersionError sem tocar no arquivo.
        """
        if not self._state_path.exists():
            state = AppState()
            self.save(state)
            return LoadResult(state)

        try:
            state, migrated_from = self._read(self._state_path)
        except ValueError:
            logger.exception("state.json inválido: %s", self._state_path)
        else:
            self._preserve_original(self._state_path, migrated_from)
            shutil.copy2(self._state_path, self._backup_path)
            return LoadResult(state, migrated_from=migrated_from)

        corrupt_path = self._quarantine_corrupt_file()
        logger.error("state.json corrompido preservado em %s", corrupt_path)

        try:
            state, migrated_from = self._read(self._backup_path)
        except (OSError, ValueError):
            logger.exception("Backup indisponível ou inválido: %s", self._backup_path)
            return LoadResult(AppState(), StateRecoveredWarning(restored_from_backup=False))
        self._preserve_original(self._backup_path, migrated_from)
        return LoadResult(state, StateRecoveredWarning(restored_from_backup=True), migrated_from)

    def save(self, state: AppState) -> None:
        """Grava o estado de forma atômica (state.json.tmp -> state.json)."""
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        self._tmp_path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        try:
            self._replace_with_retry()
        except OSError:
            self._tmp_path.unlink(missing_ok=True)
            raise

    def _replace_with_retry(self) -> None:
        # OneDrive e antivírus podem bloquear o state.json por alguns milissegundos.
        for attempt in range(1, _REPLACE_ATTEMPTS + 1):
            try:
                os.replace(self._tmp_path, self._state_path)
                return
            except PermissionError:
                if attempt == _REPLACE_ATTEMPTS:
                    logger.exception("Não foi possível gravar %s após %d tentativas",
                                     self._state_path, _REPLACE_ATTEMPTS)
                    raise
                time.sleep(self._retry_delay)

    def _quarantine_corrupt_file(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        corrupt_path = self._state_path.with_name(f"state.corrupt-{timestamp}.json")
        os.replace(self._state_path, corrupt_path)
        return corrupt_path

    def _preserve_original(self, source: Path, migrated_from: Optional[str]) -> None:
        # Cópia do arquivo antes da 1ª gravação no schema novo; nunca sobrescreve uma existente
        if migrated_from is None:
            return
        original_path = self._state_path.with_name(f"state.v{migrated_from}.json")
        if not original_path.exists():
            shutil.copy2(source, original_path)
            logger.info("state.json migrado da versão %s; original preservado em %s",
                        migrated_from, original_path)

    @staticmethod
    def _read(path: Path) -> Tuple[AppState, Optional[str]]:
        """Valida o arquivo após migrá-lo; devolve a versão original se houve migração."""
        data, original_version = migrate(json.loads(path.read_bytes()))
        state = AppState.model_validate(data)
        return state, (original_version if original_version != state.version else None)
