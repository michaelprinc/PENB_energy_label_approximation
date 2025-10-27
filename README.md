# Energetický štítek - výpočet měrné potřeby tepla

Python aplikace pro odhad měrné potřeby tepla (kWh/m²·rok) a orientační energetické třídy bytu.

## Popis

Aplikace odhaduje energetickou náročnost bytu na základě reálné spotřeby energie a meteorologických dat. Využívá jednoduchý RC tepelný model budovy, který je kalibrován na naměřenou spotřebu a následně simuluje roční profil spotřeby.

### Hlavní funkce

- **Stažení meteorologických dat**: Hodinová data o počasí z weatherapi.com (nebo demo režim s syntetickými daty)
- **Rozdělení spotřeby**: Automatické rozdělení celkové spotřeby na TUV (teplou užitkovou vodu) a vytápění
- **RC tepelný model**: Kalibrace modelu s parametry:
  - HLC (Heat Loss Coefficient) - součinitel tepelných ztrát
  - Infiltrace - rychlost výměny vzduchu
  - Tepelná kapacita budovy
- **Roční simulace**: Simulace roční spotřeby na základě kalibrovaného modelu
- **Energetická třída**: Výpočet energetické třídy (A-G) podle měrné potřeby tepla
- **Míra spolehlivosti**: Odhad spolehlivosti výpočtu (0-100%)

## Instalace

1. Naklonujte repozitář:
```bash
git clone https://github.com/michaelprinc/energeticky_stitek.git
cd energeticky_stitek
```

2. Nainstalujte závislosti:
```bash
pip install -r requirements.txt
```

## Použití

### Základní použití (demo režim bez API klíče)

```bash
python energeticky_stitek.py \
  --area 75 \
  --ceiling-height 2.6 \
  --heat-source gas-boiler \
  --efficiency 0.9 \
  --daily-consumption 25 \
  --indoor-temp 21 \
  --location Prague
```

### Použití s API klíčem pro weatherapi.com

```bash
python energeticky_stitek.py \
  --area 75 \
  --ceiling-height 2.6 \
  --heat-source heat-pump \
  --efficiency 3.5 \
  --daily-consumption 15 \
  --indoor-temp 21 \
  --location Prague \
  --api-key VÁŠ_API_KLÍČ \
  --year 2023
```

### Parametry

**Povinné parametry:**

- `--area`: Plocha bytu v m²
- `--ceiling-height`: Výška stropu v m
- `--heat-source`: Typ zdroje tepla
  - `gas-boiler`: Plynový kotel
  - `electric`: Elektrické topení
  - `heat-pump`: Tepelné čerpadlo
  - `district-heating`: Dálkové vytápění
- `--efficiency`: Účinnost zdroje (0-1 pro kotle, >1 pro tepelná čerpadla - COP)
- `--daily-consumption`: Průměrná denní spotřeba energie v kWh
- `--indoor-temp`: Požadovaná vnitřní teplota ve °C
- `--location`: Lokalita (např. 'Prague', 'Brno', 'Ostrava')

**Volitelné parametry:**

- `--api-key`: API klíč pro weatherapi.com (bez něj běží demo režim)
- `--year`: Rok pro historická meteorologická data (výchozí: minulý rok)
- `--people`: Počet osob v bytě (výchozí: 2, používá se pro odhad spotřeby TUV)
- `--output`: Název výstupního souboru s reportem

### Příklady

**Příklad 1: Byt s plynovým kotlem**
```bash
python energeticky_stitek.py \
  --area 80 \
  --ceiling-height 2.7 \
  --heat-source gas-boiler \
  --efficiency 0.92 \
  --daily-consumption 28 \
  --indoor-temp 21 \
  --location Prague \
  --people 3
```

**Příklad 2: Byt s tepelným čerpadlem**
```bash
python energeticky_stitek.py \
  --area 65 \
  --ceiling-height 2.5 \
  --heat-source heat-pump \
  --efficiency 3.8 \
  --daily-consumption 12 \
  --indoor-temp 20 \
  --location Brno \
  --output energeticka_trida.txt
```

**Příklad 3: Malý byt s elektrickým topením**
```bash
python energeticky_stitek.py \
  --area 45 \
  --ceiling-height 2.6 \
  --heat-source electric \
  --efficiency 0.99 \
  --daily-consumption 18 \
  --indoor-temp 22 \
  --location Ostrava \
  --people 1
```

## Energetické třídy

Aplikace vyhodnocuje energetickou třídu podle měrné potřeby tepla na vytápění:

- **Třída A**: 0-50 kWh/(m²·rok) - vynikající
- **Třída B**: 50-75 kWh/(m²·rok) - velmi úsporná
- **Třída C**: 75-110 kWh/(m²·rok) - úsporná
- **Třída D**: 110-150 kWh/(m²·rok) - méně úsporná
- **Třída E**: 150-200 kWh/(m²·rok) - nehospodárná
- **Třída F**: 200-250 kWh/(m²·rok) - velmi nehospodárná
- **Třída G**: >250 kWh/(m²·rok) - mimořádně nehospodárná

## Výstup

Aplikace generuje podrobný report obsahující:

1. **Vstupní parametry**: Shrnutí všech zadaných hodnot
2. **Kalibrované parametry RC modelu**: Vypočítané tepelně-technické charakteristiky
3. **Roční simulace**: Celková roční spotřeba na vytápění a TUV
4. **Měrná potřeba tepla**: Klíčová hodnota v kWh/(m²·rok)
5. **Energetická třída**: Výsledná třída A-G
6. **Míra spolehlivosti**: Procento spolehlivosti odhadu
7. **Interpretace**: Doporučení na základě spolehlivosti

Report je zobrazen na standardním výstupu a uložen do souboru.

## Metodika

### RC model budovy

Aplikace používá zjednodušený RC (odpor-kapacita) model tepelného chování budovy:

1. **HLC (Heat Loss Coefficient)**: Celkový součinitel tepelných ztrát přes obálku budovy [W/K]
2. **Infiltrace**: Rychlost výměny vzduchu způsobená netěsnostmi [1/h]
3. **Tepelná kapacita**: Schopnost budovy akumulovat teplo [Wh/K]

### Kalibrace

Model je kalibrován metodou nejmenších čtverců tak, aby predikovaná spotřeba odpovídala naměřené hodnotě. Kalibrace probíhá automaticky na základě:
- Zadané denní spotřeby
- Vnitřní a průměrné venkovní teploty
- Geometrie bytu

### Míra spolehlivosti

Spolehlivost odhadu zohledňuje:
- Shodu mezi měřenou a simulovanou spotřebou
- Chybu kalibračního procesu
- Délku a kvalitu vstupních dat

## Omezení

- Aplikace je určena pro orientační odhad, ne pro certifikovaný energetický štítek
- Předpokládá konstantní vnitřní teplotu (nezohledňuje termostatické regulace)
- Neuvažuje solární zisky přes okna
- Neuvažuje vnitřní zisky od osob a spotřebičů
- Zjednodušený model TUV (konstantní spotřeba na osobu)

## API klíč pro weatherapi.com

Pro získání reálných meteorologických dat je potřeba API klíč:

1. Zaregistrujte se na https://www.weatherapi.com
2. V účtu získáte API klíč zdarma (až 1 milion požadavků/měsíc v bezplatném plánu)
3. Použijte klíč s parametrem `--api-key`

Bez API klíče aplikace běží v demo režimu s generovanými syntetickými daty (roční teplotní cyklus).

## Licence

MIT

## Autor

Michael Princ
