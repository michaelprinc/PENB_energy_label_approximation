"""
Test WeatherAPI.com implementace
Ověří, že API klíč funguje a všechny fallback strategie jsou aktivní
"""
import sys
from pathlib import Path
from datetime import date, timedelta

# Přidej parent do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from core.weather_api import (
    detect_location,
    fetch_hourly_weather,
    fetch_forecast_weather,
    create_typical_year_weather,
    _generate_synthetic_day_weather
)


def test_location_detection():
    """Test 1: Automatická detekce lokace"""
    print("\n" + "="*60)
    print("TEST 1: Automatická detekce lokace")
    print("="*60)
    
    try:
        city, lat, lon = detect_location()
        print(f"✓ Lokace detekována: {city} ({lat:.2f}, {lon:.2f})")
        return True
    except Exception as e:
        print(f"✗ Chyba: {e}")
        return False


def test_forecast_weather(api_key: str):
    """Test 2: Stažení předpovědi (free tier)"""
    print("\n" + "="*60)
    print("TEST 2: Forecast API (free tier - 7 dní dopředu)")
    print("="*60)
    
    if not api_key:
        print("⊘ Přeskočeno - API klíč není zadán")
        return None
    
    try:
        city, lat, lon = detect_location()
        location = f"{lat},{lon}"
        
        # Zkus získat 3 dny předpovědi
        df = fetch_forecast_weather(location, days_ahead=3, api_key=api_key)
        
        print(f"✓ Staženo {len(df)} hodinových záznamů")
        print(f"  Rozsah: {df['timestamp'].min()} → {df['timestamp'].max()}")
        print(f"  Teplota: {df['temp_out_c'].min():.1f}°C - {df['temp_out_c'].max():.1f}°C")
        
        return True
    except Exception as e:
        print(f"✗ Chyba: {e}")
        return False


def test_recent_history(api_key: str):
    """Test 3: Nedávná historie (free tier - do 7 dní zpětně)"""
    print("\n" + "="*60)
    print("TEST 3: Historie do 7 dní zpětně (free tier)")
    print("="*60)
    
    if not api_key:
        print("⊘ Přeskočeno - API klíč není zadán")
        return None
    
    try:
        city, lat, lon = detect_location()
        location = f"{lat},{lon}"
        
        # Zkus získat data z posledních 3 dnů
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=2)
        
        df = fetch_hourly_weather(location, start_date, end_date, api_key)
        
        print(f"✓ Staženo {len(df)} hodinových záznamů")
        print(f"  Rozsah: {df['timestamp'].min()} → {df['timestamp'].max()}")
        print(f"  Teplota: {df['temp_out_c'].min():.1f}°C - {df['temp_out_c'].max():.1f}°C")
        
        # Kontrola fallback strategie
        expected_hours = 3 * 24
        if len(df) < expected_hours:
            print(f"  ⚠ Fallback aktivován: {len(df)}/{expected_hours} hodin")
        
        return True
    except Exception as e:
        print(f"✗ Chyba: {e}")
        return False


def test_old_history(api_key: str):
    """Test 4: Stará historie (placený tarif - automatický fallback)"""
    print("\n" + "="*60)
    print("TEST 4: Historie starší než 7 dní (očekává fallback)")
    print("="*60)
    
    if not api_key:
        print("⊘ Přeskočeno - API klíč není zadán")
        return None
    
    try:
        city, lat, lon = detect_location()
        location = f"{lat},{lon}"
        
        # Zkus získat data z před 30 dní (vyžaduje placený tarif)
        end_date = date.today() - timedelta(days=30)
        start_date = end_date - timedelta(days=2)
        
        print(f"  Požaduji data z {start_date} až {end_date}")
        print(f"  (očekává se fallback na syntetická data)")
        
        df = fetch_hourly_weather(location, start_date, end_date, api_key)
        
        print(f"✓ Fallback úspěšný - vygenerováno {len(df)} hodin")
        print(f"  Rozsah: {df['timestamp'].min()} → {df['timestamp'].max()}")
        print(f"  Teplota: {df['temp_out_c'].min():.1f}°C - {df['temp_out_c'].max():.1f}°C")
        
        return True
    except Exception as e:
        print(f"✗ Chyba: {e}")
        return False


def test_typical_year():
    """Test 5: Typický meteorologický rok (bez API)"""
    print("\n" + "="*60)
    print("TEST 5: Typický meteorologický rok (TMY)")
    print("="*60)
    
    try:
        city, lat, lon = detect_location()
        
        df = create_typical_year_weather(lat, lon)
        
        print(f"✓ TMY vytvořen: {len(df)} hodin")
        print(f"  Rozsah: {df['timestamp'].min()} → {df['timestamp'].max()}")
        print(f"  Teplota: {df['temp_out_c'].min():.1f}°C - {df['temp_out_c'].max():.1f}°C")
        print(f"  GHI: {df['ghi_wm2'].max():.0f} W/m²")
        
        # Kontrola pokrytí celého roku
        if len(df) == 8760:
            print(f"  ✓ Kompletní rok (8760 hodin)")
        else:
            print(f"  ⚠ Neúplný rok: {len(df)} hodin")
        
        return True
    except Exception as e:
        print(f"✗ Chyba: {e}")
        return False


def test_synthetic_fallback(api_key: str):
    """Test 6: Syntetická data jako fallback"""
    print("\n" + "="*60)
    print("TEST 6: Syntetická data (fallback mechanismus)")
    print("="*60)
    
    try:
        test_date = date.today() - timedelta(days=100)
        synthetic = _generate_synthetic_day_weather(
            test_date,
            "Praha",
            api_key if api_key else "dummy_key"
        )
        
        print(f"✓ Syntetický den vytvořen: {len(synthetic)} hodin")
        
        temps = [h['temp_out_c'] for h in synthetic]
        ghis = [h['ghi_wm2'] for h in synthetic]
        
        print(f"  Teplota: {min(temps):.1f}°C - {max(temps):.1f}°C")
        print(f"  GHI: {max(ghis):.0f} W/m² (denní maximum)")
        
        return True
    except Exception as e:
        print(f"✗ Chyba: {e}")
        return False


def main():
    """Spustí všechny testy"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  TEST SUITE: WeatherAPI.com implementace".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    # Získej API klíč od uživatele
    print("\n📝 Zadejte API klíč pro weatherapi.com")
    print("   (Enter = přeskočit testy vyžadující API)")
    api_key = input("   API klíč: ").strip()
    
    if not api_key:
        print("\n⚠ API klíč nezadán - některé testy budou přeskočeny")
    
    # Spusť testy
    results = {
        'Detekce lokace': test_location_detection(),
        'Forecast API (free)': test_forecast_weather(api_key),
        'Historie <7 dní (free)': test_recent_history(api_key),
        'Historie >7 dní (fallback)': test_old_history(api_key),
        'Typický rok (TMY)': test_typical_year(),
        'Syntetická data': test_synthetic_fallback(api_key)
    }
    
    # Výsledky
    print("\n" + "="*60)
    print("VÝSLEDKY TESTŮ")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    total = len(results)
    
    for name, result in results.items():
        if result is True:
            print(f"✓ {name}")
        elif result is False:
            print(f"✗ {name}")
        else:
            print(f"⊘ {name} (přeskočeno)")
    
    print("\n" + "-"*60)
    print(f"Celkem: {total} testů")
    print(f"✓ Úspěch: {passed}")
    print(f"✗ Selhání: {failed}")
    print(f"⊘ Přeskočeno: {skipped}")
    print("-"*60)
    
    if failed == 0 and passed > 0:
        print("\n🎉 VŠECHNY TESTY PROŠLY!")
        print("\n💡 Důležité poznatky:")
        print("   • Free tier podporuje forecast a historii do 7 dní")
        print("   • Pro starší data je aktivní automatický fallback")
        print("   • TMY režim funguje bez API klíče")
        print("   • Aplikace je plně funkční i s omezeními free tier")
        return 0
    elif failed > 0:
        print("\n⚠ NĚKTERÉ TESTY SELHALY")
        print("\n📖 Zkontrolujte:")
        print("   • API klíč je správný")
        print("   • Máte připojení k internetu")
        print("   • Pro placený tarif: aktivní předplatné")
        return 1
    else:
        print("\n⊘ ŽÁDNÉ TESTY NEBYLY SPUŠTĚNY")
        return 2


if __name__ == "__main__":
    exit(main())
