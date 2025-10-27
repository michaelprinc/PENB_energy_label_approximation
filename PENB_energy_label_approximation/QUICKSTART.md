# 🚀 Rychlý Start

## ✅ Oprava problému s importy

**Problém vyřešen!** Pokud jste měli chybu `ModuleNotFoundError: No module named 'core'`, 
byla opravena nastavením PYTHONPATH. Viz `TROUBLESHOOTING.md` pro detaily.

---

## Pro uživatele Windows (nejjednodušší)

1. **Dvojklik na `run.bat`**
2. Počkejte, než se otevře prohlížeč
3. Postupujte podle záložek v aplikaci

---

## Manuální spuštění

### Krok 1: Instalace závislostí

```powershell
pip install -r requirements.txt
```

### Krok 2: Test funkčnosti (volitelné, ale doporučené)

```powershell
python test_imports.py
```

Měli byste vidět: `✓ Všechny testy prošly!`

### Krok 3: Spuštění aplikace

**Doporučeno (automaticky nastaví PYTHONPATH):**
```powershell
.\run.bat
```

**Alternativně (manuálně):**
```powershell
$env:PYTHONPATH = (Get-Location).Path
streamlit run app_gui/gui_main.py
```

### Krok 3: API klíč WeatherAPI.com

1. Zaregistrujte se na https://www.weatherapi.com/
2. Získejte API klíč (free tier je dostačující)
3. Zadejte ho v bočním panelu aplikace

**ℹ️ Co podporuje free tier:**
- ✅ Aktuální počasí (`current.json`)
- ✅ 14denní předpověď dopředu (`forecast.json`)
- ✅ Historická data **do 7 dní zpětně** (`forecast.json`)
- ❌ Historická data **starší než 7 dní** (vyžaduje placený tarif)

**🔄 Automatický fallback:**
Aplikace má inteligentní fallback systém:
1. Pro data do 7 dní zpětně → použije forecast API (free tier ✓)
2. Pro starší data → zkusí history API (placený)
3. Pokud selže → vygeneruje syntetická data s varováním

**💡 Doporučení pro nejlepší výsledky:**
- **BASIC režim**: Použije typický meteorologický rok (TMY) - žádná historická data nutná
- **STANDARD/ADVANCED režim**: Pro přesnou kalibraci nahrajte vlastní CSV s měřeními

---

## 📝 Ukázkový workflow

### 1. Lokalita
- Klikněte "Automaticky detekovat lokaci"
- Nebo zadejte "Praha"

### 2. Parametry bytu
- Plocha: 70 m²
- Výška: 2.7 m
- Systém: Kondenzační plynový kotel
- Účinnost: 0.9 (pokud znáte)

### 3. Data
- Klikněte "Generovat ukázková data"
- Nebo nahrajte vlastní CSV (formát viz example_data.csv)
- Průměrná teplota: 21°C

### 4. Výpočet
- Klikněte "SPUSTIT VÝPOČET"
- Počkejte 10-30 sekund

### 5. Výsledky
- Prohlédněte si energetickou třídu
- Exportujte HTML report

---

## ⚠️ Řešení problémů

### "Import error" při spuštění
```powershell
pip install --upgrade -r requirements.txt
```

### "API key error"
- Zkontrolujte, zda jste zadali správný API klíč
- Ověřte na https://www.weatherapi.com/my-account.aspx

### "Historical data not available"
- Bezplatný API klíč má omezený přístup k historii
- Zkuste kratší období (7 dní místo 28)
- Nebo použijte placený tarif WeatherAPI

### Aplikace se nezobrazuje
- Otevřete ručně http://localhost:8501 v prohlížeči
- Zkuste jiný port: `streamlit run app_gui/gui_main.py --server.port=8502`

---

## 💡 Tipy

- **První spuštění**: Použijte režim STANDARD s ukázkovými daty
- **Nejlepší výsledky**: 28+ dní skutečných dat + režim ADVANCED
- **Rychlá zkouška**: Režim BASIC s generovanými daty

---

## 📞 Podpora

Problémy? Otevřete issue na GitHubu nebo se podívejte do README.md pro detailní dokumentaci.
