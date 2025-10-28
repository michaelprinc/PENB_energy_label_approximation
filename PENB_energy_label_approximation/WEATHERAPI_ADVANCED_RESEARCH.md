# POKROČILÝ VÝZKUM WEATHERAPI - ALTERNATIVNÍ METODY

**Datum:** 28. října 2025  
**Zdroj:** Oficiální dokumentace WeatherAPI.com

---

## 🔍 ZJIŠTĚNÉ INFORMACE Z DOKUMENTACE

### 1. **Future API - 3 hodinový interval**

✅ **POTVRZENO:**  
WeatherAPI poskytuje **Future API** pro data mezi 14-300/365 dny v budoucnosti.

**Klíčové vlastnosti:**
- **Hodinový interval:** Pro Free a nižší tarifu - data v **3 hodinovém intervalu**
- **Dostupnost:** 
  - Pro+ plan: 300 dní dopředu, daily + hourly (3h interval)
  - Business: 300 dní dopředu, daily + hourly (3h interval)
  - Enterprise: 365 dní dopředu, daily, hourly a **15 min interval**

**Endpoint:**
```
http://api.weatherapi.com/v1/future.json
```

**Parametry:**
- `dt`: datum ve formátu yyyy-MM-dd (mezi 14-300/365 dny od dneška)
- `q`: lokace (město, souřadnice, atd.)

**⚠️ PROBLÉM PRO HISTORICKÁ DATA:**
- Future API je pro **BUDOUCNOST**, ne historii
- Pro historická data je stále nutné History API

---

### 2. **History API - Skutečné omezení**

**Z dokumentace a testů:**
- **FREE tier:** Max 7-8 dní zpětně
- **Pro+ plan:** Max 365 dní zpětně
- **Business plan:** Max 365 dní zpětně
- **Enterprise plan:** Od 1. ledna 2010 zpětně

**Formát dat:**
- FREE: Hodinový interval (24 hodin/den)
- Enterprise: Volitelný **15 min interval** (`tp=15`)

**⚠️ ZÁVĚR:**
- **Není dostupná 3hodinová frekvence** pro historická data
- Free tier má skutečně limit ~8 dní
- Pro starší data je nutný **placený tarif** nebo **alternativní řešení**

---

### 3. **Search/Autocomplete API - Location ID**

✅ **POTVRZENO:**  
WeatherAPI má Search API pro získání location ID.

**Endpoint:**
```
http://api.weatherapi.com/v1/search.json?key=<API_KEY>&q=<query>
```

**Vrací:**
```json
[
  {
    "id": 2801268,
    "name": "London",
    "region": "City of London, Greater London",
    "country": "United Kingdom",
    "lat": 51.52,
    "lon": -0.11,
    "url": "london-city-of-london-greater-london-united-kingdom"
  }
]
```

**Následné použití:**
```
q=id:2801268
```

**POUŽITÍ PRO APLIKACI:**
1. GPS → `q=50.0755,14.4378`
2. Search API vrátí název + ID
3. Použít ID pro další volání (lepší stabilita)

---

### 4. **Bulk Request - Možnost optimalizace**

✅ **DOSTUPNÉ:** Pro Pro+ a vyšší tarifu

**Endpoint:**
```
POST http://api.weatherapi.com/v1/current.json?key=<API_KEY>&q=bulk
Content-Type: application/json
```

**Body:**
```json
{
  "locations": [
    {"q": "53,-0.12", "custom_id": "my-id-1"},
    {"q": "London", "custom_id": "any-internal-id"}
  ]
}
```

**Výhody:**
- 1 request pro více lokací
- Každá lokace = 1 call k limitu
- Max 50 lokací/request

**⚠️ NEVHODNÉ PRO NAŠE POUŽITÍ:**
- Nepomůže s free tier limitem
- Bulk funguje jen pro současné API, ne historii

---

## 💡 ALTERNATIVNÍ ŘEŠENÍ PRO HISTORICKÁ DATA

### A) **Doporučené řešení: Hybridní přístup**

```python
def fetch_weather_hybrid(location, start_date, end_date, api_key):
    """
    1. Čerstvá data (0-8 dní): History API (hodinový)
    2. Stará data (9+ dní): Syntetická s upozorněním
    3. Location ID cache pro stabilitu
    """
    
    # 1. Získej Location ID (jen 1x, cache)
    location_id = get_or_cache_location_id(location, api_key)
    
    # 2. Stáhni dostupná data
    recent_data = fetch_history(location_id, recent_dates)
    
    # 3. Pro starší data - syntetická aproximace
    old_data = generate_synthetic_with_astronomy(
        location_id, old_dates, api_key
    )
    
    return merge(recent_data, old_data)
```

### B) **Astronomy API jako základ syntetických dat**

✅ **ZDARMA** a dostupné i pro historická data!

**Endpoint:**
```
http://api.weatherapi.com/v1/astronomy.json?key=<API_KEY>&q=London&dt=2023-01-15
```

**Vrací:**
- Sunrise/sunset časy
- Moonrise/moonset
- Moon phase a illumination

**POUŽITÍ:**
```python
def generate_synthetic_with_astronomy(location, date, api_key):
    # Získej astronomická data (ZDARMA!)
    astro = fetch_astronomy(location, date, api_key)
    
    # Použij sunrise/sunset pro přesnější GHI model
    sunrise = astro['sunrise']  # e.g., "06:45 AM"
    sunset = astro['sunset']    # e.g., "05:30 PM"
    
    # Generuj GHI jen mezi sunrise-sunset
    # Výrazně přesnější než固定ní 6:00-18:00!
```

### C) **Timezone API pro lokalizaci**

✅ **ZDARMA** - Získej timezone pro lokaci

```
http://api.weatherapi.com/v1/timezone.json?key=<API_KEY>&q=London
```

Vrací:
- `tz_id`: "Europe/London"
- `localtime`: "2025-01-15 14:30"

**POUŽITÍ:** Správná konverze UTC ↔ local time

---

## 🛠️ IMPLEMENTAČNÍ DOPORUČENÍ

### **Strategie 1: FREE TIER optimalizace**

```python
# 1. Location ID cache
location_cache = {
    "Praha": {"id": 2759794, "lat": 50.08, "lon": 14.42},
    # ... cached při prvním použití
}

# 2. Astronomy-based synthetic data
def synthetic_weather(location_id, date, api_key):
    # Použij Astronomy API (free!)
    astro = fetch_astronomy(f"id:{location_id}", date, api_key)
    
    # Timezone API (free!)
    tz = fetch_timezone(f"id:{location_id}", api_key)
    
    # Generuj přesnější syntetická data
    return generate_with_astro_context(astro, tz, date)

# 3. Smart fallback
def fetch_historical(location, dates, api_key):
    location_id = get_cached_location_id(location, api_key)
    
    recent = []
    synthetic = []
    
    for date in dates:
        age = (today - date).days
        
        if age <= 8:
            # Real data
            data = fetch_history_api(location_id, date, api_key)
            recent.append(data)
        else:
            # Synthetic with astronomy
            data = synthetic_weather(location_id, date, api_key)
            data['is_synthetic'] = True
            synthetic.append(data)
    
    return {
        'real': recent,
        'synthetic': synthetic,
        'warnings': [f"{len(synthetic)} dní použito syntetická data"]
    }
```

### **Strategie 2: Placený tarif (Pro+)**

**Cena:** ~$10/měsíc  
**Benefit:**
- Historie 365 dní zpětně
- 3M volání/měsíc
- Pollen, Air Quality data
- Marine weather s tide

**ROI kalkulace:**
```
Cena: $10/měsíc = $120/rok
Volání: 3M/měsíc = 100k/den

Pro aplikaci s >50 uživateli/měsíc → vyplatí se!
```

---

## 📊 POROVNÁNÍ ŘEŠENÍ

| Řešení | Přesnost | Cena | Složitost | Doporučení |
|--------|----------|------|-----------|------------|
| **Free tier + synthetic** | ⭐⭐⭐ | $0 | Střední | ✅ MVP/Demo |
| **Free tier + astronomy** | ⭐⭐⭐⭐ | $0 | Vysoká | ✅ Produkce (free) |
| **Pro+ tarif** | ⭐⭐⭐⭐⭐ | $10/m | Nízká | ✅ Produkce (paid) |
| **Enterprise** | ⭐⭐⭐⭐⭐ | $100+/m | Nízká | ⚠️ Až při škálování |

---

## 🎯 FINÁLNÍ DOPORUČENÍ

### **Pro aktuální verzi aplikace:**

1. **Zachovat current implementation** s fallbacky
2. **Přidat Location ID caching:**
   ```python
   # Jednou pro lokalitu → cache na disk
   location_id = search_and_cache(location, api_key)
   q = f"id:{location_id}"  # Stabilnější než název
   ```

3. **Vylepšit syntetická data pomocí Astronomy API:**
   ```python
   # ZDARMA a přesnější!
   astro = fetch_astronomy(location, date, api_key)
   synthetic_data = generate_with_sunrise_sunset(astro)
   ```

4. **Informovat uživatele:**
   ```
   "⚠️ Data starší než 8 dní jsou aproximována pomocí 
   astronomického modelu. Pro přesnější výsledky použijte 
   data z posledních 7 dní."
   ```

5. **Future upgrade path:**
   - Nabídnout Pro+ tarif jako premium feature
   - $10/měsíc → neomezená historie, pollen, air quality
   - ROI při >10 aktivních uživatelích/měsíc

---

## 📝 ZÁVĚR

**Odpovědi na vaše otázky:**

1. ✅ **3 hodinový interval:** Existuje, ale jen pro **Future API** (budoucnost)
2. ❌ **Pro historii:** Není dostupný ve free tier
3. ✅ **Location ID přístup:** Funguje, doporučuji implementovat!
4. ✅ **Astronomy API:** Vynikající zdroj pro vylepšení syntetických dat (ZDARMA)
5. ❌ **Free tier historie:** Potvrzeno max 8 dní

**Nejlepší řešení:**  
Hybrid: Real data (0-8 dní) + Astronomy-enhanced synthetic (9+ dní)

---

**Testovací skripty připravené:**
- `test_weather_history.py` - Základní test
- `test_weather_boundary.py` - Detailní hranice
- `test_astronomy_api.py` - **NOVÝ** (připravím)
- `test_location_search.py` - **NOVÝ** (připravím)
