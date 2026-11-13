@echo off
rem Builds "dist\MKV Muxing Batch GUI\MKV Muxing Batch GUI.exe" (needs: pip install -r build-exe\requirements-build.txt)
cd /d "%~dp0.."
python -m PyInstaller --noconfirm --clean --workpath build --distpath dist build-exe\build.spec
