# Orientační Energetický Štítek

🏠 **Aplikace pro odhad energetické náročnosti bytu z provozních dat**

---

## 📋 Popis

Tato aplikace umožňuje vypočítat **orientační energetický štítek** vašeho bytu na základě skutečných provozních dat - denních odečtů spotřeby energie a venkovního počasí.

**⚠️ DŮLEŽITÉ UPOZORNĚNÍ:**
- Toto **NENÍ** oficiální Průkaz energetické náročnosti budovy (PENB)
- Výsledky jsou pouze orientační odhad
- Pro oficiální PENB kontaktujte oprávněnou osobu

---

## 🎯 Vlastnosti

### Tři režimy výpočtu:
- **BASIC** - Rychlý hrubý odhad (min. 1 den dat)
- **STANDARD** - Doporučený režim s 1R1C modelem (min. 7 dní dat)
- **ADVANCED** - Pokročilá kalibrace s globální optimalizací (min. 28 dní dat)

### Funkce:
✅ Automatická detekce lokace podle IP  
✅ Stahování historického počasí z WeatherAPI.com  
✅ Fyzikální 1R1C tepelný model budovy  
✅ Kalibrace na skutečná provozní data  
✅ Rozdělení spotřeby na vytápění vs. TUV  
✅ Simulace typického meteorologického roku  
✅ Klasifikace do energetických tříd A-G  
✅ Hodnocení spolehlivosti výsledků  
✅ Export HTML reportů  
✅ Doporučení pro zlepšení  

---

## 🚀 Instalace

### 1. Požadavky
- Python 3.9 nebo novější
- pip (správce balíčků)

### 2. Instalace závislostí

```powershell
# Přejděte do složky projektu
cd PENB_energy_label_approximation

# Instalujte závislosti
pip install -r requirements.txt
```

### 3. API klíč pro počasí

1. Zaregistrujte se na [WeatherAPI.com](https://www.weatherapi.com/) (zdarma)
2. Získejte API klíč z vašeho účtu
3. Při prvním spuštění aplikace jej zadejte do bočního panelu

---

## 💻 Spuštění

### Spuštění GUI (doporučeno)

```powershell
# Jednoduchý způsob
python main.py

# Nebo přímo Streamlit
streamlit run app_gui/gui_main.py
```

Aplikace se otevře v prohlížeči na adrese: `http://localhost:8501`

---

## 📖 Jak používat

### Krok 1: Nastavení
1. V bočním panelu zadejte **API klíč** pro WeatherAPI.com
2. Zvolte **režim výpočtu** (BASIC / STANDARD / ADVANCED)

### Krok 2: Lokalita
1. Klikněte na "Automaticky detekovat lokaci" nebo
2. Zadejte město (např. "Praha") nebo souřadnice (např. "50.0755,14.4378")

### Krok 3: Parametry bytu
1. Zadejte **plochu bytu** (m²)
2. Zadejte **výšku stropu** (m)
3. Nastavte **komfortní teploty** (den/noc)
4. Vyberte **typ vytápěcího systému**
5. Volitelně zadejte známou **účinnost** nebo **COP**

### Krok 4: Data o spotřebě
1. Nahrajte CSV soubor s denními spotřebami NEBO
2. Použijte tlačítko "Generovat ukázková data" pro demo
3. CSV formát: `date,energy_total_kwh`
   ```
   2025-01-01,12.5
   2025-01-02,14.2
   ...
   ```
4. Zadejte **průměrnou vnitřní teplotu** během sledovaného období

### Krok 5: Výpočet
1. Zkontrolujte, že jsou všechny údaje správně
2. Klikněte na **"SPUSTIT VÝPOČET"**
3. Počkejte na dokončení (10-30 sekund)

### Krok 6: Výsledky
1. Prohlédněte si **energetickou třídu**
2. Zkontrolujte **metriky** (měrná potřeba tepla, primární energie)
3. Přečtěte si **upozornění** a **doporučení**
4. Exportujte **HTML report**

---

## 📂 Struktura projektu

```
PENB_energy_label_approximation/
├── core/                       # Jádro aplikace
│   ├── config.py              # Správa konfigurace a tokenu
│   ├── data_models.py         # Datové modely (pydantic)
│   ├── weather_api.py         # API pro počasí
│   ├── preprocess.py          # Preprocessing dat
│   ├── baseline_split.py      # Rozdělení TUV/vytápění
│   ├── rc_model.py            # 1R1C tepelný model
│   ├── calibrator.py          # Kalibrace parametrů
│   ├── simulate_year.py       # Roční simulace
│   ├── metrics.py             # Klasifikace do tříd
│   └── quality_flags.py       # Hodnocení kvality
│
├── app_gui/                    # GUI vrstva
│   └── gui_main.py            # Streamlit aplikace
│
├── reports/                    # Generování reportů
│   └── report_builder.py     # HTML reporty
│
├── storage/                    # Lokální úložiště
│   ├── token_store.json       # API token (auto-vytvoří se)
│   └── user_inputs.json       # Poslední vstupy (auto)
│
├── main.py                     # Hlavní launcher
├── requirements.txt            # Závislosti
└── README.md                   # Tento soubor
```

---

## 🔬 Jak to funguje

### Fyzikální model

Aplikace používá **1R1C tepelný model**:
- **1R** (odpor) = tepelné ztráty obálkou + větráním
- **1C** (kapacita) = tepelná setrvačnost budovy

Diferenciální rovnice:
```
C_th · dT_in/dt = Q_heat + Q_solar + Q_internal - H_total · (T_in - T_out)
```

### Kalibrace

1. **Baseline TUV**: Odhadne se jako 10. percentil nejnižších denních spotřeb
2. **Rozdělení energie**: Denní spotřeba se rozloží do hodin podle ΔT
3. **Optimalizace**: Hledají se parametry H_env, n, C_th minimalizující chybu mezi:
   - Simulovanou a pozorovanou vnitřní teplotou
   - Predikovanou a skutečnou denní spotřebou

### Roční přepočet

1. Vytvoří se **typický meteorologický rok** (TMY) pro lokalitu
2. S kalibrovaným modelem se simuluje celý rok
3. Spočítá se **roční potřeba tepla** [kWh/m²·rok]
4. Přepočítá se na **primární energii** podle typu zdroje
5. Přiřadí se **energetická třída** A-G

---

## 📊 Režimy výpočtu

| Režim | Min. data | Metoda | Spolehlivost |
|-------|-----------|--------|--------------|
| **BASIC** | 1 den | Lineární regrese | NÍZKÁ |
| **STANDARD** | 7 dní | 1R1C + lokální optimalizace | STŘEDNÍ |
| **ADVANCED** | 28 dní | 1R1C + globální optimalizace | VYSOKÁ |

---

## ⚙️ Technické detaily

### Závislosti
- `pandas` - Práce s daty
- `numpy` - Numerické výpočty
- `scipy` - Optimalizace
- `pydantic` - Validace dat
- `streamlit` - GUI
- `plotly` - Grafy
- `requests` - HTTP requesty
- `geocoder` - Detekce lokace
- `jinja2` - HTML šablony

### Fyzikální konstanty
- Hustota vzduchu: 1.2 kg/m³
- Měrné teplo vzduchu: 1005 J/(kg·K)
- Faktory primární energie:
  - Elektřina: 3.0
  - Zemní plyn: 1.1

---

## ❓ FAQ

**Q: Je to oficiální PENB?**  
A: Ne, toto je pouze orientační odhad. Oficiální PENB musí vyhotovit oprávněná osoba.

**Q: Jak přesné jsou výsledky?**  
A: Závisí na:
- Množství a kvalitě dat (doporučeno 28+ dní)
- Přesnosti zadaných parametrů
- Režimu výpočtu (ADVANCED je nejpřesnější)

**Q: Potřebuji hodinová data?**  
A: Ne, stačí denní odečty z měřidla. Hodinové počasí se stáhne automaticky.

**Q: Kolik stojí WeatherAPI?**  
A: Free tier umožňuje 1M requestů/měsíc, což bohatě stačí. Historická data mohou vyžadovat placený tarif.

**Q: Funguje to i pro rodinné domy?**  
A: Základní logika ano, ale aplikace je optimalizována pro byty. Pro domy doporučujeme úpravu parametrů.

**Q: Můžu to použít komerčně?**  
A: Aplikace je pro osobní/vzdělávací účely. Pro komerční využití konzultujte licenci.

---

## 🐛 Známé limitace (MVP)

- ⚠️ Typický rok je zatím sinusoidní aproximace (ne skutečný TMY dataset)
- ⚠️ Hodinová vnitřní teplota zatím není plně podporována
- ⚠️ Grafy v GUI jsou zatím placeholdery
- ⚠️ Pouze 1R1C model (2R2C plánováno)
- ⚠️ Nepodporuje chlazení
- ⚠️ Zjednodušené hranice energetických tříd

---

## 🚧 Plánované vylepšení

### V2.0:
- [ ] Skutečný TMY dataset (EnergyPlus EPW soubory)
- [ ] Support pro hodinovou vnitřní teplotu
- [ ] Interaktivní grafy (Plotly)
- [ ] 2R2C model (pokročilý)
- [ ] Export do PDF
- [ ] Porovnání "před/po" zateplení
- [ ] Multi-zone model

### V3.0:
- [ ] Podpora chlazení
- [ ] Machine learning kalibrace
- [ ] Databáze typických parametrů budov
- [ ] API pro integraci
- [ ] Mobilní aplikace

---

## 📝 Licence

Tento projekt je poskytován "jak je" pro vzdělávací a výzkumné účely.

---

## 👨‍💻 Autor & Kontakt

Vytvořeno podle implementačního plánu pro výpočet orientačního energetického štítku.

Pro dotazy a návrhy otevřete issue nebo kontaktujte autora.

---

## 🙏 Poděkování

- [WeatherAPI.com](https://www.weatherapi.com/) - Meteorologická data
- [Streamlit](https://streamlit.io/) - Skvělý framework pro GUI
- Komunita open-source za vynikající knihovny

---

**Užijte si aplikaci a šetřete energii! 🌱**
