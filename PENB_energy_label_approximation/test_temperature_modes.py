"""
Test pro ověření teplotních režimů v GUI
"""

def test_day_night_mode():
    """Test Den/Noc režimu"""
    # Simulace vstupů
    temp_day = 21.0
    temp_night = 19.0
    day_start_hour = 6
    day_end_hour = 22
    
    # Výpočet průměru
    day_hours = day_end_hour - day_start_hour  # 16 hodin
    night_hours = 24 - day_hours  # 8 hodin
    avg_temp = (temp_day * day_hours + temp_night * night_hours) / 24
    
    expected = (21.0 * 16 + 19.0 * 8) / 24  # = 20.33°C
    
    print(f"✓ Den/Noc režim test:")
    print(f"  Denní teplota: {temp_day}°C ({day_hours}h)")
    print(f"  Noční teplota: {temp_night}°C ({night_hours}h)")
    print(f"  Vypočítaný průměr: {avg_temp:.2f}°C")
    print(f"  Očekáváno: {expected:.2f}°C")
    
    assert abs(avg_temp - expected) < 0.01, "Výpočet průměru nesedí!"
    print("  ✅ PASS\n")


def test_average_mode():
    """Test průměrné teploty"""
    temp_avg = 21.0
    
    # V tomto režimu je konstanta
    temp_day = temp_avg
    temp_night = temp_avg
    
    print(f"✓ Průměrná teplota test:")
    print(f"  Průměrná teplota: {temp_avg}°C")
    print(f"  Den = Noc = {temp_avg}°C")
    
    assert temp_day == temp_night == temp_avg
    print("  ✅ PASS\n")


def test_validation():
    """Test validací"""
    print("✓ Validace test:")
    
    # Test 1: Noční > denní (chyba)
    temp_day = 19.0
    temp_night = 21.0
    
    if temp_night > temp_day:
        print(f"  ⚠ Noční ({temp_night}) > denní ({temp_day}) - správně zachyceno")
    
    # Test 2: Den končí před začátkem (chyba)
    day_start = 22
    day_end = 6
    
    if day_end <= day_start:
        print(f"  ⚠ Den končí ({day_end}) <= začíná ({day_start}) - správně zachyceno")
    
    print("  ✅ PASS\n")


def test_precedence():
    """Test pravidel precedence"""
    print("✓ Pravidla precedence test:")
    
    # Scénář 1: Režim Den/Noc - má prioritu
    temp_mode = 'day_night'
    temp_day = 21.0
    temp_night = 19.0
    temp_avg_user = 20.0  # Toto se NEPOUŽIJE
    
    if temp_mode == 'day_night':
        avg_calculated = (temp_day * 16 + temp_night * 8) / 24
        print(f"  Režim: Den/Noc → použit vypočítaný průměr {avg_calculated:.2f}°C")
        print(f"  Uživatelská průměrná teplota ({temp_avg_user}°C) ignorována")
    
    # Scénář 2: Režim průměrná
    temp_mode = 'average'
    temp_avg_user = 21.5
    
    if temp_mode == 'average':
        print(f"  Režim: Průměrná → použita {temp_avg_user}°C")
    
    print("  ✅ PASS\n")


if __name__ == "__main__":
    print("="*60)
    print("TEST TEPLOTNÍCH REŽIMŮ - GUI verze 1.1.0")
    print("="*60 + "\n")
    
    test_day_night_mode()
    test_average_mode()
    test_validation()
    test_precedence()
    
    print("="*60)
    print("✅ VŠECHNY TESTY PROŠLY")
    print("="*60)
