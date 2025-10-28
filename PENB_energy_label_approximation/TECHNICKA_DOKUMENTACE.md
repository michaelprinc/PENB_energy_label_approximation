# TECHNICKÁ DOKUMENTACE
## Aplikace pro Orientační Odhad Energetické Náročnosti Bytu

**Verze:** 1.1.0  
**Datum:** 28. října 2025  
**Autor:** Systém pro aproximaci PENB z provozních dat

---

## 📑 OBSAH

1. [Úvod a účel](#1-úvod-a-účel)
2. [Architektura systému](#2-architektura-systému)
3. [Datové modely](#3-datové-modely)
4. [Metodologie výpočtu](#4-metodologie-výpočtu)
5. [Fyzikální model (RC model)](#5-fyzikální-model-rc-model)
6. [Kalibrace parametrů](#6-kalibrace-parametrů)
7. [Preprocessing dat](#7-preprocessing-dat)
8. [Weather API integrace](#8-weather-api-integrace)
9. [Simulace a výpočet](#9-simulace-a-výpočet)
10. [Klasifikace a metriky](#10-klasifikace-a-metriky)
11. [Hodnocení kvality](#11-hodnocení-kvality)
12. [Uživatelské rozhraní](#12-uživatelské-rozhraní)
13. [API Reference](#13-api-reference)
14. [Konfigurace](#14-konfigurace)
15. [Limitace a omezení](#15-limitace-a-omezení)

---

## 1. ÚVOD A ÚČEL

### 1.1 Cíl aplikace

Aplikace poskytuje **orientační odhad energetické náročnosti bytu** na základě:
- Provozních dat (měřené spotřeby energie)
- Meteorologických dat (stažených z WeatherAPI.com)
- Geometrie bytu
- Parametrů vytápěcího systému

**NENÍ** náhradou za oficiální Průkaz energetické náročnosti budovy (PENB) podle vyhlášky č. 264/2020 Sb.

### 1.2 Klíčové funkce

✅ **Automatická kalibrace** termického modelu na provozní data  
✅ **Tři režimy** kvality výpočtu (BASIC, STANDARD, ADVANCED)  
✅ **Interaktivní GUI** (Streamlit)  
✅ **HTML reporty** s grafickým znázorněním  
✅ **Flexibilní nastavení** den/noc režimů a měsíců bez topení  
✅ **Hodnocení spolehlivosti** výsledků

### 1.3 Použité technologie

- **Python 3.8+**
- **Streamlit** - webové GUI
- **Pandas & NumPy** - zpracování dat
- **SciPy** - optimalizace
- **Pydantic** - validace dat
- **WeatherAPI.com** - meteorologická data
- **Jinja2** - HTML reporty

---

## 2. ARCHITEKTURA SYSTÉMU

### 2.1 Struktura projektu

```
PENB_energy_label_approximation/
├── main.py                     # Hlavní vstupní bod
├── requirements.txt            # Python závislosti
├── app_gui/
│   ├── __init__.py
│   └── gui_main.py            # Streamlit aplikace
├── core/
│   ├── __init__.py
│   ├── data_models.py         # Pydantic modely
│   ├── config.py              # Správa konfigurace
│   ├── weather_api.py         # WeatherAPI integrace
│   ├── preprocess.py          # Čištění a preprocessing
│   ├── baseline_split.py      # Rozdělení vytápění/TUV
│   ├── rc_model.py            # Fyzikální model 1R1C
│   ├── calibrator.py          # Kalibrace parametrů
│   ├── simulate_year.py       # Roční simulace
│   ├── metrics.py             # Klasifikace a metriky
│   └── quality_flags.py       # Hodnocení kvality
├── reports/
│   ├── __init__.py
│   └── report_builder.py      # Generátor HTML reportů
├── storage/
│   ├── token_store.json       # API klíče (lokální)
│   └── user_inputs.json       # Poslední vstupy
└── tests/
    ├── test_imports.py
    ├── test_new_features.py
    └── ...
```

### 2.2 Datový tok

```
┌─────────────────┐
│ Uživatelský     │
│ vstup (GUI)     │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────┐
│ 1. VALIDACE VSTUPŮ              │
│    (Pydantic models)            │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│ 2. STAŽENÍ POČASÍ               │
│    (WeatherAPI.com)             │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│ 3. PREPROCESSING                │
│    - Čištění dat                │
│    - Zarovnání časových řad     │
│    - Rozdělení vytápění/TUV     │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│ 4. KALIBRACE RC MODELU          │
│    - Lineární odhad             │
│    - Optimalizace (L-BFGS-B)    │
│    - nebo Differential Evolution│
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│ 5. SIMULACE REFERENČNÍHO ROKU   │
│    - Typický meteorologický rok │
│    - Hodinová simulace          │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│ 6. VÝPOČET VÝSLEDKŮ             │
│    - Roční potřeba tepla        │
│    - Primární energie           │
│    - Klasifikace do tříd A-G    │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│ 7. HODNOCENÍ KVALITY            │
│    - Quality score              │
│    - Disclaimery                │
│    - Návrhy zlepšení            │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────┐
│ HTML Report     │
│ + GUI výstup    │
└─────────────────┘
```

---

## 3. DATOVÉ MODELY

### 3.1 Hlavní datové struktury (Pydantic)

#### 3.1.1 `ApartmentGeometry`
```python
class ApartmentGeometry(BaseModel):
    area_m2: float           # Plocha bytu [m²]
    height_m: float          # Výška stropu [m]
    
    @property
    def volume_m3(self) -> float:
        return self.area_m2 * self.height_m
```

#### 3.1.2 `HeatingSystemInfo`
```python
class HeatingSystemInfo(BaseModel):
    system_type: HeatingSystemType
    # Možnosti: CONDENSING_BOILER, DIRECT_ELECTRIC,
    #           HEAT_PUMP_AIR, HEAT_PUMP_WATER, UNKNOWN
    
    efficiency_or_cop: Optional[float]
    # Pro kotel: účinnost 0-1
    # Pro TČ: COP > 1
```

#### 3.1.3 `TemperatureProfile`
```python
class TemperatureProfile(BaseModel):
    day_temp_c: float = 21.0          # Denní teplota [°C]
    night_temp_c: float = 19.0        # Noční teplota [°C]
    day_start_hour: int = 6           # Začátek dne [hodina 0-23]
    day_end_hour: int = 22            # Konec dne [hodina 0-23]
```

**Validace:**
- `night_temp_c` ≤ `day_temp_c`
- `day_end_hour` > `day_start_hour`

#### 3.1.4 `DailyEnergyData`
```python
class DailyEnergyData(BaseModel):
    date: date                        # Datum
    energy_total_kwh: float           # Celková spotřeba [kWh]
    note: Optional[str]               # Poznámka
```

#### 3.1.5 `UserInputs` (kompletní vstup)
```python
class UserInputs(BaseModel):
    geometry: ApartmentGeometry
    heating_system: HeatingSystemInfo
    location: str                      # Město nebo "lat,lon"
    computation_mode: ComputationMode  # BASIC/STANDARD/ADVANCED
    comfort_temperature: TemperatureProfile
    daily_energy: List[DailyEnergyData]
    avg_indoor_temp_c: Optional[float]
    non_heating_months: Optional[List[int]]  # NOVÉ v 1.1.0
```

#### 3.1.6 `CalibratedParameters`
```python
class CalibratedParameters(BaseModel):
    H_env_W_per_K: float               # Tepelné ztráty obálkou [W/K]
    infiltration_rate_per_h: float     # Intenzita infiltrace [1/h]
    C_th_J_per_K: float                # Tepelná kapacita [J/K]
    baseline_TUV_kwh_per_day: float    # Baseline TUV [kWh/den]
    internal_gains_W_per_m2: float     # Interní zisky [W/m²]
    
    # Kvalita kalibrace
    rmse_temperature_c: float          # RMSE vnitřní teploty [°C]
    mape_energy_pct: float             # MAPE denní energie [%]
```

#### 3.1.7 `AnnualResults`
```python
class AnnualResults(BaseModel):
    heating_demand_kwh_per_m2_year: float    # Měrná potřeba tepla
    primary_energy_kwh_per_m2_year: float    # Primární energie
    energy_class: EnergyClass                # Třída A-G
    quality_level: QualityLevel              # LOW/MEDIUM/HIGH
    
    # Interval spolehlivosti
    heating_demand_lower_bound: Optional[float]
    heating_demand_upper_bound: Optional[float]
    
    disclaimers: List[str]
    computation_date: datetime
```

### 3.2 Enumerace

```python
class ComputationMode(str, Enum):
    BASIC = "basic"        # Min. 1 den, hrubý odhad
    STANDARD = "standard"  # Min. 7 dní, 1R1C kalibrace
    ADVANCED = "advanced"  # Min. 28 dní, globální optimalizace

class QualityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class EnergyClass(str, Enum):
    A = "A"  # Nejlepší
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"  # Nejhorší
```

---

## 4. METODOLOGIE VÝPOČTU

### 4.1 Přehled režimů výpočtu

| Režim | Min. data | Metoda | Přesnost | Rychlost |
|-------|-----------|--------|----------|----------|
| **BASIC** | 1 den | Lineární regrese | ⭐⭐ | ⚡⚡⚡ |
| **STANDARD** | 7 dní | 1R1C + L-BFGS-B | ⭐⭐⭐⭐ | ⚡⚡ |
| **ADVANCED** | 28 dní | 1R1C + Diff. Evolution | ⭐⭐⭐⭐⭐ | ⚡ |

### 4.2 Fáze výpočtu

#### Fáze 1: Získání dat
1. **Validace vstupů** (Pydantic)
2. **Stažení počasí** (WeatherAPI.com)
3. **Čištění dat** (interpolace krátkých mezer, detekce outlierů)

#### Fáze 2: Preprocessing
1. **Zarovnání** časových řad (denní ↔ hodinová)
2. **Rozdělení** spotřeby na vytápění vs. TUV
3. **Vytvoření** hodinového teplotního profilu

#### Fáze 3: Kalibrace
1. **Počáteční odhad** parametrů (lineární regrese)
2. **Optimalizace** parametrů RC modelu
3. **Validace** kvality kalibrace (RMSE, MAPE)

#### Fáze 4: Simulace
1. **Vytvoření** typického meteorologického roku
2. **Hodinová simulace** s kalibrovaným modelem
3. **Agregace** na roční potřebu tepla

#### Fáze 5: Výsledky
1. **Výpočet** primární energie
2. **Klasifikace** do energetických tříd
3. **Hodnocení** spolehlivosti
4. **Generování** reportu

---

## 5. FYZIKÁLNÍ MODEL (RC MODEL)

### 5.1 Teorie 1R1C modelu

**Koncept:**  
Budova je reprezentována jako **jeden tepelný uzel** s:
- **1 tepelným odporem (R)** → tepelné ztráty obálkou
- **1 tepelnou kapacitou (C)** → tepelná setrvačnost

**Diferenciální rovnice:**

$$
C_{th} \frac{dT_{in}}{dt} = Q_{heat} + Q_{solar} + Q_{internal} - H_{total} \cdot (T_{in} - T_{out})
$$

Kde:
- $C_{th}$ [J/K] = tepelná kapacita budovy
- $T_{in}$ [°C] = vnitřní teplota
- $T_{out}$ [°C] = venkovní teplota
- $Q_{heat}$ [W] = dodané teplo z topení
- $Q_{solar}$ [W] = sluneční zisky
- $Q_{internal}$ [W] = interní zisky (lidé, spotřebiče)
- $H_{total}$ [W/K] = celkové tepelné ztráty

### 5.2 Komponenty $H_{total}$

$$
H_{total} = H_{env} + H_{vent}
$$

**1. Tepelné ztráty obálkou:**
$$
H_{env} = \sum (U_i \cdot A_i)
$$
- $U_i$ [W/(m²·K)] = součinitel prostupu tepla
- $A_i$ [m²] = plocha konstrukce

**2. Větrací ztráty:**
$$
H_{vent} = \rho_{air} \cdot c_p \cdot n \cdot V / 3600
$$
- $\rho_{air}$ = 1.2 kg/m³ (hustota vzduchu)
- $c_p$ = 1005 J/(kg·K) (měrné teplo vzduchu)
- $n$ [1/h] = intenzita infiltrace
- $V$ [m³] = objem bytu

### 5.3 Tepelné zisky

**Sluneční zisky:**
$$
Q_{solar} = GHI \cdot A_{floor} \cdot \alpha_{solar}
$$
- $GHI$ [W/m²] = globální sluneční záření
- $A_{floor}$ [m²] = plocha bytu
- $\alpha_{solar}$ = 0.02 (efektivní apertura pro byty, typicky malá)

**Interní zisky:**
$$
Q_{internal} = q_{int} \cdot A_{floor}
$$
- $q_{int}$ = 3 W/m² (typická hodnota pro byty)

### 5.4 Numerická integrace (Euler forward)

Pro časový krok $\Delta t$ = 3600 s (1 hodina):

$$
T_{in}(t + \Delta t) = T_{in}(t) + \frac{dT_{in}}{dt} \cdot \Delta t
$$

$$
\frac{dT_{in}}{dt} = \frac{Q_{in} - Q_{out}}{C_{th}}
$$

### 5.5 Odhad potřebného výkonu

V **ustáleném stavu** ($dT_{in}/dt = 0$):

$$
Q_{heat} = H_{total} \cdot (T_{setpoint} - T_{out}) - Q_{solar} - Q_{internal}
$$

Pokud $Q_{heat} < 0$ → **není potřeba topit** (nebo by bylo potřeba chladit).

---

## 6. KALIBRACE PARAMETRŮ

### 6.1 Metody kalibrace podle režimu

#### 6.1.1 BASIC režim
**Metoda:** Lineární regrese  
**Vstup:** Denní spotřeby + průměrné venkovní teploty  
**Model:**
$$
E_{heating,daily} = a \cdot \Delta T + b
$$

Kde:
- $a \approx 24 \cdot H_{total} / 1000$ [kWh/(K·den)]
- $\Delta T = T_{in,avg} - T_{out,avg}$

**Výstup:**
- Hrubý odhad $H_{total}$
- Předpokládaná infiltrace $n = 0.3$ 1/h
- Tepelná kapacita $C_{th} = 50 \cdot V$ Wh/K/m³

**Výhody:** Velmi rychlé, nevyžaduje hodinová data  
**Nevýhody:** Nízká přesnost, žádná dynamická simulace

#### 6.1.2 STANDARD režim
**Metoda:** L-BFGS-B lokální optimalizace  
**Vstup:** Hodinová data (weather + distributed energy)

**Optimalizované parametry:**
```python
params = [H_env, n, log(C_th), q_int]
```

**Cost funkce:**
$$
\text{cost} = 10 \cdot \text{RMSE}_{temp} + \text{MAPE}_{energy}
$$

- $\text{RMSE}_{temp}$ = RMS chyba vnitřní teploty [°C]
- $\text{MAPE}_{energy}$ = střední absolutní procentní chyba energie [%]

**Bounds:**
- $H_{env}$: 10 - 1000 W/K
- $n$: 0.05 - 2.0 1/h
- $\log(C_{th})$: $\ln(10^5)$ - $\ln(10^8)$ (→ $C_{th}$: 100 kJ/K - 100 MJ/K)
- $q_{int}$: 0 - 10 W/m²

**Algoritmus:** SciPy `minimize(..., method='L-BFGS-B')`

**Výhody:** Dobrá rovnováha rychlost/přesnost  
**Nevýhody:** Může uváznout v lokálním minimu

#### 6.1.3 ADVANCED režim
**Metoda:** Differential Evolution (globální optimalizace)  
**Vstup:** Stejný jako STANDARD

**Algoritmus:** SciPy `differential_evolution(...)`
```python
de_kwargs = dict(
    bounds=bounds,
    maxiter=100,
    popsize=10,
    seed=42,
    workers=ThreadPoolExecutor(max_workers=cpu_count-1)
)
```

**Výhody:** Najde globální minimum, robustnější  
**Nevýhody:** Pomalejší (paralelizace pomáhá)

### 6.2 Metriky kvality kalibrace

**RMSE teploty:**
$$
\text{RMSE}_{temp} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (T_{in,sim}^i - T_{in,obs}^i)^2}
$$

**MAPE energie:**
$$
\text{MAPE}_{energy} = \frac{100}{M} \sum_{j=1}^{M} \left| \frac{E_{obs}^j - E_{sim}^j}{E_{obs}^j + \epsilon} \right|
$$

**Interpretace:**
- RMSE < 0.5°C → **výborná** kalibrace
- RMSE < 1.0°C → **dobrá** kalibrace
- RMSE < 2.0°C → **přijatelná** kalibrace
- MAPE < 5% → **výborná** kalibrace
- MAPE < 10% → **dobrá** kalibrace
- MAPE < 20% → **přijatelná** kalibrace

---

## 7. PREPROCESSING DAT

### 7.1 Čištění meteorologických dat

**Funkce:** `clean_weather_data(df)`

**Kroky:**
1. **Kontrola časových razítek** → převod na datetime
2. **Odstranění duplikátů** podle timestamp
3. **Detekce mezer** v časové řadě
4. **Interpolace krátkých mezer** (max 3 hodiny)
   - Metoda: lineární interpolace
   - `limit=3, limit_area='inside'`
5. **Označení dlouhých mezer** (>3h) → **neinterpolovat!**
6. **Odstranění řádků** s NaN (dlouhé mezery)
7. **Kontrola rozsahu hodnot**
   - Teplota: -40°C až +50°C
   - Vlhkost: 0-100%

**KRITICKÉ:**  
Nesmí interpolovat mezi oddělenými měsíci! Data z června a srpna NESMÍ být spojována interpolací.

### 7.2 Baseline TUV (teplá užitková voda)

**Funkce:** `split_heating_and_tuv(daily_df, baseline_tuv_kwh=None)`

**Strategie:**

#### A) Automatický odhad (default)
```python
baseline_tuv = np.percentile(energy_total_kwh, 10)
```
- **Předpoklad:** 10% nejnižších spotřeb = dny bez topení (jen TUV)
- **Sanity check:** baseline < 50% průměru

#### B) Z měsíců bez topení (NOVÉ v 1.1.0)
```python
if non_heating_months:  # např. [5,6,7,8,9]
    summer_mask = (df['month'].isin(non_heating_months)) & (df['year'] == 2025)
    baseline_tuv = df.loc[summer_mask, 'energy_total_kwh'].mean()
```
- **Výhoda:** Přesnější (více dat, explicitní výběr)
- **Stabilnější** než percentil

#### C) Manuální podíl
```python
baseline_tuv = energy_total * (tuv_percentage / 100)
```

**Rozdělení:**
$$
E_{heating} = \max(E_{total} - E_{TUV,baseline}, 0)
$$

### 7.3 Distribuce denní energie na hodiny

**Funkce:** `distribute_daily_heating_to_hours(...)`

**Metoda:** Proporcionální podle tepelné potřeby

Pro každý den:
1. Vypočti $\Delta T_i = \max(T_{in} - T_{out,i}, 0)$ pro každou hodinu $i$
2. Celková denní potřeba: $\sum_i \Delta T_i$
3. Podíl hodiny: $w_i = \Delta T_i / \sum_i \Delta T_i$
4. Energie hodiny: $E_i = w_i \cdot E_{day,total}$

**Ověření:** $\sum_i E_i = E_{day,total}$ (rekonstrukce musí sedět)

### 7.4 Hodinový teplotní profil

**Funkce:** `create_hourly_indoor_temp(...)`

**Verze 1.1.0 - Flexibilní den/noc:**

```python
def create_hourly_indoor_temp(
    daily_avg_temp: Optional[float],
    hourly_weather_df: pd.DataFrame,
    day_temp: Optional[float] = None,
    night_temp: Optional[float] = None,
    day_start_hour: int = 6,
    day_end_hour: int = 22,
    day_night_delta: float = 0.5
):
    """
    Vytvoří hodinový teplotní profil.
    
    PRAVIDLA PRECEDENCE:
    1. Pokud jsou day_temp a night_temp zadány → použijí se (PRIORITA)
    2. Jinak pokud je zadána daily_avg_temp → odvození day/night = avg ± delta
    3. Jinak → fallback na konstantní profil (daily_avg_temp)
    
    Validace: night_temp ≤ day_temp
    """
    for hour in hours:
        if day_start_hour <= hour < day_end_hour:
            T_in[hour] = day_temp
        else:
            T_in[hour] = night_temp
```

**Pravidla precedence (GUI verze 1.1.0):**

V GUI uživatel volí jeden ze dvou režimů:

**Režim A: "Den/Noc režim"** (doporučeno pro přesnost)
- Zadá denní teplotu (např. 21°C)
- Zadá noční teplotu (např. 19°C)  
- Zadá časové rozsahy (např. den 6:00-22:00)
- Průměrná teplota se **automaticky vypočítá** vážením podle hodin
- Tento režim má **PRIORITU** při výpočtu

**Režim B: "Průměrná teplota"** (jednodušší, méně přesné)
- Zadá pouze jednu hodnotu (např. 21°C)
- Použije se **konstantní** teplotní profil (den = noc = průměr)
- Vhodné pro rychlý odhad nebo pokud není známý teplotní režim

**GUI implementace:**
- Radio button v TAB 2 "Byt & Systém" pro výběr režimu
- Dynamické zobrazení vstupních polí podle zvoleného režimu
- Validace: night_temp ≤ day_temp, day_end_hour > day_start_hour
- Info tooltip s vypočítanou průměrnou teplotou v režimu A

**Starší verze (fallback):**  
Sinusoidní variace kolem průměru:
$$
T_{in}(h) = T_{avg} + \Delta T \cdot \sin\left(2\pi \frac{h - 2}{24}\right)
$$

---

## 8. WEATHER API INTEGRACE

### 8.1 WeatherAPI.com

**Endpoint:** `http://api.weatherapi.com/v1/`

**Podporované API:**
1. **forecast.json** - předpověď + nedávná historie (free tier: 7 dní)
2. **history.json** - historická data (placený tarif)
3. **current.json** - aktuální počasí

### 8.2 Strategie stahování

**Funkce:** `fetch_hourly_weather(location, start_date, end_date, api_key)`

**Třístupňová strategie:**

```python
for date in date_range:
    # Krok 1: Zkus forecast API (free tier)
    if days_back <= 7:
        try:
            data = fetch_forecast(date)
            success = True
        except:
            pass
    
    # Krok 2: Zkus history API (placený)
    if not success:
        try:
            data = fetch_history(date)
            success = True
        except HTTP_400:  # Free tier limitation
            pass
    
    # Krok 3: Fallback - syntetická data
    if not success:
        data = generate_synthetic(date)
```

**Syntetická data:**
- Teplotní sinusoida podle měsíce
- GHI podle denní doby
- Konstantní vlhkost a vítr

### 8.3 Typický meteorologický rok (TMY)

**Funkce:** `create_typical_year_weather(location, api_key)`

**MVP implementace:**  
Sinusoidní aproximace (8760 hodin):

$$
T(d, h) = T_{avg} + 10 \cdot \sin\left(2\pi \frac{d - 80}{365}\right) + 3 \cdot \sin\left(2\pi \frac{h - 6}{24}\right)
$$

- $d$ = den v roce (1-365)
- $h$ = hodina dne (0-23)
- $T_{avg}$ = průměrná roční teplota (detekována z aktuálního počasí)

**Sluneční záření:**
$$
GHI(d, h) = 500 \cdot \sin\left(\pi \frac{h - 6}{12}\right) \cdot \left(1 + 0.5 \sin\left(2\pi \frac{d}{365}\right)\right)
$$
- Pouze 6:00-18:00
- Maximum v létě, minimum v zimě

**Produkční verze (TODO):**  
Použít skutečná TMY data (např. PVGIS, Meteonorm)

### 8.4 Detekce lokace

**Funkce:** `detect_location()`

**Metoda:** IP geolokace pomocí `geocoder` library

```python
g = geocoder.ip('me')
city = g.city
lat, lng = g.lat, g.lng
```

**Fallback:** Praha (50.0755, 14.4378)

---

## 9. SIMULACE A VÝPOČET

### 9.1 Roční simulace

**Funkce:** `simulate_annual_heating_demand(...)`

**Vstup:**
- Kalibrované parametry
- Typický meteorologický rok (8760 hodin)
- Geometrie bytu
- Komfortní teplotní profil

**Proces:**

```python
model = RC1Model(calibrated_params)

for hour in tmy_year:
    # Urči setpoint podle hodiny
    T_setpoint = comfort_profile.get_temp(hour.hour)
    
    # Vypočti potřebné teplo
    Q_heat = model.estimate_heating_demand(
        T_setpoint,
        hour.temp_out,
        hour.ghi
    )
    
    annual_demand[hour] = Q_heat
```

**Výstup:**
- Hodinová potřeba topného výkonu [W]
- Agregace na roční energii [kWh]
- Měrná potřeba [kWh/(m²·rok)]

### 9.2 Primární energie

**Funkce:** `calculate_primary_energy(...)`

**Vzorce:**

$$
E_{primary} = \frac{E_{heating}}{\eta_{system}} \cdot f_{PE}
$$

Kde:
- $\eta_{system}$ = účinnost (kotel) nebo 1/COP (TČ)
- $f_{PE}$ = faktor primární energie

**Faktory primární energie (ČR orientačně):**
- Elektřina: $f_{PE}$ = 3.0
- Zemní plyn: $f_{PE}$ = 1.1

**Příklady:**

**1. Kondenzační kotel (η = 0.92):**
$$
E_{plyn} = \frac{E_{heating}}{0.92}
$$
$$
E_{primary} = E_{plyn} \cdot 1.1
$$

**2. Tepelné čerpadlo (COP = 3.2):**
$$
E_{el} = \frac{E_{heating}}{3.2}
$$
$$
E_{primary} = E_{el} \cdot 3.0
$$

**3. Přímotop (η = 1.0):**
$$
E_{primary} = E_{heating} \cdot 3.0
$$

### 9.3 Interval spolehlivosti

**Funkce:** `estimate_uncertainty_bounds(...)`

**Metoda:** Empirický odhad podle kvality kalibrace

$$
\text{uncertainty} = \frac{\text{MAPE}_{energy}}{100} + 0.05 \cdot N_{warnings}
$$

$$
E_{lower} = E_{heating} \cdot (1 - \text{uncertainty})
$$
$$
E_{upper} = E_{heating} \cdot (1 + \text{uncertainty})
$$

**Max uncertainty:** 50%

**Interpretace:**
- MAPE 5%, 0 varování → ±5% interval
- MAPE 15%, 3 varování → ±30% interval

---

## 10. KLASIFIKACE A METRIKY

### 10.1 Energetické třídy

**Funkce:** `classify_energy_label(...)`

**Hranice (orientační, zjednodušené):**

#### Podle primární energie [kWh/(m²·rok)]:

| Třída | Rozsah | Popis |
|-------|--------|-------|
| **A** | < 50 | Mimořádně úsporná (pasivní domy) |
| **B** | 50-75 | Velmi úsporná (nízkoenergetické) |
| **C** | 75-110 | Úsporná (moderní budovy) |
| **D** | 110-150 | Méně úsporná (průměr nové výstavby) |
| **E** | 150-200 | Nehospodárná |
| **F** | 200-270 | Velmi nehospodárná |
| **G** | > 270 | Mimořádně nehospodárná (panelové domy) |

**POZNÁMKA:**  
Skutečný PENB používá složitější metodiku podle TNI 73 0329/Z1.  
Tyto hranice jsou **pouze orientační** pro účely této aplikace!

### 10.2 Barvy tříd

```python
colors = {
    'A': "#00A651",  # tmavě zelená
    'B': "#4AB849",  # zelená
    'C': "#C5D82F",  # žlutozelená
    'D': "#FFF200",  # žlutá
    'E': "#FDB913",  # oranžová
    'F': "#F37021",  # tmavě oranžová
    'G': "#ED1C24"   # červená
}
```

### 10.3 Popisky tříd

| Třída | Popis |
|-------|-------|
| A | Mimořádně úsporná |
| B | Velmi úsporná |
| C | Úsporná |
| D | Méně úsporná |
| E | Nehospodárná |
| F | Velmi nehospodárná |
| G | Mimořádně nehospodárná |

---

## 11. HODNOCENÍ KVALITY

### 11.1 Quality Score systém

**Funkce:** `assess_quality_level(...)`

**Skóre (0-100):**

```python
score = 0

# 1. Režim výpočtu
score += {ADVANCED: 30, STANDARD: 20, BASIC: 5}

# 2. Délka dat
if n_days >= 28:  score += 30
elif n_days >= 14: score += 20
elif n_days >= 7:  score += 10
else:              score += 2

# 3. RMSE teploty
if RMSE < 0.5:  score += 20
elif RMSE < 1.0: score += 15
elif RMSE < 2.0: score += 10
else:            score += 2

# 4. MAPE energie
if MAPE < 5:   score += 20
elif MAPE < 10: score += 15
elif MAPE < 20: score += 10
else:           score += 2

# 5. Penalizace za varování
score -= len(warnings) * 5
```

**Klasifikace:**
- score ≥ 70 → **HIGH** quality
- score ≥ 40 → **MEDIUM** quality
- score < 40 → **LOW** quality

### 11.2 Disclaimery

**Funkce:** `generate_disclaimers(...)`

**Vždy:**
- "Toto NENÍ oficiální PENB"
- Upozornění podle quality level

**Podmíněné:**
- Režim BASIC → "Pouze hrubý odhad"
- Málo dat → "Doporučeno více dat"
- Varování v datech → "Zjištěny problémy"

### 11.3 Návrhy zlepšení

**Funkce:** `suggest_improvements(...)`

**Kategorie návrhů:**

1. **Výpočetní režim:**
   - BASIC → "Použijte STANDARD/ADVANCED"

2. **Množství dat:**
   - < 28 dní → "Doplňte více dat"

3. **Kalibrace:**
   - RMSE > 2°C → "Zkontrolujte vnitřní teploty"
   - MAPE > 20% → "Zkontrolujte odečty spotřeby"

4. **Fyzikální parametry:**
   - n > 0.8 → "Vysoká infiltrace, zvažte výměnu oken"
   - H_env > 200 → "Vysoké ztráty, zvažte zateplení"

5. **Úspěch:**
   - HIGH quality → "Pro oficiální PENB kontaktujte odborníka"

---

## 12. UŽIVATELSKÉ ROZHRANÍ

### 12.1 Streamlit GUI

**Soubor:** `app_gui/gui_main.py`

**Struktura:** 5 záložek (tabs)

#### TAB 1: Lokalita 📍
```python
- Auto-detekce lokace (IP geolokace)
- Ruční zadání (město nebo "lat,lon")
- Uložení poslední lokace
```

#### TAB 2: Byt & Systém 🏠
```python
# Geometrie
- Plocha [m²]: number_input(10-500)
- Výška stropu [m]: number_input(2.0-5.0)
- → Automatický výpočet objemu

# Vnitřní teplota (NOVÉ v 1.1.0)
- Režim: radio("Den/Noc režim", "Průměrná teplota")

## Pokud "Den/Noc režim":
- Denní teplota [°C]: slider(18-24)
- Noční teplota [°C]: slider(16-24)
- Den začíná [h]: number_input(0-23)
- Den končí [h]: number_input(0-23)
- Info: Vypočítaná průměrná teplota

## Pokud "Průměrná teplota":
- Průměrná vnitřní teplota [°C]: slider(16-26)
- Info: Použije se konstantní profil

# Systém vytápění
- Typ: selectbox(CONDENSING_BOILER, HEAT_PUMP_AIR, ...)
- Účinnost/COP: number_input (volitelné)
```

#### TAB 3: Data 📊
```python
# Denní spotřeby
- Nahrát CSV: file_uploader
- nebo Zadat ručně: data_editor

# Měsíce bez topení (NOVÉ v 1.1.0)
- Multiselect: [Leden, Únor, ..., Prosinec]
- Default: [Květen, Červen, Červenec, Srpen, Září]

# TUV aproximace
- Použít model: checkbox(True)
- nebo Manuální podíl [%]: slider(0-100)
```

**Poznámka:** Průměrná vnitřní teplota byla přesunuta do TAB 2 (verze 1.1.0).

#### TAB 4: Výpočet ⚙️
```python
# Kontrola před výpočtem
- API klíč OK?
- Lokalita zadána?
- Dostatek dat?

# Spuštění
- Button "SPUSTIT VÝPOČET"
- Progress bar (0-100%)
- Status text (každá fáze)
```

#### TAB 5: Výsledky 🎉
```python
# Energetická třída
- Velký barevný banner (třída A-G)
- Popis třídy

# Metriky (4 sloupce)
- Měrná potřeba tepla
- Primární energie
- Spolehlivost (badge)
- MAPE kalibrace

# Grafy (TODO)

# Upozornění a doporučení
- Disclaimery (warning boxes)
- Suggestions (info boxes)

# Export
- Generovat HTML report
- Download button
```

### 12.2 Sidebar nastavení

```python
# API klíč
- text_input(type="password")
- Auto-uložení

# Režim výpočtu
- selectbox: BASIC / STANDARD / ADVANCED
- Info o režimu
```

### 12.3 Session state

```python
st.session_state['location']            # str
st.session_state['daily_energy_data']   # List[DailyEnergyData]

# Teplotní režim (NOVÉ v 1.1.0)
st.session_state['temp_mode']           # 'day_night' | 'average'
# Pokud 'day_night':
st.session_state['temp_day']            # float
st.session_state['temp_night']          # float
st.session_state['day_start_hour']      # int
st.session_state['day_end_hour']        # int
# Pokud 'average':
st.session_state['temp_avg']            # float

st.session_state['non_heating_months']  # List[int]
st.session_state['tuv_percentage']      # Optional[int]
st.session_state['use_tuv_model']       # bool
st.session_state['results']             # dict
```

---

## 13. API REFERENCE

### 13.1 Core moduly

#### `rc_model.py`

**class RC1Model:**
```python
def __init__(
    H_env_W_per_K: float,
    infiltration_rate_per_h: float,
    volume_m3: float,
    C_th_J_per_K: float,
    area_m2: float,
    internal_gains_W_per_m2: float = 3.0,
    solar_aperture: float = 0.02
)

def simulate_step(
    T_in_prev: float,
    T_out: float,
    Q_heat_W: float,
    GHI_W_per_m2: float,
    dt_seconds: float = 3600
) -> float

def simulate_hourly(
    T_in_initial: float,
    hourly_df: pd.DataFrame,
    Q_heat_column: str = 'heating_power_W'
) -> pd.DataFrame

def estimate_heating_demand(
    T_in_setpoint: float,
    T_out: float,
    GHI_W_per_m2: float = 0
) -> float
```

**Funkce:**
```python
def estimate_initial_parameters(
    daily_energy_df: pd.DataFrame,
    hourly_weather_df: pd.DataFrame,
    volume_m3: float,
    avg_indoor_temp: float
) -> Tuple[float, float, float]
```

#### `calibrator.py`

```python
def calibrate_model_simple(
    daily_energy_df: pd.DataFrame,
    hourly_weather_df: pd.DataFrame,
    geometry_volume_m3: float,
    geometry_area_m2: float,
    avg_indoor_temp: float,
    baseline_tuv_kwh: float,
    mode: str = "standard"  # "basic" | "standard" | "advanced"
) -> CalibratedParameters
```

#### `preprocess.py`

```python
def clean_weather_data(
    df: pd.DataFrame
) -> pd.DataFrame

def align_daily_energy_to_hourly(
    daily_energy_df: pd.DataFrame,
    hourly_weather_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]

def create_hourly_indoor_temp(
    daily_avg_temp: float,
    hourly_weather_df: pd.DataFrame,
    day_temp: Optional[float] = None,
    night_temp: Optional[float] = None,
    day_start_hour: int = 6,
    day_end_hour: int = 22,
    day_night_delta: float = 0.5
) -> pd.DataFrame

def validate_data_quality(
    daily_energy_df: pd.DataFrame,
    hourly_df: pd.DataFrame
) -> List[str]
```

#### `baseline_split.py`

```python
def estimate_baseline_tuv(
    daily_energy_df: pd.DataFrame,
    percentile: float = 10.0
) -> float

def split_heating_and_tuv(
    daily_energy_df: pd.DataFrame,
    baseline_tuv_kwh: Optional[float] = None
) -> pd.DataFrame

def distribute_daily_heating_to_hours(
    daily_heating_df: pd.DataFrame,
    hourly_weather_df: pd.DataFrame,
    indoor_temp_c: float = 21.0
) -> pd.DataFrame
```

#### `weather_api.py`

```python
def detect_location() -> Tuple[str, float, float]

def fetch_hourly_weather(
    location: str,
    start_date: date,
    end_date: date,
    api_key: str
) -> pd.DataFrame

def create_typical_year_weather(
    location: str,
    api_key: str
) -> pd.DataFrame
```

#### `simulate_year.py`

```python
def simulate_annual_heating_demand(
    calibrated_params: CalibratedParameters,
    typical_year_weather: pd.DataFrame,
    geometry_volume_m3: float,
    geometry_area_m2: float,
    comfort_profile: TemperatureProfile
) -> pd.DataFrame

def calculate_primary_energy(
    heating_demand_kwh_per_year: float,
    system_type: str,
    efficiency_or_cop: float,
    primary_energy_factors: dict = None
) -> float

def estimate_uncertainty_bounds(
    calibrated_params: CalibratedParameters,
    heating_demand_kwh_per_m2: float,
    data_quality_warnings: list
) -> tuple[float, float]
```

#### `metrics.py`

```python
def classify_energy_label(
    heating_demand_kwh_per_m2_year: float,
    primary_energy_kwh_per_m2_year: float,
    use_primary: bool = True
) -> EnergyClass

def get_class_description(energy_class: EnergyClass) -> str
def get_class_color(energy_class: EnergyClass) -> str
```

#### `quality_flags.py`

```python
def assess_quality_level(
    computation_mode: ComputationMode,
    n_days_data: int,
    calibrated_params: CalibratedParameters,
    data_warnings: list
) -> QualityLevel

def generate_disclaimers(
    quality_level: QualityLevel,
    computation_mode: ComputationMode,
    n_days_data: int,
    data_warnings: list
) -> list[str]

def suggest_improvements(
    quality_level: QualityLevel,
    computation_mode: ComputationMode,
    n_days_data: int,
    calibrated_params: CalibratedParameters
) -> list[str]
```

#### `report_builder.py`

```python
def generate_html_report(
    annual_results: AnnualResults,
    calibrated_params: CalibratedParameters,
    user_inputs: UserInputs,
    suggestions: list[str]
) -> str

def save_html_report(html: str, filepath: str)
```

### 13.2 Konfigurace

#### `config.py`

```python
def get_api_key() -> Optional[str]
def set_api_key(api_key: str)

def get_last_location() -> Optional[str]
def set_last_location(location: str)

def save_user_inputs(inputs_dict: dict)
def load_user_inputs() -> Optional[dict]
```

---

## 14. KONFIGURACE

### 14.1 Úložiště

**Adresář:** `storage/`

**Soubory:**
- `token_store.json` - API klíče a konfigurace
- `user_inputs.json` - Poslední uživatelské vstupy

**Formát token_store.json:**
```json
{
  "weather_api_key": "YOUR_API_KEY",
  "last_location": "Praha"
}
```

### 14.2 Environment proměnné

```bash
# Pro ADVANCED režim - počet vláken
PENB_ADVANCED_THREADS=4  # Default: cpu_count - 1
```

### 14.3 Fyzikální konstanty

```python
# rc_model.py
RHO_AIR = 1.2        # kg/m³
CP_AIR = 1005        # J/(kg·K)

# Výchozí parametry
internal_gains = 3.0  # W/m²
solar_aperture = 0.02 # pro byty
```

### 14.4 API limity

**WeatherAPI.com free tier:**
- Historie: 7 dní zpětně
- Předpověď: 3 dny dopředu
- 1 000 000 volání/měsíc

**Placený tarif:**
- Historie: neomezená
- Předpověď: 14 dní

---

## 15. LIMITACE A OMEZENÍ

### 15.1 Metodologická omezení

❌ **NENÍ oficiální PENB:**
- Chybí detailní geometrie (okna, orientace)
- Zjednodušený model (1R1C místo multi-zone)
- Nepočítá všechny komponenty (větrání, chlazení)

❌ **Aproximace:**
- Typický rok = sinusoida (ne skutečný TMY)
- Hranice tříd zjednodušené
- Primární energie orientační

❌ **Závislost na kvalitě dat:**
- Provozní data mohou být neúplná
- Uživatelské chování variabilní
- Průměrné teploty odhad

### 15.2 Technická omezení

⚠️ **WeatherAPI:**
- Free tier: max 7 dní zpětně
- Syntetická data pro starší období

⚠️ **Výpočetní výkon:**
- ADVANCED režim pomalý (minutes)
- Paralelizace pomáhá

⚠️ **Přesnost:**
- RMSE typicky 0.5-2°C
- MAPE typicky 5-20%

### 15.3 Doporučení pro použití

✅ **Vhodné pro:**
- Orientační odhad před zateplením
- Porovnání variant vytápění
- Identifikace problémů (velké ztráty)
- Výukové účely

❌ **Nevhodné pro:**
- Úřední doklady
- Dotační řízení
- Právně závazné dokumenty
- Certifikace budov

### 15.4 Cesty k zlepšení

**Vyšší priorita:**
1. Skutečná TMY data (PVGIS, Meteonorm)
2. Multi-zone model (více místností)
3. Detailní geometrie vstup
4. Validace na reálných PENB datech

**Nižší priorita:**
5. Víkendový režim (jiné teploty)
6. Sezónní adaptace
7. Machine learning kalibrace
8. Offline režim (cached weather)

---

## 📌 ZÁVĚR

Tato aplikace poskytuje **rychlý a přístupný způsob** orientačního odhadu energetické náročnosti bytu z provozních dat. Používá fyzikálně založený přístup (RC model) s automatickou kalibrací, což zajišťuje lepší přesnost než jednoduché lineární regrese.

**Klíčové výhody:**
- ✅ Nevyžaduje detailní znalost konstrukcí
- ✅ Funguje s běžně dostupnými daty
- ✅ Poskytuje srozumitelné výsledky
- ✅ Hodnotí spolehlivost výsledků
- ✅ Flexibilní nastavení (verze 1.1.0)

**Pro oficiální PENB kontaktujte oprávněnou osobu!**

---

**Datum vytvoření dokumentace:** 28. října 2025  
**Verze aplikace:** 1.1.0  
**Status:** ✅ Produkční

---

