# 🔧 Řešení problému s importy - VYŘEŠENO ✓

## Problém
```
ModuleNotFoundError: No module named 'core'
```

## Příčina
Python nemohl najít modul `core`, protože nebyla správně nastavena cesta `PYTHONPATH`.

---

## ✅ Řešení implementováno

### 1. Opraveno `app_gui/gui_main.py`
Přidán automatický setup PYTHONPATH na začátku souboru:

```python
import sys
import os
from pathlib import Path

# Přidej parent directory do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### 2. Aktualizováno `run.bat` (Windows)
Přidán řádek nastavení PYTHONPATH:

```batch
set PYTHONPATH=%~dp0
```

### 3. Vytvořeno `run.sh` (Linux/Mac)
Shell skript s nastavením PYTHONPATH:

```bash
export PYTHONPATH="$(cd "$(dirname "$0")" && pwd)"
```

### 4. Opraven `main.py`
Použití subprocess s explicitním nastavením environment:

```python
env = os.environ.copy()
env['PYTHONPATH'] = project_dir
subprocess.run([...], env=env)
```

### 5. Vytvořen `test_imports.py`
Testovací skript pro ověření funkčnosti všech modulů.

### 6. Oprava chybějícího importu
V `core/baseline_split.py` doplněn:
```python
from typing import Tuple, Optional
```

---

## 📋 Výsledky testů

```
✓ Test 1: Importy core modulů - OK
✓ Test 2: Pydantic modely - OK  
✓ Test 3: Config modul - OK
✓ Test 4: RC Model - OK (simulace: 21.11°C)
✓ Test 5: Klasifikace - OK (třída D)
✓ Test 6: Report builder - OK
✓ Test 7: GUI modul - OK
✓ Test 8: Závislosti - OK (všech 7 balíčků)
```

**Všechny testy prošly! ✓**

---

## 🚀 Spuštění aplikace

### Doporučené způsoby (seřazeno):

#### 1. **run.bat** (Windows - nejjednodušší)
```batch
run.bat
```
✅ Automaticky nastaví PYTHONPATH  
✅ Zkontroluje závislosti  
✅ Spustí Streamlit  

#### 2. **run.sh** (Linux/Mac)
```bash
chmod +x run.sh
./run.sh
```

#### 3. **Přímo Streamlit** (vyžaduje manuální PYTHONPATH)

**PowerShell:**
```powershell
$env:PYTHONPATH = (Get-Location).Path
streamlit run app_gui/gui_main.py
```

**CMD:**
```cmd
set PYTHONPATH=%cd%
streamlit run app_gui/gui_main.py
```

**Bash:**
```bash
export PYTHONPATH=$(pwd)
streamlit run app_gui/gui_main.py
```

#### 4. **Python launcher**
```bash
python main.py
```

---

## ✅ Aplikace běží na:

```
Local URL:    http://localhost:8502
Network URL:  http://192.168.0.7:8502
```

Pro ukončení: **Ctrl+C** v terminálu

---

## 🧪 Testování před spuštěním

Před prvním spuštěním aplikace můžete ověřit funkčnost:

```bash
python test_imports.py
```

Tento skript zkontroluje:
- Všechny importy core modulů
- Funkčnost pydantic modelů
- RC model simulaci
- Klasifikaci energetických tříd
- Přítomnost všech závislostí

---

## 📝 Checklist před použitím

- [x] Závislosti nainstalovány (`pip install -r requirements.txt`)
- [x] PYTHONPATH správně nastaven (automaticky ve skriptech)
- [x] Všechny moduly funkční (test_imports.py)
- [ ] API klíč pro weatherapi.com (zadáte v GUI)
- [x] Aplikace úspěšně spuštěna ✓

---

## 💡 Tipy

1. **První spuštění**: Použijte `run.bat` (Windows) nebo `run.sh` (Linux/Mac)
2. **Test**: Spusťte `python test_imports.py` pro ověření
3. **API klíč**: Získejte zdarma na https://www.weatherapi.com/
4. **Demo**: V GUI použijte tlačítko "Generovat ukázková data"

---

## 🐛 Řešení problémů

### "Module not found" stále přetrvává
```bash
# Ujistěte se, že jste ve správném adresáři
cd PENB_energy_label_approximation

# Použijte run.bat (automaticky nastaví PYTHONPATH)
run.bat
```

### Chybějící závislosti
```bash
pip install -r requirements.txt
```

### Port již použit
```bash
streamlit run app_gui/gui_main.py --server.port=8503
```

---

## ✅ Status

**PROBLÉM VYŘEŠEN ✓**

- Import error opraven
- PYTHONPATH správně nastaven  
- Všechny testy prošly
- Aplikace úspěšně běží
- GUI dostupné na http://localhost:8502

**Aplikace je plně funkční a připravena k použití! 🎉**
