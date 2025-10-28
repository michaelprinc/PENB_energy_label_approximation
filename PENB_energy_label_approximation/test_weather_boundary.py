"""
Detailni test pro zjisteni presne hranice dostupnosti historickych dat
"""

from datetime import date, timedelta
from core.weather_api import fetch_hourly_weather
from core.config import get_api_key
import sys
import io


def test_exact_boundary():
    """
    Zjisti presnou hranici dostupnosti historickych dat
    Testuje den po dni od dneska zpet
    """
    print("="*70)
    print("HLEDANI PRESNE HRANICE DOSTUPNOSTI HISTORICKYCH DAT")
    print("="*70)
    
    api_key = get_api_key()
    if not api_key:
        print("\nCHYBA: API klic neni nastaven!")
        sys.exit(1)
    
    print(f"\nOK: API klic nacten")
    
    location = "Praha"
    today = date.today()
    
    print(f"Lokace: {location}")
    print(f"Dnes: {today}\n")
    print("Testuji den po dni zpet, dokud nenajdu hranici...\n")
    print("-"*70)
    
    last_success = None
    first_failure = None
    
    # Testuj od 1 dne zpět až do 30 dní
    for days_back in range(1, 31):
        test_date = today - timedelta(days=days_back)
        
        try:
            # Zkrácený výpis
            print(f"Den -{days_back:2d} ({test_date}): ", end="", flush=True)
            
            df = fetch_hourly_weather(location, test_date, test_date, api_key)
            
            if len(df) > 0:
                print(f"OK ({len(df)} hodin)")
                last_success = (days_back, test_date)
            else:
                print(f"FAIL (0 hodin)")
                if first_failure is None:
                    first_failure = (days_back, test_date)
                
        except Exception as e:
            print(f"CHYBA")
            if first_failure is None:
                first_failure = (days_back, test_date)
    
    # Výsledek
    print("-"*70)
    print(f"\n{'='*70}")
    print("VYSLEDEK ANALYZY")
    print(f"{'='*70}\n")
    
    if last_success:
        print(f"Posledni uspesny den: {last_success[1]} (pred {last_success[0]} dny)")
    
    if first_failure:
        print(f"Prvni neuspesny den: {first_failure[1]} (pred {first_failure[0]} dny)")
    
    if last_success and first_failure:
        boundary = last_success[0]
        print(f"\n{'='*70}")
        print(f"ZJISTENA HRANICE: {boundary} DNU ZPET")
        print(f"{'='*70}\n")
        print(f"WeatherAPI.com free tier poskytuje historicka data")
        print(f"maximalne {boundary} dni zpetne od aktualniho data.")
        print(f"\nPro starsi data je nutny placeny tarif nebo pouziti")
        print(f"syntetickych/interpolovanych dat.")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    test_exact_boundary()
