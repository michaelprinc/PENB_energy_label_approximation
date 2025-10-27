"""
Test pro ověření, že NEDOCHÁZÍ k extrapolaci mezi rozdálenými měsíci.

Tento test ověřuje opravu v preprocess.py:
- Data z března a října by NEMĚLA být interpolována
- Měly by zůstat oddělené mezery
- Žádná forward/backward fill přes dlouhé periody

Autor: GitHub Copilot
Datum: 2025-10-27
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.preprocess import clean_weather_data


def create_test_data_with_gap():
    """
    Vytvoří testovací data:
    - Březen 2024: 1-7 (7 dní)
    - MEZERA: 8. března - 30. září (žádná data)
    - Říjen 2024: 1-7 (7 dní)
    """
    data = []
    
    # Březen 2024 (teploty kolem 8°C)
    for day in range(1, 8):
        date = datetime(2024, 3, day)
        for hour in range(24):
            timestamp = date + timedelta(hours=hour)
            temp = 8.0 + 3 * np.sin(2 * np.pi * hour / 24)  # denní variace
            
            data.append({
                'timestamp': timestamp,
                'temp_out_c': temp,
                'humidity_pct': 65.0,
                'wind_mps': 3.0,
                'ghi_wm2': max(0, 400 * np.sin(np.pi * (hour - 6) / 12) if 6 <= hour <= 18 else 0)
            })
    
    # MEZERA - žádná data mezi březnem a říjnem
    
    # Říjen 2024 (teploty kolem 12°C)
    for day in range(1, 8):
        date = datetime(2024, 10, day)
        for hour in range(24):
            timestamp = date + timedelta(hours=hour)
            temp = 12.0 + 3 * np.sin(2 * np.pi * hour / 24)  # denní variace
            
            data.append({
                'timestamp': timestamp,
                'temp_out_c': temp,
                'humidity_pct': 70.0,
                'wind_mps': 2.5,
                'ghi_wm2': max(0, 300 * np.sin(np.pi * (hour - 6) / 12) if 6 <= hour <= 18 else 0)
            })
    
    df = pd.DataFrame(data)
    return df


def test_no_extrapolation():
    """
    HLAVNÍ TEST: Ověří, že clean_weather_data() NEINTERPOLUJE mezi měsíci
    """
    print("\n" + "="*70)
    print("TEST: Ověření ABSENCE extrapolace mezi rozdálenými měsíci")
    print("="*70)
    
    # 1. Vytvoř testovací data
    print("\n1️⃣ Vytvářím testovací data (březen + říjen 2024)...")
    df_input = create_test_data_with_gap()
    
    print(f"   ✓ Vstupní data:")
    print(f"     - Březen: {(df_input['timestamp'] < datetime(2024, 4, 1)).sum()} hodin")
    print(f"     - Říjen: {(df_input['timestamp'] >= datetime(2024, 10, 1)).sum()} hodin")
    print(f"     - Celkem: {len(df_input)} hodin")
    print(f"     - Časové rozmezí: {df_input['timestamp'].min()} až {df_input['timestamp'].max()}")
    
    gap_days = (datetime(2024, 10, 1) - datetime(2024, 3, 8)).days
    print(f"     - MEZERA: {gap_days} dní (duben - září)")
    
    # 2. Aplikuj clean_weather_data
    print("\n2️⃣ Aplikuji clean_weather_data()...")
    df_output = clean_weather_data(df_input)
    
    print(f"   ✓ Výstupní data:")
    print(f"     - Celkem: {len(df_output)} hodin")
    print(f"     - Časové rozmezí: {df_output['timestamp'].min()} až {df_output['timestamp'].max()}")
    
    # 3. KLÍČOVÝ TEST: Zkontroluj, že NEEXISTUJÍ data v mezeře
    print("\n3️⃣ KONTROLA: Jsou data v mezeře (duben - září)?")
    
    gap_start = datetime(2024, 3, 8)
    gap_end = datetime(2024, 10, 1)
    
    gap_data = df_output[
        (df_output['timestamp'] >= gap_start) & 
        (df_output['timestamp'] < gap_end)
    ]
    
    if len(gap_data) == 0:
        print(f"   ✅ VÝBORNĚ! Žádná data v mezeře (duben - září)")
        print(f"      → Nedošlo k extrapolaci/interpolaci")
        test_passed_gap = True
    else:
        print(f"   ❌ CHYBA! Nalezeno {len(gap_data)} hodin v mezeře!")
        print(f"      → Došlo k nežádoucí interpolaci")
        print(f"\n   První data v mezeře:")
        print(gap_data.head())
        test_passed_gap = False
    
    # 4. Zkontroluj, že data z března a října ZŮSTALA
    print("\n4️⃣ KONTROLA: Zůstala data z března a října?")
    
    march_data = df_output[df_output['timestamp'] < datetime(2024, 4, 1)]
    october_data = df_output[df_output['timestamp'] >= datetime(2024, 10, 1)]
    
    march_count = len(march_data)
    october_count = len(october_data)
    
    # Očekáváme 7 dní * 24 hodin = 168 hodin v březnu
    # A 7 dní * 24 hodin = 168 hodin v říjnu
    # (může být méně kvůli interpolation limit=3)
    
    print(f"   Březen: {march_count} hodin")
    print(f"   Říjen: {october_count} hodin")
    
    if march_count >= 150 and october_count >= 150:  # tolerance
        print(f"   ✅ Data z března a října jsou zachována")
        test_passed_data = True
    else:
        print(f"   ❌ CHYBA! Ztratila se data")
        test_passed_data = False
    
    # 5. Zkontroluj průměrné teploty
    print("\n5️⃣ KONTROLA: Průměrné teploty jsou správné?")
    
    avg_march = march_data['temp_out_c'].mean()
    avg_october = october_data['temp_out_c'].mean()
    
    print(f"   Březen: {avg_march:.2f}°C (očekáváno ~8°C)")
    print(f"   Říjen: {avg_october:.2f}°C (očekáváno ~12°C)")
    
    if 7 <= avg_march <= 9 and 11 <= avg_october <= 13:
        print(f"   ✅ Teploty odpovídají vstupním datům")
        test_passed_temp = True
    else:
        print(f"   ❌ CHYBA! Teploty neodpovídají")
        test_passed_temp = False
    
    # 6. VÝSLEDEK
    print("\n" + "="*70)
    print("VÝSLEDKY TESTŮ")
    print("="*70)
    
    all_passed = test_passed_gap and test_passed_data and test_passed_temp
    
    print(f"\n{'✅' if test_passed_gap else '❌'} Test 1: Žádná extrapolace v mezeře")
    print(f"{'✅' if test_passed_data else '❌'} Test 2: Data z března/října zachována")
    print(f"{'✅' if test_passed_temp else '❌'} Test 3: Správné průměrné teploty")
    
    print("\n" + "="*70)
    
    if all_passed:
        print("🎉 VŠECHNY TESTY PROŠLY!")
        print("✓ Oprava extrapolace funguje správně")
        print("✓ Data jsou zpracována pouze tam, kde skutečně existují")
        return True
    else:
        print("❌ NĚKTERÉ TESTY SELHALY!")
        print("⚠ Je potřeba zkontrolovat implementaci clean_weather_data()")
        return False


def test_short_gap_interpolation():
    """
    Test, že KRÁTKÉ mezery (do 3h) SE interpolují
    """
    print("\n" + "="*70)
    print("TEST: Ověření interpolace KRÁTKÝCH mezer (max 3h)")
    print("="*70)
    
    # Vytvoř data s krátkou mezerou
    data = []
    base_time = datetime(2024, 3, 1, 0, 0, 0)
    
    for hour in range(10):
        if hour in [3, 4]:  # 2-hodinová mezera
            continue  # přeskoč
        
        data.append({
            'timestamp': base_time + timedelta(hours=hour),
            'temp_out_c': 10.0 + hour * 0.5,
            'humidity_pct': 70.0,
            'wind_mps': 2.0,
            'ghi_wm2': 100.0
        })
    
    df_input = pd.DataFrame(data)
    print(f"\n   Vstup: {len(df_input)} hodin (s 2h mezerou)")
    
    df_output = clean_weather_data(df_input)
    print(f"   Výstup: {len(df_output)} hodin")
    
    # Zkontroluj, že mezera byla interpolována
    if len(df_output) > len(df_input):
        print(f"\n   ✅ Krátká mezera (2h) byla interpolována")
        return True
    else:
        print(f"\n   ❌ Krátká mezera nebyla interpolována (možná chyba)")
        return False


if __name__ == "__main__":
    print("\n" + "█"*70)
    print("█  TEST SUITE: Verifikace opravy extrapolace dat" + " "*17 + "█")
    print("█"*70 + "\n")
    
    # Test 1: Hlavní test - žádná extrapolace mezi měsíci
    test1_passed = test_no_extrapolation()
    
    # Test 2: Interpolace krátkých mezer funguje
    test2_passed = test_short_gap_interpolation()
    
    # Celkový výsledek
    print("\n" + "█"*70)
    print("█  CELKOVÝ VÝSLEDEK" + " "*50 + "█")
    print("█"*70)
    
    if test1_passed and test2_passed:
        print("\n✅ ✅ ✅  VŠECHNY TESTY ÚSPĚŠNÉ  ✅ ✅ ✅")
        print("\n✓ Oprava extrapolace funguje správně")
        print("✓ Model bude používat POUZE skutečná data")
        print("✓ Nebude doplňovat hodnoty mezi rozd6lenými měsíci")
        exit(0)
    else:
        print("\n❌ ❌ ❌  NĚKTERÉ TESTY SELHALY  ❌ ❌ ❌")
        exit(1)
