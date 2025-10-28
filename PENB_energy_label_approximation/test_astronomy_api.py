"""
Test WeatherAPI Astronomy API pro zlepseni syntetickych dat
"""

from core.config import get_api_key
import requests
from datetime import date, timedelta, datetime
import json


def test_astronomy_api():
    """
    Testuje Astronomy API pro různá data
    """
    print("="*70)
    print("TEST ASTRONOMY API")
    print("="*70)
    
    api_key = get_api_key()
    if not api_key:
        print("\nCHYBA: API klic neni nastaven!")
        return
    
    print(f"\nOK: API klic nacten\n")
    
    location = "Praha"
    today = date.today()
    
    # Test různých dat
    test_dates = [
        ("Dnes", today),
        ("Pred tydnem", today - timedelta(days=7)),
        ("Pred mesic", today - timedelta(days=30)),
        ("Pred 6 mesicu", today - timedelta(days=180)),
        ("Pred rok", today - timedelta(days=365)),
    ]
    
    results = []
    
    for name, test_date in test_dates:
        print(f"-"*70)
        print(f"TEST: {name} ({test_date})")
        print(f"-"*70)
        
        try:
            url = "http://api.weatherapi.com/v1/astronomy.json"
            params = {
                'key': api_key,
                'q': location,
                'dt': test_date.strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            astro = data['astronomy']['astro']
            
            print(f"\nOK: Data ziskana")
            print(f"  Vychod slunce: {astro['sunrise']}")
            print(f"  Zapad slunce:  {astro['sunset']}")
            print(f"  Vychod mesice: {astro['moonrise']}")
            print(f"  Zapad mesice:  {astro['moonset']}")
            print(f"  Faze mesice:   {astro['moon_phase']}")
            print(f"  Osvit mesice:  {astro['moon_illumination']}%")
            print(f"  Mesic nahore:  {'Ano' if astro['is_moon_up'] else 'Ne'}")
            print(f"  Slunce nahore: {'Ano' if astro['is_sun_up'] else 'Ne'}")
            
            results.append({
                'name': name,
                'date': test_date,
                'success': True,
                'sunrise': astro['sunrise'],
                'sunset': astro['sunset']
            })
            
        except Exception as e:
            print(f"\nCHYBA: {e}")
            results.append({
                'name': name,
                'date': test_date,
                'success': False
            })
    
    # Souhrn
    print(f"\n{'='*70}")
    print("SOUHRN DOSTUPNOSTI")
    print(f"{'='*70}\n")
    
    for r in results:
        status = "OK" if r['success'] else "FAIL"
        print(f"{r['name']:20} ({r['date']}) -> {status}")
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\nUspesnost: {success_count}/{len(results)}")
    
    print(f"\n{'='*70}\n")


def demo_astronomy_enhanced_synthetic():
    """
    Ukázka použití Astronomy API pro vylepšení syntetických dat
    """
    print("="*70)
    print("UKAZKA: ASTRONOMY-ENHANCED SYNTHETIC DATA")
    print("="*70)
    
    api_key = get_api_key()
    if not api_key:
        return
    
    location = "Praha"
    test_date = date.today() - timedelta(days=30)
    
    print(f"\nGeneruji synteticka data pro: {test_date}")
    print(f"Lokace: {location}\n")
    
    # 1. Získej astronomická data
    print("1. Ziskavam astronomicka data...")
    try:
        url = "http://api.weatherapi.com/v1/astronomy.json"
        params = {
            'key': api_key,
            'q': location,
            'dt': test_date.strftime('%Y-%m-%d')
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        astro = data['astronomy']['astro']
        
        sunrise = astro['sunrise']
        sunset = astro['sunset']
        
        print(f"   OK: Sunrise: {sunrise}, Sunset: {sunset}")
        
        # 2. Parsuj časy
        def parse_time(time_str):
            """Parse '06:45 AM' to hour"""
            time_obj = datetime.strptime(time_str, '%I:%M %p')
            return time_obj.hour + time_obj.minute / 60
        
        sunrise_hour = parse_time(sunrise)
        sunset_hour = parse_time(sunset)
        daylight_hours = sunset_hour - sunrise_hour
        
        print(f"\n2. Vypocitane parametry:")
        print(f"   Vychod slunce: {sunrise_hour:.2f}h")
        print(f"   Zapad slunce:  {sunset_hour:.2f}h")
        print(f"   Delka dne:     {daylight_hours:.2f}h")
        
        # 3. Generuj přesnější GHI
        print(f"\n3. Generovane hodinove GHI hodnoty:")
        print(f"   Hodina | GHI [W/m2] | Popis")
        print(f"   "+"─"*40)
        
        for hour in range(0, 24, 3):
            if hour < sunrise_hour or hour > sunset_hour:
                ghi = 0
                desc = "Noc"
            else:
                # Sinusoida mezi sunrise-sunset
                hour_in_day = hour - sunrise_hour
                fraction = hour_in_day / daylight_hours
                ghi = 600 * abs(1 - 2 * abs(fraction - 0.5))  # Peak v poledne
                desc = "Den"
            
            print(f"   {hour:2d}:00  | {ghi:7.1f}    | {desc}")
        
        print(f"\n   -> Presnejsi nez fixni 6:00-18:00!")
        
    except Exception as e:
        print(f"\nCHYBA: {e}")
    
    print(f"\n{'='*70}\n")


def test_timezone_api():
    """
    Test Timezone API
    """
    print("="*70)
    print("TEST TIMEZONE API")
    print("="*70)
    
    api_key = get_api_key()
    if not api_key:
        print("\nCHYBA: API klic neni nastaven!")
        return
    
    print(f"\nOK: API klic nacten\n")
    
    locations = ["Praha", "London", "New York", "Tokyo"]
    
    for location in locations:
        print(f"-"*70)
        print(f"Lokace: {location}")
        
        try:
            url = "http://api.weatherapi.com/v1/timezone.json"
            params = {
                'key': api_key,
                'q': location
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            loc = data['location']
            print(f"  Timezone ID:   {loc['tz_id']}")
            print(f"  Lokalni cas:   {loc['localtime']}")
            print(f"  GPS:           {loc['lat']}, {loc['lon']}")
            
        except Exception as e:
            print(f"  CHYBA: {e}")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    test_astronomy_api()
    print("\n\n")
    demo_astronomy_enhanced_synthetic()
    print("\n\n")
    test_timezone_api()
