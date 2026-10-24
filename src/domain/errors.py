"""Exceções e avisos do domínio."""


class InvalidComicError(Exception):
    """HQ corrompida, protegida por senha ou sem imagens válidas (RF20)."""


class StateRecoveredWarning(UserWarning):
    """O state.json estava corrompido e foi recuperado (RNF02).

    `restored_from_backup` indica se o estado veio do state.json.bak (True) ou se foi
    reiniciado do zero por falta de backup válido (False).
    """

    def __init__(self, restored_from_backup: bool):
        self.restored_from_backup = restored_from_backup
        source = "do backup" if restored_from_backup else "do zero (backup indisponível)"
        super().__init__(f"Arquivo de estado corrompido; estado restaurado {source}.")
