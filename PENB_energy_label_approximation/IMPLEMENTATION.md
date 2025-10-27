# 📋 Implementační Dokumentace

## Přehled implementace

Kompletní aplikace pro výpočet orientačního energetického štítku bytu byla úspěšně implementována podle specifikace.

---

## ✅ Implementované komponenty

### 1. Struktura projektu ✓

```
PENB_energy_label_approximation/
├── core/                       # Jádro - fyzika a výpočty
│   ├── __init__.py
│   ├── config.py              # Správa API tokenu
│   ├── data_models.py         # Pydantic modely
│   ├── weather_api.py         # WeatherAPI + auto-detekce
│   ├── preprocess.py          # Čištění dat
│   ├── baseline_split.py      # TUV vs vytápění
│   ├── rc_model.py            # 1R1C fyzikální model
│   ├── calibrator.py          # Kalibrace parametrů
│   ├── simulate_year.py       # Roční simulace
│   ├── metrics.py             # Klasifikace A-G
│   └── quality_flags.py       # Hodnocení spolehlivosti
│
├── app_gui/                    # GUI vrstva
│   ├── __init__.py
│   └── gui_main.py            # Streamlit aplikace (5 záložek)
│
├── reports/                    # Reporty
│   ├── __init__.py
│   └── report_builder.py     # HTML generátor
│
├── storage/                    # Perzistence (auto-vytvoří se)
│
├── main.py                     # Launcher
├── run.bat                     # Windows spouštěč
├── requirements.txt            # Závislosti
├── example_data.csv           # Ukázková data
├── .gitignore                 # Git ignore
├── README.md                   # Hlavní dokumentace
└── QUICKSTART.md              # Rychlý start
```

---

## 🎯 Implementované funkce

### ✅ Core moduly

#### 1. **data_models.py** - Datové struktury
- `HeatingSystemType` enum (kotel, TČ, elektro, ...)
- `ComputationMode` enum (BASIC, STANDARD, ADVANCED)
- `QualityLevel` enum (LOW, MEDIUM, HIGH)
- `EnergyClass` enum (A-G)
- `ApartmentGeometry` - geometrie bytu
- `HeatingSystemInfo` - info o systému
- `UserInputs` - kompletní validované vstupy
- `CalibratedParameters` - výsledky kalibrace
- `AnnualResults` - roční výsledky

#### 2. **config.py** - Správa konfigurace
- `load_api_config()` - načte token
- `save_api_config()` - uloží token
- `get_api_key()` / `set_api_key()` - práce s API klíčem
- `save_user_inputs()` / `load_user_inputs()` - perzistence

#### 3. **weather_api.py** - Počasí
- `detect_location()` - **automatická detekce lokace podle IP** ✓
- `fetch_hourly_weather()` - stažení hodinových dat
- `fetch_forecast_weather()` - předpověď
- `create_typical_year_weather()` - TMY (MVP: sinusoida)

#### 4. **preprocess.py** - Preprocessing
- `clean_weather_data()` - čištění a interpolace
- `align_daily_energy_to_hourly()` - zarovnání časových řad
- `create_hourly_indoor_temp()` - pseudo-hodinová T_in
- `validate_data_quality()` - kontrola kvality dat

#### 5. **baseline_split.py** - Rozdělení TUV
- `estimate_baseline_tuv()` - 10. percentil
- `split_heating_and_tuv()` - separace vytápění
- `distribute_daily_heating_to_hours()` - rozklad do hodin

#### 6. **rc_model.py** - Fyzikální model
- `RC1Model` třída - 1R1C model budovy
  - `simulate_step()` - Eulerova metoda
  - `simulate_hourly()` - hodinová simulace
  - `estimate_heating_demand()` - ustálený stav
- `estimate_initial_parameters()` - počáteční odhad

#### 7. **calibrator.py** - Kalibrace
- `calibrate_model_simple()` - hlavní funkce
  - BASIC: lineární regrese
  - STANDARD: L-BFGS-B optimalizace
  - ADVANCED: differential evolution
- Kombinovaná cost funkce (RMSE T_in + MAPE energie)

#### 8. **simulate_year.py** - Roční simulace
- `simulate_annual_heating_demand()` - 8760 hodin
- `calculate_primary_energy()` - faktory PEF
- `estimate_uncertainty_bounds()` - interval spolehlivosti

#### 9. **metrics.py** - Klasifikace
- `classify_energy_label()` - třídy A-G
- `get_class_description()` - popisky
- `get_class_color()` - barvy pro vizualizaci

#### 10. **quality_flags.py** - Kvalita
- `assess_quality_level()` - skórovací systém
- `generate_disclaimers()` - upozornění
- `suggest_improvements()` - doporučení

---

### ✅ GUI (Streamlit)

#### **gui_main.py** - 5 záložek:

1. **Lokalita**
   - Tlačítko "Automaticky detekovat" ✓
   - Ruční zadání města/souřadnic
   - Uložení poslední lokality

2. **Byt & Systém**
   - Plocha (m²)
   - Výška stropu (m)
   - Komfortní teploty (den/noc)
   - Typ vytápění (dropdown)
   - Účinnost/COP (volitelné)

3. **Data**
   - Upload CSV
   - Generátor ukázkových dat
   - Editovatelná tabulka
   - Průměrná T_in

4. **Výpočet**
   - Kontrola prerekvizit
   - Tlačítko "SPUSTIT VÝPOČET"
   - Progress spinner
   - Volání `run_computation()`

5. **Výsledky**
   - Velké zobrazení třídy (barevné)
   - 4 metriky (cards)
   - Disclaimery
   - Doporučení
   - Export HTML

#### Režimy výpočtu v sidebaru:
- 🔸 BASIC
- 🔹 STANDARD (default)
- 🔺 ADVANCED

---

### ✅ Reporty

#### **report_builder.py**
- `generate_html_report()` - Jinja2 šablona
- `save_html_report()` - uložení
- Barevný HTML s:
  - Hlavička s třídou
  - Tabulky parametrů
  - Kalibrované hodnoty
  - Disclaimery
  - Doporučení

---

## 🔬 Fyzikální model

### 1R1C Model

**Diferenciální rovnice:**
```
C_th · dT_in/dt = Q_heat + Q_solar + Q_internal - H_total · (T_in - T_out)
```

**Parametry:**
- `H_env` [W/K] - ztráty obálkou
- `n` [1/h] - infiltrace
- `C_th` [J/K] - tepelná kapacita
- `q_int` [W/m²] - interní zisky

**Celkové ztráty:**
```
H_total = H_env + H_vent
H_vent = ρ_air · c_p · n · V / 3600
```

### Kalibrace

**Cost funkce:**
```
cost = α · RMSE(T_in_sim, T_in_obs) + β · MAPE(E_sim, E_obs)
```

**Metody:**
- BASIC: žádná optimalizace
- STANDARD: `scipy.optimize.minimize` (L-BFGS-B)
- ADVANCED: `scipy.optimize.differential_evolution`

---

## 📊 Workflow výpočtu

1. **Input validation** (pydantic)
2. **Stažení počasí** (WeatherAPI)
3. **Preprocessing** (čištění, interpolace)
4. **Baseline TUV** (10. percentil)
5. **Rozklad energie** do hodin (proporcionálně ΔT)
6. **Kalibrace** (optimalizace H_env, n, C_th)
7. **TMY generování** (sinusoida v MVP)
8. **Roční simulace** (8760 hodin)
9. **Primární energie** (PEF faktory)
10. **Klasifikace** (A-G)
11. **Quality assessment** (LOW/MED/HIGH)
12. **Report generování** (HTML)

---

## 🎨 GUI Flow

```
START
  │
  ├─→ Sidebar: API klíč + režim
  │
  ├─→ Tab 1: Lokalita
  │     └─→ Auto-detect ✓
  │
  ├─→ Tab 2: Parametry
  │     ├─→ Geometrie
  │     └─→ Systém
  │
  ├─→ Tab 3: Data
  │     ├─→ CSV upload
  │     └─→ Demo generator
  │
  ├─→ Tab 4: Výpočet
  │     └─→ run_computation()
  │          ├─→ Fetch weather
  │          ├─→ Preprocess
  │          ├─→ Calibrate
  │          ├─→ Simulate
  │          └─→ Results
  │
  └─→ Tab 5: Výsledky
        ├─→ Třída (velké)
        ├─→ Metriky
        ├─→ Warnings
        └─→ Export HTML
```

---

## 🚀 Spuštění

### Windows (nejjednodušší):
```batch
run.bat
```

### Cross-platform:
```bash
streamlit run app_gui/gui_main.py
```

### Python launcher:
```bash
python main.py
```

---

## 📦 Závislosti (requirements.txt)

```
pandas>=2.0.0          # Data manipulation
numpy>=1.24.0          # Numerical computing
scipy>=1.10.0          # Optimization
pydantic>=2.0.0        # Data validation
requests>=2.31.0       # HTTP
python-dateutil>=2.8.0 # Date handling
pytz>=2023.3           # Timezones
streamlit>=1.28.0      # GUI framework
plotly>=5.17.0         # Interactive plots
matplotlib>=3.7.0      # Plotting
scikit-learn>=1.3.0    # ML utilities
jinja2>=3.1.2          # HTML templating
geocoder>=1.38.1       # Auto-location ✓
```

---

## ✨ Klíčové features

### ✅ Implementováno v MVP:

1. **Automatická detekce lokace** podle IP ✓
2. **Tři režimy kvality** (BASIC/STANDARD/ADVANCED) ✓
3. **1R1C fyzikální model** ✓
4. **Kalibrace** s optimalizací ✓
5. **Baseline TUV** separace ✓
6. **Roční simulace** ✓
7. **Klasifikace A-G** ✓
8. **Quality assessment** ✓
9. **HTML reporty** ✓
10. **Streamlit GUI** s 5 záložkami ✓
11. **Demo data generátor** ✓
12. **CSV import/export** ✓

### ⚠️ MVP limitace:

- TMY je sinusoida (ne skutečný dataset)
- Hodinová T_in zatím jen průměr
- Grafy jsou placeholdery
- Free API má limity na historii

### 🔮 Plánováno (V2):

- Skutečný TMY (EPW soubory)
- 2R2C model
- Interaktivní Plotly grafy
- PDF export
- Multi-zone support

---

## 📝 Testování

### Doporučený test flow:

1. Spustit `run.bat`
2. Zadat dummy API klíč nebo získat skutečný
3. Kliknout "Auto-detect lokace"
4. Zadat parametry: 70 m², 2.7 m, kotel, 0.9
5. Generovat demo data (14 dní)
6. Standard režim
7. Spustit výpočet
8. Zkontrolovat výsledky
9. Exportovat HTML

---

## 🎓 Použité algoritmy

1. **Lineární regrese** (BASIC) - `scipy.stats.linregress`
2. **L-BFGS-B** (STANDARD) - `scipy.optimize.minimize`
3. **Differential Evolution** (ADVANCED) - `scipy.optimize.differential_evolution`
4. **Euler forward** - numerická integrace ODE
5. **Percentilový baseline** - robustní odhad TUV
6. **Cost fusion** - multi-objective optimization

---

## 🏆 Dosažené cíle

✅ Modulární architektura  
✅ Validace vstupů (pydantic)  
✅ Auto-detekce lokace  
✅ 3 režimy kvality  
✅ Fyzikální model  
✅ Optimalizační kalibrace  
✅ Roční simulace  
✅ Quality scoring  
✅ HTML reporty  
✅ User-friendly GUI  
✅ Dokumentace  
✅ Ukázková data  
✅ Cross-platform  

---

## 🎉 Závěr

Aplikace je **plně funkční MVP** připravené k použití!

**Next steps:**
1. Nainstalovat závislosti: `pip install -r requirements.txt`
2. Získat API klíč: https://www.weatherapi.com/
3. Spustit: `run.bat` nebo `streamlit run app_gui/gui_main.py`
4. Postupovat podle QUICKSTART.md

---

**Implementace dokončena! 🚀**
