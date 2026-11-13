@echo off
rem Builds "dist\MKV Muxing Batch GUI\MKV Muxing Batch GUI.exe" (needs: pip install pyinstaller)
cd /d "%~dp0.."
python -m PyInstaller --noconfirm --clean --workpath build --distpath dist build-exe\build.spec
