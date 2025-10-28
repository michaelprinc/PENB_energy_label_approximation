# UŽIVATELSKÁ PŘÍRUČKA
## Aplikace pro Orientační Energetický Štítek

**Verze:** 1.1.0  
**Pro:** Majitelé bytů a bytových jednotek  
**Účel:** Rychlý odhad energetické náročnosti z provozních dat

---

## 🚀 RYCHLÝ START

### 1. Instalace

```bash
# Naklonujte repozitář nebo stáhněte ZIP
git clone https://github.com/michaelprinc/PENB_energy_label_approximation

# Nainstalujte závislosti
cd PENB_energy_label_approximation
pip install -r requirements.txt
```

### 2. Získání API klíče

1. Navštivte: https://www.weatherapi.com/
2. Zaregistrujte se (zdarma)
3. Zkopírujte API klíč z dashboardu

### 3. Spuštění aplikace

```bash
# Jednoduchý způsob
python main.py

# Nebo přímo Streamlit
streamlit run app_gui/gui_main.py
```

Otevře se webový prohlížeč s aplikací na `http://localhost:8501`

---

## 📋 KROK ZA KROKEM

### Krok 1️⃣: Zadejte lokalitu

**V záložce "1️⃣ Lokalita":**

1. Klikněte na **"🌍 Automaticky detekovat lokaci"**
   - Nebo zadejte ručně město: `Praha`
   - Nebo souřadnice: `50.0755,14.4378`

2. Lokalita se automaticky uloží pro příště

---

### Krok 2️⃣: Zadejte parametry bytu

**V záložce "2️⃣ Byt & Systém":**

#### A) Geometrie
- **Plocha bytu:** např. `70` m²
- **Výška stropu:** např. `2.7` m
- → Objem se vypočítá automaticky

#### B) Komfortní teploty
- **Denní teplota:** např. `21°C` (když jste doma)
- **Noční teplota:** např. `19°C` (v noci)

#### C) Časové rozsahy (NOVÉ! ⭐)
- **Den začíná:** např. `6` = 6:00 ráno
- **Den končí:** např. `22` = 22:00 večer

💡 **Tip:** Nastavte časy podle svého režimu:
- Pracující doma: `8:00 - 20:00`
- Normální režim: `6:00 - 22:00`
- Důchodci: `7:00 - 21:00`

#### D) Systém vytápění
- **Typ zdroje:** vyberte z nabídky
  - Kondenzační plynový kotel
  - Přímotopné elektrické
  - Tepelné čerpadlo vzduch/voda
  - Tepelné čerpadlo voda/voda

- **Znám účinnost/COP:** zaškrtněte, pokud znáte
  - Pro kotel: např. `0.92` (92%)
  - Pro TČ: např. `3.2` (COP)

---

### Krok 3️⃣: Nahrajte data o spotřebě

**V záložce "3️⃣ Data":**

#### A) Denní spotřeby energie

**Varianta 1 - Nahrát CSV soubor:**

Připravte CSV soubor s tímto formátem:
```csv
date,energy_total_kwh
2025-01-01,12.5
2025-01-02,11.8
2025-01-03,13.2
...
```

**Varianta 2 - Zadat ručně:**
1. Klikněte "Generovat ukázková data"
2. Upravte hodnoty v tabulce
3. Můžete přidávat/mazat řádky

📊 **Kolik dat potřebuji?**
- **Minimum:** 1 den (BASIC režim)
- **Doporučeno:** 7-14 dní (STANDARD režim)
- **Ideální:** 28+ dní (ADVANCED režim)

#### B) Vnitřní teplota

**Průměrná vnitřní teplota:**
- Odhadněte průměr: typicky `20-22°C`
- Měřeno např. pokojovým teploměrem

#### C) Měsíce bez topení (NOVÉ! ⭐)

**Co to je?**  
Označte měsíce v roce 2025, kdy jste NEtopili (bylo teplo).

**Proč?**  
Aplikace použije spotřebu z těchto měsíců pro přesnější odhad spotřeby na ohřev vody.

**Jak nastavit:**
1. Vyberte měsíce: typicky **Květen, Červen, Červenec, Srpen, Září**
2. Pro jižní lokality možná přidejte Duben a Říjen

💡 **Tip:** Pokud máte data z celého roku, toto VÝRAZNĚ zlepší přesnost!

#### D) Ohřev vody (TUV)

**Použít modelovou aproximaci TUV:** ✅ (doporučeno)
- Automatický odhad

**Nebo:**  
Zaškrtněte "Znám podíl" a zadejte např. `20%`

---

### Krok 4️⃣: Spusťte výpočet

**V záložce "4️⃣ Výpočet":**

#### Nastavení v Sidebaru

**API klíč:**
- Zadejte API klíč z WeatherAPI.com
- Uloží se automaticky

**Režim výpočtu:**
- 🔸 **BASIC:** Rychlý odhad (1 sekunda)
  - Pro hrubý náhled
  
- 🔹 **STANDARD:** Doporučeno (10 sekund)
  - Dobrá rovnováha rychlost/přesnost
  
- 🔺 **ADVANCED:** Nejpřesnější (1-2 minuty)
  - Pro finální odhad

#### Spuštění

1. Zkontrolujte zelené zatržítko "✓ Vše připraveno"
2. Klikněte **"🚀 SPUSTIT VÝPOČET"**
3. Sledujte progress bar:
   - 📡 Stahování počasí...
   - 🔧 Zpracování dat...
   - 🎯 Kalibrace modelu...
   - 📅 Simulace roku...
   - ✅ Hotovo!

---

### Krok 5️⃣: Prohlédněte si výsledky

**V záložce "5️⃣ Výsledky":**

#### Energetická třída

```
╔═══════════════════╗
║                   ║
║     Třída B       ║
║                   ║
║  Velmi úsporná    ║
╚═══════════════════╝
```

**Třídy A-G:**
- **A:** Mimořádně úsporná (pasivní domy)
- **B:** Velmi úsporná ← Moderní byty
- **C:** Úsporná
- **D:** Méně úsporná ← Průměr ČR
- **E:** Nehospodárná
- **F:** Velmi nehospodárná
- **G:** Mimořádně nehospodárná (staré panelové domy)

#### Klíčové metriky

📊 **Měrná potřeba tepla:**  
`85.5 kWh/(m²·rok)`

⚡ **Primární energie:**  
`105.2 kWh/(m²·rok)`

🎯 **Spolehlivost:**  
`STŘEDNÍ` / `VYSOKÁ` / `NÍZKÁ`

📈 **MAPE kalibrace:**  
`8.3%` (čím nižší, tím lepší)

#### Upozornění

⚠️ **Vždy si přečtěte disclaimery!**

Např.:
- "Toto NENÍ oficiální PENB"
- "STŘEDNÍ spolehlivost výsledků"
- "Málo dat (12 dní). Doporučeno alespoň 14-28 dní"

#### Doporučení

💡 **Návrhy na zlepšení:**

Např.:
- "📅 Doplňte více dat"
- "🪟 Vysoká infiltrace - zvažte výměnu oken"
- "🏠 Vysoké ztráty - zvažte zateplení"

#### Export

**Vygenerovat HTML report:**
1. Klikněte "Vygenerovat HTML report"
2. Uloží se do `reports/energy_label_YYYYMMDD_HHMMSS.html`
3. Klikněte "📥 Stáhnout HTML"
4. Otevřete v prohlížeči nebo vytiskněte

---

## 🎓 PRAKTICKÉ TIPY

### Jak získat nejlepší výsledky?

#### ✅ DO:

1. **Sbírejte data alespoň 2 týdny**
   - Ideálně zahrnující chladné i teplejší dny

2. **Označte měsíce bez topení**
   - Pokud máte data z léta (květen-září)

3. **Nastavte správné časové rozsahy**
   - Podle svého skutečného režimu doma

4. **Ověřte odečty spotřeby**
   - Zkontrolujte, že jsou realistické
   - Typicky 5-15 kWh/den v zimě pro 70m² byt

5. **Použijte STANDARD nebo ADVANCED režim**
   - Pro přesnější výsledky

#### ❌ DON'T:

1. **Nepoužívejte data z období výpadku topení**
   - Vánoce u rodičů
   - Dovolená
   - Porucha kotle

2. **Nevynechávejte extrémní dny**
   - I mrazivé dny patří do dat

3. **Neměňte dramaticky režim během sběru**
   - Konstantní chování = lepší kalibrace

4. **Neočekávejte shodu s oficiálním PENB**
   - Toto je pouze orientační odhad!

---

## ❓ ČASTO KLADENÉ OTÁZKY

### Q: Je to oficiální PENB?

**A:** **NE!** Toto je pouze orientační odhad. Pro oficiální PENB kontaktujte oprávněnou osobu.

---

### Q: Proč mám NÍZKOU spolehlivost?

**A:** Nejčastější důvody:
1. Málo dat (< 7 dní)
2. Použit BASIC režim
3. Špatná kalibrace (vysoké RMSE/MAPE)
4. Problémy v datech (mezery, outliers)

**Řešení:**
- Sbírejte více dat
- Použijte STANDARD/ADVANCED režim
- Zkontrolujte správnost odečtů

---

### Q: Mám třidu horší než jsem čekal. Co s tím?

**A:** Podívejte se na **doporučení**:

- **Vysoká infiltrace (n > 0.8)?**
  → Výměna oken, těsnění

- **Vysoké ztráty obálkou (H_env > 200)?**
  → Zateplení stěn, střechy

- **Nízká účinnost kotle?**
  → Výměna za kondenzační nebo TČ

---

### Q: Mohu použít data z elektroměru?

**A:** **Ano**, pokud topíte elektřinou (přímotop, TČ).

**Ne**, pokud topíte plynem a elektřina je jen pro spotřebiče.

---

### Q: Kolik stojí WeatherAPI?

**A:** **Zdarma** až 1 000 000 volání/měsíc.

**Limit:** Historie jen 7 dní zpětně (free tier).  
Pro starší data aplikace generuje syntetická data s varováním.

---

### Q: Mám data jen z ledna. Funguje to?

**A:** **Částečně.**

- ✅ Kalibrace bude fungovat
- ⚠️ Odhad TUV nebude přesný (chybí léto)
- ⚠️ Nižší spolehlivost

**Doporučení:**  
Sbírejte data alespoň z jednoho chladného a jednoho teplého měsíce.

---

### Q: Jak interpretovat MAPE kalibrace?

**A:**
- **< 5%** → Výborná kalibrace ✅
- **5-10%** → Dobrá kalibrace ✅
- **10-20%** → Přijatelná kalibrace ⚠️
- **> 20%** → Špatná kalibrace ❌

Při MAPE > 20% zkontrolujte data a nastavení.

---

### Q: Můžu to použít pro celý dům?

**A:** Aplikace je navržena pro **byty**.

Pro **rodinné domy** může fungovat, ale:
- Větší plocha → vyšší variabilita
- Více oken → složitější zisky
- Může vyžadovat ADVANCED režim

---

### Q: Jak často mám aktualizovat výpočet?

**A:**
- Po **větších změnách:** zateplení, výměna oken, nový kotel
- Jednou **ročně** pro monitoring
- Před **investicí** do úsporných opatření

---

### Q: Výsledek se liší od PENB. Proč?

**A:** Několik důvodů:

1. **Jiná metodika**
   - PENB: normalizované podmínky
   - Tato app: skutečné provozní data

2. **Zjednodušený model**
   - PENB: detailní geometrie
   - Tato app: 1R1C model

3. **Aproximace**
   - Typický rok je sinusoida
   - Hranice tříd zjednodušené

**Je to normální!** Používejte pro orientaci, ne jako náhradu PENB.

---

## 🛠️ ŘEŠENÍ PROBLÉMŮ

### Chyba: "API klíč není nastaven"

**Řešení:**
1. Otevřete sidebar (←)
2. Zadejte API klíč do pole
3. Klíč se automaticky uloží

---

### Chyba: "Nelze detekovat lokaci"

**Řešení:**
1. Zadejte lokalitu ručně: `Praha` nebo `50.0755,14.4378`
2. Zkontrolujte připojení k internetu

---

### Chyba: "Nepodařilo se získat počasí"

**Možné příčiny:**
1. Neplatný API klíč → Zkontrolujte
2. Překročen limit → Free tier: 1M volání/měsíc
3. Špatná lokalita → Zkuste souřadnice

---

### Chyba: "Málo dat"

**Řešení:**
- BASIC: min. 1 den ✅
- STANDARD: min. 7 dní
- ADVANCED: min. 28 dní

Snižte režim nebo sbírejte více dat.

---

### Výpočet trvá věčně

**Řešení:**
1. **ADVANCED režim je pomalý** (1-2 min) → normální
2. Pro rychlý náhled použijte **STANDARD**
3. Paralelizace: nastavte `PENB_ADVANCED_THREADS=4`

---

### MAPE > 50%

**Řešení:**
1. **Zkontrolujte data:**
   - Správné jednotky? (kWh, ne Wh)
   - Realistické hodnoty?
   - Žádné chyby v odečtech?

2. **Zkontrolujte nastavení:**
   - Správná vnitřní teplota?
   - Správný typ systému?

3. **Vyloučit mimořádné události:**
   - Týden dovolené
   - Porucha topení
   - Extrémní větrání

---

## 📚 DALŠÍ ZDROJE

### Dokumentace

- **Technická dokumentace:** `TECHNICKA_DOKUMENTACE.md`
- **README:** `README.md`
- **Quickstart:** `QUICKSTART.md`

### Podpora

- **GitHub Issues:** https://github.com/michaelprinc/PENB_energy_label_approximation/issues
- **Email:** (doplňte)

### Odkazy

- **WeatherAPI:** https://www.weatherapi.com/
- **Oficiální PENB:** https://www.mpo.cz/
- **TNI 73 0329/Z1:** Metodika pro PENB

---

## 📄 LICENCE

MIT License - viz soubor `LICENSE`

---

## ✅ CHECKLIST PŘED PRVNÍM POUŽITÍM

- [ ] Python 3.8+ nainstalován
- [ ] Závislosti nainstalovány (`pip install -r requirements.txt`)
- [ ] WeatherAPI.com účet vytvořen
- [ ] API klíč zkopírován
- [ ] Aplikace spuštěna (`python main.py`)
- [ ] Data o spotřebě připravena (CSV nebo ruční zadání)
- [ ] Znám parametry bytu (plocha, výška)
- [ ] Znám typ vytápění

---

**Verze příručky:** 1.1.0  
**Datum:** 28. října 2025  
**Pro podporu:** Vytvořte GitHub Issue

---

**Hodně štěstí s odhadem energetické náročnosti vašeho bytu! 🏠💚**

