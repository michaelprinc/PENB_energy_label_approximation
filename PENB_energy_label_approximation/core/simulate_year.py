"""
Simulace referenčního roku a výpočet roční potřeby tepla
"""
import pandas as pd
import numpy as np
from core.rc_model import RC1Model
from core.data_models import TemperatureProfile, CalibratedParameters


def simulate_annual_heating_demand(
    calibrated_params: CalibratedParameters,
    typical_year_weather: pd.DataFrame,
    geometry_volume_m3: float,
    geometry_area_m2: float,
    comfort_profile: TemperatureProfile
) -> pd.DataFrame:
    """
    Simuluje roční potřebu tepla s kalibrovaným modelem.
    
    Args:
        calibrated_params: kalibrované parametry
        typical_year_weather: DataFrame s typickým rokem (8760 hodin)
        geometry_volume_m3: objem bytu
        geometry_area_m2: plocha bytu
        comfort_profile: požadovaný teplotní profil
    
    Returns:
        DataFrame s hodinovou simulací + sloupcem heating_demand_W
    """
    print("\n=== Simulace referenčního roku ===")
    
    # Vytvoř model s kalibrovanými parametry
    model = RC1Model(
        H_env_W_per_K=calibrated_params.H_env_W_per_K,
        infiltration_rate_per_h=calibrated_params.infiltration_rate_per_h,
        volume_m3=geometry_volume_m3,
        C_th_J_per_K=calibrated_params.C_th_J_per_K,
        area_m2=geometry_area_m2,
        internal_gains_W_per_m2=calibrated_params.internal_gains_W_per_m2
    )
    
    # Připrav teplotní profil (den/noc)
    df = typical_year_weather.copy()
    
    # Urči setpoint podle hodiny (6-22 = den, jinak noc)
    hours = df['timestamp'].dt.hour
    df['T_setpoint_c'] = np.where(
        (hours >= 6) & (hours < 22),
        comfort_profile.day_temp_c,
        comfort_profile.night_temp_c
    )
    
    # Pro každou hodinu vypočti potřebné teplo
    heating_demands = []
    
    for idx, row in df.iterrows():
        T_setpoint = row['T_setpoint_c']
        T_out = row['temp_out_c']
        GHI = row.get('ghi_wm2', 0)
        
        Q_heat_needed = model.estimate_heating_demand(T_setpoint, T_out, GHI)
        heating_demands.append(Q_heat_needed)
    
    df['heating_demand_W'] = heating_demands
    
    # Statistika
    total_heating_Wh = df['heating_demand_W'].sum()
    total_heating_kWh = total_heating_Wh / 1000
    
    heating_per_m2 = total_heating_kWh / geometry_area_m2
    
    print(f"✓ Roční simulace dokončena:")
    print(f"  - Celková potřeba tepla: {total_heating_kWh:.0f} kWh/rok")
    print(f"  - Měrná potřeba: {heating_per_m2:.1f} kWh/(m²·rok)")
    
    return df


def calculate_primary_energy(
    heating_demand_kwh_per_year: float,
    system_type: str,
    efficiency_or_cop: float,
    primary_energy_factors: dict = None
) -> float:
    """
    Vypočítá orientační primární energii.
    
    Args:
        heating_demand_kwh_per_year: roční potřeba tepla
        system_type: typ systému ("condensing_boiler", "heat_pump_air", ...)
        efficiency_or_cop: účinnost nebo COP
        primary_energy_factors: faktory primární energie
    
    Returns:
        Primární energie kWh/rok
    """
    if primary_energy_factors is None:
        # Výchozí faktory (ČR orientačně)
        primary_energy_factors = {
            'electricity': 3.0,  # elektřina
            'natural_gas': 1.1,  # zemní plyn
        }
    
    # Podle typu systému
    if system_type in ['condensing_boiler']:
        # Plynový kotel
        fuel_consumption = heating_demand_kwh_per_year / efficiency_or_cop
        primary_energy = fuel_consumption * primary_energy_factors['natural_gas']
    
    elif system_type in ['heat_pump_air', 'heat_pump_water']:
        # Tepelné čerpadlo
        electricity_consumption = heating_demand_kwh_per_year / efficiency_or_cop
        primary_energy = electricity_consumption * primary_energy_factors['electricity']
    
    elif system_type == 'direct_electric':
        # Přímotop
        electricity_consumption = heating_demand_kwh_per_year / efficiency_or_cop
        primary_energy = electricity_consumption * primary_energy_factors['electricity']
    
    else:
        # Neznámý systém - použij průměr
        primary_energy = heating_demand_kwh_per_year * 2.0
    
    return primary_energy


def estimate_uncertainty_bounds(
    calibrated_params: CalibratedParameters,
    heating_demand_kwh_per_m2: float,
    data_quality_warnings: list
) -> tuple[float, float]:
    """
    Odhadne interval spolehlivosti (5% - 95%) pro výsledek.
    
    Založeno na:
    - RMSE a MAPE kalibrace
    - Počtu a závažnosti varování
    
    Returns:
        (lower_bound, upper_bound) v kWh/m²/rok
    """
    # Základní nejistota z kalibrace
    relative_uncertainty = calibrated_params.mape_energy_pct / 100
    
    # Přidej penalizaci za varování
    warning_penalty = len(data_quality_warnings) * 0.05
    
    total_uncertainty = relative_uncertainty + warning_penalty
    total_uncertainty = min(total_uncertainty, 0.5)  # max 50%
    
    lower = heating_demand_kwh_per_m2 * (1 - total_uncertainty)
    upper = heating_demand_kwh_per_m2 * (1 + total_uncertainty)
    
    return lower, upper
