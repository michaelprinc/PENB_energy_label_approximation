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
    
    KRITICKÉ: NESMÍ interpolovat mezi rozd6lenými měsíci!
    Pouze zpracovává skutečná data a krátké mezery (max 3 hodiny).
    
    Args:
        df: DataFrame s počasím (timestamp, temp_out_c, ...)
    
    Returns:
        Vyčištěný DataFrame - POUZE s daty která skutečně existují + krátké mezery
    """
    df = df.copy()
    
    # Ujisti se, že timestamp je datetime
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Seřaď podle času
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Odstraň duplikáty
    df = df.drop_duplicates(subset=['timestamp'], keep='first')
    
    # Set index pro časové operace
    df = df.set_index('timestamp')
    
    # KRITICKÁ ZMĚNA: Resample POUZE tam kde data existují
    # NESMÍ interpolovat dlouhé mezery (>3h)
    
    # Vytvoř kompletní hodinový index POUZE v rozsahu kde máme data
    min_time = df.index.min()
    max_time = df.index.max()
    
    # Kompletní hodinový rozsah
    full_hourly_range = pd.date_range(start=min_time, end=max_time, freq='h')
    
    # Reindex - toto vytvoří NaN pro chybějící hodiny
    df = df.reindex(full_hourly_range)
    
    # KLÍČOVÉ: Detekuj dlouhé mezery PŘED interpolací
    # Najdi všechny NaN segmenty
    is_missing = df['temp_out_c'].isna()
    
    # Označ změny (začátky a konce mezer)
    missing_changes = is_missing != is_missing.shift()
    missing_groups = missing_changes.cumsum()
    
    # Pro každou skupinu NaN zjisti délku
    for group_id in missing_groups[is_missing].unique():
        group_mask = (missing_groups == group_id) & is_missing
        gap_length = group_mask.sum()
        
        # Pokud je mezera > 3 hodiny, označ ji jako "dlouhá mezera" (neinterpolovat)
        if gap_length > 3:
            df.loc[group_mask, 'long_gap'] = True
    
    # KLÍČOVÉ: Interpoluj POUZE krátké mezery (max 3 hodiny)
    # limit_area='inside' zajistí že neinterpoluje na krajích datasetu
    if 'long_gap' not in df.columns:
        df['long_gap'] = False
    df['long_gap'] = df['long_gap'].fillna(False)
    
    # Interpoluj pouze tam, kde NENÍ dlouhá mezera
    mask_interpolate = is_missing & ~df['long_gap']
    
    if mask_interpolate.any():
        # Interpoluj pouze označená místa
        df_interpolated = df.interpolate(method='linear', limit=3, limit_area='inside')
        # Aplikuj interpolaci pouze na krátké mezery
        for col in ['temp_out_c', 'humidity_pct', 'wind_mps', 'ghi_wm2']:
            if col in df.columns:
                df.loc[mask_interpolate, col] = df_interpolated.loc[mask_interpolate, col]
    
    # Označení mezer
    missing_count = df['temp_out_c'].isna().sum()
    total_count = len(df)
    
    if missing_count > 0:
        missing_pct = missing_count / total_count * 100
        print(f"⚠ Chybí {missing_count} hodinových záznamů z {total_count} ({missing_pct:.1f}%)")
        print(f"  Tyto mezery NEBYLY interpolovány (>3h gap)")
    
    # Reset index
    df = df.reset_index()
    df.rename(columns={'index': 'timestamp'}, inplace=True)
    
    # DŮLEŽITÉ: Odstraň řádky kde je stále NaN (dlouhé mezery)
    rows_before = len(df)
    df = df.dropna(subset=['temp_out_c'])
    rows_after = len(df)
    
    # Odstraň pomocný sloupec
    if 'long_gap' in df.columns:
        df = df.drop(columns=['long_gap'])
    
    if rows_before != rows_after:
        print(f"✓ Odstraněno {rows_before - rows_after} hodin s dlouhými mezerami")
        print(f"  Zbývá {rows_after} hodin se skutečnými/interpolovanými daty")
    
    # Kontrola rozsahu hodnot
    if len(df) > 0:
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
    day_temp: Optional[float] = None,
    night_temp: Optional[float] = None,
    day_start_hour: int = 6,
    day_end_hour: int = 22,
    day_night_delta: float = 0.5
) -> pd.DataFrame:
    """
    Vytvoří pseudo-hodinovou vnitřní teplotu z denního průměru.
    
    Args:
        daily_avg_temp: průměrná vnitřní teplota °C (použije se pokud nejsou day_temp/night_temp)
        hourly_weather_df: DataFrame s časovými razítky
        day_temp: denní teplota °C (volitelné)
        night_temp: noční teplota °C (volitelné)
        day_start_hour: hodina začátku denního režimu (0-23)
        day_end_hour: hodina konce denního režimu (0-23)
        day_night_delta: rozdíl den/noc °C (použije se pouze pokud nejsou day_temp/night_temp)
    
    Returns:
        DataFrame s timestamp, temp_in_c
    """
    df = hourly_weather_df[['timestamp']].copy()
    hours = df['timestamp'].dt.hour
    
    if day_temp is not None and night_temp is not None:
        # Použij explicitní denní a noční teploty
        df['temp_in_c'] = night_temp  # Default = noční teplota
        
        # Denní režim: od day_start_hour do day_end_hour
        day_mask = (hours >= day_start_hour) & (hours < day_end_hour)
        df.loc[day_mask, 'temp_in_c'] = day_temp
        
        print(f"✓ Vytvořena hodinová T_in:")
        print(f"  - Den ({day_start_hour}:00-{day_end_hour}:00): {day_temp}°C")
        print(f"  - Noc: {night_temp}°C")
    else:
        # Staré chování: sinusoida s daily_avg_temp ± day_night_delta
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
