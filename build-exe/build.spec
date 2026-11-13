# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the Windows build, run build-exe\build.bat from anywhere
import os

build_files = SPECPATH
repo = os.path.abspath(os.path.join(SPECPATH, ".."))

a = Analysis([os.path.join(repo, "main.py")],
             pathex=[repo],
             binaries=[],
             datas=[(os.path.join(repo, "Resources"), "Resources")],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             # not used by the app, but picked up from the python environment
             excludes=["numpy", "charset_normalizer"],
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name="MKV Muxing Batch GUI",
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          # keep all files next to the exe, the app looks for "Resources" relative to the exe
          contents_directory=".",
          version=os.path.join(build_files, "VersionFile.txt"),
          icon=os.path.join(build_files, "App.ico"))
coll = COLLECT(exe,
               a.binaries,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude=[],
               name="MKV Muxing Batch GUI")
