"""Persistência do state.json: escrita atômica, backup e recuperação (RNF02)."""
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Optional

from src import config
from src.domain.errors import StateRecoveredWarning
from src.domain.models import AppState

logger = logging.getLogger(__name__)

_REPLACE_ATTEMPTS = 5
_REPLACE_RETRY_DELAY = 0.1


class LoadResult(NamedTuple):
    state: AppState
    recovery_warning: Optional[StateRecoveredWarning] = None


class JsonStateRepository:
    def __init__(self, state_path: Path = config.STATE_JSON_PATH,
                 backup_path: Path = config.STATE_BACKUP_PATH,
                 retry_delay: float = _REPLACE_RETRY_DELAY):
        self._state_path = state_path
        self._backup_path = backup_path
        self._tmp_path = state_path.with_name(state_path.name + ".tmp")
        self._retry_delay = retry_delay

    def load(self) -> LoadResult:
        """Carrega o estado, recuperando do backup se o state.json estiver corrompido."""
        if not self._state_path.exists():
            state = AppState()
            self.save(state)
            return LoadResult(state)

        try:
            state = self._read(self._state_path)
        except ValueError:
            logger.exception("state.json inválido: %s", self._state_path)
        else:
            shutil.copy2(self._state_path, self._backup_path)
            return LoadResult(state)

        corrupt_path = self._quarantine_corrupt_file()
        logger.error("state.json corrompido preservado em %s", corrupt_path)

        try:
            state = self._read(self._backup_path)
        except (OSError, ValueError):
            logger.exception("Backup indisponível ou inválido: %s", self._backup_path)
            return LoadResult(AppState(), StateRecoveredWarning(restored_from_backup=False))
        return LoadResult(state, StateRecoveredWarning(restored_from_backup=True))

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

    @staticmethod
    def _read(path: Path) -> AppState:
        return AppState.model_validate_json(path.read_bytes())
