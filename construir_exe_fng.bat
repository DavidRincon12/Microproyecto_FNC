@echo off
echo ============================================================
echo   Compilando ConversorFNG con PyInstaller
echo ============================================================
echo.

py -m pip install --upgrade pyinstaller
py -m PyInstaller --noconfirm --onefile --windowed --name ConversorFNG --add-data "ejemplos_fng;ejemplos_fng" main_fng.py

echo.
echo ============================================================
echo   Ejecutable generado exitosamente en dist\ConversorFNG.exe
echo ============================================================
pause
