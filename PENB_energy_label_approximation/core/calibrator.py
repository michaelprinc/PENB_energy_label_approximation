"""
Kalibrace parametrů RC modelu podle naměřených dat
"""
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Optional

import numpy as np
import pandas as pd
from scipy.optimize import minimize, differential_evolution

from core.rc_model import RC1Model, estimate_initial_parameters
from core.data_models import CalibratedParameters


def calibrate_model_simple(
    daily_energy_df: pd.DataFrame,
    hourly_weather_df: pd.DataFrame,
    geometry_volume_m3: float,
    geometry_area_m2: float,
    avg_indoor_temp: float,
    baseline_tuv_kwh: float,
    mode: str = "standard"
) -> CalibratedParameters:
    """
    Kalibruje parametry 1R1C modelu.
    
    Args:
        daily_energy_df: denní spotřeby s heating_kwh
        hourly_weather_df: hodinové počasí
        geometry_volume_m3: objem bytu
        geometry_area_m2: plocha bytu
        avg_indoor_temp: průměrná vnitřní teplota
        baseline_tuv_kwh: baseline TUV
        mode: "basic", "standard", nebo "advanced"
    
    Returns:
        CalibratedParameters
    """
    print("\n=== Kalibrace parametrů ===")
    
    # Počáteční odhad
    H_env_init, n_init, C_th_init = estimate_initial_parameters(
        daily_energy_df,
        hourly_weather_df,
        geometry_volume_m3,
        avg_indoor_temp
    )
    
    if mode == "basic":
        # BASIC: použij pouze lineární odhad, žádná optimalizace
        print("  Režim BASIC: používám hrubý lineární odhad")
        
        return CalibratedParameters(
            H_env_W_per_K=H_env_init,
            infiltration_rate_per_h=n_init,
            C_th_J_per_K=C_th_init,
            baseline_TUV_kwh_per_day=baseline_tuv_kwh,
            internal_gains_W_per_m2=3.0,
            rmse_temperature_c=999.0,  # neznámé
            mape_energy_pct=999.0
        )
    
    # STANDARD nebo ADVANCED: optimalizace
    
    # Připrav hodinová data s energií
    from core.baseline_split import distribute_daily_heating_to_hours
    
    hourly_with_energy = distribute_daily_heating_to_hours(
        daily_energy_df,
        hourly_weather_df,
        indoor_temp_c=avg_indoor_temp
    ).copy()
    
    # Připrav T_in (pokud nemáme skutečné, použijeme konstantu)
    if 'temp_in_c' not in hourly_with_energy.columns:
        hourly_with_energy['temp_in_c'] = avg_indoor_temp

    # Převeď hodinovou energii na střední výkon ve wattech (pro simulaci)
    hourly_with_energy['heating_power_W'] = (
        hourly_with_energy['heating_energy_kwh'] * 1000  # kWh → W (průměrný výkon za hodinu)
    )

    if hourly_with_energy.empty:
        raise ValueError("Hourly dataframe for calibration is empty; cannot calibrate model.")

    initial_indoor_temp = float(hourly_with_energy['temp_in_c'].iloc[0])
    
    # Funkce cost
    def cost_function(params):
        """
        Funkce nákladů: kombinace chyby teploty a energie.
        
        params: [H_env, n, log(C_th), q_int]
        """
        H_env = params[0]
        n = params[1]
        C_th = np.exp(params[2])  # log pro stabilitu
        q_int = params[3]
        
        # Vytvoř model
        model = RC1Model(
            H_env_W_per_K=H_env,
            infiltration_rate_per_h=n,
            volume_m3=geometry_volume_m3,
            C_th_J_per_K=C_th,
            area_m2=geometry_area_m2,
            internal_gains_W_per_m2=q_int
        )
        
        # Simuluj hodinový průběh
        simulated = model.simulate_hourly(
            initial_indoor_temp,
            hourly_with_energy,
            Q_heat_column='heating_power_W'
        )
        
        # Chyba teploty
        rmse_temp = np.sqrt(np.mean(
            (simulated['T_in_simulated_c'] - simulated['temp_in_c'])**2
        ))
        
        # Chyba denní energie
        # Seskup simulaci zpět na dny
        simulated['date'] = pd.to_datetime(simulated['timestamp'].dt.date)
        
        # Spočti potřebné teplo podle delta T
        simulated['Q_needed_W'] = model.H_total * np.maximum(
            simulated['T_in_simulated_c'] - simulated['temp_out_c'], 0
        )
        
        daily_sim = simulated.groupby('date')['Q_needed_W'].sum().reset_index()
        daily_sim['energy_sim_kwh'] = daily_sim['Q_needed_W'] / 1000  # W*h → kWh
        
        # Porovnej s pozorovanou
        merged_daily = daily_energy_df.merge(
            daily_sim[['date', 'energy_sim_kwh']], 
            on='date', 
            how='inner'
        )
        
        if len(merged_daily) > 0:
            mape_energy = np.mean(
                np.abs(merged_daily['heating_kwh'] - merged_daily['energy_sim_kwh']) / 
                (merged_daily['heating_kwh'] + 1e-6)
            ) * 100
        else:
            mape_energy = 100
        
        # Kombinovaná cost
        # Normalizuj RMSE (např. 1°C = 10% MAPE)
        cost = rmse_temp * 10 + mape_energy
        
        return cost
    
    # Počáteční parametry
    x0 = [
        H_env_init,
        n_init,
        np.log(C_th_init),
        3.0  # internal gains
    ]
    
    # Bounds
    bounds = [
        (10, 1000),      # H_env
        (0.05, 2.0),     # n
        (np.log(1e5), np.log(1e8)),  # log(C_th)
        (0, 10)          # q_int
    ]
    
    if mode == "advanced":
        # ADVANCED: použij differential evolution (globální optimalizace)
        print("  Režim ADVANCED: globální optimalizace...")
        cpu_count = os.cpu_count() or 2
        default_workers = max(1, cpu_count - 1)
        env_override = os.getenv("PENB_ADVANCED_THREADS")
        try:
            max_workers = max(1, int(env_override)) if env_override else default_workers
        except ValueError:
            max_workers = default_workers
        
        de_kwargs = dict(
            bounds=bounds,
            maxiter=100,
            popsize=10,
            seed=42,
            disp=False
        )
        
        if max_workers > 1:
            print(f"    * paralelní vyhodnocení ({max_workers} vláken)")
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                result = differential_evolution(
                    cost_function,
                    workers=executor.map,
                    updating='deferred',
                    **de_kwargs
                )
        else:
            result = differential_evolution(
                cost_function,
                **de_kwargs
            )
    else:
        # STANDARD: lokální optimalizace
        print("  Režim STANDARD: lokální optimalizace...")
        
        result = minimize(
            cost_function,
            x0,
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 100}
        )
    
    # Extrahuj výsledky
    H_env_opt = result.x[0]
    n_opt = result.x[1]
    C_th_opt = np.exp(result.x[2])
    q_int_opt = result.x[3]
    
    # Spočti finální metriky
    final_model = RC1Model(
        H_env_W_per_K=H_env_opt,
        infiltration_rate_per_h=n_opt,
        volume_m3=geometry_volume_m3,
        C_th_J_per_K=C_th_opt,
        area_m2=geometry_area_m2,
        internal_gains_W_per_m2=q_int_opt
    )
    
    final_sim = final_model.simulate_hourly(
        initial_indoor_temp,
        hourly_with_energy,
        Q_heat_column='heating_power_W'
    )
    
    rmse_final = np.sqrt(np.mean(
        (final_sim['T_in_simulated_c'] - final_sim['temp_in_c'])**2
    ))
    
    # MAPE energie
    final_sim['date'] = pd.to_datetime(final_sim['timestamp'].dt.date)
    final_sim['Q_needed_W'] = final_model.H_total * np.maximum(
        final_sim['T_in_simulated_c'] - final_sim['temp_out_c'], 0
    )
    
    daily_final = final_sim.groupby('date')['Q_needed_W'].sum().reset_index()
    daily_final['energy_sim_kwh'] = daily_final['Q_needed_W'] / 1000
    
    merged = daily_energy_df.merge(daily_final[['date', 'energy_sim_kwh']], on='date')
    
    mape_final = np.mean(
        np.abs(merged['heating_kwh'] - merged['energy_sim_kwh']) / 
        (merged['heating_kwh'] + 1e-6)
    ) * 100
    
    print(f"\n✓ Kalibrace dokončena:")
    print(f"  - H_env = {H_env_opt:.1f} W/K")
    print(f"  - Infiltrace = {n_opt:.3f} 1/h")
    print(f"  - C_th = {C_th_opt/1e6:.1f} MJ/K")
    print(f"  - Interní zisky = {q_int_opt:.1f} W/m²")
    print(f"  - RMSE teploty = {rmse_final:.2f} °C")
    print(f"  - MAPE energie = {mape_final:.1f} %")
    
    return CalibratedParameters(
        H_env_W_per_K=H_env_opt,
        infiltration_rate_per_h=n_opt,
        C_th_J_per_K=C_th_opt,
        baseline_TUV_kwh_per_day=baseline_tuv_kwh,
        internal_gains_W_per_m2=q_int_opt,
        rmse_temperature_c=rmse_final,
        mape_energy_pct=mape_final
    )
