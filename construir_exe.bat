@echo off
echo ============================================================
echo   Compilando DepuradorFNC con PyInstaller
echo ============================================================
echo.

py -m pip install --upgrade pyinstaller
py -m PyInstaller --onefile --windowed --name DepuradorFNC --add-data "ejemplos;ejemplos" main.py

echo.
echo ============================================================
echo   Ejecutable generado exitosamente en dist\DepuradorFNC.exe
echo ============================================================
pause
