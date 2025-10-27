# ⚡ TL;DR - Orientační Energetický Štítek

## Co je to?
Aplikace pro **orientační odhad energetické náročnosti bytu** z provozních dat.

## Status
✅ **PLNĚ FUNKČNÍ** - Aplikace běží na http://localhost:8502

---

## Jak spustit (3 kroky)

### 1️⃣ Instalace
```powershell
pip install -r requirements.txt
```

### 2️⃣ Test (volitelné)
```powershell
python test_imports.py
```
Očekávaný výsledek: `✓ Všechny testy prošly!`

### 3️⃣ Spuštění
```powershell
run.bat          # Windows
./run.sh         # Linux/Mac
```

Nebo přímo:
```powershell
$env:PYTHONPATH = (Get-Location).Path
streamlit run app_gui/gui_main.py
```

---

## Co aplikace umí?

✅ **Automatická detekce lokace** podle IP  
✅ **Stažení historického počasí** (WeatherAPI.com)  
✅ **3 režimy výpočtu** (BASIC/STANDARD/ADVANCED)  
✅ **Fyzikální 1R1C model** budovy  
✅ **Kalibrace** na vaše data  
✅ **Klasifikace A-G** jako u PENB  
✅ **HTML reporty** k exportu  
✅ **Quality scoring** výsledků  

---

## Co potřebuji?

### Minimální data:
- **Plochu bytu** (m²)
- **Výšku stropu** (m)  
- **Typ vytápění** (kotel/TČ/elektro)
- **Denní spotřeby** (min. 1 den, doporučeno 7-28)
- **API klíč** z weatherapi.com (zdarma)

### Demo režim:
✅ Aplikace umí generovat ukázková data!

---

## GUI Flow (5 záložek)

```
1. Lokalita → Auto-detekce nebo zadání města
2. Byt & Systém → Parametry + vytápění  
3. Data → CSV upload nebo demo generátor
4. Výpočet → Tlačítko "SPUSTIT"
5. Výsledky → Třída A-G + metriky + export
```

---

## Problémy?

### "ModuleNotFoundError: No module named 'core'"
✅ **VYŘEŠENO** - Použijte `run.bat` (automaticky nastaví PYTHONPATH)

### "Import errors"
```powershell
pip install -r requirements.txt
```

### Detaily viz:
- `TROUBLESHOOTING.md` - Řešení problémů
- `QUICKSTART.md` - Rychlý start
- `README.md` - Kompletní dokumentace

---

## Testování

```powershell
python test_imports.py
```

Výsledek:
```
✓ Test 1: Importy core modulů......... PASS
✓ Test 2: Pydantic modely............. PASS
✓ Test 3: Config modul................ PASS
✓ Test 4: RC Model.................... PASS
✓ Test 5: Klasifikace................. PASS
✓ Test 6: Report builder.............. PASS
✓ Test 7: GUI modul................... PASS
✓ Test 8: Závislosti (7/7)............ PASS

✓ Všechny testy prošly!
```

---

## Architektura

```
core/           → Fyzika, kalibrace, simulace (10 modulů)
app_gui/        → Streamlit GUI (5 záložek)
reports/        → HTML generátor
storage/        → API token + cache (auto)
```

---

## Klíčové soubory

| Soubor | Popis |
|--------|-------|
| `run.bat` | Spouštěč Windows ⭐ |
| `run.sh` | Spouštěč Linux/Mac ⭐ |
| `test_imports.py` | Test funkčnosti |
| `README.md` | Hlavní dokumentace |
| `QUICKSTART.md` | Rychlý start |
| `TROUBLESHOOTING.md` | Řešení problémů |
| `requirements.txt` | Závislosti |
| `example_data.csv` | Ukázková data |

---

## Režimy výpočtu

| Režim | Min. data | Přesnost |
|-------|-----------|----------|
| BASIC | 1 den | Nízká (hrubý odhad) |
| STANDARD | 7 dní | Střední ⭐ (doporučeno) |
| ADVANCED | 28 dní | Vysoká (nejpřesnější) |

---

## Výsledky

Po výpočtu dostanete:

📊 **Energetickou třídu** (A-G)  
📈 **Měrnou potřebu tepla** (kWh/m²·rok)  
⚡ **Primární energii** (orientačně)  
🎯 **Spolehlivost** (LOW/MED/HIGH)  
📄 **HTML report** k exportu  
💡 **Doporučení** pro zlepšení  

---

## API klíč

1. Registrace: https://www.weatherapi.com/signup.aspx
2. Free tier: 1M requestů/měsíc (stačí)
3. Kopírovat klíč z My Account
4. Vložit do sidebaru v aplikaci

---

## Rychlý test workflow

```powershell
# 1. Test
python test_imports.py

# 2. Spuštění
run.bat

# 3. V GUI:
# - Kliknout "Auto-detekce lokace"
# - Zadat: 70 m², 2.7 m, Kotel, 0.9
# - Kliknout "Generovat ukázková data"
# - Režim: STANDARD
# - Zadat API klíč
# - "SPUSTIT VÝPOČET"

# 4. Výsledek za ~20 sekund!
```

---

## ⚠️ Disclaimer

Toto **NENÍ** oficiální PENB!  
Pouze orientační odhad pro osobní použití.

---

## 📚 Dokumentace

- **README.md** - Kompletní (200+ řádků)
- **QUICKSTART.md** - Rychlý start
- **IMPLEMENTATION.md** - Technická dokumentace
- **TROUBLESHOOTING.md** - Řešení problémů
- **PROJECT_STATUS.md** - Stav projektu

---

## ✅ Checklist

- [x] Závislosti nainstalovány
- [x] Testy prošly
- [x] Aplikace běží
- [ ] API klíč získán (weatherapi.com)
- [ ] První výpočet hotov

---

## 🎉 Status

**PROJEKT DOKONČEN ✓**

- ✅ Všechny moduly implementovány
- ✅ GUI plně funkční
- ✅ Testy passed
- ✅ Dokumentace kompletní
- ✅ Aplikace běží

**Připraveno k použití!**

---

Otázky? → `README.md` nebo `TROUBLESHOOTING.md`
