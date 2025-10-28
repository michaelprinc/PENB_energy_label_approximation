"""
Jednoduchý test hybridní strategie
"""

from datetime import date, timedelta
from core.weather_api import fetch_hourly_weather
from core.config import get_api_key


def test_simple_hybrid():
    """Test základní funkcionality"""
    
    api_key = get_api_key()
    if not api_key:
        print("CHYBA: API klic neni nastaven!")
        return
    
    print("="*70)
    print("JEDNODUCHÝ TEST HYBRIDNÍ STRATEGIE")
    print("="*70)
    
    # Test 1: Jen stará data (Open-Meteo)
    print("\n\nTEST 1: Stará data (30 dní zpět, mělo by použít Open-Meteo)")
    print("-"*70)
    
    today = date.today()
    start = today - timedelta(days=31)
    end = today - timedelta(days=30)
    
    try:
        df = fetch_hourly_weather(
            "Praha",
            start,
            end,
            api_key,
            use_openmeteo_fallback=True
        )
        
        print(f"\n✅ SUCCESS: {len(df)} hodin")
        print(f"\nPrvních 5 hodin:")
        print(df.head())
        
    except Exception as e:
        print(f"\n❌ CHYBA: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_simple_hybrid()
