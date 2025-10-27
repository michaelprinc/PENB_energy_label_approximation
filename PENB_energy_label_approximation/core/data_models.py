"""
Datové modely pro energetický štítek
Využívá pydantic pro validaci vstupů
"""
from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator


class HeatingSystemType(str, Enum):
    """Typy vytápěcích systémů"""
    CONDENSING_BOILER = "condensing_boiler"
    DIRECT_ELECTRIC = "direct_electric"
    HEAT_PUMP_AIR = "heat_pump_air"
    HEAT_PUMP_WATER = "heat_pump_water"
    UNKNOWN = "unknown"


class ComputationMode(str, Enum):
    """Režimy kvality výpočtu"""
    BASIC = "basic"  # Minimální data, rychlý odhad
    STANDARD = "standard"  # 7+ dní, hodinová data
    ADVANCED = "advanced"  # 28+ dní, pokročilá kalibrace


class QualityLevel(str, Enum):
    """Úroveň spolehlivosti výsledků"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EnergyClass(str, Enum):
    """Energetické třídy (orientační)"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"


class ApartmentGeometry(BaseModel):
    """Geometrie bytu"""
    area_m2: float = Field(gt=0, description="Plocha bytu v m²")
    height_m: float = Field(gt=0, le=5.0, description="Výška stropu v m")
    
    @property
    def volume_m3(self) -> float:
        """Vypočítá objem bytu"""
        return self.area_m2 * self.height_m


class HeatingSystemInfo(BaseModel):
    """Informace o vytápěcím systému"""
    system_type: HeatingSystemType
    efficiency_or_cop: Optional[float] = Field(
        None, 
        gt=0, 
        le=10.0,
        description="Účinnost kotle (0-1) nebo COP tepelného čerpadla (>1)"
    )
    
    def get_default_efficiency(self) -> tuple[float, float]:
        """Vrátí výchozí rozsah účinnosti/COP jako (min, max)"""
        defaults = {
            HeatingSystemType.CONDENSING_BOILER: (0.85, 0.95),
            HeatingSystemType.DIRECT_ELECTRIC: (0.98, 1.0),
            HeatingSystemType.HEAT_PUMP_AIR: (2.5, 3.5),
            HeatingSystemType.HEAT_PUMP_WATER: (3.0, 4.5),
            HeatingSystemType.UNKNOWN: (0.7, 1.0),
        }
        return defaults.get(self.system_type, (0.8, 1.0))


class DailyEnergyData(BaseModel):
    """Denní spotřeba energie"""
    date: date
    energy_total_kwh: float = Field(ge=0, description="Celková spotřeba za den v kWh")
    note: Optional[str] = None  # Např. "hodně větrání", "porucha"
    

class TemperatureProfile(BaseModel):
    """Teplotní profil (den/noc)"""
    day_temp_c: float = Field(default=21.0, ge=15.0, le=26.0)
    night_temp_c: float = Field(default=19.0, ge=15.0, le=26.0)
    
    @field_validator('night_temp_c')
    @classmethod
    def night_not_higher_than_day(cls, v, info):
        if 'day_temp_c' in info.data and v > info.data['day_temp_c']:
            raise ValueError('Noční teplota nemůže být vyšší než denní')
        return v


class UserInputs(BaseModel):
    """Kompletní uživatelské vstupy"""
    # Geometrie
    geometry: ApartmentGeometry
    
    # Systém vytápění
    heating_system: HeatingSystemInfo
    
    # Lokalita
    location: str = Field(description="Město nebo souřadnice (lat,lon)")
    
    # Režim výpočtu
    computation_mode: ComputationMode = ComputationMode.STANDARD
    
    # Požadovaná komfortní teplota
    comfort_temperature: TemperatureProfile = TemperatureProfile()
    
    # Denní spotřeby (seznam)
    daily_energy: List[DailyEnergyData] = Field(min_length=1)
    
    # Průměrná vnitřní teplota (pokud nemáme hodinová data)
    avg_indoor_temp_c: Optional[float] = Field(None, ge=15.0, le=30.0)
    
    @field_validator('daily_energy')
    @classmethod
    def validate_data_length(cls, v, info):
        """Kontrola dostatečného množství dat podle režimu"""
        if 'computation_mode' not in info.data:
            return v
            
        mode = info.data['computation_mode']
        required_days = {
            ComputationMode.BASIC: 1,
            ComputationMode.STANDARD: 7,
            ComputationMode.ADVANCED: 28
        }
        
        min_days = required_days.get(mode, 7)
        if len(v) < min_days:
            raise ValueError(
                f'Režim {mode.value} vyžaduje alespoň {min_days} dní dat, '
                f'máte pouze {len(v)}'
            )
        return v


class WeatherData(BaseModel):
    """Meteorologická data pro jedno časové razítko"""
    timestamp: datetime
    temp_out_c: float = Field(description="Venkovní teplota °C")
    ghi_wm2: Optional[float] = Field(None, ge=0, description="Globální sluneční záření W/m²")
    wind_mps: Optional[float] = Field(None, ge=0, description="Rychlost větru m/s")
    humidity_pct: Optional[float] = Field(None, ge=0, le=100, description="Relativní vlhkost %")


class CalibratedParameters(BaseModel):
    """Kalibrované parametry budovy"""
    H_env_W_per_K: float = Field(gt=0, description="Tepelné ztráty obálkou W/K")
    infiltration_rate_per_h: float = Field(gt=0, le=5.0, description="Intenzita infiltrace 1/h")
    C_th_J_per_K: float = Field(gt=0, description="Tepelná kapacita J/K")
    baseline_TUV_kwh_per_day: float = Field(ge=0, description="Baseline spotřeba TUV kWh/den")
    internal_gains_W_per_m2: float = Field(ge=0, description="Interní zisky W/m²")
    
    # Kvalita kalibrace
    rmse_temperature_c: float = Field(ge=0, description="RMSE vnitřní teploty °C")
    mape_energy_pct: float = Field(ge=0, description="MAPE denní energie %")


class AnnualResults(BaseModel):
    """Roční výsledky"""
    heating_demand_kwh_per_m2_year: float = Field(ge=0)
    primary_energy_kwh_per_m2_year: float = Field(ge=0)
    energy_class: EnergyClass
    quality_level: QualityLevel
    
    # Interval spolehlivosti (5% - 95%)
    heating_demand_lower_bound: Optional[float] = None
    heating_demand_upper_bound: Optional[float] = None
    
    # Metadata
    disclaimers: List[str] = []
    computation_date: datetime = Field(default_factory=datetime.now)


class APIConfig(BaseModel):
    """Konfigurace API"""
    weather_api_key: Optional[str] = None
    last_location: Optional[str] = None
    
    class Config:
        # Pro ukládání do JSON
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
