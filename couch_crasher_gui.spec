# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller Configuration File
"""

import os
import platform
import couchcrasher

from PyInstaller.building.api import PYZ, EXE
from PyInstaller.building.osx import BUNDLE
from PyInstaller.building.build_main import Analysis


# Grab support/macos_utilities/* binaries from the couchcrasher library

def get_couchcrasher_binaries():
    binaries = []

    if platform.system() != "Darwin":
        return binaries

    for root, dirs, files in os.walk(os.path.join(os.path.dirname(couchcrasher.__file__), "support", "macos_binaries")):
        for file in files:
            if "cpython" in file:
                continue
            if any(file.endswith(ext) for ext in [".py", ".pyc"]):
                continue
            binaries.append((os.path.join(root, file), "support/macos_binaries"))

    return binaries


block_cipher = None

a = Analysis(['couch_crasher_gui.py'],
             pathex=[],
             binaries=[],
             datas=get_couchcrasher_binaries(),
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False
)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher
)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Couch-Crasher-UI' + (".exe" if platform.system() == "Windows" else ""),
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch="universal2",
          icon="Resources/AppIcon.png" if platform.system() != "Darwin" else "Resources/AppIcon.icns",
          entitlements_file="Resources/entitlements.plist",
)

app = BUNDLE(exe,
         name='Couch-Crasher-UI.app',
         bundle_identifier="com.couch-crasher.ui",
         icon="Resources/AppIcon.icns",
         info_plist={
             "CFBundleShortVersionString": couchcrasher.__version__,
         }
)