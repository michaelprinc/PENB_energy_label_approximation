"""
Open-Meteo Historical Weather API integrace
Fallback pro data starší než 8 dní (WeatherAPI limit)

API dokumentace: https://open-meteo.com/en/docs/historical-weather-api
Limit: 10,000 volání denně (zdarma, bez API klíče)
"""

import requests
from datetime import date, datetime, timedelta
from typing import List, Tuple
import pandas as pd
import numpy as np


def fetch_openmeteo_historical(
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date
) -> pd.DataFrame:
    """
    Stáhne historická data z Open-Meteo API.
    
    VÝHODY:
    - Zdarma, 10,000 volání/den
    - Bez API klíče
    - Data od 1940 do současnosti (s 5 dní zpožděním)
    - Vysoká přesnost (reanalysis data ERA5)
    
    Args:
        latitude: Zeměpisná šířka
        longitude: Zeměpisná délka
        start_date: Začátek období
        end_date: Konec období
    
    Returns:
        DataFrame s sloupci: timestamp, temp_out_c, humidity_pct, wind_mps, ghi_wm2
    """
    
    print(f"\n📡 Open-Meteo API: Stahuji data pro {latitude:.4f}, {longitude:.4f}")
    print(f"   Období: {start_date} až {end_date}")
    
    # Endpoint pro historická data
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    # Parametry podle dokumentace
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'hourly': [
            'temperature_2m',           # Teplota 2m nad zemí [°C]
            'relative_humidity_2m',     # Relativní vlhkost [%]
            'wind_speed_10m',           # Rychlost větru 10m [km/h]
            'shortwave_radiation',      # GHI - Global Horizontal Irradiation [W/m²]
        ],
        'timezone': 'auto',             # Automatická timezone podle souřadnic
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Parse odpověď
        hourly = data['hourly']
        times = hourly['time']
        
        # Vytvoř DataFrame
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(times),
            'temp_out_c': hourly['temperature_2m'],
            'humidity_pct': hourly['relative_humidity_2m'],
            'wind_kmh': hourly['wind_speed_10m'],
            'ghi_wm2': hourly['shortwave_radiation']
        })
        
        # Konverze km/h → m/s
        df['wind_mps'] = df['wind_kmh'] / 3.6
        df = df.drop('wind_kmh', axis=1)
        
        # Kontrola NaN hodnot
        nan_count = df.isna().sum().sum()
        if nan_count > 0:
            print(f"   ⚠️  Varování: {nan_count} NaN hodnot - doplněno interpolací")
            df = df.interpolate(method='linear', limit=3, limit_area='inside')
            df = df.bfill().ffill()
        
        print(f"   ✅ Úspěšně staženo: {len(df)} hodin")
        print(f"   📍 Skutečná poloha: {data['latitude']:.4f}, {data['longitude']:.4f}")
        print(f"   🏔️  Nadmořská výška: {data['elevation']:.1f} m")
        
        return df
        
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ HTTP chyba: {e}")
        raise
    except Exception as e:
        print(f"   ❌ Chyba: {e}")
        raise


def get_coordinates_for_location(location: str) -> Tuple[float, float]:
    """
    Převede název města nebo souřadnice na lat/lon.
    
    Args:
        location: Název města nebo "lat,lon"
    
    Returns:
        (latitude, longitude)
    """
    
    # Zkus parsovat jako souřadnice
    if ',' in location:
        try:
            parts = location.split(',')
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return lat, lon
        except:
            pass
    
    # Použij Open-Meteo Geocoding API (zdarma!)
    # https://open-meteo.com/en/docs/geocoding-api
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            'name': location,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'results' in data and len(data['results']) > 0:
            result = data['results'][0]
            lat = result['latitude']
            lon = result['longitude']
            
            print(f"   📍 Geocoding: {location} → {result['name']}, {result['country']}")
            print(f"   📍 Souřadnice: {lat:.4f}, {lon:.4f}")
            
            return lat, lon
        else:
            raise ValueError(f"Lokalita '{location}' nebyla nalezena")
            
    except Exception as e:
        print(f"   ⚠️  Chyba geocoding: {e}")
        # Fallback - Praha
        print(f"   ℹ️  Použita Praha jako fallback")
        return 50.0755, 14.4378


def test_openmeteo_availability(
    latitude: float,
    longitude: float,
    test_date: date
) -> bool:
    """
    Testuje, zda jsou data pro dané datum dostupná.
    
    Args:
        latitude: Zeměpisná šířka
        longitude: Zeměpisná délka
        test_date: Datum k testování
    
    Returns:
        True pokud jsou data dostupná
    """
    
    try:
        df = fetch_openmeteo_historical(
            latitude, longitude,
            test_date, test_date
        )
        return len(df) > 0
    except:
        return False


def fetch_with_fallback_strategy(
    location: str,
    start_date: date,
    end_date: date,
    weatherapi_key: str = None
) -> pd.DataFrame:
    """
    Kombinovaná strategie:
    1. WeatherAPI pro čerstvá data (0-8 dní)
    2. Open-Meteo pro starší data (9+ dní)
    
    Args:
        location: Město nebo souřadnice
        start_date: Začátek období
        end_date: Konec období
        weatherapi_key: API klíč pro WeatherAPI (optional)
    
    Returns:
        DataFrame se všemi daty
    """
    
    print(f"\n{'='*70}")
    print(f"HYBRIDNÍ SBĚR DAT: WeatherAPI + Open-Meteo")
    print(f"{'='*70}")
    
    all_data = []
    today = date.today()
    
    # Získej souřadnice
    lat, lon = get_coordinates_for_location(location)
    
    # Rozdělení na čerstvá vs. stará data
    current_date = start_date
    recent_dates = []
    old_dates = []
    
    while current_date <= end_date:
        days_back = (today - current_date).days
        
        if days_back <= 8:
            recent_dates.append(current_date)
        else:
            old_dates.append(current_date)
        
        current_date += timedelta(days=1)
    
    # 1. WeatherAPI pro čerstvá data
    if recent_dates and weatherapi_key:
        print(f"\n📊 Část 1: WeatherAPI ({len(recent_dates)} dní)")
        print(f"   Rozsah: {recent_dates[0]} až {recent_dates[-1]}")
        
        try:
            from core.weather_api import fetch_hourly_weather
            
            df_recent = fetch_hourly_weather(
                location,
                recent_dates[0],
                recent_dates[-1],
                weatherapi_key
            )
            all_data.append(df_recent)
            print(f"   ✅ WeatherAPI: {len(df_recent)} hodin")
            
        except Exception as e:
            print(f"   ⚠️  WeatherAPI selhalo: {e}")
            print(f"   ℹ️  Fallback na Open-Meteo i pro čerstvá data")
            
            if recent_dates:
                df_recent = fetch_openmeteo_historical(
                    lat, lon,
                    recent_dates[0],
                    recent_dates[-1]
                )
                all_data.append(df_recent)
    
    # 2. Open-Meteo pro stará data
    if old_dates:
        print(f"\n📊 Část 2: Open-Meteo ({len(old_dates)} dní)")
        print(f"   Rozsah: {old_dates[0]} až {old_dates[-1]}")
        
        # Open-Meteo má 5 dní zpožděním - zkontroluj
        oldest_available = today - timedelta(days=5)
        
        if old_dates[-1] > oldest_available:
            print(f"   ⚠️  Varování: Open-Meteo má 5 dní zpožd ění")
            print(f"   ℹ️  Nejnovější dostupné datum: {oldest_available}")
            
            # Filtruj jen dostupná data
            old_dates = [d for d in old_dates if d <= oldest_available]
        
        if old_dates:
            df_old = fetch_openmeteo_historical(
                lat, lon,
                old_dates[0],
                old_dates[-1]
            )
            all_data.append(df_old)
            print(f"   ✅ Open-Meteo: {len(df_old)} hodin")
    
    # Spojení dat
    if all_data:
        df_combined = pd.concat(all_data, ignore_index=True)
        df_combined = df_combined.sort_values('timestamp').reset_index(drop=True)
        
        print(f"\n{'='*70}")
        print(f"✅ CELKEM: {len(df_combined)} hodin")
        print(f"   Pokrytí: {df_combined['timestamp'].min()} až {df_combined['timestamp'].max()}")
        print(f"{'='*70}\n")
        
        return df_combined
    else:
        raise ValueError("Nepodařilo se získat žádná data!")


if __name__ == "__main__":
    # Test
    print("TEST Open-Meteo API\n")
    
    # Test 1: Základní stažení
    print("1. Test: Stažení historických dat")
    praha_lat, praha_lon = 50.0755, 14.4378
    test_date = date.today() - timedelta(days=30)
    
    df = fetch_openmeteo_historical(
        praha_lat, praha_lon,
        test_date, test_date
    )
    
    print(f"\nPrvních 5 řádků:")
    print(df.head())
    
    # Test 2: Geocoding
    print(f"\n2. Test: Geocoding")
    lat, lon = get_coordinates_for_location("London")
    print(f"   → {lat}, {lon}")
