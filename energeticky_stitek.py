#!/usr/bin/env python3
"""
Energetický štítek - výpočet měrné potřeby tepla a energetické třídy bytu

Aplikace odhaduje měrnou potřebu tepla (kWh/m²·rok) a orientační energetickou třídu bytu.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import requests
import numpy as np
from scipy.optimize import minimize


# Energetické třídy podle měrné potřeby tepla (kWh/m²·rok)
ENERGY_CLASSES = [
    ("A", 0, 50),
    ("B", 50, 75),
    ("C", 75, 110),
    ("D", 110, 150),
    ("E", 150, 200),
    ("F", 200, 250),
    ("G", 250, float('inf'))
]


class WeatherDataFetcher:
    """Stahování hodinových dat o počasí z weatherapi.com"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1"
    
    def fetch_hourly_data(self, location: str, date: datetime) -> Optional[Dict]:
        """Stáhne hodinová data pro daný den"""
        date_str = date.strftime("%Y-%m-%d")
        url = f"{self.base_url}/history.json"
        params = {
            "key": self.api_key,
            "q": location,
            "dt": date_str
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Chyba při stahování dat pro {date_str}: {e}", file=sys.stderr)
            return None
    
    def fetch_annual_data(self, location: str, year: int = None) -> List[Dict]:
        """Stáhne hodinová data pro celý rok (použije poslední rok, pokud není zadán)"""
        if year is None:
            year = datetime.now().year - 1
        
        all_data = []
        start_date = datetime(year, 1, 1)
        
        for day in range(365):
            current_date = start_date + timedelta(days=day)
            data = self.fetch_hourly_data(location, current_date)
            if data and 'forecast' in data and 'forecastday' in data['forecast']:
                for day_data in data['forecast']['forecastday']:
                    if 'hour' in day_data:
                        all_data.extend(day_data['hour'])
        
        return all_data


class ConsumptionSplitter:
    """Rozdělení spotřeby energie na TUV (teplá užitková voda) a vytápění"""
    
    @staticmethod
    def split_consumption(
        daily_consumption_kwh: float,
        indoor_temp_c: float,
        outdoor_temp_c: float,
        area_m2: float,
        people_count: int = 2
    ) -> Tuple[float, float]:
        """
        Rozdělí denní spotřebu na TUV a vytápění
        
        Returns:
            (tuv_kwh, heating_kwh)
        """
        # Odhad TUV: cca 1.5-2 kWh na osobu na den (40-50°C ohřev vody)
        tuv_per_person = 1.75
        tuv_kwh = people_count * tuv_per_person
        
        # Zbytek jde na vytápění
        heating_kwh = max(0, daily_consumption_kwh - tuv_kwh)
        
        return tuv_kwh, heating_kwh


class RCThermalModel:
    """
    Jednoduchý RC tepelný model budovy
    
    Parametry:
    - HLC (Heat Loss Coefficient): celkový součinitel tepelných ztrát [W/K]
    - infiltrace: rychlost výměny vzduchu [1/h]
    - tepelná kapacita: efektivní tepelná kapacita budovy [Wh/K]
    """
    
    def __init__(self, hlc: float, infiltration_rate: float, thermal_capacity: float):
        self.hlc = hlc  # W/K
        self.infiltration_rate = infiltration_rate  # 1/h
        self.thermal_capacity = thermal_capacity  # Wh/K
    
    def calculate_heating_demand(
        self,
        indoor_temp: float,
        outdoor_temp: float,
        volume_m3: float,
        timestep_h: float = 1.0
    ) -> float:
        """
        Vypočítá potřebu tepla pro udržení vnitřní teploty
        
        Returns:
            Potřeba tepla v kWh
        """
        temp_diff = indoor_temp - outdoor_temp
        
        # Ztráty přes stavební konstrukce
        transmission_loss_w = self.hlc * temp_diff
        
        # Infiltrační ztráty
        air_density = 1.2  # kg/m³
        air_specific_heat = 1005  # J/(kg·K)
        infiltration_loss_w = (
            self.infiltration_rate * volume_m3 * air_density * 
            air_specific_heat * temp_diff / 3600
        )
        
        total_loss_w = transmission_loss_w + infiltration_loss_w
        heating_demand_kwh = (total_loss_w * timestep_h) / 1000
        
        return max(0, heating_demand_kwh)
    
    def simulate_temperature(
        self,
        initial_temp: float,
        outdoor_temp: float,
        heating_power_w: float,
        timestep_h: float = 1.0
    ) -> float:
        """
        Simuluje změnu vnitřní teploty
        
        Returns:
            Nová vnitřní teplota ve °C
        """
        temp_diff = initial_temp - outdoor_temp
        heat_loss_w = self.hlc * temp_diff
        
        net_heat_w = heating_power_w - heat_loss_w
        temp_change = (net_heat_w * timestep_h) / self.thermal_capacity
        
        return initial_temp + temp_change


class ModelCalibrator:
    """Kalibrace RC modelu na základě naměřených dat"""
    
    def __init__(self, area_m2: float, ceiling_height_m: float):
        self.area_m2 = area_m2
        self.ceiling_height_m = ceiling_height_m
        self.volume_m3 = area_m2 * ceiling_height_m
    
    def calibrate(
        self,
        measured_daily_heating_kwh: float,
        indoor_temp: float,
        avg_outdoor_temp: float
    ) -> RCThermalModel:
        """
        Kalibruje model na základě naměřené spotřeby
        
        Returns:
            Kalibrovaný RC model
        """
        # Počáteční odhady parametrů
        # HLC: typicky 1-3 W/(m²·K) * plocha
        initial_hlc = 2.0 * self.area_m2
        
        # Infiltrace: typicky 0.3-0.8 1/h
        initial_infiltration = 0.5
        
        # Tepelná kapacita: typicky 50-150 Wh/(m²·K) * plocha
        initial_capacity = 100.0 * self.area_m2
        
        # Optimalizace parametrů
        def objective(params):
            hlc, infiltration, capacity = params
            if hlc <= 0 or infiltration <= 0 or capacity <= 0:
                return 1e10
            
            model = RCThermalModel(hlc, infiltration, capacity)
            predicted = model.calculate_heating_demand(
                indoor_temp, avg_outdoor_temp, self.volume_m3, 24.0
            )
            
            # Minimalizace rozdílu mezi měřenou a predikovanou spotřebou
            return abs(predicted - measured_daily_heating_kwh)
        
        # Bounds pro parametry
        bounds = [
            (self.area_m2 * 0.5, self.area_m2 * 5.0),  # HLC
            (0.1, 2.0),  # infiltrace
            (self.area_m2 * 30, self.area_m2 * 200)  # kapacita
        ]
        
        result = minimize(
            objective,
            [initial_hlc, initial_infiltration, initial_capacity],
            bounds=bounds,
            method='L-BFGS-B'
        )
        
        hlc, infiltration, capacity = result.x
        return RCThermalModel(hlc, infiltration, capacity)


class AnnualSimulator:
    """Simulace roční spotřeby energie"""
    
    def __init__(self, model: RCThermalModel, area_m2: float, ceiling_height_m: float):
        self.model = model
        self.area_m2 = area_m2
        self.volume_m3 = area_m2 * ceiling_height_m
    
    def simulate_annual(
        self,
        weather_data: List[Dict],
        indoor_temp: float,
        tuv_daily_kwh: float,
        heat_source_efficiency: float
    ) -> Dict:
        """
        Simuluje roční spotřebu
        
        Returns:
            Dict s výsledky simulace
        """
        total_heating_demand = 0.0
        total_tuv_demand = tuv_daily_kwh * 365
        hourly_demands = []
        
        for hour_data in weather_data:
            outdoor_temp = hour_data.get('temp_c', 0)
            
            heating_demand = self.model.calculate_heating_demand(
                indoor_temp, outdoor_temp, self.volume_m3, 1.0
            )
            
            total_heating_demand += heating_demand
            hourly_demands.append(heating_demand)
        
        # Celková spotřeba energie ze zdroje (započítání účinnosti)
        total_energy_source = (total_heating_demand + total_tuv_demand) / heat_source_efficiency
        
        # Měrná potřeba tepla
        specific_heat_demand = total_heating_demand / self.area_m2
        
        # Měrná potřeba energie (ze zdroje)
        specific_energy_demand = total_energy_source / self.area_m2
        
        return {
            'total_heating_kwh': total_heating_demand,
            'total_tuv_kwh': total_tuv_demand,
            'total_energy_source_kwh': total_energy_source,
            'specific_heat_demand_kwh_m2': specific_heat_demand,
            'specific_energy_demand_kwh_m2': specific_energy_demand,
            'hourly_demands': hourly_demands
        }


class EnergyClassCalculator:
    """Výpočet energetické třídy"""
    
    @staticmethod
    def get_energy_class(specific_heat_demand: float) -> str:
        """Určí energetickou třídu podle měrné potřeby tepla"""
        for class_name, min_val, max_val in ENERGY_CLASSES:
            if min_val <= specific_heat_demand < max_val:
                return class_name
        return "G"
    
    @staticmethod
    def calculate_reliability(
        measured_consumption: float,
        simulated_consumption: float,
        calibration_error: float
    ) -> float:
        """
        Vypočítá míru spolehlivosti odhadu (0-100%)
        
        Bere v úvahu:
        - Shodu měřené a simulované spotřeby
        - Chybu kalibrace
        """
        # Relativní odchylka
        if measured_consumption > 0:
            relative_error = abs(measured_consumption - simulated_consumption) / measured_consumption
        else:
            relative_error = 1.0
        
        # Spolehlivost klesá s rostoucí chybou
        accuracy = max(0, 1 - relative_error)
        
        # Zahrnout chybu kalibrace
        calibration_factor = max(0, 1 - calibration_error)
        
        reliability = (accuracy * 0.7 + calibration_factor * 0.3) * 100
        
        return max(0, min(100, reliability))


class ReportGenerator:
    """Generování reportu"""
    
    @staticmethod
    def generate_report(
        inputs: Dict,
        simulation_results: Dict,
        energy_class: str,
        reliability: float,
        model: RCThermalModel
    ) -> str:
        """Vygeneruje textový report"""
        report = []
        report.append("=" * 80)
        report.append("ENERGETICKÝ ŠTÍTEK - VÝPOČET MĚRNÉ POTŘEBY TEPLA")
        report.append("=" * 80)
        report.append("")
        
        report.append("VSTUPNÍ PARAMETRY:")
        report.append(f"  Plocha bytu: {inputs['area_m2']:.1f} m²")
        report.append(f"  Výška stropu: {inputs['ceiling_height_m']:.2f} m")
        report.append(f"  Objem bytu: {inputs['area_m2'] * inputs['ceiling_height_m']:.1f} m³")
        report.append(f"  Typ zdroje tepla: {inputs['heat_source_type']}")
        report.append(f"  Účinnost/COP zdroje: {inputs['heat_source_efficiency']:.2f}")
        report.append(f"  Denní spotřeba energie: {inputs['daily_consumption_kwh']:.2f} kWh")
        report.append(f"  Vnitřní teplota: {inputs['indoor_temp_c']:.1f} °C")
        report.append(f"  Lokalita: {inputs['location']}")
        report.append("")
        
        report.append("KALIBROVANÉ PARAMETRY RC MODELU:")
        report.append(f"  HLC (Heat Loss Coefficient): {model.hlc:.2f} W/K")
        report.append(f"  Měrný HLC: {model.hlc / inputs['area_m2']:.2f} W/(m²·K)")
        report.append(f"  Infiltrace: {model.infiltration_rate:.3f} 1/h")
        report.append(f"  Tepelná kapacita: {model.thermal_capacity:.0f} Wh/K")
        report.append(f"  Měrná kapacita: {model.thermal_capacity / inputs['area_m2']:.1f} Wh/(m²·K)")
        report.append("")
        
        report.append("ROČNÍ SIMULACE:")
        report.append(f"  Celková potřeba tepla na vytápění: {simulation_results['total_heating_kwh']:.1f} kWh/rok")
        report.append(f"  Celková potřeba na TUV: {simulation_results['total_tuv_kwh']:.1f} kWh/rok")
        report.append(f"  Celková energie ze zdroje: {simulation_results['total_energy_source_kwh']:.1f} kWh/rok")
        report.append("")
        
        report.append("MĚRNÁ POTŘEBA TEPLA:")
        report.append(f"  Vytápění: {simulation_results['specific_heat_demand_kwh_m2']:.1f} kWh/(m²·rok)")
        report.append(f"  Celková (ze zdroje): {simulation_results['specific_energy_demand_kwh_m2']:.1f} kWh/(m²·rok)")
        report.append("")
        
        report.append("ENERGETICKÁ TŘÍDA:")
        report.append(f"  Třída: {energy_class}")
        report.append("")
        
        report.append("MÍRA SPOLEHLIVOSTI ODHADU:")
        report.append(f"  {reliability:.1f} %")
        report.append("")
        
        # Interpretace
        report.append("INTERPRETACE:")
        if reliability >= 80:
            report.append("  Odhad je vysoce spolehlivý.")
        elif reliability >= 60:
            report.append("  Odhad je středně spolehlivý. Doporučuje se delší měření.")
        else:
            report.append("  Odhad má nižší spolehlivost. Je potřeba více dat pro přesnější výsledek.")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Hlavní funkce aplikace"""
    parser = argparse.ArgumentParser(
        description="Výpočet měrné potřeby tepla a energetické třídy bytu"
    )
    
    # Povinné parametry
    parser.add_argument("--area", type=float, required=True,
                       help="Plocha bytu v m²")
    parser.add_argument("--ceiling-height", type=float, required=True,
                       help="Výška stropu v m")
    parser.add_argument("--heat-source", type=str, required=True,
                       choices=['gas-boiler', 'electric', 'heat-pump', 'district-heating'],
                       help="Typ zdroje tepla")
    parser.add_argument("--efficiency", type=float, required=True,
                       help="Účinnost (kotel) nebo COP (tepelné čerpadlo)")
    parser.add_argument("--daily-consumption", type=float, required=True,
                       help="Denní spotřeba energie v kWh")
    parser.add_argument("--indoor-temp", type=float, required=True,
                       help="Požadovaná vnitřní teplota ve °C")
    parser.add_argument("--location", type=str, required=True,
                       help="Lokalita (např. 'Prague', 'Brno')")
    
    # Volitelné parametry
    parser.add_argument("--api-key", type=str,
                       help="API klíč pro weatherapi.com (pokud není zadán, použije se demo režim)")
    parser.add_argument("--year", type=int,
                       help="Rok pro stažení dat (výchozí: minulý rok)")
    parser.add_argument("--people", type=int, default=2,
                       help="Počet osob v bytě (výchozí: 2)")
    parser.add_argument("--output", type=str,
                       help="Název výstupního souboru (výchozí: report_TIMESTAMP.txt)")
    
    args = parser.parse_args()
    
    # Příprava vstupních dat
    inputs = {
        'area_m2': args.area,
        'ceiling_height_m': args.ceiling_height,
        'heat_source_type': args.heat_source,
        'heat_source_efficiency': args.efficiency,
        'daily_consumption_kwh': args.daily_consumption,
        'indoor_temp_c': args.indoor_temp,
        'location': args.location
    }
    
    print("Zpracování vstupních dat...")
    
    # Stažení dat o počasí nebo použití demo dat
    if args.api_key:
        print(f"Stahuji data o počasí pro {args.location}...")
        fetcher = WeatherDataFetcher(args.api_key)
        weather_data = fetcher.fetch_annual_data(args.location, args.year)
        
        if not weather_data:
            print("Chyba: Nepodařilo se stáhnout data o počasí.", file=sys.stderr)
            print("Přepínám na demo režim s odhadovanými daty.", file=sys.stderr)
            weather_data = None
    else:
        print("API klíč nebyl zadán, používám demo režim s odhadovanými daty.")
        weather_data = None
    
    # Demo režim - generování syntetických dat
    if weather_data is None or len(weather_data) == 0:
        print("Generuji syntetická data o počasí...")
        weather_data = []
        # Modelujeme roční cyklus teplot pro střední Evropu
        for day in range(365):
            for hour in range(24):
                # Roční teplotní cyklus (sinusoida)
                annual_cycle = -10 * np.cos(2 * np.pi * day / 365)
                # Denní cyklus (menší amplituda)
                daily_cycle = -3 * np.cos(2 * np.pi * hour / 24)
                # Základní teplota + cykly
                temp = 8 + annual_cycle + daily_cycle
                weather_data.append({'temp_c': temp})
    
    # Výpočet průměrné venkovní teploty
    avg_outdoor_temp = np.mean([h.get('temp_c', 0) for h in weather_data])
    
    print(f"Průměrná venkovní teplota: {avg_outdoor_temp:.1f} °C")
    
    # Rozdělení spotřeby na TUV a vytápění
    splitter = ConsumptionSplitter()
    tuv_kwh, heating_kwh = splitter.split_consumption(
        args.daily_consumption,
        args.indoor_temp,
        avg_outdoor_temp,
        args.area,
        args.people
    )
    
    print(f"Rozdělení denní spotřeby: TUV={tuv_kwh:.2f} kWh, Vytápění={heating_kwh:.2f} kWh")
    
    # Kalibrace modelu
    print("Kalibrace RC modelu...")
    calibrator = ModelCalibrator(args.area, args.ceiling_height)
    model = calibrator.calibrate(heating_kwh, args.indoor_temp, avg_outdoor_temp)
    
    print(f"Kalibrovaný HLC: {model.hlc:.2f} W/K")
    print(f"Infiltrace: {model.infiltration_rate:.3f} 1/h")
    
    # Roční simulace
    print("Provádím roční simulaci...")
    simulator = AnnualSimulator(model, args.area, args.ceiling_height)
    simulation_results = simulator.simulate_annual(
        weather_data,
        args.indoor_temp,
        tuv_kwh,
        args.efficiency
    )
    
    # Výpočet energetické třídy
    energy_class = EnergyClassCalculator.get_energy_class(
        simulation_results['specific_heat_demand_kwh_m2']
    )
    
    print(f"Měrná potřeba tepla: {simulation_results['specific_heat_demand_kwh_m2']:.1f} kWh/(m²·rok)")
    print(f"Energetická třída: {energy_class}")
    
    # Výpočet spolehlivosti
    # Porovnání vstupní spotřeby se simulovanou (přepočítané na roční)
    annual_measured = args.daily_consumption * 365
    calibration_error = abs(heating_kwh - model.calculate_heating_demand(
        args.indoor_temp, avg_outdoor_temp, args.area * args.ceiling_height, 24.0
    )) / max(heating_kwh, 1.0)
    
    reliability = EnergyClassCalculator.calculate_reliability(
        annual_measured,
        simulation_results['total_energy_source_kwh'],
        calibration_error
    )
    
    # Generování reportu
    print("\nGeneruji report...")
    report = ReportGenerator.generate_report(
        inputs,
        simulation_results,
        energy_class,
        reliability,
        model
    )
    
    # Výstup reportu
    print("\n" + report)
    
    # Uložení do souboru
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"report_{timestamp}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport byl uložen do souboru: {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
