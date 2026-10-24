"""Log rotativo em arquivo e captura de exceções não tratadas (RNF06, ADR-07)."""
import logging
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable, Optional

LOG_FILE_NAME = "hqfriend.log"
_MAX_BYTES = 1_000_000
_BACKUP_COUNT = 3
_FORMAT = "%(asctime)s [%(levelname)s] %(threadName)s %(name)s: %(message)s"

UnhandledCallback = Callable[[BaseException], None]

_logger = logging.getLogger("hqfriend")
_handler: Optional[RotatingFileHandler] = None
_previous_hooks = None


def configure(logs_dir: Path, on_unhandled: Optional[UnhandledCallback] = None) -> Path:
    """Ativa o log rotativo em `logs_dir` e instala os excepthooks.

    `on_unhandled` é chamado após o registro de cada exceção não tratada (ex: para exibir
    uma mensagem ao usuário). Pode ser chamado a partir de uma thread secundária; a camada
    de UI é responsável por despachar a exibição para a thread principal.
    """
    global _handler, _previous_hooks
    shutdown()

    log_path = logs_dir / LOG_FILE_NAME
    _handler = RotatingFileHandler(log_path, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT,
                                   encoding="utf-8")
    _handler.setFormatter(logging.Formatter(_FORMAT))
    root_logger = logging.getLogger()
    root_logger.addHandler(_handler)
    root_logger.setLevel(logging.INFO)

    def _excepthook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        _logger.critical("Exceção não tratada", exc_info=(exc_type, exc_value, exc_traceback))
        if on_unhandled is not None:
            on_unhandled(exc_value)

    def _thread_excepthook(args: threading.ExceptHookArgs):
        if args.exc_type is SystemExit:
            return
        thread_name = args.thread.name if args.thread is not None else "desconhecida"
        _logger.critical("Exceção não tratada na thread %s", thread_name,
                         exc_info=(args.exc_type, args.exc_value, args.exc_traceback))
        if on_unhandled is not None and args.exc_value is not None:
            on_unhandled(args.exc_value)

    _previous_hooks = (sys.excepthook, threading.excepthook)
    sys.excepthook = _excepthook
    threading.excepthook = _thread_excepthook
    return log_path


def shutdown() -> None:
    """Remove o handler de arquivo e restaura os excepthooks anteriores."""
    global _handler, _previous_hooks
    if _handler is not None:
        logging.getLogger().removeHandler(_handler)
        _handler.close()
        _handler = None
    if _previous_hooks is not None:
        sys.excepthook, threading.excepthook = _previous_hooks
        _previous_hooks = None
