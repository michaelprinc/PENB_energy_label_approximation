"""
RC model budovy (1R1C - jednoduchá tepelná kapacita + odpor)

Fyzikální model:
- Jedna tepelná kapacita C_th reprezentující tepelnou setrvačnost budovy
- Jeden tepelný odpor R = 1/H_env reprezentující tepelné ztráty obálkou
- Větrací ztráty H_vent = rho * c_p * n * V
"""
import numpy as np
from typing import Tuple, Optional
import pandas as pd


# Fyzikální konstanty
RHO_AIR = 1.2  # kg/m³ (hustota vzduchu)
CP_AIR = 1005  # J/(kg·K) (měrné teplo vzduchu)


class RC1Model:
    """
    Jednoduchý 1R1C model budovy.
    
    Diferenciální rovnice:
    C_th * dT_in/dt = Q_heat + Q_solar + Q_internal - H_total * (T_in - T_out)
    
    Kde:
    - H_total = H_env + H_vent (celkové tepelné ztráty)
    - Q_heat = dodané teplo z topení [W]
    - Q_solar = sluneční zisky [W]
    - Q_internal = interní zisky (lidé, spotřebiče) [W]
    """
    
    def __init__(
        self,
        H_env_W_per_K: float,
        infiltration_rate_per_h: float,
        volume_m3: float,
        C_th_J_per_K: float,
        area_m2: float,
        internal_gains_W_per_m2: float = 3.0,
        solar_aperture: float = 0.02  # typicky malé pro byty
    ):
        """
        Args:
            H_env_W_per_K: tepelné ztráty obálkou
            infiltration_rate_per_h: intenzita infiltrace
            volume_m3: objem bytu
            C_th_J_per_K: tepelná kapacita
            area_m2: plocha bytu
            internal_gains_W_per_m2: interní zisky na m²
            solar_aperture: efektivní plocha pro sluneční zisky (fraction)
        """
        self.H_env = H_env_W_per_K
        self.n = infiltration_rate_per_h
        self.V = volume_m3
        self.C_th = C_th_J_per_K
        self.A = area_m2
        self.q_int = internal_gains_W_per_m2
        self.solar_ap = solar_aperture
        
        # Vypočti H_vent
        self.H_vent = RHO_AIR * CP_AIR * self.n * self.V / 3600  # /3600 pro převod 1/h na 1/s
        self.H_total = self.H_env + self.H_vent
    
    def simulate_step(
        self,
        T_in_prev: float,
        T_out: float,
        Q_heat_W: float,
        GHI_W_per_m2: float,
        dt_seconds: float = 3600
    ) -> float:
        """
        Simuluj jeden časový krok (Euler forward).
        
        Args:
            T_in_prev: vnitřní teplota na začátku kroku [°C]
            T_out: venkovní teplota [°C]
            Q_heat_W: dodané teplo z topení [W]
            GHI_W_per_m2: globální sluneční záření [W/m²]
            dt_seconds: časový krok v sekundách
        
        Returns:
            Nová vnitřní teplota [°C]
        """
        # Sluneční zisky
        Q_solar = GHI_W_per_m2 * self.A * self.solar_ap
        
        # Interní zisky
        Q_internal = self.q_int * self.A
        
        # Tepelná bilance
        Q_in = Q_heat_W + Q_solar + Q_internal
        Q_out = self.H_total * (T_in_prev - T_out)
        
        # dT/dt
        dT_dt = (Q_in - Q_out) / self.C_th
        
        # Nová teplota
        T_in_new = T_in_prev + dT_dt * dt_seconds
        
        return T_in_new
    
    def simulate_hourly(
        self,
        T_in_initial: float,
        hourly_df: pd.DataFrame,
        Q_heat_column: str = 'heating_power_W'
    ) -> pd.DataFrame:
        """
        Simuluj hodinový průběh.
        
        Args:
            T_in_initial: počáteční vnitřní teplota
            hourly_df: DataFrame s temp_out_c, heating_power_W, ghi_wm2
            Q_heat_column: název sloupce s topným výkonem
        
        Returns:
            DataFrame s přidaným sloupcem T_in_simulated_c
        """
        df = hourly_df.copy()
        
        T_in = T_in_initial
        T_in_values = []
        
        for idx, row in df.iterrows():
            T_out = row['temp_out_c']
            Q_heat = row.get(Q_heat_column, 0) * 1000  # kW → W
            GHI = row.get('ghi_wm2', 0)
            
            T_in = self.simulate_step(T_in, T_out, Q_heat, GHI, dt_seconds=3600)
            T_in_values.append(T_in)
        
        df['T_in_simulated_c'] = T_in_values
        
        return df
    
    def estimate_heating_demand(
        self,
        T_in_setpoint: float,
        T_out: float,
        GHI_W_per_m2: float = 0
    ) -> float:
        """
        Odhadne potřebný topný výkon pro udržení T_in = T_in_setpoint.
        
        Při ustáleném stavu: Q_heat = H_total * (T_in - T_out) - Q_solar - Q_internal
        
        Returns:
            Potřebný výkon [W]
        """
        Q_solar = GHI_W_per_m2 * self.A * self.solar_ap
        Q_internal = self.q_int * self.A
        
        Q_heat = self.H_total * (T_in_setpoint - T_out) - Q_solar - Q_internal
        
        return max(0, Q_heat)  # Nemůže být záporné (bez chlazení)


def estimate_initial_parameters(
    daily_energy_df: pd.DataFrame,
    hourly_weather_df: pd.DataFrame,
    volume_m3: float,
    avg_indoor_temp: float
) -> Tuple[float, float, float]:
    """
    Hrubý počáteční odhad parametrů pomocí lineární regrese.
    
    Returns:
        (H_env_initial, infiltration_initial, C_th_initial)
    """
    # Merge denní průměry
    daily_avg = hourly_weather_df.groupby(
        hourly_weather_df['timestamp'].dt.date
    ).agg({
        'temp_out_c': 'mean'
    }).reset_index()
    
    daily_avg.columns = ['date', 'avg_temp_out']
    
    # Převeď date na datetime pro konzistentní merge
    daily_avg['date'] = pd.to_datetime(daily_avg['date'])
    
    merged = daily_energy_df.merge(daily_avg, on='date', how='inner')
    
    # Delta teplota
    merged['delta_T'] = avg_indoor_temp - merged['avg_temp_out']
    
    # Jednoduchá lineární regrese: heating_kwh ≈ a * delta_T + b
    # kde a ≈ 24 * H_total / 1000 (24 hodin, kW)
    
    if len(merged) > 1 and 'heating_kwh' in merged.columns:
        from scipy.stats import linregress
        
        slope, intercept, r_value, p_value, std_err = linregress(
            merged['delta_T'], 
            merged['heating_kwh']
        )
        
        # H_total z slope
        H_total_estimate = slope * 1000 / 24  # kWh/K/den → W/K
        
        # Rozdělíme na H_env a H_vent (předpokládáme n=0.3)
        n_guess = 0.3
        H_vent_guess = RHO_AIR * CP_AIR * n_guess * volume_m3 / 3600
        H_env_guess = max(10, H_total_estimate - H_vent_guess)
        
        print(f"  Odhad z lineární regrese: R²={r_value**2:.3f}")
        print(f"  H_env ~ {H_env_guess:.1f} W/K, infiltrace ~ {n_guess:.2f} 1/h")
    else:
        # Fallback - odhad podle objemu
        H_env_guess = volume_m3 * 2.0  # ~ 2 W/K na m³
        n_guess = 0.3
    
    # Tepelná kapacita - odhad podle objemu
    # Typicky ~10-30 Wh/K na m³ = 36-108 kJ/K na m³
    C_th_guess = volume_m3 * 50 * 3600  # 50 Wh/K/m³ → J/K
    
    return H_env_guess, n_guess, C_th_guess
