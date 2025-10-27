# 🌤️ WeatherAPI.com - Kompletní průvodce

## 📋 Obsah

1. [Přehled implementace](#přehled-implementace)
2. [Free tier vs placený tarif](#free-tier-vs-placený-tarif)
3. [Inteligentní fallback strategie](#inteligentní-fallback-strategie)
4. [Testování](#testování)
5. [Best practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Přehled implementace

Aplikace využívá WeatherAPI.com pro získání meteorologických dat. Implementace je navržena s důrazem na:

✅ **Robustnost** - automatický fallback při selhání  
✅ **Flexibilita** - funguje s free i placeným tarifem  
✅ **Transparentnost** - jasné varování o limitech  
✅ **Offline režim** - syntetická data jako záloha  

---

## Free tier vs placený tarif

### ✅ Co JE dostupné zdarma (Free tier)

| Endpoint | Popis | Limit |
|----------|-------|-------|
| `current.json` | Aktuální počasí | ✓ Unlimited |
| `forecast.json` | Předpověď dopředu | ✓ 14 dní |
| `forecast.json` | Historie **do 7 dní zpětně** | ✓ Ano |

### ❌ Co NENÍ dostupné zdarma

| Endpoint | Popis | Požaduje |
|----------|-------|----------|
| `history.json` | Historie **starší než 7 dní** | 💰 Placený tarif |

### 💡 Praktické důsledky

**Pro BASIC režim (orientační výpočet):**
- ✅ **Žádný problém** - používá typický meteorologický rok (TMY)
- ✅ **Nepotřebuje historická data**
- ✅ **Funguje bez API klíče**

**Pro STANDARD/ADVANCED režim (kalibrace):**
- ⚠ **Vyžaduje historická data** - pro přesnou kalibraci
- **Řešení A:** Nahrajte vlastní CSV s měřeními spotřeby/teploty
- **Řešení B:** Použijte data do 7 dní zpětně (free tier)
- **Řešení C:** Aplikace automaticky vygeneruje syntetická data

---

## Inteligentní fallback strategie

Aplikace má tříúrovňový fallback systém:

### Strategie 1: Forecast API (FREE TIER) ✓

```python
# Pro data do 7 dní zpětně
if (today - date).days <= 7:
    → zkus forecast.json (free tier)
```

**Výhody:**
- ✅ Zdarma
- ✅ Skutečná historická data
- ✅ Vysoká přesnost

### Strategie 2: History API (PLACENÝ) 💰

```python
# Pro starší data
if forecast API selže:
    → zkus history.json (placený tarif)
```

**Výhody:**
- ✅ Skutečná historická data bez omezení
- ✅ Vysoká přesnost
- ❌ Vyžaduje předplatné

### Strategie 3: Syntetická data (FALLBACK) 🔄

```python
# Pokud obě API selžou
if history API selže:
    → vygeneruj syntetická data
```

**Jak fungují syntetická data:**

1. **Baseline teplota:**
   - Zkusí získat aktuální teplotu z `current.json`
   - Pokud selže → použije měsíční průměry pro střední Evropu

2. **Denní křivka:**
   ```python
   temp(t) = baseline + 5°C · sin(2π(t-6)/24)
   ```
   - Maximum ve 14:00
   - Minimum v 02:00
   - Amplituda 5°C

3. **Sluneční záření:**
   ```python
   GHI(t) = 400 W/m² · sin(π(t-6)/12)  pro 6:00-18:00
   GHI(t) = 0                          pro 18:00-6:00
   ```

4. **Ostatní parametry:**
   - Vlhkost: 70%
   - Vítr: 2 m/s

**Varování uživateli:**
```
⚠ VAROVÁNÍ: Pouze 45.2% dat - výsledky mohou být nepřesné
⚙ 2024-01-15: Generuji syntetická data
```

---

## Testování

### Automatický test suite

Spusťte test:

```powershell
python test_weather_api.py
```

**Co se testuje:**

| Test | Popis | Bez API klíče |
|------|-------|---------------|
| 1. Detekce lokace | Geocoding z IP | ✓ Funguje |
| 2. Forecast API | 7 dní dopředu | ❌ Potřebuje API |
| 3. Historie <7 dní | Nedávná data | ❌ Potřebuje API |
| 4. Historie >7 dní | Starší data + fallback | ✓ Test fallbacku |
| 5. Typický rok (TMY) | Syntetický TMY | ✓ Funguje |
| 6. Syntetická data | Fallback mechanismus | ✓ Funguje |

### Příklad výstupu

```
█████████████████████████████████████████████████████████████
█  TEST SUITE: WeatherAPI.com implementace                  █
█████████████████████████████████████████████████████████████

📡 Stahuji počasí pro období 2023-12-01 až 2023-12-03
✓ Data jsou do 7 dní zpětně - použiji free tier forecast API
  ✓ 2023-12-01 (forecast API)
  ✓ 2023-12-02 (forecast API)
  ✓ 2023-12-03 (forecast API)
✓ Staženo 72/72 hodin (100.0% pokrytí)

═════════════════════════════════════════════════════════════
VÝSLEDKY TESTŮ
═════════════════════════════════════════════════════════════
✓ Detekce lokace
✓ Forecast API (free)
✓ Historie <7 dní (free)
✓ Historie >7 dní (fallback)
✓ Typický rok (TMY)
✓ Syntetická data

Celkem: 6 testů
✓ Úspěch: 6
✗ Selhání: 0
⊘ Přeskočeno: 0

🎉 VŠECHNY TESTY PROŠLY!
```

---

## Best practices

### 1. Optimalizace požadavků

❌ **NE:**
```python
# Stahuje každý den samostatně (365 API callů)
for day in range(365):
    fetch_hourly_weather(location, day, day, api_key)
```

✅ **ANO:**
```python
# Jeden request pro celé období (pokud možné)
fetch_hourly_weather(location, start_date, end_date, api_key)
# Aplikace interně rozdělí na denní požadavky
```

### 2. Využití free tier

✅ **Doporučené workflow:**

1. **BASIC režim** - orientační výpočet
   - Použij `create_typical_year_weather()` (TMY)
   - Žádný API call potřeba
   - Rychlé, funguje offline

2. **STANDARD režim** - kalibrace s nedávnými daty
   - Nahraj CSV s posledními 7 dny spotřeby
   - Použij `fetch_hourly_weather()` pro free tier historii
   - Přesná kalibrace, zdarma

3. **ADVANCED režim** - dlouhodobá kalibrace
   - **Varianta A:** Vlastní dlouhodobá CSV data
   - **Varianta B:** Placený tarif pro historii
   - **Varianta C:** Syntetická data (méně přesné)

### 3. Error handling

Aplikace automaticky loguje:

```
📡 Stahuji počasí pro období 2023-01-01 až 2023-01-31
⚠ Data jsou 330 dní zpětně - vyžadují history API (placený)
  ⚠ 2023-01-01: History API nedostupné (free tier)
  ⚙ 2023-01-01: Generuji syntetická data
  ⚙ 2023-01-02: Generuji syntetická data
  ...
✓ Staženo 744/744 hodin (100.0% pokrytí)
⚠ VAROVÁNÍ: Použita syntetická data - výsledky mohou být nepřesné
```

### 4. Caching (budoucí zlepšení)

Pro snížení API callů zvažte:

```python
# Uložit stažená data do cache
import pickle

cache_file = f"cache_{location}_{start_date}_{end_date}.pkl"
if os.path.exists(cache_file):
    df = pd.read_pickle(cache_file)
else:
    df = fetch_hourly_weather(...)
    df.to_pickle(cache_file)
```

---

## Troubleshooting

### Problém 1: "API klíč není nastaven"

**Příčina:** Prázdný API klíč v konfiguraci

**Řešení:**
1. Zaregistrujte se na https://www.weatherapi.com/
2. Získejte API klíč
3. Zadejte v bočním panelu aplikace

### Problém 2: "History API nedostupné (free tier)"

**Příčina:** Požadujete data starší než 7 dní s free tier účtem

**Řešení A** (doporučeno):
- Použijte BASIC režim s TMY
- Nebo nahrajte vlastní CSV data

**Řešení B:**
- Upgradujte na placený tarif
- https://www.weatherapi.com/pricing.aspx

**Řešení C:**
- Pokračujte se syntetickými daty
- Berete na vědomí nižší přesnost

### Problém 3: "403 Forbidden"

**Příčina:** API klíč neplatný nebo překročen limit

**Řešení:**
1. Zkontrolujte API klíč (copy-paste)
2. Zkontrolujte limity na https://www.weatherapi.com/my/
3. Vyčkejte reset limitu (měsíční/denní)

### Problém 4: Prázdná data

**Příčina:** Všechny API cally selhaly

**Diagnostika:**
```powershell
python test_weather_api.py
```

Zkontrolujte výstup pro detaily selhání.

### Problém 5: Nízké pokrytí (<80%)

**Varování:**
```
✓ Staženo 6500/8760 hodin (74.2% pokrytí)
⚠ VAROVÁNÍ: Pouze 74.2% dat - výsledky mohou být nepřesné
```

**Příčina:** Syntetická data doplňují mezery

**Řešení:**
- Pro přesné výsledky: použijte úplná data
- Pro odhad: pokračujte s varováním

---

## 📞 Podpora

**WeatherAPI.com dokumentace:**
- https://www.weatherapi.com/docs/

**Naše implementace:**
- Soubor: `core/weather_api.py`
- Testy: `test_weather_api.py`
- Issues: viz `TROUBLESHOOTING.md`

---

## 📝 Changelog

### v1.1 (2024) - Vylepšená verze
- ✅ Přidán tříúrovňový fallback systém
- ✅ Automatická detekce free tier limitů
- ✅ Syntetická data jako záloha
- ✅ Lepší error handling a uživatelské zprávy
- ✅ Validace pokrytí dat (coverage %)
- ✅ Optimalizace pro free tier

### v1.0 (2024) - Původní verze
- Basic implementace history.json
- Jednoduchý error handling

---

**✅ Aplikace je nyní plně funkční i s free tier účtem WeatherAPI.com!**
