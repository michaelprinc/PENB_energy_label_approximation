"""
Test dostupnosti historických dat z WeatherAPI
Tento skript testuje, zda free tier skutečně podporuje historická data
"""

from datetime import date, timedelta
from core.weather_api import fetch_hourly_weather
from core.config import get_api_key
import sys


def test_weather_history():
    """
    Testuje dostupnost historických dat pro různé časové úseky
    """
    print("="*70)
    print("TEST DOSTUPNOSTI HISTORICKÝCH DAT - WeatherAPI.com")
    print("="*70)
    
    # Získej API klíč
    api_key = get_api_key()
    if not api_key:
        print("\n❌ CHYBA: API klíč není nastaven!")
        print("   Nastavte jej ve Streamlit GUI nebo v storage/token_store.json")
        sys.exit(1)
    
    print(f"\n✅ API klíč načten (délka: {len(api_key)} znaků)")
    
    # Testovací lokace
    location = "Praha"
    print(f"📍 Testovací lokace: {location}")
    
    # Testovací scénáře
    today = date.today()
    
    test_scenarios = [
        ("Před 3 dny", today - timedelta(days=3), today - timedelta(days=3)),
        ("Před týdnem", today - timedelta(days=7), today - timedelta(days=7)),
        ("Před 14 dny", today - timedelta(days=14), today - timedelta(days=14)),
        ("Před měsícem", today - timedelta(days=30), today - timedelta(days=30)),
        ("Před 2 měsíci", today - timedelta(days=60), today - timedelta(days=60)),
        ("Před 3 měsíci", today - timedelta(days=90), today - timedelta(days=90)),
    ]
    
    print(f"\n📋 Budu testovat {len(test_scenarios)} scénářů:\n")
    
    results = []
    
    for name, start, end in test_scenarios:
        print(f"\n{'─'*70}")
        print(f"🧪 SCÉNÁŘ: {name}")
        print(f"   Datum: {start}")
        print(f"{'─'*70}")
        
        try:
            df = fetch_hourly_weather(location, start, end, api_key)
            
            if len(df) > 0:
                results.append((name, start, "✅ ÚSPĚCH", len(df)))
                print(f"\n✅ SUCCESS: Získáno {len(df)} hodin dat")
            else:
                results.append((name, start, "❌ SELHÁNÍ", 0))
                print(f"\n❌ FAIL: Žádná data nebyla získána")
                
        except Exception as e:
            results.append((name, start, "❌ CHYBA", 0))
            print(f"\n❌ EXCEPTION: {str(e)[:200]}")
    
    # Závěrečný report
    print(f"\n\n{'='*70}")
    print("📊 SOUHRNNÉ VÝSLEDKY")
    print(f"{'='*70}\n")
    
    print(f"{'Scénář':<20} {'Datum':<12} {'Status':<15} {'Hodin dat':<10}")
    print("─"*70)
    
    success_count = 0
    for name, start, status, hours in results:
        print(f"{name:<20} {str(start):<12} {status:<15} {hours:<10}")
        if "ÚSPĚCH" in status:
            success_count += 1
    
    print("─"*70)
    print(f"\n✅ Úspěšné: {success_count}/{len(test_scenarios)}")
    print(f"❌ Neúspěšné: {len(test_scenarios) - success_count}/{len(test_scenarios)}")
    
    # Interpretace
    print(f"\n{'='*70}")
    print("💡 INTERPRETACE")
    print(f"{'='*70}\n")
    
    if success_count == len(test_scenarios):
        print("🎉 VŠECHNY TESTY ÚSPĚŠNÉ!")
        print("   → Free tier WeatherAPI skutečně podporuje neomezená historická data")
    elif success_count == 0:
        print("❌ VŠECHNY TESTY SELHALY!")
        print("   → Free tier WeatherAPI NEsupportuje historická data")
        print("   → Nebo je problém s API klíčem / připojením")
    else:
        print("⚠️  ČÁSTEČNÝ ÚSPĚCH")
        print(f"   → Úspěšné: scénáře do {results[success_count-1][1]} dní zpět")
        print(f"   → Neúspěšné: starší data")
        print("   → Free tier má pravděpodobně časové omezení")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    test_weather_history()
