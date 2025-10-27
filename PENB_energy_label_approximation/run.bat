@echo off
REM Spouštěcí skript pro Windows
echo ========================================
echo   Orientační Energetický Štítek
echo ========================================
echo.

REM Nastav PYTHONPATH na aktuální složku
set PYTHONPATH=%~dp0
echo PYTHONPATH: %PYTHONPATH%
echo.

REM Kontrola Python
python --version >nul 2>&1
if errorlevel 1 (
    echo CHYBA: Python není nainstalován!
    echo Stáhněte Python z https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Kontroluji závislosti...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [!] Instaluji závislosti (první spuštění)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo CHYBA: Instalace závislostí selhala!
        pause
        exit /b 1
    )
)

echo [2/3] Spouštím aplikaci...
echo [3/3] Otevírám prohlížeč na http://localhost:8501
echo.
echo Aplikace běží... (Pro ukončení stiskněte Ctrl+C)
echo.

streamlit run app_gui/gui_main.py

pause
