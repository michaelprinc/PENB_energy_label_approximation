"""
Testovací skript pro ověření importů a základní funkcionality
"""
import sys
import os
from pathlib import Path

# Přidej projekt do PYTHONPATH
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

print("=" * 60)
print("TEST IMPORTŮ A ZÁKLADNÍ FUNKCIONALITY")
print("=" * 60)
print()

# Test 1: Importy core modulů
print("Test 1: Importy core modulů...")
try:
    from core import config, data_models, weather_api, preprocess
    from core import baseline_split, rc_model, calibrator
    from core import simulate_year, metrics, quality_flags
    print("✓ Všechny core moduly naimportovány")
except Exception as e:
    print(f"✗ Chyba při importu core modulů: {e}")
    sys.exit(1)

# Test 2: Pydantic modely
print("\nTest 2: Pydantic modely...")
try:
    from core.data_models import (
        ApartmentGeometry, HeatingSystemInfo, HeatingSystemType,
        ComputationMode, QualityLevel, EnergyClass
    )
    
    # Vytvoř testovací objekt
    geom = ApartmentGeometry(area_m2=70.0, height_m=2.7)
    assert geom.volume_m3 == 70.0 * 2.7
    print(f"✓ Pydantic modely fungují (test: {geom.volume_m3:.1f} m³)")
except Exception as e:
    print(f"✗ Chyba v pydantic modelech: {e}")
    sys.exit(1)

# Test 3: Config
print("\nTest 3: Config modul...")
try:
    from core.config import ensure_storage_dir, load_api_config
    ensure_storage_dir()
    config_obj = load_api_config()
    print(f"✓ Config funguje (storage vytvořen)")
except Exception as e:
    print(f"✗ Chyba v config: {e}")
    sys.exit(1)

# Test 4: RC Model
print("\nTest 4: RC Model...")
try:
    from core.rc_model import RC1Model
    
    model = RC1Model(
        H_env_W_per_K=100.0,
        infiltration_rate_per_h=0.3,
        volume_m3=189.0,
        C_th_J_per_K=1e7,
        area_m2=70.0
    )
    
    # Simuluj jeden krok
    T_new = model.simulate_step(
        T_in_prev=21.0,
        T_out=5.0,
        Q_heat_W=2000.0,
        GHI_W_per_m2=0.0,
        dt_seconds=3600
    )
    
    print(f"✓ RC Model funguje (test simulace: {T_new:.2f}°C)")
except Exception as e:
    print(f"✗ Chyba v RC modelu: {e}")
    sys.exit(1)

# Test 5: Metrics
print("\nTest 5: Klasifikace energetických tříd...")
try:
    from core.metrics import classify_energy_label, get_class_description
    
    energy_class = classify_energy_label(
        heating_demand_kwh_per_m2_year=80.0,
        primary_energy_kwh_per_m2_year=120.0,
        use_primary=True
    )
    
    desc = get_class_description(energy_class)
    print(f"✓ Klasifikace funguje (test: třída {energy_class.value} - {desc})")
except Exception as e:
    print(f"✗ Chyba v klasifikaci: {e}")
    sys.exit(1)

# Test 6: Report builder
print("\nTest 6: Report builder...")
try:
    from reports.report_builder import generate_html_report
    print("✓ Report builder naimportován")
except Exception as e:
    print(f"✗ Chyba v report builderu: {e}")
    sys.exit(1)

# Test 7: GUI modul (jen import, nespouštíme)
print("\nTest 7: GUI modul...")
try:
    # Neimportujeme streamlit, jen zkontrolujeme, že soubor existuje
    gui_path = project_dir / "app_gui" / "gui_main.py"
    if gui_path.exists():
        print(f"✓ GUI soubor existuje: {gui_path}")
    else:
        print(f"✗ GUI soubor nenalezen: {gui_path}")
        sys.exit(1)
except Exception as e:
    print(f"✗ Chyba v GUI: {e}")
    sys.exit(1)

# Test 8: Závislosti
print("\nTest 8: Klíčové závislosti...")
missing = []

try:
    import pandas
    print("  ✓ pandas")
except ImportError:
    missing.append("pandas")
    print("  ✗ pandas CHYBÍ")

try:
    import numpy
    print("  ✓ numpy")
except ImportError:
    missing.append("numpy")
    print("  ✗ numpy CHYBÍ")

try:
    import scipy
    print("  ✓ scipy")
except ImportError:
    missing.append("scipy")
    print("  ✗ scipy CHYBÍ")

try:
    import pydantic
    print("  ✓ pydantic")
except ImportError:
    missing.append("pydantic")
    print("  ✗ pydantic CHYBÍ")

try:
    import requests
    print("  ✓ requests")
except ImportError:
    missing.append("requests")
    print("  ✗ requests CHYBÍ")

try:
    import streamlit
    print("  ✓ streamlit")
except ImportError:
    missing.append("streamlit")
    print("  ✗ streamlit CHYBÍ")

try:
    import geocoder
    print("  ✓ geocoder")
except ImportError:
    missing.append("geocoder")
    print("  ✗ geocoder CHYBÍ")

if missing:
    print(f"\n⚠ Chybějící závislosti: {', '.join(missing)}")
    print("Nainstalujte: pip install -r requirements.txt")
else:
    print("\n✓ Všechny závislosti jsou nainstalovány")

# Shrnutí
print("\n" + "=" * 60)
print("VÝSLEDEK TESTŮ")
print("=" * 60)

if not missing:
    print("✓ Všechny testy prošly!")
    print("✓ Aplikace je připravena ke spuštění")
    print("\nSpusťte aplikaci:")
    print("  Windows: run.bat")
    print("  Linux/Mac: ./run.sh")
    print("  Přímo: streamlit run app_gui/gui_main.py")
else:
    print("⚠ Některé závislosti chybí")
    print("Nainstalujte: pip install -r requirements.txt")
    sys.exit(1)
