"""
Test nových funkcí: měsíce bez topení + flexibilní den/noc časy
"""
import pandas as pd
import numpy as np
from datetime import date, timedelta

from core.data_models import TemperatureProfile, UserInputs, ApartmentGeometry, HeatingSystemInfo, HeatingSystemType, ComputationMode, DailyEnergyData
from core.preprocess import create_hourly_indoor_temp


def test_temperature_profile():
    """Test nového TemperatureProfile s časovými rozsahy"""
    print("\n=== Test 1: TemperatureProfile ===")
    
    # Základní profil
    profile = TemperatureProfile(
        day_temp_c=21.0,
        night_temp_c=19.0,
        day_start_hour=6,
        day_end_hour=22
    )
    
    print(f"✓ Den: {profile.day_temp_c}°C ({profile.day_start_hour}:00 - {profile.day_end_hour}:00)")
    print(f"✓ Noc: {profile.night_temp_c}°C")
    
    # Test validace - konec před začátkem
    try:
        bad_profile = TemperatureProfile(
            day_temp_c=21.0,
            night_temp_c=19.0,
            day_start_hour=22,
            day_end_hour=6  # Chyba!
        )
        print("❌ CHYBA: Měla být vyvolána ValidationError!")
    except Exception as e:
        print(f"✓ Validace funguje: {type(e).__name__}")
    
    # Test validace - noční teplota vyšší než denní
    try:
        bad_profile2 = TemperatureProfile(
            day_temp_c=19.0,
            night_temp_c=21.0  # Chyba!
        )
        print("❌ CHYBA: Měla být vyvolána ValidationError!")
    except Exception as e:
        print(f"✓ Validace funguje: {type(e).__name__}")


def test_non_heating_months():
    """Test měsíců bez topení v UserInputs"""
    print("\n=== Test 2: Měsíce bez topení ===")
    
    # Vytvoř ukázková data - včetně letních měsíců
    daily_data = []
    start_date = date(2025, 1, 1)
    
    for i in range(180):  # Půl roku
        current_date = start_date + timedelta(days=i)
        month = current_date.month
        
        # Simuluj nižší spotřebu v létě
        if month in [5, 6, 7, 8, 9]:
            energy = 2.0 + np.random.uniform(-0.5, 0.5)  # Jen TUV
        else:
            energy = 10.0 + np.random.uniform(-2, 2)  # Vytápění + TUV
        
        daily_data.append(DailyEnergyData(date=current_date, energy_total_kwh=energy))
    
    # Vytvoř UserInputs s měsíci bez topení
    user_inputs = UserInputs(
        geometry=ApartmentGeometry(area_m2=70, height_m=2.7),
        heating_system=HeatingSystemInfo(system_type=HeatingSystemType.CONDENSING_BOILER),
        location="Praha",
        computation_mode=ComputationMode.STANDARD,
        daily_energy=daily_data,
        avg_indoor_temp_c=21.0,
        non_heating_months=[5, 6, 7, 8, 9]  # Květen-září
    )
    
    print(f"✓ Vytvořeno {len(user_inputs.daily_energy)} denních záznamů")
    print(f"✓ Měsíce bez topení: {user_inputs.non_heating_months}")
    
    # Test baseline TUV z letních měsíců
    df = pd.DataFrame([d.model_dump() for d in user_inputs.daily_energy])
    df['month'] = pd.to_datetime(df['date']).dt.month
    
    summer_mask = df['month'].isin(user_inputs.non_heating_months)
    summer_avg = df.loc[summer_mask, 'energy_total_kwh'].mean()
    winter_avg = df.loc[~summer_mask, 'energy_total_kwh'].mean()
    
    print(f"✓ Průměrná spotřeba v létě: {summer_avg:.2f} kWh/den")
    print(f"✓ Průměrná spotřeba v zimě: {winter_avg:.2f} kWh/den")
    print(f"✓ Rozdíl (odhad vytápění): {winter_avg - summer_avg:.2f} kWh/den")


def test_flexible_day_night():
    """Test flexibilního denního/nočního režimu"""
    print("\n=== Test 3: Flexibilní den/noc ===")
    
    # Vytvoř ukázková hodinová data
    timestamps = pd.date_range('2025-01-01', periods=24, freq='h')
    weather_df = pd.DataFrame({'timestamp': timestamps})
    
    # Test s explicitními teplotami
    indoor_df = create_hourly_indoor_temp(
        daily_avg_temp=20.0,  # Nebude použito
        hourly_weather_df=weather_df,
        day_temp=22.0,
        night_temp=18.0,
        day_start_hour=7,
        day_end_hour=23
    )
    
    print("\n✓ Hodinové teploty:")
    for hour in range(24):
        temp = indoor_df.iloc[hour]['temp_in_c']
        regime = "DEN" if 7 <= hour < 23 else "NOC"
        print(f"  {hour:02d}:00 → {temp:.1f}°C ({regime})")
    
    # Ověř správnost
    day_hours = indoor_df.iloc[7:23]['temp_in_c'].unique()
    night_hours_early = indoor_df.iloc[0:7]['temp_in_c'].unique()
    night_hours_late = indoor_df.iloc[23:24]['temp_in_c'].unique()
    
    assert len(day_hours) == 1 and day_hours[0] == 22.0, "Denní teplota nesedí!"
    assert len(night_hours_early) == 1 and night_hours_early[0] == 18.0, "Noční teplota nesedí!"
    assert len(night_hours_late) == 1 and night_hours_late[0] == 18.0, "Noční teplota nesedí!"
    
    print("\n✓ Všechny kontroly prošly!")


if __name__ == "__main__":
    print("=" * 60)
    print("TEST NOVÝCH FUNKCÍ")
    print("=" * 60)
    
    try:
        test_temperature_profile()
        test_non_heating_months()
        test_flexible_day_night()
        
        print("\n" + "=" * 60)
        print("✅ VŠECHNY TESTY ÚSPĚŠNĚ PROŠLY!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ CHYBA: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
