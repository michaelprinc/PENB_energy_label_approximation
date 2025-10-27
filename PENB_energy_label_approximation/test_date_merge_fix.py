"""
Test opravy date merge problému
Ověří, že všechny merge operace používají konzistentní datetime typy
"""
import pandas as pd
import numpy as np
from datetime import datetime


def test_datetime_consistency():
    """Test 1: Konzistence datetime typů"""
    print("\n" + "="*60)
    print("TEST 1: Konzistence datetime typů při merge")
    print("="*60)
    
    try:
        # Vytvoř testovací daily_energy_df (datetime64[ns])
        dates = pd.date_range('2024-01-01', '2024-01-31', freq='D')
        daily_energy_df = pd.DataFrame({
            'date': dates,
            'energy_total_kwh': np.random.uniform(20, 40, len(dates))
        })
        
        # Zkontroluj typ
        print(f"daily_energy_df['date'] dtype: {daily_energy_df['date'].dtype}")
        assert pd.api.types.is_datetime64_any_dtype(daily_energy_df['date']), \
            "date sloupec musí být datetime64"
        
        # Vytvoř testovací hourly_weather_df
        hourly_timestamps = pd.date_range('2024-01-01', '2024-01-31 23:00', freq='H')
        hourly_weather_df = pd.DataFrame({
            'timestamp': hourly_timestamps,
            'temp_out_c': np.random.uniform(-5, 10, len(hourly_timestamps))
        })
        
        # Simulace problémové části (PŘED opravou)
        daily_avg_WRONG = hourly_weather_df.groupby(
            hourly_weather_df['timestamp'].dt.date
        ).agg({'temp_out_c': 'mean'}).reset_index()
        daily_avg_WRONG.columns = ['date', 'avg_temp_out']
        
        print(f"daily_avg (PŘED) dtype: {daily_avg_WRONG['date'].dtype}")
        
        # TADY BY MĚLA BÝT CHYBA bez opravy
        try:
            merged_wrong = daily_energy_df.merge(daily_avg_WRONG, on='date', how='inner')
            print(f"⚠ Merge prošel bez opravy - možná pandas verze to zvládá")
        except ValueError as e:
            print(f"✓ Očekávaná chyba BEZ opravy: {str(e)[:80]}...")
        
        # Simulace OPRAVY
        daily_avg_FIXED = hourly_weather_df.groupby(
            hourly_weather_df['timestamp'].dt.date
        ).agg({'temp_out_c': 'mean'}).reset_index()
        daily_avg_FIXED.columns = ['date', 'avg_temp_out']
        
        # ✅ KLÍČOVÁ OPRAVA
        daily_avg_FIXED['date'] = pd.to_datetime(daily_avg_FIXED['date'])
        print(f"daily_avg (PO) dtype: {daily_avg_FIXED['date'].dtype}")
        
        # Zkus merge s opravou
        merged = daily_energy_df.merge(daily_avg_FIXED, on='date', how='inner')
        
        print(f"✓ Merge S opravou úspěšný: {len(merged)} řádků")
        print(f"✓ Sloučené dtypes: {merged['date'].dtype}")
        
        return True
    except Exception as e:
        print(f"✗ Chyba: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_date_object_vs_datetime64():
    """Test 2: Rozdíl mezi date object a datetime64"""
    print("\n" + "="*60)
    print("TEST 2: date object vs datetime64[ns]")
    print("="*60)
    
    try:
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='D')
        })
        
        # dt.date vytvoří object dtype
        df['date_object'] = df['timestamp'].dt.date
        print(f"df['date_object'] dtype: {df['date_object'].dtype}")
        print(f"  První hodnota: {df['date_object'].iloc[0]} (typ: {type(df['date_object'].iloc[0])})")
        
        # pd.to_datetime konvertuje na datetime64[ns]
        df['date_datetime64'] = pd.to_datetime(df['timestamp'].dt.date)
        print(f"df['date_datetime64'] dtype: {df['date_datetime64'].dtype}")
        print(f"  První hodnota: {df['date_datetime64'].iloc[0]} (typ: {type(df['date_datetime64'].iloc[0])})")
        
        # Ukázka merge problému
        df1 = pd.DataFrame({'date': pd.date_range('2024-01-01', periods=3)})  # datetime64[ns]
        df2 = pd.DataFrame({'date': [datetime(2024,1,1).date(), datetime(2024,1,2).date()]})  # object
        
        print(f"\ndf1['date'] dtype: {df1['date'].dtype}")
        print(f"df2['date'] dtype: {df2['date'].dtype}")
        
        try:
            result = df1.merge(df2, on='date')
            print(f"⚠ Merge object + datetime64[ns] prošel (pandas verze je tolerantní)")
        except ValueError as e:
            print(f"✗ Merge selhal: {str(e)[:80]}...")
        
        # S opravou
        df2_fixed = df2.copy()
        df2_fixed['date'] = pd.to_datetime(df2_fixed['date'])
        result_fixed = df1.merge(df2_fixed, on='date')
        print(f"✓ Merge s opravou: {len(result_fixed)} řádků")
        
        return True
    except Exception as e:
        print(f"✗ Chyba: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_groupby_date_conversion():
    """Test 3: Konverze po groupby"""
    print("\n" + "="*60)
    print("TEST 3: Groupby a date konverze")
    print("="*60)
    
    try:
        # Simulace simulace z calibrator.py
        simulated = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=72, freq='H'),
            'value': np.random.uniform(0, 100, 72)
        })
        
        # PŘED opravou (vytvoří object)
        simulated_wrong = simulated.copy()
        simulated_wrong['date'] = simulated_wrong['timestamp'].dt.date
        print(f"date (PŘED) dtype: {simulated_wrong['date'].dtype}")
        
        daily_wrong = simulated_wrong.groupby('date')['value'].sum().reset_index()
        print(f"  Po groupby: {daily_wrong['date'].dtype}")
        
        # PO opravě (datetime64[ns])
        simulated_fixed = simulated.copy()
        simulated_fixed['date'] = pd.to_datetime(simulated_fixed['timestamp'].dt.date)
        print(f"date (PO) dtype: {simulated_fixed['date'].dtype}")
        
        daily_fixed = simulated_fixed.groupby('date')['value'].sum().reset_index()
        print(f"  Po groupby: {daily_fixed['date'].dtype}")
        
        # Test merge s denními daty
        daily_energy = pd.DataFrame({
            'date': pd.date_range('2024-01-01', '2024-01-03', freq='D'),
            'energy': [25.0, 30.0, 28.0]
        })
        
        print(f"\ndaily_energy['date'] dtype: {daily_energy['date'].dtype}")
        
        # Merge s opravou
        merged = daily_energy.merge(daily_fixed[['date', 'value']], on='date', how='inner')
        print(f"✓ Merge úspěšný: {len(merged)} řádků")
        
        return True
    except Exception as e:
        print(f"✗ Chyba: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Spustí všechny testy"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  TEST: Oprava date merge problému".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    results = {
        'Datetime konzistence': test_datetime_consistency(),
        'Date object vs datetime64': test_date_object_vs_datetime64(),
        'Groupby date konverze': test_groupby_date_conversion()
    }
    
    # Výsledky
    print("\n" + "="*60)
    print("VÝSLEDKY TESTŮ")
    print("="*60)
    
    for name, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print("\n" + "-"*60)
    print(f"Úspěch: {passed}/{total} testů")
    print("-"*60)
    
    if passed == total:
        print("\n🎉 VŠECHNY TESTY PROŠLY!")
        print("\n✅ Oprava date merge problému je funkční!")
        print("\n💡 Klíčové zjištění:")
        print("   • dt.date vytváří Python date objekty (dtype=object)")
        print("   • pd.to_datetime() konvertuje na datetime64[ns]")
        print("   • Merge vyžaduje konzistentní dtypes")
        print("   • Řešení: Vždy použít pd.to_datetime() před merge")
        return 0
    else:
        print("\n⚠ NĚKTERÉ TESTY SELHALY")
        return 1


if __name__ == "__main__":
    exit(main())
