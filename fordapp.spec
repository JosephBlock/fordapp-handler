# -*- mode: python ; coding: utf-8 -*-
import sys
import platform
import os
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

# Detect OS and Architecture to name the output file dynamically
os_name = 'windows' if sys.platform == 'win32' else ('macos' if sys.platform == 'darwin' else 'linux')

def get_build_arch():
    # Allow overriding via environment variable ARCH (useful for CI/CD matrix builds)
    env_arch = os.environ.get('ARCH')
    if env_arch:
        return env_arch.lower()
        
    raw_arch = platform.machine().lower()
    is_64bit = sys.maxsize > 2**32
    if 'arm64' in raw_arch or 'aarch64' in raw_arch or 'arm' in raw_arch:
        return 'arm64'
    elif not is_64bit or 'i386' in raw_arch or 'i686' in raw_arch or 'x86' in raw_arch and '64' not in raw_arch:
        return 'x86'
    else:
        return 'x86_64'

arch_name = get_build_arch()
output_name = f"FordAppHandler-{os_name}-{arch_name}"

# On macOS, determine target architecture for PyInstaller
mac_target_arch = arch_name if sys.platform == 'darwin' else None

# Compile a standalone executable (for Windows and Linux)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=output_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True, # Critical for macOS Apple Events
    target_arch=mac_target_arch,
    codesign_identity=None,
    entitlements_file=None,
)

# On macOS, wrap the executable into a .app bundle with URI Scheme plist rules
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name=f'{output_name}.app',
        bundle_identifier='com.custom.fordapp',
        info_plist={
            'CFBundleURLTypes': [
                {
                    'CFBundleURLName': 'Ford/Lincoln App Protocol',
                    'CFBundleURLSchemes': ['fordapp', 'lincolnapp']
                }
            ]
        }
    )

# Post-build step to copy or create README in dist
dist_dir = 'dist'
if os.path.exists(dist_dir):
    readme_dest = os.path.join(dist_dir, 'README.txt')
    
    # Format executable extension for readme instructions
    exe_display_name = f"{output_name}.exe" if sys.platform == 'win32' else output_name
    
    readme_content = f"""Ford/Lincoln Protocol Handler
=============================

A helper tool to register and handle custom URI schemes `fordapp://` and `lincolnapp://`.

Current Build: {output_name}

Installation
------------
1. Run `{exe_display_name}` directly (without any command-line arguments) to launch the Setup Wizard.
2. Choose one of the setup options:
   - **Option A (Recommended)**: Click "Install & Register Protocol (Recommended)" to permanently copy the application to your User Programs directory and register it.
   - **Option B**: Click "Register Current File Location (Temporary - Removed on Close)" to register the protocol temporarily in-place. The registration will be cleaned up automatically when you close the Setup window.

Uninstallation
--------------
To completely remove the handler and clean up registrations:
- Option A: Run the application and click the "Uninstall / Clean Up" button in the Setup GUI.
- Option B (CLI): Run the executable from your terminal with the uninstall argument:
    {exe_display_name} --uninstall
- Option C (Silent CLI): Run the executable silently (no prompts/dialogs):
    {exe_display_name} --uninstall --silent

Command Line Arguments
----------------------
- `--uninstall` / `-u` / `/uninstall`: Directly uninstalls the protocol registration and cleans up.
- `--silent` / `-s`: Runs the uninstaller silently without displaying any GUI dialogs.
"""
    try:
        with open(readme_dest, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"Created README.txt at {readme_dest}")
    except Exception as e:
        print(f"Error creating README.txt: {e}")