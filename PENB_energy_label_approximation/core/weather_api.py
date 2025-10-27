"""
Práce s WeatherAPI.com a automatická detekce lokace
"""
import requests
from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple
import pandas as pd
import numpy as np
import geocoder


def detect_location() -> Tuple[str, float, float]:
    """
    Automaticky detekuje lokaci podle IP adresy počítače.
    
    Returns:
        (city_name, latitude, longitude)
    """
    try:
        # Použije geocoder pro detekci IP
        g = geocoder.ip('me')
        
        if g.ok:
            city = g.city or "Unknown"
            lat = g.lat
            lng = g.lng
            
            print(f"✓ Detekována lokace: {city} ({lat:.4f}, {lng:.4f})")
            return city, lat, lng
        else:
            # Fallback - Praha
            print("⚠ Nelze detekovat lokaci, použita Praha jako výchozí")
            return "Praha", 50.0755, 14.4378
            
    except Exception as e:
        print(f"⚠ Chyba při detekci lokace: {e}, použita Praha jako výchozí")
        return "Praha", 50.0755, 14.4378


def parse_location(location: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parsuje lokaci jako město nebo souřadnice.
    
    Args:
        location: buď "Praha" nebo "50.0755,14.4378"
    
    Returns:
        (latitude, longitude) pokud jsou souřadnice, jinak (None, None)
    """
    if ',' in location:
        try:
            parts = location.split(',')
            lat = float(parts[0].strip())
            lng = float(parts[1].strip())
            return lat, lng
        except:
            return None, None
    return None, None


def fetch_hourly_weather(
    location: str,
    start_date: date,
    end_date: date,
    api_key: str
) -> pd.DataFrame:
    """
    Stáhne hodinová data o počasí z weatherapi.com.
    
    Strategie:
    1. Pro data do 7 dní zpětně: zkusí forecast.json (free tier)
    2. Pro starší data: zkusí history.json (vyžaduje placený tarif)
    3. Pokud selže: vygeneruje syntetická data s varováním
    
    Args:
        location: město nebo "lat,lon"
        start_date: začátek období
        end_date: konec období
        api_key: API klíč pro weatherapi.com
    
    Returns:
        DataFrame s sloupci: timestamp, temp_out_c, humidity_pct, wind_mps, ghi_wm2
    """
    if not api_key:
        raise ValueError("API klíč pro weatherapi.com není nastaven!")
    
    print(f"\n📡 Stahuji počasí pro období {start_date} až {end_date}")
    
    all_data = []
    current_date = start_date
    today = date.today()
    
    # Kontrola, zda jsou data v dosahu free tier (7 dní zpětně)
    days_back = (today - start_date).days
    use_free_tier = days_back <= 7
    
    if use_free_tier:
        print(f"✓ Data jsou do 7 dní zpětně - použiji free tier forecast API")
    else:
        print(f"⚠ Data jsou {days_back} dní zpětně - vyžadují history API (placený)")
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        success = False
        
        # Strategie 1: Zkus forecast API pro nedávná data (free tier)
        if (today - current_date).days <= 7:
            try:
                url = "http://api.weatherapi.com/v1/forecast.json"
                params = {
                    'key': api_key,
                    'q': location,
                    'dt': date_str,
                    'aqi': 'no'
                }
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                # Zpracuj hodinová data
                for hour in data['forecast']['forecastday'][0]['hour']:
                    timestamp = datetime.fromisoformat(hour['time'].replace(' ', 'T'))
                    
                    all_data.append({
                        'timestamp': timestamp,
                        'temp_out_c': hour['temp_c'],
                        'humidity_pct': hour['humidity'],
                        'wind_mps': hour['wind_kph'] / 3.6,
                        'ghi_wm2': hour.get('uv', 0) * 25
                    })
                
                success = True
                print(f"  ✓ {date_str} (forecast API)")
                
            except Exception as e:
                print(f"  ⚠ Forecast API selhalo pro {date_str}: {e}")
        
        # Strategie 2: Zkus history API (placený tarif)
        if not success:
            try:
                url = "http://api.weatherapi.com/v1/history.json"
                params = {
                    'key': api_key,
                    'q': location,
                    'dt': date_str
                }
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                # Zpracuj hodinová data
                for hour in data['forecast']['forecastday'][0]['hour']:
                    timestamp = datetime.fromisoformat(hour['time'].replace(' ', 'T'))
                    
                    all_data.append({
                        'timestamp': timestamp,
                        'temp_out_c': hour['temp_c'],
                        'humidity_pct': hour['humidity'],
                        'wind_mps': hour['wind_kph'] / 3.6,
                        'ghi_wm2': hour.get('uv', 0) * 25
                    })
                
                success = True
                print(f"  ✓ {date_str} (history API)")
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 400:
                    # Pravděpodobně free tier - vygeneruj syntetická data
                    print(f"  ⚠ {date_str}: History API nedostupné (free tier)")
                elif e.response.status_code == 403:
                    print(f"  ⚠ {date_str}: Přístup odepřen - vyžaduje placený tarif")
                else:
                    print(f"  ⚠ {date_str}: HTTP {e.response.status_code}")
            except Exception as e:
                print(f"  ⚠ {date_str}: {e}")
        
        # Strategie 3: Vygeneruj syntetická data jako fallback
        if not success:
            print(f"  ⚙ {date_str}: Generuji syntetická data")
            synthetic_data = _generate_synthetic_day_weather(
                current_date, location, api_key
            )
            all_data.extend(synthetic_data)
        
        current_date += timedelta(days=1)
    
    if not all_data:
        raise ValueError(
            "Nepodařilo se získat žádná data o počasí!\n"
            "Zkontrolujte:\n"
            "1. API klíč je správný\n"
            "2. Máte aktivní připojení k internetu\n"
            "3. Pro historická data (>7 dní) potřebujete placený tarif"
        )
    
    df = pd.DataFrame(all_data)
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Kontrola pokrytí
    expected_hours = (end_date - start_date).days * 24 + 24
    actual_hours = len(df)
    coverage = actual_hours / expected_hours * 100
    
    print(f"\n✓ Staženo {actual_hours}/{expected_hours} hodin ({coverage:.1f}% pokrytí)")
    
    if coverage < 80:
        print(f"⚠ VAROVÁNÍ: Pouze {coverage:.1f}% dat - výsledky mohou být nepřesné")
    
    return df


def _generate_synthetic_day_weather(
    day: date,
    location: str,
    api_key: str
) -> List[dict]:
    """
    Vygeneruje syntetická hodinová data pro jeden den.
    Použije se jako fallback, když API není dostupné.
    """
    # Zkus získat aktuální teplotu pro lokalitu (jako baseline)
    try:
        url = "http://api.weatherapi.com/v1/current.json"
        params = {'key': api_key, 'q': location}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        base_temp = data['current']['temp_c']
    except:
        # Fallback podle měsíce (střední Evropa)
        month_temps = {
            1: -2, 2: 0, 3: 5, 4: 10, 5: 15, 6: 18,
            7: 20, 8: 20, 9: 16, 10: 10, 11: 4, 12: 0
        }
        base_temp = month_temps.get(day.month, 10)
    
    synthetic_hours = []
    
    for hour in range(24):
        timestamp = datetime.combine(day, datetime.min.time()) + timedelta(hours=hour)
        
        # Denní teplotní křivka
        temp_variation = 5 * np.sin(2 * np.pi * (hour - 6) / 24)
        temp = base_temp + temp_variation
        
        # Sluneční záření
        if 6 <= hour <= 18:
            ghi = 400 * np.sin(np.pi * (hour - 6) / 12)
        else:
            ghi = 0
        
        synthetic_hours.append({
            'timestamp': timestamp,
            'temp_out_c': temp,
            'humidity_pct': 70.0,
            'wind_mps': 2.0,
            'ghi_wm2': max(0, ghi)
        })
    
    return synthetic_hours


def fetch_forecast_weather(
    location: str,
    days_ahead: int,
    api_key: str
) -> pd.DataFrame:
    """
    Stáhne předpověď počasí (pro budoucí simulace).
    
    Args:
        location: město nebo "lat,lon"
        days_ahead: počet dní dopředu (max 14 ve free verzi)
        api_key: API klíč
    
    Returns:
        DataFrame s hodinovými daty
    """
    if not api_key:
        raise ValueError("API klíč není nastaven!")
    
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        'key': api_key,
        'q': location,
        'days': min(days_ahead, 14),  # API limit
        'aqi': 'no'
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    all_data = []
    for day in data['forecast']['forecastday']:
        for hour in day['hour']:
            timestamp = datetime.fromisoformat(hour['time'].replace(' ', 'T'))
            
            all_data.append({
                'timestamp': timestamp,
                'temp_out_c': hour['temp_c'],
                'humidity_pct': hour['humidity'],
                'wind_mps': hour['wind_kph'] / 3.6,
                'ghi_wm2': hour.get('uv', 0) * 25
            })
    
    df = pd.DataFrame(all_data)
    return df


def create_typical_year_weather(location: str, api_key: str) -> pd.DataFrame:
    """
    Vytvoří typický meteorologický rok (TMY) pro danou lokalitu.
    
    V MVP verzi použijeme jednoduchou aproximaci:
    - Stáhneme aktuální předpověď
    - Extrapolujeme na celý rok podle průměrných hodnot
    
    Pro produkční verzi by se použil skutečný TMY dataset.
    
    Args:
        location: lokalita
        api_key: API klíč
    
    Returns:
        DataFrame s hodinovými daty pro celý rok (8760 hodin)
    """
    # V MVP verzi vytvoříme sinusoidní approximaci teploty
    print("⚠ MVP: Používám zjednodušený typický rok (sinusoida)")
    
    # Detekuj lokaci pro získání průměrné teploty
    try:
        lat, lng = parse_location(location)
        if lat is None:
            # Je to město, zkus stáhnout aktuální počasí
            url = "http://api.weatherapi.com/v1/current.json"
            params = {'key': api_key, 'q': location}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            avg_temp = data['current']['temp_c']
        else:
            # Odhadni podle latitude (velmi hrubé)
            avg_temp = 20 - abs(lat) * 0.5
    except:
        avg_temp = 10  # Střední Evropa default
    
    # Vytvoř hodinová data pro rok
    start = datetime(2024, 1, 1, 0, 0, 0)
    hours = []
    
    for h in range(8760):  # 365 * 24
        timestamp = start + timedelta(hours=h)
        day_of_year = timestamp.timetuple().tm_yday
        hour_of_day = timestamp.hour
        
        # Sinusoida - roční variace
        temp_seasonal = avg_temp + 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Denní variace
        temp_daily = temp_seasonal + 3 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)
        
        # Sluneční záření (hrubý odhad)
        if 6 <= hour_of_day <= 18:
            ghi = 500 * np.sin(np.pi * (hour_of_day - 6) / 12) * (1 + 0.5 * np.sin(2 * np.pi * day_of_year / 365))
        else:
            ghi = 0
        
        hours.append({
            'timestamp': timestamp,
            'temp_out_c': temp_daily,
            'humidity_pct': 70.0,
            'wind_mps': 2.5,
            'ghi_wm2': max(0, ghi)
        })
    
    df = pd.DataFrame(hours)
    print(f"✓ Vytvořen typický rok: {len(df)} hodin")
    
    return df
