# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE, BUNDLE

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

# Compile a standalone executable (for Windows and Linux)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FordAppHandler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True, # Critical for macOS Apple Events
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# On macOS, wrap the executable into a .app bundle with URI Scheme plist rules
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='FordAppHandler.app',
        bundle_identifier='com.custom.fordapp',
        info_plist={
            'CFBundleURLTypes': [
                {
                    'CFBundleURLName': 'FordApp Protocol',
                    'CFBundleURLSchemes': ['fordapp']
                }
            ]
        }
    )