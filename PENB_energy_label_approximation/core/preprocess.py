"""
Preprocessing dat - čištění, resampling, kontrola kvality
"""
import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
from datetime import datetime, timedelta


def clean_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Vyčistí a zkontroluje data o počasí.
    
    Args:
        df: DataFrame s počasím (timestamp, temp_out_c, ...)
    
    Returns:
        Vyčištěný DataFrame
    """
    df = df.copy()
    
    # Ujisti se, že timestamp je datetime
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Seřaď podle času
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Odstraň duplikáty
    df = df.drop_duplicates(subset=['timestamp'], keep='first')
    
    # Interpoluj chybějící hodnoty (pokud jsou krátké mezery)
    df = df.set_index('timestamp')
    df = df.resample('1H').mean()  # Resample na hodiny
    
    # Interpoluj krátké mezery (max 3 hodiny)
    df = df.interpolate(method='linear', limit=3)
    
    # Označ dlouhé mezery
    missing_before = df['temp_out_c'].isna().sum()
    if missing_before > 0:
        print(f"⚠ Chybí {missing_before} hodinových záznamů (z {len(df)})")
    
    # Doplň zbylé chybějící hodnoty forward/backward fill
    df = df.fillna(method='ffill', limit=6)
    df = df.fillna(method='bfill', limit=6)
    
    df = df.reset_index()
    
    # Kontrola rozsahu hodnot
    if df['temp_out_c'].min() < -40 or df['temp_out_c'].max() > 50:
        print("⚠ Podezřelé venkovní teploty mimo rozsah -40°C až 50°C")
    
    return df


def align_daily_energy_to_hourly(
    daily_energy_df: pd.DataFrame,
    hourly_weather_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Zarovná denní spotřeby s hodinovými daty počasí.
    
    Args:
        daily_energy_df: DataFrame s date, energy_total_kwh
        hourly_weather_df: DataFrame s timestamp, temp_out_c, ...
    
    Returns:
        (aligned_daily_df, aligned_hourly_df) - společné časové rozmezí
    """
    # Ujisti se, že date je datetime
    if not pd.api.types.is_datetime64_any_dtype(daily_energy_df['date']):
        daily_energy_df['date'] = pd.to_datetime(daily_energy_df['date'])
    
    # Najdi společný rozsah
    min_date = daily_energy_df['date'].min()
    max_date = daily_energy_df['date'].max()
    
    # Filtruj hodinová data na tento rozsah
    hourly_weather_df = hourly_weather_df[
        (hourly_weather_df['timestamp'].dt.date >= min_date.date()) &
        (hourly_weather_df['timestamp'].dt.date <= max_date.date())
    ].copy()
    
    print(f"✓ Zarovnáno na období {min_date.date()} až {max_date.date()}")
    print(f"  - {len(daily_energy_df)} denních záznamů")
    print(f"  - {len(hourly_weather_df)} hodinových záznamů")
    
    return daily_energy_df, hourly_weather_df


def create_hourly_indoor_temp(
    daily_avg_temp: float,
    hourly_weather_df: pd.DataFrame,
    day_night_delta: float = 0.5
) -> pd.DataFrame:
    """
    Vytvoří pseudo-hodinovou vnitřní teplotu z denního průměru.
    
    Args:
        daily_avg_temp: průměrná vnitřní teplota °C
        hourly_weather_df: DataFrame s časovými razítky
        day_night_delta: rozdíl den/noc °C
    
    Returns:
        DataFrame s timestamp, temp_in_c
    """
    df = hourly_weather_df[['timestamp']].copy()
    
    # Denní variace (jednoduchá sinusoida)
    hours = df['timestamp'].dt.hour
    
    # Maximum ve 14:00, minimum ve 2:00
    temp_variation = day_night_delta * np.sin(2 * np.pi * (hours - 2) / 24)
    
    df['temp_in_c'] = daily_avg_temp + temp_variation
    
    print(f"✓ Vytvořena pseudo-hodinová T_in (průměr {daily_avg_temp}°C, ±{day_night_delta}°C)")
    
    return df


def merge_hourly_data(
    weather_df: pd.DataFrame,
    indoor_temp_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Sloučí hodinová data do jednoho DataFrame.
    
    Args:
        weather_df: venkovní počasí
        indoor_temp_df: vnitřní teploty (volitelné)
    
    Returns:
        Sloučený DataFrame
    """
    df = weather_df.copy()
    
    if indoor_temp_df is not None:
        df = df.merge(indoor_temp_df, on='timestamp', how='left')
    
    return df


def validate_data_quality(
    daily_energy_df: pd.DataFrame,
    hourly_df: pd.DataFrame
) -> List[str]:
    """
    Zkontroluje kvalitu vstupních dat a vrátí seznam varování.
    
    Returns:
        Seznam varování/problémů
    """
    warnings = []
    
    # Počet dní
    n_days = len(daily_energy_df)
    if n_days < 7:
        warnings.append(f"Málo dat: pouze {n_days} dní (doporučeno min. 7)")
    
    # Chybějící hodinová data
    expected_hours = n_days * 24
    actual_hours = len(hourly_df)
    missing_pct = (expected_hours - actual_hours) / expected_hours * 100
    
    if missing_pct > 5:
        warnings.append(f"Chybí {missing_pct:.1f}% hodinových dat")
    
    # Konstantní spotřeba (podezřelé)
    if daily_energy_df['energy_total_kwh'].std() < 0.1:
        warnings.append("Podezřele konstantní spotřeba (možná chyba v datech)")
    
    # Nulové spotřeby
    zero_days = (daily_energy_df['energy_total_kwh'] == 0).sum()
    if zero_days > 0:
        warnings.append(f"{zero_days} dní s nulovou spotřebou")
    
    # Velké výkyvy
    mean_energy = daily_energy_df['energy_total_kwh'].mean()
    max_energy = daily_energy_df['energy_total_kwh'].max()
    
    if max_energy > mean_energy * 3:
        warnings.append("Extrémní výkyvy ve spotřebě (možná chyba v odečtu)")
    
    # Kontrola teplot
    if 'temp_in_c' in hourly_df.columns:
        avg_in = hourly_df['temp_in_c'].mean()
        if avg_in < 15 or avg_in > 28:
            warnings.append(f"Neobvyklá průměrná T_in: {avg_in:.1f}°C")
    
    avg_out = hourly_df['temp_out_c'].mean()
    if avg_out < -20 or avg_out > 35:
        warnings.append(f"Extrémní průměrná T_out: {avg_out:.1f}°C")
    
    if warnings:
        print(f"⚠ Zjištěno {len(warnings)} varování:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("✓ Data prošla kontrolou kvality")
    
    return warnings
