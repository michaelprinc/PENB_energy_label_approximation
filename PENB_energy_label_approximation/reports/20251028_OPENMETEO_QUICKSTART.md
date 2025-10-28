# Open-Meteo Integration - Quick Start

## TL;DR

**Open-Meteo.com** byl úspěšně integrován jako **free fallback** pro historická meteorologická data starší než 8 dní.

---

## ✅ Co Je Nové

### Před
- WeatherAPI: 0-8 dní zpět ✅
- WeatherAPI: 9+ dní zpět ❌ (nedostupné)
- Fallback: Pouze syntetická data (nízká kvalita)

### Po
- WeatherAPI: 0-8 dní zpět ✅
- **Open-Meteo: 9+ dní zpět až do roku 1940** ✅
- Fallback: Syntetická data (poslední záchranna)

---

## 🚀 Základní Použití

```python
from core.weather_api import fetch_hourly_weather
from datetime import date, timedelta

# Získej data za posledních 30 dní
df = fetch_hourly_weather(
    location="Praha",
    start_date=date.today() - timedelta(days=30),
    end_date=date.today() - timedelta(days=1),
    api_key="YOUR_API_KEY",
    use_openmeteo_fallback=True  # ← Nový parametr (default: True)
)

# Výsledek: 100% pokrytí reálnými daty
# - 0-8 dní: WeatherAPI (premium kvalita)
# - 9-30 dní: Open-Meteo (ERA5 reanalysis)
```

---

## 📊 Výsledky Testů

```
TEST 1: Stará data (30 dní zpět)         ✅ PASS - 100% pokrytí
TEST 2: Čerstvá data (včera)             ✅ PASS - 100% pokrytí
TEST 3: Mix dat (20 dní zpět)            ✅ PASS - 100% pokrytí
TEST 4: Bez Open-Meteo (syntetický)      ✅ PASS - 100% pokrytí

CELKEM: 4/4 testů úspěšných (100%)
```

---

## 🆓 Náklady

| Služba | Limit Free Tier | Náklady |
|--------|-----------------|---------|
| WeatherAPI | 1M volání/měsíc | €0 |
| Open-Meteo | 10k volání/den | €0 |
| **CELKEM** | - | **€0** |

---

## 📁 Nové Soubory

### Produkční Kód
- `core/openmeteo_api.py` - Open-Meteo integrace (NEW)
- `core/weather_api.py` - Upraveno pro hybridní strategii

### Testy
- `test_full_integration.py` - Komplexní test suite (NEW)
- `test_simple_hybrid.py` - Jednoduchý test (NEW)
- `test_openmeteo_integration.py` - Open-Meteo specifické (NEW)

### Dokumentace
- `reports/20251028_OPENMETEO_INTEGRATION.md` - Full report (NEW)
- `reports/20251028_OPENMETEO_QUICKSTART.md` - Tento soubor (NEW)

---

## 🧪 Jak Otestovat

### Rychlý Test
```bash
python test_simple_hybrid.py
```

### Komplexní Test
```bash
python test_full_integration.py
```

**Očekávaný výstup:**
```
🎉 VŠECHNY TESTY PROŠLY!
   ✓ Open-Meteo integrace funguje správně
   ✓ Hybridní strategie WeatherAPI + Open-Meteo OK
   ✓ Fallback mechanismus funkční
```

---

## 🔧 API Limity

### WeatherAPI (0-8 dní zpět)
- Historický limit: **8 dní** (ověřeno testováním)
- Free tier: 1,000,000 volání/měsíc
- Kvalita: Premium (měřená data)

### Open-Meteo (9+ dní zpět)
- Historický rozsah: **1940 - současnost**
- Free tier: 10,000 volání/den
- Kvalita: High (ERA5 reanalysis, ECMWF)
- **Bez API klíče!**

---

## 📈 Data Kvalita

### Test: 2025-10-20 (Překryvné datum)

| Parametr | WeatherAPI | Open-Meteo | Rozdíl |
|----------|------------|------------|--------|
| Teplota min | 4.6°C | 4.8°C | +0.2°C |
| Teplota max | 9.4°C | 9.2°C | -0.2°C |
| GHI max | ~350 W/m² | ~340 W/m² | -10 W/m² |

**Závěr: Vynikající shoda (< 0.5°C)**

---

## ⚙️ Konfigurace

### Vypnutí Open-Meteo Fallbacku

Pokud chceš používat pouze WeatherAPI + syntetická data:

```python
df = fetch_hourly_weather(
    location="Praha",
    start_date=start,
    end_date=end,
    api_key=api_key,
    use_openmeteo_fallback=False  # ← Vypnuto
)
```

**Poznámka:** Nedoporučujeme, Open-Meteo poskytuje lepší kvalitu než syntetická data.

---

## 🎯 Doporučení

### Pro Produkci
```python
# ✅ DOPORUČENO
use_openmeteo_fallback=True  # Best quality + coverage

# ❌ NEDOPORUČENO
use_openmeteo_fallback=False  # Lower quality for old data
```

### Pro Vývoj/Debug
```python
# Debug: Sleduj zdroj dat
df = fetch_hourly_weather(...)

# Během běhu se vypíše:
# 📊 VÝSLEDKY PODLE ZDROJŮ:
#   • WeatherAPI: 192 hodin (8.0 dní)
#   • Open-Meteo: 288 hodin (12.0 dní)
```

---

## 🐛 Řešení Problémů

### Chyba: "ModuleNotFoundError: No module named 'requests'"

```bash
pip install -r requirements.txt
```

### Chyba: "API klíč není nastaven"

```bash
# Nastav v environment:
export WEATHERAPI_KEY="your-api-key"

# NEBO v storage/token_store.json:
{
    "weatherapi_key": "your-api-key"
}
```

### Chyba: "Rate limit exceeded"

**WeatherAPI:**
- Limit: 1M/měsíc
- Řešení: Open-Meteo automaticky převezme stará data

**Open-Meteo:**
- Limit: 10k/den
- Řešení: Implementovat cache nebo snížit frekvenci volání

---

## 📚 Další Informace

**Dokumentace:**
- [Kompletní report](./20251028_OPENMETEO_INTEGRATION.md)
- [WeatherAPI docs](https://www.weatherapi.com/docs/)
- [Open-Meteo docs](https://open-meteo.com/en/docs/historical-weather-api)

**Testy:**
- Všechny testy v `test_*.py` souborech
- Spusť: `python test_full_integration.py`

---

**Status: ✅ PRODUCTION READY**  
**Verze: 1.0.0**  
**Datum: 2025-10-28**
