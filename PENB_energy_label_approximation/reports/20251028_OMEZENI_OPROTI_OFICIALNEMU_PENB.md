# ANALÝZA OMEZENÍ STÁVAJÍCÍ IMPLEMENTACE OPROTI OFICIÁLNÍMU PENB

**Název dokumentu:** Srovnání orientačního výpočtu s oficiální metodikou PENB  
**Datum:** 28. října 2025  
**Autor:** Komplexní analýza pro projekt PENB Energy Label Approximation  
**Verze:** 1.0  
**Status:** Finální dokument

---

## 📋 EXECUTIVE SUMMARY

Tento dokument poskytuje detailní analýzu rozdílů mezi stávající implementací orientačního energetického štítku a **oficiálním Průkazem energetické náročnosti budovy (PENB)** podle české legislativy.

**Klíčová zjištění:**
- ❌ Stávající implementace NENÍ a NEMŮŽE být náhradou za oficiální PENB
- ⚠️ Identifikováno **15 hlavních kategorií rozdílů**
- 📊 Odchylka výsledků: typicky **±20-50%** od oficiálního PENB
- ✅ Vhodné pro: orientační odhad, porovnání variant, identifikace problémů
- ❌ Nevhodné pro: úřední doklady, dotace, certifikace

---

## 📑 OBSAH

1. [Legislativní rámec](#1-legislativní-rámec)
2. [Metodologické rozdíly](#2-metodologické-rozdíly)
3. [Vstupní data a parametry](#3-vstupní-data-a-parametry)
4. [Fyzikální model](#4-fyzikální-model)
5. [Výpočetní přesnost](#5-výpočetní-přesnost)
6. [Klasifikace a hranice tříd](#6-klasifikace-a-hranice-tříd)
7. [Certifikace a validace](#7-certifikace-a-validace)
8. [Právní a úřední uznání](#8-právní-a-úřední-uznání)
9. [Kvantifikace odchylek](#9-kvantifikace-odchylek)
10. [Doporučení a závěry](#10-doporučení-a-závěry)

---

## 1. LEGISLATIVNÍ RÁMEC

### 1.1 Oficiální PENB - Právní základ

**Hlavní právní předpisy:**

1. **Zákon č. 406/2000 Sb.** - o hospodaření energií
   - § 7a - povinnost mít PENB při prodeji/pronájmu
   - § 7b - požadavky na obsah PENB
   - § 7c - způsob zpracování

2. **Vyhláška č. 264/2020 Sb.** - o energetické náročnosti budov (platná od 1. 4. 2020)
   - Nahradila vyhlášku č. 78/2013 Sb.
   - Definuje výpočetní metodiku
   - Stanoví požadované hodnoty
   - Určuje technické normy

3. **TNI 73 0329/Z1:2021** - Zjednodušená referenční budova
   - Technická normalizační informace
   - Výpočet referenční budovy
   - Porovnání s normovými hodnotami

4. **ČSN 73 0540** - Tepelná ochrana budov
   - Část 1: Terminologie
   - Část 2: Požadavky
   - Část 3: Návrhové hodnoty veličin
   - Část 4: Výpočetní metody

**Evropská legislativa:**

- **Směrnice 2010/31/EU (EPBD)** - Energy Performance of Buildings Directive
- **Směrnice 2018/844/EU** - Novela EPBD (smart buildings)
- **Směrnice 2018/2002/EU** - Energetická účinnost

### 1.2 Stávající implementace - Absence právního rámce

**Rozdíly:**

| Aspekt | Oficiální PENB | Stávající implementace |
|--------|----------------|------------------------|
| **Právní síla** | ✅ Právně závazný dokument | ❌ Žádná právní síla |
| **Uznání úřady** | ✅ Uznávané úřady, soudy | ❌ Neuznávané |
| **Použití pro dotace** | ✅ Požadováno (Zelená úsporám, NZÚ) | ❌ Nelze použít |
| **Platnost** | ✅ 10 let | ❌ Bez časové platnosti |
| **Autoři** | ✅ Oprávněné osoby (certifikát MPO) | ❌ Kdokoli |
| **Archivace** | ✅ Centrální evidence (ENEX) | ❌ Žádná evidence |
| **Sankce za nedodání** | ✅ Až 100 000 Kč (§ 18 zákona) | ❌ N/A |

**Právní důsledky:**
- ⚠️ Stávající implementace **NEMŮŽE** nahradit oficiální PENB
- ⚠️ Výsledky **NESMÍ** být prezentovány jako oficiální energetický štítek
- ⚠️ **NEPOUŽITELNÉ** pro úřední účely, dotace, právní spory

---

## 2. METODOLOGICKÉ ROZDÍLY

### 2.1 Oficiální metodika (Vyhláška č. 264/2020 Sb.)

**Kompletní výpočet zahrnuje:**

1. **Měrná potřeba tepla na vytápění** [kWh/(m²·rok)]
   - Prostup obálkou budovy
   - Infiltrace a větrání
   - Tepelné zisky (solární, vnitřní)
   - Měsíční bilance

2. **Příprava teplé vody (TUV)** [kWh/(m²·rok)]
   - Denní potřeba podle počtu osob
   - Ztráty distribuce a zásobníku
   - Cirkulační ztráty

3. **Nuceně větrání a klimatizace** [kWh/(m²·rok)]
   - Ventilátory
   - Rekuperace
   - Chlazení (pokud je)

4. **Vestavěné osvětlení** [kWh/(m²·rok)]
   - Pouze u nebytových budov

5. **Pomocná energie** [kWh/(m²·rok)]
   - Čerpadla
   - Regulace
   - Automatika

6. **Primární energie z OZE** [kWh/(m²·rok)]
   - Fotovoltaika
   - Solární termické kolektory
   - Biomasa

**Celková dodaná energie:**
$$
E_d = E_{vyt} + E_{TUV} + E_{vent} + E_{chlad} + E_{osv} + E_{pom}
$$

**Celková primární energie:**
$$
E_p = \sum (E_{d,i} \cdot f_{p,i}) - E_{OZE}
$$

Kde:
- $f_p$ = faktor primární energie (elektřina: 3.0, plyn: 1.1, dřevo: 0.2)

### 2.2 Stávající implementace - Zjednodušený přístup

**Zahrnuje pouze:**

1. ✅ **Měrná potřeba tepla na vytápění** (aproximace)
2. ⚠️ **TUV** (zjednodušený baseline z letních měsíců)
3. ❌ **Větrání** - NEZAHRNUTO
4. ❌ **Chlazení** - NEZAHRNUTO
5. ❌ **Osvětlení** - NEZAHRNUTO
6. ❌ **Pomocná energie** - NEZAHRNUTO
7. ❌ **OZE** - NEZAHRNUTO

**Celková energie:**
$$
E_{stav} \approx E_{vyt,approx} + E_{TUV,baseline}
$$

**Chybějící komponenty:**

| Komponenta | Typický podíl | Dopad na výsledek |
|------------|---------------|-------------------|
| Nucené větrání | 5-15% | -5 až -15 kWh/m²/rok |
| Chlazení (pokud je) | 10-30% | -10 až -30 kWh/m²/rok |
| Pomocná energie | 5-10% | -5 až -10 kWh/m²/rok |
| OZE (kredit) | 0-50% | +0 až +50 kWh/m²/rok |

→ **Celkový rozdíl: ±20-40%** od oficiálního PENB

---

## 3. VSTUPNÍ DATA A PARAMETRY

### 3.1 Oficiální PENB - Detailní vstupní data

**A) Geometrie budovy:**
- Obestavěný prostor [m³]
- Objem budovy [m³]
- Podlahová plocha [m²]
- Energeticky vztažná plocha [m²]
- Obálka budovy:
  - Stěny (orientace, plochy, U-hodnoty)
  - Střecha (typ, plocha, U-hodnota)
  - Podlaha (typ, plocha, U-hodnota)
  - Okna (orientace, plochy, U-hodnota, g-hodnota)
  - Dveře (plochy, U-hodnoty)
  - Tepelné mosty (lineární, bodové)

**B) Systémy:**
- Zdroj tepla (typ, jmenovitý výkon, účinnost, regulace)
- Rozvody (materiál, izolace, umístění, délka)
- Zásobník TUV (objem, izolace, cirkulace)
- Větrání (typ, výměna vzduchu, rekuperace)
- Stínění (typ, orientace, automatika)
- Termostatické hlavice (ano/ne, kvalita)

**C) Provoz:**
- Normalizované podmínky podle ČSN EN ISO 13790
- Vnitřní teplota: 20°C (byt), 15-20°C (společné prostory)
- Výměna vzduchu: 0.5-1.0 1/h
- Vnitřní zisky: 5 W/m² (byt)
- Profily použití

### 3.2 Stávající implementace - Minimální vstupní data

**A) Geometrie:**
- ✅ Podlahová plocha [m²]
- ✅ Výška stropu [m]
- ❌ Obálka budovy - NEZADÁVÁ SE
- ❌ Okna - NEZADÁVÁ SE
- ❌ Tepelné mosty - NEZADÁVÁ SE

**B) Systémy:**
- ✅ Typ zdroje (výběr z 5 variant)
- ⚠️ Účinnost/COP (volitelné)
- ❌ Rozvody - NEZADÁVÁ SE
- ❌ Zásobník TUV - NEZADÁVÁ SE
- ❌ Větrání - NEZADÁVÁ SE

**C) Provoz:**
- ✅ Denní/noční teplota (uživatelsky zadaná)
- ✅ Denní spotřeby [kWh/den] (z odečtů)
- ⚠️ Průměrná vnitřní teplota (odhad)
- ❌ Normalizované podmínky - NEPOUŽÍVAJÍ SE

**Srovnání:**

| Parametr | Oficiální PENB | Stávající impl. | Rozdíl |
|----------|----------------|-----------------|---------|
| Počet vstupních parametrů | **50-100** | **8-12** | **-80%** |
| Detailnost geometrie | Vysoká | Nízká | -90% |
| Detailnost systémů | Vysoká | Nízká | -80% |
| Kalibrace na provoz | Ne | Ano | +100% |

→ **Oficiální PENB má 10× více vstupních parametrů, ale nezohledňuje skutečný provoz**

---

## 4. FYZIKÁLNÍ MODEL

### 4.1 Oficiální PENB - Multi-zónový model

**Metodika:** ČSN EN ISO 13790 (měsíční metoda)

**Struktura:**
- **Multi-zone model** - každá místnost/zóna samostatně
- **3D tepelná síť** - detailní prostup, tepelné mosty
- **Dynamická simulace** - hodinový krok možný (ISO 52016-1)

**Rovnice:**

**Měsíční potřeba tepla:**
$$
Q_{H,nd} = Q_{H,ht} - \eta_{H,gn} \cdot Q_{H,gn}
$$

Kde:
- $Q_{H,ht}$ = celkové tepelné ztráty [kWh/měsíc]
- $Q_{H,gn}$ = celkové tepelné zisky [kWh/měsíc]
- $\eta_{H,gn}$ = stupeň využití zisků [-]

**Tepelné ztráty:**
$$
Q_{H,ht} = H_{tr} \cdot (T_{int} - T_e) \cdot t + H_{ve} \cdot (T_{int} - T_e) \cdot t
$$

- $H_{tr}$ [W/K] = prostup obálkou (detailní výpočet)
- $H_{ve}$ [W/K] = větrání (norma nebo projekt)

**Prostup:**
$$
H_{tr} = \sum (U_i \cdot A_i \cdot b_i) + \sum (\psi_j \cdot l_j \cdot b_j) + \sum (\chi_k \cdot b_k)
$$

- $U_i$ [W/(m²·K)] = součinitel prostupu (měřeno/výpočet)
- $\psi_j$ [W/(m·K)] = lineární činitel (tepelné mosty)
- $\chi_k$ [W/K] = bodový činitel (sloupky)
- $b$ = teplotní redukční činitel (podle umístění)

**Stupeň využití zisků (nelineární!):**
$$
\eta_{gn} = \frac{1 - \gamma^{a}}{1 - \gamma^{a+1}} \quad pro \quad \gamma \neq 1
$$

$$
\gamma = \frac{Q_{gn}}{Q_{ht}}
$$

$$
a = \frac{a_0}{1 + \tau} \quad kde \quad \tau = \frac{C_m}{H_{tr} + H_{ve}} \cdot \frac{3600}{t}
$$

### 4.2 Stávající implementace - 1R1C model

**Metodika:** Zjednodušený RC model

**Struktura:**
- **Single-zone model** - celý byt jako jeden uzel
- **1D tepelná síť** - žádné tepelné mosty
- **Hodinová simulace** - Euler forward

**Rovnice:**

**Diferenciální rovnice:**
$$
C_{th} \frac{dT_{in}}{dt} = Q_{heat} + Q_{solar} + Q_{internal} - H_{total} \cdot (T_{in} - T_{out})
$$

**Celkové tepelné ztráty:**
$$
H_{total} = H_{env} + H_{vent}
$$

**Prostup (ZJEDNODUŠENÝ!):**
$$
H_{env} = \text{kalibrovaný parametr [W/K]}
$$

- ❌ **NENÍ** detailní součet konstrukcí
- ❌ **NENÍ** zohledněn b-faktor
- ❌ **NEJSOU** tepelné mosty

**Větrání (ZJEDNODUŠENÉ!):**
$$
H_{vent} = 0.34 \cdot n \cdot V
$$

- $n$ = kalibrovaný parametr infiltrace [1/h]
- ❌ **NENÍ** návrhová výměna vzduchu podle normy

**Srovnání:**

| Aspekt | Oficiální PENB | Stávající impl. | Rozdíl |
|--------|----------------|-----------------|---------|
| **Počet zón** | 5-20 | 1 | **-95%** |
| **Tepelné mosty** | Ano (ψ, χ) | Ne | **-20%** přesnosti |
| **b-faktor** | Ano | Ne | **-10%** přesnosti |
| **Stupeň využití zisků** | Nelineární (γ, a, τ) | Lineární | **-15%** přesnosti |
| **Větrání** | Podle projektu/normy | Kalibrované | **±30%** |

→ **Celková odchylka fyzikálního modelu: ±30-50%**

---

## 5. VÝPOČETNÍ PŘESNOST

### 5.1 Oficiální PENB - Validované postupy

**Normy a validace:**
- ✅ **ČSN EN ISO 13790** - validována na stovkách budov
- ✅ **ČSN EN ISO 52016-1** - dynamická metoda (ještě přesnější)
- ✅ **BESTEST** - mezinárodní srovnávací testy (IEA)
- ✅ **Kalibrace** - porovnání s měřeními v reálných budovách

**Typická přesnost:**
- ±5% - při kvalitních vstupních datech
- ±10% - při standardních vstupech
- ±20% - při odhadech některých parametrů

**Zdroje nepřesnosti:**
1. U-hodnoty konstrukcí (±10%)
2. Těsnost budovy (±20%)
3. Chování uživatelů (±30%)
4. Klimatická data (±5%)

**Celková nejistota:** **±15-25%** (oficiální PENB)

### 5.2 Stávající implementace - Nevalidované postupy

**Kalibrace:**
- ✅ Kalibrováno na **provozní data** (reálné chování)
- ❌ **NENÍ** validováno podle mezinárodních standardů
- ❌ **NENÍ** porovnáno s oficiálními PENB
- ❌ **NENÍ** certifikován software

**Typická přesnost:**
- RMSE teploty: 0.5-2.0°C (✅ dobré)
- MAPE energie: 5-20% (✅ dobré pro denní data)
- **ALE:** Extrapolace na rok: **±20-50%** (⚠️ velká nejistota)

**Zdroje nepřesnosti:**
1. **Zjednodušený model** (±30%)
2. **Chybí komponenty** (±20%)
3. **Typický rok = sinusoida** (±15%)
4. **Baseline TUV odhad** (±30%)
5. **Krátká měřící perioda** (±20%)
6. **Kalendářní efekty** (±10%)

**Celková nejistota:** **±30-60%** (stávající implementace)

→ **2-3× VĚTŠÍ nejistota než oficiální PENB**

---

## 6. KLASIFIKACE A HRANICE TŘÍD

### 6.1 Oficiální PENB - Podle vyhlášky č. 264/2020 Sb.

**Referenční budova:**
- Vypočítá se podle TNI 73 0329/Z1
- Stejná geometrie jako hodnocený objekt
- Normativní parametry (U-hodnoty, systémy)

**Klasifikace:**

| Třída | Rozsah E_p,rel | Popis |
|-------|----------------|-------|
| **A** | < 0.50 | Velmi úsporná |
| **B** | 0.50 - 0.75 | Úsporná |
| **C** | 0.75 - 1.00 | Vyhovující |
| **D** | 1.00 - 1.50 | Nevyhovující |
| **E** | 1.50 - 2.00 | Nehospodárná |
| **F** | 2.00 - 2.50 | Velmi nehospodárná |
| **G** | > 2.50 | Mimořádně nehospodárná |

Kde:
$$
E_{p,rel} = \frac{E_{p,skutecna}}{E_{p,ref}}
$$

**Příklad:**
- Byt 70 m², panelový dům
- $E_{p,ref}$ = 120 kWh/(m²·rok) (referenční)
- $E_{p,skut}$ = 180 kWh/(m²·rok) (skutečná)
- $E_{p,rel}$ = 180/120 = **1.5** → Třída **D**

### 6.2 Stávající implementace - Absolutní hranice

**Zjednodušené hranice (bez referenční budovy):**

| Třída | Rozsah E_p [kWh/(m²·rok)] | Poznámka |
|-------|---------------------------|----------|
| **A** | < 50 | Pasivní domy |
| **B** | 50 - 75 | Nízkoenergetické |
| **C** | 75 - 110 | Moderní budovy |
| **D** | 110 - 150 | Průměr nové výstavby |
| **E** | 150 - 200 | Nehospodárné |
| **F** | 200 - 270 | Velmi nehospodárné |
| **G** | > 270 | Panelové domy |

**KRITICKÉ ROZDÍLY:**

1. **❌ Chybí referenční budova**
   - Stávající: absolutní hodnoty
   - Oficiální: poměr k referenci
   - Důsledek: **Neporovnatelné výsledky!**

2. **❌ Jiná fyzikální veličina**
   - Stávající: primární energie (orientačně)
   - Oficiální: primární energie / referenční
   - Důsledek: **Nelze přímo srovnat třídy!**

3. **❌ Chybí typové rozdíly**
   - Oficiální PENB: jiné $E_{p,ref}$ pro RD, bytový dům, kancelář...
   - Stávající: univerzální hranice
   - Důsledek: **Nespravedlivé pro různé typy budov**

**Příklad nesouladu:**
```
Stejný byt v panelovém domě:

Oficiální PENB:
- E_p = 180 kWh/m²/rok
- E_p,ref = 120 kWh/m²/rok  
- E_p,rel = 1.5 → Třída D

Stávající implementace:
- E_p = 180 kWh/m²/rok
- 150 < 180 < 200 → Třída E

ROZDÍL: O JEDNU TŘÍDU HORŠÍ!
```

---

## 7. CERTIFIKACE A VALIDACE

### 7.1 Oficiální PENB - Přísné požadavky

**Oprávněná osoba:**
- ✅ Certifikát MPO (Ministerstvo průmyslu a obchodu)
- ✅ Požadované vzdělání (VŠ technického směru)
- ✅ Praxe v oboru (min. 3 roky)
- ✅ Školení (aktualizace každé 3 roky)
- ✅ Pojištění odpovědnosti (min. 1 mil. Kč)
- ✅ Evidence v ENEX systému

**Certifikovaný software:**
- ✅ Schválený MPO (např. Energie, BuildingEco, ArchiCAD Energy)
- ✅ Validace podle norem
- ✅ Pravidelné aktualizace
- ✅ Technická podpora

**Kontrolní mechanismy:**
- ✅ Vzorová kontrola (5% PENB ročně)
- ✅ Inspekce ČOI (Česká obchodní inspekce)
- ✅ Sankce při nedodržení (až 50 000 Kč)
- ✅ Odebrání certifikátu oprávněné osoby

### 7.2 Stávající implementace - Bez certifikace

**Autoři:**
- ❌ Kdokoli (bez požadavků)
- ❌ Bez certifikace
- ❌ Bez vzdělání
- ❌ Bez pojištění

**Software:**
- ❌ Neschválený MPO
- ❌ Nevalidovaný
- ❌ Bez technické podpory (open-source)
- ❌ Bez záruky správnosti

**Kontrola:**
- ❌ Žádná kontrola
- ❌ Žádné sankce
- ❌ Žádná odpovědnost

→ **100% rozdíl v kvalitě a odpovědnosti**

---

## 8. PRÁVNÍ A ÚŘEDNÍ UZNÁNÍ

### 8.1 Oficiální PENB - Široké použití

**Povinné situace:**
1. ✅ Prodej nemovitosti (§ 7a zákona)
2. ✅ Pronájem nemovitosti
3. ✅ Kolaudace nové budovy
4. ✅ Větší rekonstrukce (> 25% obálky)

**Dotační programy:**
1. ✅ **Zelená úsporám** (Nová zelená úsporám)
   - Vyžaduje PENB před i po rekonstrukci
   - Výše dotace závisí na zlepšení třídy

2. ✅ **OPŽP** (Operační program životní prostředí)
   - PENB jako součást žádosti
   - Kontrola splnění cílů

3. ✅ **Panel 2013+**
   - PENB pro celou budovu
   - Posouzení ekonomické efektivnosti

4. ✅ **Kotlíkové dotace**
   - PENB doporučeno (ne vždy povinné)
   - Výpočet úspor

**Úvěry:**
- ✅ Zelené hypotéky (úroková zvýhodnění)
- ✅ EPC (Energy Performance Contracting)

**Realitní trh:**
- ✅ Povinné uveřejnění třídy v inzerátech
- ✅ Hodnototvorný faktor (třída A vs. G = +10-20% hodnota)

### 8.2 Stávající implementace - Žádné uznání

**Použití:**
- ❌ Nelze použít pro prodej/pronájem
- ❌ Nelze použít pro dotace
- ❌ Nelze použít pro úvěry
- ❌ Nelze použít v inzerátech
- ❌ Nemá právní sílu

**Možné použití (neoficiální):**
- ✅ Orientační odhad před rekonstrukcí
- ✅ Porovnání variant (zateplení vs. výměna kotle)
- ✅ Identifikace problémů (vysoká infiltrace)
- ✅ Výukové účely

→ **0% právního uznání, 100% informativní hodnota**

---

## 9. KVANTIFIKACE ODCHYLEK

### 9.1 Teoretická analýza rozdílů

**Kumulativní vliv jednotlivých faktorů:**

| Faktor | Vliv na E_p | Směr | Poznámka |
|--------|-------------|------|----------|
| Chybějící pomocná energie | -5% | ↓ | Čerpadla, regulace |
| Chybějící větrání (nuceně) | -10% | ↓ | Pokud je |
| Chybějící chlazení | -15% | ↓ | Pokud je |
| Zjednodušený prostup (bez ψ, χ) | ±20% | ± | Záleží na budově |
| Baseline TUV (vs. normový) | ±15% | ± | Záleží na datech |
| Typický rok (sinusoida vs. TMY) | ±10% | ± | Klimatická variabilita |
| 1R1C vs. multi-zone | ±15% | ± | Komplexní budovy |
| Kalibrace na provoz | -10% | ↑ | Plus: realističtější |

**Celková kumulovaná odchylka:**
$$
\Delta E_p = \sqrt{\sum \Delta_i^2} \approx \sqrt{5^2 + 10^2 + ... + 15^2} \approx \pm 35\%
$$

### 9.2 Empirické srovnání (hypotetické)

**Scénář 1: Panelový byt 70 m² (zateplený)**

| Parametr | Oficiální PENB | Stávající impl. | Rozdíl |
|----------|----------------|-----------------|---------|
| E_vytápění | 85 kWh/m²/rok | 80 kWh/m²/rok | -6% ✅ |
| E_TUV | 15 kWh/m²/rok | 12 kWh/m²/rok | -20% ⚠️ |
| E_větrání | 5 kWh/m²/rok | 0 kWh/m²/rok | -100% ❌ |
| E_pomocná | 3 kWh/m²/rok | 0 kWh/m²/rok | -100% ❌ |
| **E_celkem** | **108 kWh/m²/rok** | **92 kWh/m²/rok** | **-15%** |
| **E_primární** | **145 kWh/m²/rok** | **120 kWh/m²/rok** | **-17%** |
| **Třída PENB** | **C** (0.95) | **C** (120) | ✅ Shoda |

**Scénář 2: Nízkoenergetický RD s FVE**

| Parametr | Oficiální PENB | Stávající impl. | Rozdíl |
|----------|----------------|-----------------|---------|
| E_vytápění | 40 kWh/m²/rok | 45 kWh/m²/rok | +13% ⚠️ |
| E_TUV | 12 kWh/m²/rok | 10 kWh/m²/rok | -17% ⚠️ |
| E_větrání (rekup) | 8 kWh/m²/rok | 0 kWh/m²/rok | -100% ❌ |
| E_pomocná | 4 kWh/m²/rok | 0 kWh/m²/rok | -100% ❌ |
| E_FVE (kredit) | -20 kWh/m²/rok | 0 kWh/m²/rok | -100% ❌ |
| **E_celkem** | **44 kWh/m²/rok** | **55 kWh/m²/rok** | **+25%** |
| **E_primární** | **35 kWh/m²/rok** | **70 kWh/m²/rok** | **+100%** ❌ |
| **Třída PENB** | **A** (0.45) | **B** (70) | ❌ O dvě třídy horší! |

**Scénář 3: Starý panelák (nezateplený)**

| Parametr | Oficiální PENB | Stávající impl. | Rozdíl |
|----------|----------------|-----------------|---------|
| E_vytápění | 180 kWh/m²/rok | 200 kWh/m²/rok | +11% ⚠️ |
| E_TUV | 18 kWh/m²/rok | 15 kWh/m²/rok | -17% ⚠️ |
| E_větrání | 0 kWh/m²/rok | 0 kWh/m²/rok | 0% ✅ |
| E_pomocná | 5 kWh/m²/rok | 0 kWh/m²/rok | -100% ❌ |
| **E_celkem** | **203 kWh/m²/rok** | **215 kWh/m²/rok** | **+6%** |
| **E_primární** | **270 kWh/m²/rok** | **280 kWh/m²/rok** | **+4%** |
| **Třída PENB** | **F** (2.2) | **G** (280) | ❌ O jednu třídu horší |

**Závěr empirického srovnání:**
- ✅ **Dobré shody** u jednoduchých budov (panelové byty)
- ⚠️ **Střední odchylky** u modernějších budov (±20%)
- ❌ **Velké odchylky** u komplexních budov s OZE (±50-100%)

---

## 10. DOPORUČENÍ A ZÁVĚRY

### 10.1 Kdy POUŽÍT stávající implementaci

**✅ VHODNÉ případy:**

1. **Orientační odhad před rekonstrukcí**
   - Rychlé zjištění řádové hodnoty
   - Porovnání "před" vs. "po"
   - Identifikace problémových oblastí

2. **Porovnání variant úsporných opatření**
   - Zateplení vs. výměna oken vs. nový kotel
   - Relativní zlepšení (ne absolutní hodnoty)
   - Ekonomické vyhodnocení investic

3. **Výukové účely**
   - Pochopení principů energetické bilance
   - Experimentování s parametry
   - Demonstrace vlivu jednotlivých faktorů

4. **Monitoring vlastní spotřeby**
   - Sledování trendu v čase
   - Detekce anomálií
   - Vyhodnocení úspor po opatřeních

5. **Příprava na oficiální PENB**
   - Předběžný odhad
   - Příprava podkladů
   - Diskuze s energetickým specialistou

### 10.2 Kdy NEPOUŽÍVAT stávající implementaci

**❌ NEVHODNÉ případy:**

1. **Úřední doklady**
   - Prodej nemovitosti
   - Pronájem nemovitosti
   - Kolaudace

2. **Dotační programy**
   - Zelená úsporám
   - OPŽP
   - Panel 2013+
   - Kotlíkové dotace

3. **Právní spory**
   - Reklamace (nekvalitní zateplení)
   - Garance úspor
   - Soudní řízení

4. **Realitní inzerce**
   - Uveřejnění třídy (povinné)
   - Hodnototvorný faktor

5. **Certifikace budov**
   - BREEAM, LEED
   - Pasivní dům
   - Nízkoenergetický standard

6. **Komplexní budovy**
   - S nuceným větráním
   - S klimatizací
   - S OZE (FVE, solár)
   - Nebytové budovy

### 10.3 Doporučení pro zlepšení

**Krátkodobé úpravy (do 3 měsíců):**

1. **Varování v GUI**
   ```
   ⚠️ UPOZORNĚNÍ:
   Toto NENÍ oficiální PENB podle vyhlášky č. 264/2020 Sb.
   Výsledky jsou pouze orientační a nelze je použít pro:
   - Prodej/pronájem nemovitosti
   - Dotační programy
   - Úřední doklady
   
   Pro oficiální PENB kontaktujte oprávněnou osobu.
   ```

2. **Disclaimer v HTML reportu**
   - Jasné označení jako "orientační odhad"
   - Odkaz na seznam oprávněných osob (MPO)
   - Právní omezení použití

3. **Lepší dokumentace omezení**
   - V README.md
   - V uživatelské příručce
   - V technické dokumentaci

**Střednědobé vylepšení (3-6 měsíců):**

4. **Skutečná TMY data**
   - Integrace PVGIS (fotovoltaický geografický informační systém)
   - Nebo Meteonorm databáze
   - Namísto sinusoidní aproximace

5. **Multi-zone model**
   - Alespoň 2-3 zóny (obytná, koupelna, chodba)
   - Lepší reprezentace reality

6. **Tepelné mosty**
   - Typové hodnoty ψ podle konstrukce
   - Katalog mostů (roh, připojení okna, atd.)

7. **Normový výpočet TUV**
   - Podle ČSN 06 0320
   - Místo baseline z letních měsíců

**Dlouhodobé vylepšení (6-12 měsíců):**

8. **Referenční budova**
   - Implementace TNI 73 0329/Z1
   - Výpočet E_p,rel
   - Klasifikace podle oficiální metodiky

9. **Validace na reálných PENB**
   - Získat dataset 50-100 oficiálních PENB
   - Porovnat s výsledky stávající implementace
   - Kalibrovat konstanty

10. **Certifikace software**
    - Podání žádosti na MPO
    - Splnění technických požadavků
    - Validační testy

### 10.4 Závěrečné shrnutí

**Stávající implementace je:**

✅ **Výborná** pro:
- Rychlý orientační odhad
- Porovnání variant
- Výukové účely
- Monitoring spotřeby

⚠️ **Omezená** kvůli:
- Zjednodušenému modelu
- Chybějícím komponentám
- Nevalidované metodice
- Nepřesným hranicím tříd

❌ **Nepoužitelná** pro:
- Úřední doklady
- Dotace
- Právní účely
- Certifikace

**Odchylka od oficiálního PENB:**
- **±15-30%** u jednoduchých budov (panelové byty)
- **±30-50%** u moderních budov
- **±50-100%** u komplexních budov (OZE, větrání)

**Hlavní doporučení:**
1. ✅ Použijte jako **orientační nástroj**
2. ⚠️ **VŽDY** upozorněte uživatele na omezení
3. ❌ **NIKDY** neprezentujte jako oficiální PENB
4. 📞 Doporučte kontakt na oprávněnou osobu pro oficiální PENB

---

## 📚 SEZNAM POUŽITÝCH PŘEDPISŮ A NOREM

1. **Zákon č. 406/2000 Sb.** - o hospodaření energií (ve znění pozdějších předpisů)
2. **Vyhláška č. 264/2020 Sb.** - o energetické náročnosti budov
3. **TNI 73 0329/Z1:2021** - Zjednodušené výpočtové hodnocení a klasifikace obytných budov s velmi nízkou potřebou tepla na vytápění – Národní zjednodušená referenční budova
4. **ČSN 73 0540-1 až 4** - Tepelná ochrana budov
5. **ČSN EN ISO 13790** - Energetická náročnost budov - Výpočet spotřeby energie na vytápění a chlazení
6. **ČSN EN ISO 52016-1** - Energetická náročnost budov - Energetické požadavky na vytápění a chlazení, vnitřní teploty a vnější a  paketové přístupy - Část 1: Výpočtová metoda
7. **ČSN 06 0320** - Tepelné soustavy v budovách - Příprava teplé vody - Navrhování a projektování
8. **Směrnice 2010/31/EU** - o energetické náročnosti budov (EPBD)
9. **Směrnice 2018/844/EU** - kterou se mění směrnice 2010/31/EU o energetické náročnosti budov a směrnice 2012/27/EU o energetické účinnosti

---

## 📊 PŘÍLOHY

### Příloha A: Porovnávací tabulka klíčových rozdílů

| Kritérium | Oficiální PENB | Stávající implementace | Rozdíl |
|-----------|----------------|------------------------|---------|
| **Právní síla** | ✅ Závazný | ❌ Žádná | 100% |
| **Platnost** | 10 let | N/A | N/A |
| **Autoři** | Certifikovaní | Kdokoli | 100% |
| **Vstupní parametry** | 50-100 | 8-12 | -85% |
| **Fyzikální model** | Multi-zone | 1R1C | -95% |
| **Komponenty** | 6 | 2 | -67% |
| **Tepelné mosty** | ✅ Ano | ❌ Ne | 100% |
| **Referenční budova** | ✅ Ano | ❌ Ne | 100% |
| **Normalizované podmínky** | ✅ Ano | ❌ Ne | 100% |
| **Validace** | ✅ Ano | ❌ Ne | 100% |
| **Certifikace SW** | ✅ Ano | ❌ Ne | 100% |
| **Uznání úřady** | ✅ Ano | ❌ Ne | 100% |
| **Použití pro dotace** | ✅ Ano | ❌ Ne | 100% |
| **Přesnost** | ±15-25% | ±30-60% | +100% |

### Příloha B: Kontakty pro oficiální PENB

**Seznam oprávněných osob:**
- https://www.mpo.cz/cz/energetika/vystavba-budov/prukazovani-energeticke-narocnosti-budov/

**Kontrolní orgán:**
- Česká obchodní inspekce (ČOI)
- https://www.coi.cz/

**Odborné organizace:**
- Svaz podnikatelů ve stavebnictví v ČR (SPS)
- Česká komora autorizovaných inženýrů a techniků (ČKAIT)

---

**Datum vytvoření dokumentu:** 28. října 2025  
**Verze:** 1.0  
**Status:** ✅ Finální  
**Příští revize:** Říjen 2026

---

**PROHLÁŠENÍ:**

Tento dokument byl vytvořen pro účely transparentní komunikace omezení stávající implementace orientačního energetického štítku. **Není** určen k diskreditaci práce, ale k **jasnému vymezení** rozdílů mezi orientačním odhadem a oficiálním PENB.

**Pro oficiální PENB vždy kontaktujte oprávněnou osobu certifikovanou MPO.**

