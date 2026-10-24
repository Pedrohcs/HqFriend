"""Constantes de caminhos do sistema e resolvedor de recursos internos (PyInstaller)."""
import ctypes
import sys
import uuid
from ctypes import wintypes
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """Resolve caminho de recursos internos tanto em dev quanto no .exe (PyInstaller)."""
    base_path = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
    return base_path / relative_path


class _GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]


_FOLDERID_DOCUMENTS = "{FDD39AD0-238F-46AF-ADB4-6C85480369C7}"
_FOLDERID_PICTURES = "{33E28130-4E1E-4676-835A-98395C3BC3BB}"


def _known_folder(folder_id: str) -> Path:
    """Resolve uma pasta conhecida do Windows (ex: Documentos redirecionado ao OneDrive)."""
    guid = _GUID.from_buffer_copy(uuid.UUID(folder_id).bytes_le)
    path_ptr = ctypes.c_wchar_p()
    hresult = ctypes.windll.shell32.SHGetKnownFolderPath(
        ctypes.byref(guid), 0, None, ctypes.byref(path_ptr))
    try:
        if hresult != 0:
            raise OSError(f"SHGetKnownFolderPath falhou (HRESULT {hresult & 0xFFFFFFFF:#010x})")
        return Path(path_ptr.value)
    finally:
        ctypes.windll.ole32.CoTaskMemFree(path_ptr)


# Diretórios exigidos pelos requisitos (RNF02, RNF03, RNF06, RF17)
DOCUMENTS_DIR = _known_folder(_FOLDERID_DOCUMENTS)
PICTURES_DIR = _known_folder(_FOLDERID_PICTURES)

APP_DATA_DIR = DOCUMENTS_DIR / "HqFriend"
COVERS_CACHE_DIR = APP_DATA_DIR / "covers"
LOGS_DIR = APP_DATA_DIR / "logs"
STATE_JSON_PATH = APP_DATA_DIR / "state.json"
STATE_BACKUP_PATH = APP_DATA_DIR / "state.json.bak"
LOCK_FILE_PATH = APP_DATA_DIR / "hqfriend.lock"
EXPORT_PICTURES_DIR = PICTURES_DIR / "HQs"

# Pastas criadas automaticamente na inicialização (RNF03)
SYSTEM_DIRECTORIES = (APP_DATA_DIR, COVERS_CACHE_DIR, LOGS_DIR, EXPORT_PICTURES_DIR)

UNRAR_BINARY_PATH = get_resource_path("bin/UnRAR.exe")
