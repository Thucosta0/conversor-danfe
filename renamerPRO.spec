# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['danfe_app.py'],
    pathex=[],
    binaries=[
        # Incluir todo o diretório PHP
        ('php/*', 'php/'),
        ('vendor/*', 'vendor/'),
    ],
    datas=[
        # Arquivos de dados necessários
        ('gerador_danfe.php', '.'),
        ('composer.json', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('LEIA-ME.txt', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'tkinter',
        'subprocess',
        'threading',
        'xml.etree.ElementTree',
        'concurrent.futures',
        'webbrowser',
        'time',
        'os',
        'pandas',
        'openpyxl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='renamerPRO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Interface gráfica, sem console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='einstein_icon.ico' if os.path.exists('einstein_icon.ico') else None,
)