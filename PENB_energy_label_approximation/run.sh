#!/bin/bash
# Spouštěcí skript pro Linux/Mac

echo "========================================"
echo "  Orientační Energetický Štítek"
echo "========================================"
echo ""

# Nastav PYTHONPATH na aktuální složku
export PYTHONPATH="$(cd "$(dirname "$0")" && pwd)"
echo "PYTHONPATH: $PYTHONPATH"
echo ""

# Kontrola Python
if ! command -v python3 &> /dev/null; then
    echo "CHYBA: Python není nainstalován!"
    echo "Nainstalujte Python 3.9 nebo novější"
    exit 1
fi

echo "[1/3] Kontroluji závislosti..."
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "[!] Instaluji závislosti (první spuštění)..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "CHYBA: Instalace závislostí selhala!"
        exit 1
    fi
fi

echo "[2/3] Spouštím aplikaci..."
echo "[3/3] Otevírám prohlížeč na http://localhost:8501"
echo ""
echo "Aplikace běží... (Pro ukončení stiskněte Ctrl+C)"
echo ""

streamlit run app_gui/gui_main.py
