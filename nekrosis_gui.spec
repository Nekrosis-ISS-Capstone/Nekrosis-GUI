# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller Configuration File
"""

import os
import platform
import nekrosis

from PyInstaller.building.api import PYZ, EXE
from PyInstaller.building.osx import BUNDLE
from PyInstaller.building.build_main import Analysis


# Grab support/macos_utilities/* binaries from the nekrosis library
def get_binaries():
    binaries = []

    if platform.system() != "Darwin":
        return binaries

    for root, dirs, files in os.walk(os.path.join(os.path.dirname(nekrosis.__file__), "support", "macos_binaries")):
        for file in files:
            if "cpython" in file:
                continue
            if any(file.endswith(ext) for ext in [".py", ".pyc"]):
                continue
            binaries.append((os.path.join(root, file), "support/macos_binaries"))

    return binaries


block_cipher = None

a = Analysis(['nekrosis_gui.py'],
             pathex=[],
             binaries=[],
             datas=get_binaries(),
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
          name='Nekrosis-GUI' + (".exe" if platform.system() == "Windows" else ""),
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch="universal2",
          icon="resources/icons/AppIcon.ico" if platform.system() != "Darwin" else "resources/icons/AppIcon.icns",
          entitlements_file="resources/signing/entitlements.plist",
)

app = BUNDLE(exe,
         name='Nekrosis-GUI.app',
         bundle_identifier="com.nekrosis.ui",
         icon="resources/icons/AppIcon.icns",
         info_plist={
             "CFBundleShortVersionString": nekrosis.__version__,
         }
)