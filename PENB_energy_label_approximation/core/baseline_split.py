"""
Rozdělení denní spotřeby na vytápění vs. TUV (teplá užitková voda)
"""
import pandas as pd
import numpy as np
from typing import Tuple, Optional


def estimate_baseline_tuv(daily_energy_df: pd.DataFrame, percentile: float = 10.0) -> float:
    """
    Odhadne baseline spotřebu TUV jako percentil nejnižších spotřeb.
    
    Předpoklad: dny s minimální spotřebou = pouze TUV + ztráty systému,
    téměř žádné vytápění.
    
    Args:
        daily_energy_df: DataFrame s energy_total_kwh
        percentile: percentil pro baseline (default 10%)
    
    Returns:
        Baseline spotřeba TUV v kWh/den
    """
    baseline = np.percentile(daily_energy_df['energy_total_kwh'], percentile)
    
    # Sanity check - baseline by neměl být záporný ani příliš vysoký
    mean_energy = daily_energy_df['energy_total_kwh'].mean()
    
    if baseline < 0:
        baseline = 0
    elif baseline > mean_energy * 0.5:
        # Baseline je víc než polovina průměru - pravděpodobně není období bez topení
        print(f"⚠ Vysoký baseline ({baseline:.1f} kWh/den), možná chybí data z léta")
        baseline = mean_energy * 0.3  # Odhad
    
    print(f"✓ Odhadnutý baseline TUV: {baseline:.2f} kWh/den")
    
    return baseline


def split_heating_and_tuv(
    daily_energy_df: pd.DataFrame,
    baseline_tuv_kwh: Optional[float] = None
) -> pd.DataFrame:
    """
    Rozdělí denní spotřebu na vytápění a TUV.
    
    Args:
        daily_energy_df: DataFrame s date, energy_total_kwh
        baseline_tuv_kwh: baseline TUV (pokud None, odhadne se)
    
    Returns:
        DataFrame s přidanými sloupci: baseline_tuv_kwh, heating_kwh
    """
    df = daily_energy_df.copy()
    
    if baseline_tuv_kwh is None:
        baseline_tuv_kwh = estimate_baseline_tuv(df)
    
    # Vytápění = celková spotřeba - baseline
    df['baseline_tuv_kwh'] = baseline_tuv_kwh
    df['heating_kwh'] = np.maximum(df['energy_total_kwh'] - baseline_tuv_kwh, 0)
    
    # Statistika
    total_energy = df['energy_total_kwh'].sum()
    total_heating = df['heating_kwh'].sum()
    total_tuv = total_energy - total_heating
    
    heating_pct = (total_heating / total_energy * 100) if total_energy > 0 else 0
    
    print(f"✓ Rozdělení spotřeby:")
    print(f"  - Vytápění: {total_heating:.1f} kWh ({heating_pct:.1f}%)")
    print(f"  - TUV+ztráty: {total_tuv:.1f} kWh ({100-heating_pct:.1f}%)")
    
    return df


def distribute_daily_heating_to_hours(
    daily_heating_df: pd.DataFrame,
    hourly_weather_df: pd.DataFrame,
    indoor_temp_c: float = 21.0
) -> pd.DataFrame:
    """
    Rozloží denní vytápěcí energii do hodin podle tepelné potřeby.
    
    Jednoduché rozdělení proporcionálně k (T_in - T_out)+.
    
    Args:
        daily_heating_df: DataFrame s date, heating_kwh
        hourly_weather_df: DataFrame s timestamp, temp_out_c
        indoor_temp_c: požadovaná vnitřní teplota
    
    Returns:
        DataFrame s timestamp, heating_power_estimate_kw (rozložená energie)
    """
    # Připrav denní lookup
    daily_lookup = {}
    for _, row in daily_heating_df.iterrows():
        # Zajisti, že date je porovnatelný jako date object
        date_key = row['date'].date() if hasattr(row['date'], 'date') else row['date']
        daily_lookup[date_key] = row['heating_kwh']
    
    # Pro každou hodinu vypočti tepelnou potřebu
    hourly_df = hourly_weather_df.copy()
    hourly_df['date'] = hourly_df['timestamp'].dt.date
    hourly_df['heating_day_total_kwh'] = hourly_df['date'].map(daily_lookup)
    
    # Delta teploty (pozitivní = potřeba topení)
    hourly_df['delta_t'] = np.maximum(indoor_temp_c - hourly_df['temp_out_c'], 0)
    
    # Seskup podle dne a vypočti podíl každé hodiny
    def distribute_day(group):
        total_delta = group['delta_t'].sum()
        
        if total_delta > 0:
            group['hour_share'] = group['delta_t'] / total_delta
        else:
            # Žádná potřeba topení - rovnoměrně rozděl (např. losses)
            group['hour_share'] = 1.0 / len(group)
        
        # Energie této hodiny
        day_total = group['heating_day_total_kwh'].iloc[0]
        group['heating_energy_kwh'] = group['hour_share'] * day_total
        
        return group
    
    hourly_df = hourly_df.groupby('date', group_keys=False).apply(distribute_day)
    
    # Kontrola konzistence
    reconstructed_daily = hourly_df.groupby('date')['heating_energy_kwh'].sum()
    original_daily = daily_heating_df.set_index('date')['heating_kwh']
    
    diff = (reconstructed_daily - original_daily).abs().mean()
    if diff > 0.01:
        print(f"⚠ Rekonstrukce denní energie má odchylku {diff:.4f} kWh")
    else:
        print(f"✓ Denní energie úspěšně rozložena do hodin")
    
    return hourly_df[['timestamp', 'temp_out_c', 'heating_energy_kwh']]

