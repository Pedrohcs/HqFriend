# -*- mode: python ; coding: utf-8 -*-
# Build: .venv\Scripts\pyinstaller.exe --noconfirm --clean HqFriend.spec  ->  dist\HqFriend\HqFriend.exe

a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[
        ('bin/UnRAR.exe', 'bin'),  # Embarca o UnRAR.exe junto ao executável
    ],
    datas=[
        ('assets/styles/dark_theme.qss', 'assets/styles'),
        ('assets/icon.ico', 'assets'),
        ('bin/license.txt', 'bin'),  # Licença freeware do UnRAR, distribuída junto ao binário (ADR-12)
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HqFriend',
    icon='assets/icon.ico',
    debug=False,
    strip=False,
    upx=False,      # UPX corrompe DLLs do Qt com frequência e aumenta falsos positivos de antivírus
    console=False,  # Oculta a janela de terminal (GUI pura)
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='HqFriend',
)
