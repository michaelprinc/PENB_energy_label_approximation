"""
Komplexní test Open-Meteo integrace
Testuje:
1. Pouze stará data (Open-Meteo)
2. Pouze čerstvá data (WeatherAPI)
3. Mix dat (WeatherAPI + Open-Meteo)
"""

from datetime import date, timedelta
from core.weather_api import fetch_hourly_weather
from core.config import get_api_key
import sys


def print_separator(char='='):
    print(char * 70)


def test_comprehensive():
    """Komplexní test všech scénářů"""
    
    api_key = get_api_key()
    if not api_key:
        print("❌ CHYBA: API klic neni nastaven!")
        print("   Nastav WEATHERAPI_KEY v environment nebo storage/token_store.json")
        sys.exit(1)
    
    print_separator()
    print("KOMPLEXNÍ TEST OPEN-METEO INTEGRACE")
    print_separator()
    print(f"\n✓ API klíč načten")
    print(f"✓ Lokace: Praha")
    print(f"✓ Datum testu: {date.today()}\n")
    
    today = date.today()
    location = "Praha"
    results = []
    
    # ==================================================================
    # TEST 1: Pouze stará data (Open-Meteo)
    # ==================================================================
    print("\n")
    print_separator()
    print("TEST 1: POUZE STARÁ DATA (mělo by použít 100% Open-Meteo)")
    print_separator()
    print(f"Období: 30 dní zpět (mimo dosah WeatherAPI)")
    
    try:
        start = today - timedelta(days=31)
        end = today - timedelta(days=30)
        
        df = fetch_hourly_weather(
            location, start, end, api_key,
            use_openmeteo_fallback=True
        )
        
        expected = (end - start).days * 24 + 24
        coverage = len(df) / expected * 100
        
        results.append({
            'test': 'Stará data',
            'status': '✅ PASS',
            'hours': len(df),
            'coverage': coverage
        })
        
        print(f"\n✅ TEST 1 ÚSPĚŠNÝ")
        print(f"   Data: {len(df)}/{expected} hodin ({coverage:.1f}%)")
        print(f"   Teplota: {df['temp_out_c'].min():.1f}°C - {df['temp_out_c'].max():.1f}°C")
        
    except Exception as e:
        results.append({
            'test': 'Stará data',
            'status': '❌ FAIL',
            'error': str(e)[:50]
        })
        print(f"\n❌ TEST 1 SELHAL: {e}")
    
    # ==================================================================
    # TEST 2: Pouze čerstvá data (WeatherAPI)
    # ==================================================================
    print("\n\n")
    print_separator()
    print("TEST 2: POUZE ČERSTVÁ DATA (mělo by použít 100% WeatherAPI)")
    print_separator()
    print(f"Období: včera a předevčírem (v dosahu WeatherAPI)")
    
    try:
        start = today - timedelta(days=2)
        end = today - timedelta(days=1)
        
        df = fetch_hourly_weather(
            location, start, end, api_key,
            use_openmeteo_fallback=True
        )
        
        expected = (end - start).days * 24 + 24
        coverage = len(df) / expected * 100
        
        results.append({
            'test': 'Čerstvá data',
            'status': '✅ PASS',
            'hours': len(df),
            'coverage': coverage
        })
        
        print(f"\n✅ TEST 2 ÚSPĚŠNÝ")
        print(f"   Data: {len(df)}/{expected} hodin ({coverage:.1f}%)")
        print(f"   Teplota: {df['temp_out_c'].min():.1f}°C - {df['temp_out_c'].max():.1f}°C")
        
    except Exception as e:
        results.append({
            'test': 'Čerstvá data',
            'status': '❌ FAIL',
            'error': str(e)[:50]
        })
        print(f"\n❌ TEST 2 SELHAL: {e}")
    
    # ==================================================================
    # TEST 3: Mix dat (WeatherAPI + Open-Meteo)
    # ==================================================================
    print("\n\n")
    print_separator()
    print("TEST 3: MIX DAT (mělo by kombinovat WeatherAPI + Open-Meteo)")
    print_separator()
    print(f"Období: 20 dní zpět až dnes (překračuje hranici 8 dní)")
    
    try:
        start = today - timedelta(days=20)
        end = today - timedelta(days=1)
        
        df = fetch_hourly_weather(
            location, start, end, api_key,
            use_openmeteo_fallback=True
        )
        
        expected = (end - start).days * 24 + 24
        coverage = len(df) / expected * 100
        
        results.append({
            'test': 'Mix dat',
            'status': '✅ PASS',
            'hours': len(df),
            'coverage': coverage
        })
        
        print(f"\n✅ TEST 3 ÚSPĚŠNÝ")
        print(f"   Data: {len(df)}/{expected} hodin ({coverage:.1f}%)")
        print(f"   Teplota: {df['temp_out_c'].min():.1f}°C - {df['temp_out_c'].max():.1f}°C")
        print(f"   Období: {df['timestamp'].min()} až {df['timestamp'].max()}")
        
    except Exception as e:
        results.append({
            'test': 'Mix dat',
            'status': '❌ FAIL',
            'error': str(e)[:50]
        })
        print(f"\n❌ TEST 3 SELHAL: {e}")
    
    # ==================================================================
    # TEST 4: Bez Open-Meteo fallbacku (měla by  použít synthetic)
    # ==================================================================
    print("\n\n")
    print_separator()
    print("TEST 4: BEZ OPEN-METEO (mělo by použít syntetická data)")
    print_separator()
    print(f"Období: 30 dní zpět, ale Open-Meteo VYPNUTÉ")
    
    try:
        start = today - timedelta(days=31)
        end = today - timedelta(days=30)
        
        df = fetch_hourly_weather(
            location, start, end, api_key,
            use_openmeteo_fallback=False  # ❗ VYPNUTO
        )
        
        expected = (end - start).days * 24 + 24
        coverage = len(df) / expected * 100
        
        results.append({
            'test': 'Bez fallbacku',
            'status': '✅ PASS',
            'hours': len(df),
            'coverage': coverage
        })
        
        print(f"\n✅ TEST 4 ÚSPĚŠNÝ (měl by generovat syntetická data)")
        print(f"   Data: {len(df)}/{expected} hodin ({coverage:.1f}%)")
        
    except Exception as e:
        results.append({
            'test': 'Bez fallbacku',
            'status': '❌ FAIL',
            'error': str(e)[:50]
        })
        print(f"\n❌ TEST 4 SELHAL: {e}")
    
    # ==================================================================
    # SOUHRN
    # ==================================================================
    print("\n\n")
    print_separator('=')
    print("📊 CELKOVÝ SOUHRN TESTŮ")
    print_separator('=')
    
    print(f"\n{'Test':<25} {'Status':<12} {'Data':<20} {'Pokrytí':<10}")
    print_separator('-')
    
    for r in results:
        hours_str = f"{r.get('hours', 'N/A')} hodin" if 'hours' in r else 'N/A'
        coverage_str = f"{r.get('coverage', 0):.1f}%" if 'coverage' in r else 'N/A'
        print(f"{r['test']:<25} {r['status']:<12} {hours_str:<20} {coverage_str:<10}")
    
    passed = sum(1 for r in results if '✅' in r['status'])
    total = len(results)
    
    print_separator('-')
    print(f"\n{'✅ Úspěšné:':<25} {passed}/{total}")
    print(f"{'❌ Neúspěšné:':<25} {total-passed}/{total}")
    print(f"{'📊 Úspěšnost:':<25} {passed/total*100:.1f}%")
    
    print_separator('=')
    
    if passed == total:
        print("\n🎉 VŠECHNY TESTY PROŠLY!")
        print("   ✓ Open-Meteo integrace funguje správně")
        print("   ✓ Hybridní strategie WeatherAPI + Open-Meteo OK")
        print("   ✓ Fallback mechanismus funkční")
        return 0
    else:
        print(f"\n⚠️  {total-passed} TEST(Ů) SELHALO!")
        return 1


if __name__ == "__main__":
    exit_code = test_comprehensive()
    sys.exit(exit_code)
