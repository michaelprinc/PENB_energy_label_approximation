"""
Test Open-Meteo integrace s WeatherAPI fallback
"""

from datetime import date, timedelta
from core.weather_api import fetch_hourly_weather
from core.config import get_api_key
import sys


def test_hybrid_data_fetching():
    """
    Testuje hybridní strategii: WeatherAPI + Open-Meteo
    """
    print("="*70)
    print("TEST HYBRIDNÍ STRATEGIE: WeatherAPI + Open-Meteo")
    print("="*70)
    
    api_key = get_api_key()
    if not api_key:
        print("\nCHYBA: API klic neni nastaven!")
        sys.exit(1)
    
    print(f"\nOK: API klic nacten\n")
    
    # Test scénáře
    today = date.today()
    location = "Praha"
    
    scenarios = [
        {
            'name': "Jen čerstvá data (5 dní)",
            'start': today - timedelta(days=5),
            'end': today - timedelta(days=1),
            'expected_source': "WeatherAPI"
        },
        {
            'name': "Stará data (30 dní zpět)",
            'start': today - timedelta(days=30),
            'end': today - timedelta(days=25),
            'expected_source': "Open-Meteo"
        },
        {
            'name': "Mix (7 dní až 20 dní zpět)",
            'start': today - timedelta(days=20),
            'end': today - timedelta(days=7),
            'expected_source': "Mixed"
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n{'─'*70}")
        print(f"SCÉNÁŘ: {scenario['name']}")
        print(f"  Období: {scenario['start']} až {scenario['end']}")
        print(f"  Očekáváno: {scenario['expected_source']}")
        print(f"{'─'*70}")
        
        try:
            df = fetch_hourly_weather(
                location,
                scenario['start'],
                scenario['end'],
                api_key,
                use_openmeteo_fallback=True
            )
            
            expected_hours = (scenario['end'] - scenario['start']).days * 24 + 24
            actual_hours = len(df)
            coverage = actual_hours / expected_hours * 100
            
            results.append({
                'name': scenario['name'],
                'status': 'OK',
                'hours': actual_hours,
                'coverage': coverage
            })
            
            print(f"\n✅ SUCCESS:")
            print(f"   Získáno: {actual_hours}/{expected_hours} hodin ({coverage:.1f}%)")
            print(f"   Teplota range: {df['temp_out_c'].min():.1f}°C - {df['temp_out_c'].max():.1f}°C")
            print(f"   GHI range: {df['ghi_wm2'].min():.1f} - {df['ghi_wm2'].max():.1f} W/m²")
            
        except Exception as e:
            results.append({
                'name': scenario['name'],
                'status': 'FAIL',
                'hours': 0,
                'coverage': 0,
                'error': str(e)[:100]
            })
            
            print(f"\n❌ FAIL: {str(e)[:200]}")
    
    # Souhrn
    print(f"\n\n{'='*70}")
    print("📊 SOUHRN TESTŮ")
    print(f"{'='*70}\n")
    
    print(f"{'Scénář':<30} {'Status':<10} {'Pokrytí':<15}")
    print("─"*70)
    
    for r in results:
        status_mark = "✅" if r['status'] == 'OK' else "❌"
        coverage_str = f"{r['coverage']:.1f}%" if r['coverage'] > 0 else "N/A"
        print(f"{r['name']:<30} {status_mark} {r['status']:<8} {coverage_str:<15}")
    
    success_count = sum(1 for r in results if r['status'] == 'OK')
    print("─"*70)
    print(f"\n✅ Úspěšné: {success_count}/{len(results)}")
    print(f"❌ Neúspěšné: {len(results) - success_count}/{len(results)}")
    
    print(f"\n{'='*70}\n")


def test_openmeteo_standalone():
    """
    Test čistého Open-Meteo API (bez WeatherAPI)
    """
    print("="*70)
    print("TEST STANDALONE: Pouze Open-Meteo")
    print("="*70)
    
    try:
        from core.openmeteo_api import fetch_openmeteo_historical
        
        # Praha
        lat, lon = 50.0755, 14.4378
        test_date = date.today() - timedelta(days=30)
        
        print(f"\nTestuji Open-Meteo pro {test_date}...")
        
        df = fetch_openmeteo_historical(
            lat, lon,
            test_date,
            test_date
        )
        
        print(f"\n✅ SUCCESS: {len(df)} hodin")
        print(f"\nPrvních 5 hodin:")
        print(df.head())
        
        print(f"\nStatistiky:")
        print(df.describe())
        
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
    
    print(f"\n{'='*70}\n")


def test_fallback_behavior():
    """
    Test chování fallbacku při výpadku API
    """
    print("="*70)
    print("TEST FALLBACK: Chování při výpadku")
    print("="*70)
    
    api_key = get_api_key()
    if not api_key:
        return
    
    location = "Praha"
    start = date.today() - timedelta(days=15)
    end = date.today() - timedelta(days=10)
    
    print(f"\n1. Test: Se zapnutým Open-Meteo fallbackem")
    try:
        df1 = fetch_hourly_weather(
            location, start, end, api_key,
            use_openmeteo_fallback=True
        )
        print(f"   ✅ Získáno: {len(df1)} hodin")
    except Exception as e:
        print(f"   ❌ Chyba: {e}")
    
    print(f"\n2. Test: Bez Open-Meteo fallbacku (syntetická data)")
    try:
        df2 = fetch_hourly_weather(
            location, start, end, api_key,
            use_openmeteo_fallback=False
        )
        print(f"   ✅ Získáno: {len(df2)} hodin")
    except Exception as e:
        print(f"   ❌ Chyba: {e}")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    # Hlavní testy
    test_openmeteo_standalone()
    print("\n\n")
    test_hybrid_data_fetching()
    print("\n\n")
    test_fallback_behavior()
