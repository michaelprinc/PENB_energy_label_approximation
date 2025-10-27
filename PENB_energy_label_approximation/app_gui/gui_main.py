"""
Streamlit GUI pro energetický štítek
"""
import sys
import os
from pathlib import Path

# Přidej parent directory do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime, timedelta

# Import core modulů
from core.config import (
    get_api_key, set_api_key, get_last_location, set_last_location
)
from core.data_models import (
    ApartmentGeometry, HeatingSystemInfo, HeatingSystemType,
    ComputationMode, TemperatureProfile, UserInputs, DailyEnergyData,
    AnnualResults
)
from core.weather_api import detect_location, fetch_hourly_weather, create_typical_year_weather
from core.preprocess import (
    clean_weather_data, align_daily_energy_to_hourly,
    create_hourly_indoor_temp, validate_data_quality, merge_hourly_data
)
from core.baseline_split import split_heating_and_tuv
from core.calibrator import calibrate_model_simple
from core.simulate_year import (
    simulate_annual_heating_demand, calculate_primary_energy,
    estimate_uncertainty_bounds
)
from core.metrics import classify_energy_label, get_class_description, get_class_color
from core.quality_flags import assess_quality_level, generate_disclaimers, suggest_improvements
from reports.report_builder import generate_html_report, save_html_report


# Konfigurace stránky
st.set_page_config(
    page_title="Orientační Energetický Štítek",
    page_icon="🏠",
    layout="wide"
)


def main():
    st.title("🏠 Orientační Energetický Štítek")
    st.markdown("*Odhad energetické náročnosti bytu z provozních dat*")
    
    # Sidebar - nastavení
    with st.sidebar:
        st.header("⚙️ Nastavení")
        
        # API klíč
        st.subheader("WeatherAPI.com")
        api_key = get_api_key()
        
        api_key_input = st.text_input(
            "API klíč",
            value=api_key or "",
            type="password",
            help="Získejte zdarma na https://www.weatherapi.com/"
        )
        
        if api_key_input and api_key_input != api_key:
            set_api_key(api_key_input)
            st.success("✓ API klíč uložen")
            api_key = api_key_input
        
        if not api_key:
            st.warning("⚠ Zadejte API klíč pro stahování počasí")
        
        st.divider()
        
        # Režim výpočtu
        st.subheader("Režim výpočtu")
        mode = st.selectbox(
            "Kvalita",
            options=[
                ComputationMode.BASIC,
                ComputationMode.STANDARD,
                ComputationMode.ADVANCED
            ],
            index=1,
            format_func=lambda x: {
                ComputationMode.BASIC: "🔸 BASIC (rychlý odhad)",
                ComputationMode.STANDARD: "🔹 STANDARD (doporučeno)",
                ComputationMode.ADVANCED: "🔺 ADVANCED (pokročilé)"
            }[x]
        )
        
        # Info o režimu
        mode_info = {
            ComputationMode.BASIC: "Min. 1 den dat, hrubý lineární odhad",
            ComputationMode.STANDARD: "Min. 7 dní dat, 1R1C model s kalibrací",
            ComputationMode.ADVANCED: "Min. 28 dní dat, globální optimalizace"
        }
        st.info(mode_info[mode])
    
    # Hlavní obsah - tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1️⃣ Lokalita",
        "2️⃣ Byt & Systém",
        "3️⃣ Data",
        "4️⃣ Výpočet",
        "5️⃣ Výsledky"
    ])
    
    # === TAB 1: Lokalita ===
    with tab1:
        st.header("📍 Lokalita")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Auto-detekce
            if st.button("🌍 Automaticky detekovat lokaci"):
                with st.spinner("Detekovám lokaci..."):
                    city, lat, lng = detect_location()
                    location_str = f"{city}"
                    st.session_state['location'] = location_str
                    st.success(f"✓ Detekováno: {city} ({lat:.4f}, {lng:.4f})")
            
            # Ruční zadání
            last_loc = get_last_location()
            location = st.text_input(
                "Město nebo souřadnice (lat,lon)",
                value=st.session_state.get('location', last_loc or "Praha"),
                help="Např. 'Praha' nebo '50.0755,14.4378'"
            )
            
            st.session_state['location'] = location
            
            if location:
                set_last_location(location)
        
        with col2:
            st.info(
                "Lokalita se používá pro stažení "
                "historického počasí a vytvoření "
                "typického meteorologického roku."
            )
    
    # === TAB 2: Byt & Systém ===
    with tab2:
        st.header("🏠 Parametry bytu")
        
        col1, col2 = st.columns(2)
        
        with col1:
            area = st.number_input(
                "Plocha bytu (m²)",
                min_value=10.0,
                max_value=500.0,
                value=70.0,
                step=5.0
            )
            
            height = st.number_input(
                "Výška stropu (m)",
                min_value=2.0,
                max_value=5.0,
                value=2.7,
                step=0.1
            )
            
            volume = area * height
            st.metric("Objem bytu", f"{volume:.1f} m³")
        
        with col2:
            st.subheader("Komfortní teploty")
            
            temp_day = st.slider(
                "Denní teplota (6:00 - 22:00)",
                min_value=18.0,
                max_value=24.0,
                value=21.0,
                step=0.5
            )
            
            temp_night = st.slider(
                "Noční teplota (22:00 - 6:00)",
                min_value=16.0,
                max_value=24.0,
                value=19.0,
                step=0.5
            )
        
        st.divider()
        st.header("🔥 Systém vytápění")
        
        col1, col2 = st.columns(2)
        
        with col1:
            system_type = st.selectbox(
                "Typ zdroje",
                options=list(HeatingSystemType),
                format_func=lambda x: {
                    HeatingSystemType.CONDENSING_BOILER: "Kondenzační plynový kotel",
                    HeatingSystemType.DIRECT_ELECTRIC: "Přímotopné elektrické",
                    HeatingSystemType.HEAT_PUMP_AIR: "Tepelné čerpadlo vzduch/voda",
                    HeatingSystemType.HEAT_PUMP_WATER: "Tepelné čerpadlo voda/voda",
                    HeatingSystemType.UNKNOWN: "Neznámé / jiné"
                }[x]
            )
        
        with col2:
            efficiency_known = st.checkbox(
                "Znám účinnost/COP",
                value=False
            )
            
            if efficiency_known:
                if system_type in [HeatingSystemType.HEAT_PUMP_AIR, HeatingSystemType.HEAT_PUMP_WATER]:
                    efficiency = st.number_input(
                        "COP tepelného čerpadla",
                        min_value=1.0,
                        max_value=6.0,
                        value=3.0,
                        step=0.1
                    )
                else:
                    efficiency = st.number_input(
                        "Účinnost kotle",
                        min_value=0.5,
                        max_value=1.0,
                        value=0.9,
                        step=0.01
                    )
            else:
                efficiency = None
                heating_info = HeatingSystemInfo(
                    system_type=system_type,
                    efficiency_or_cop=None
                )
                eff_range = heating_info.get_default_efficiency()
                st.info(f"Použiji výchozí rozsah: {eff_range[0]:.2f} - {eff_range[1]:.2f}")
    
    # === TAB 3: Data ===
    with tab3:
        st.header("📊 Denní spotřeby energie")
        
        st.markdown(
            """
            Zadejte denní spotřeby energie z vašeho měřidla (plynoměr / elektroměr).
            - Pro BASIC: min. 1 den
            - Pro STANDARD: min. 7 dní
            - Pro ADVANCED: min. 28 dní
            """
        )
        
        # Možnosti zadání
        input_method = st.radio(
            "Způsob zadání",
            options=["Nahrát CSV", "Zadat ručně"],
            horizontal=True
        )
        
        daily_energy_data = []
        
        if input_method == "Nahrát CSV":
            uploaded_file = st.file_uploader(
                "Nahrajte CSV soubor",
                type=['csv'],
                help="CSV s sloupci: date (YYYY-MM-DD), energy_total_kwh"
            )
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    df['date'] = pd.to_datetime(df['date']).dt.date
                    
                    st.success(f"✓ Načteno {len(df)} záznamů")
                    st.dataframe(df.head(10))
                    
                    daily_energy_data = [
                        DailyEnergyData(date=row['date'], energy_total_kwh=row['energy_total_kwh'])
                        for _, row in df.iterrows()
                    ]
                    
                except Exception as e:
                    st.error(f"Chyba při načítání: {e}")
        
        else:  # Ruční zadání
            st.markdown("**Příklad pro demonstraci:**")
            
            n_days = st.slider("Počet dní", 7, 30, 14)
            
            # Generuj ukázková data
            if st.button("Generovat ukázková data"):
                start_date = date.today() - timedelta(days=n_days)
                
                demo_data = []
                for i in range(n_days):
                    current_date = start_date + timedelta(days=i)
                    # Simuluj spotřebu (vyšší v zimě)
                    base = 8.0 + 3.0 * abs((i - n_days/2) / n_days)
                    demo_data.append({
                        'date': current_date,
                        'energy_total_kwh': base
                    })
                
                st.session_state['demo_data'] = pd.DataFrame(demo_data)
            
            if 'demo_data' in st.session_state:
                df_edit = st.data_editor(
                    st.session_state['demo_data'],
                    num_rows="dynamic",
                    use_container_width=True
                )
                
                daily_energy_data = [
                    DailyEnergyData(date=row['date'], energy_total_kwh=row['energy_total_kwh'])
                    for _, row in df_edit.iterrows()
                ]
        
        st.session_state['daily_energy_data'] = daily_energy_data
        
        st.divider()
        st.header("🌡️ Vnitřní teplota")
        
        has_hourly_temp = st.checkbox(
            "Mám hodinová měření vnitřní teploty",
            value=False
        )
        
        if has_hourly_temp:
            st.warning("⚠ Hodinová data zatím nejsou plně podporována v MVP. Použijte průměr.")
            has_hourly_temp = False
        
        avg_indoor_temp = st.slider(
            "Průměrná vnitřní teplota (°C)",
            min_value=16.0,
            max_value=26.0,
            value=21.0,
            step=0.5,
            help="Odhadněte průměrnou teplotu ve vašem bytě během sledovaného období"
        )
        
        st.session_state['avg_indoor_temp'] = avg_indoor_temp
    
    # === TAB 4: Výpočet ===
    with tab4:
        st.header("⚙️ Spustit výpočet")
        
        # Kontrola před výpočtem
        can_compute = True
        issues = []
        
        if not api_key:
            issues.append("❌ Chybí API klíč pro počasí")
            can_compute = False
        
        if 'location' not in st.session_state or not st.session_state['location']:
            issues.append("❌ Není zadána lokalita")
            can_compute = False
        
        if 'daily_energy_data' not in st.session_state or len(st.session_state['daily_energy_data']) == 0:
            issues.append("❌ Nejsou zadána data o spotřebě")
            can_compute = False
        else:
            n_days = len(st.session_state['daily_energy_data'])
            min_days = {
                ComputationMode.BASIC: 1,
                ComputationMode.STANDARD: 7,
                ComputationMode.ADVANCED: 28
            }[mode]
            
            if n_days < min_days:
                issues.append(f"❌ Málo dat: {n_days} dní (potřeba min. {min_days})")
                can_compute = False
        
        if issues:
            for issue in issues:
                st.warning(issue)
        else:
            st.success("✓ Vše připraveno k výpočtu")
        
        st.divider()
        
        if st.button("🚀 SPUSTIT VÝPOČET", disabled=not can_compute, type="primary"):
            with st.spinner("Probíhá výpočet..."):
                try:
                    results = run_computation(
                        location=st.session_state['location'],
                        area=area,
                        height=height,
                        system_type=system_type,
                        efficiency=efficiency,
                        temp_day=temp_day,
                        temp_night=temp_night,
                        daily_energy_data=st.session_state['daily_energy_data'],
                        avg_indoor_temp=st.session_state['avg_indoor_temp'],
                        mode=mode,
                        api_key=api_key
                    )
                    
                    st.session_state['results'] = results
                    st.success("✓ Výpočet dokončen!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Chyba při výpočtu: {e}")
                    st.exception(e)
    
    # === TAB 5: Výsledky ===
    with tab5:
        if 'results' in st.session_state:
            display_results(st.session_state['results'])
        else:
            st.info("👈 Proveďte výpočet v předchozí záložce")


def run_computation(
    location, area, height, system_type, efficiency,
    temp_day, temp_night, daily_energy_data, avg_indoor_temp,
    mode, api_key
):
    """Hlavní výpočetní funkce"""
    
    # 1. Vytvoř user inputs
    geometry = ApartmentGeometry(area_m2=area, height_m=height)
    heating_system = HeatingSystemInfo(
        system_type=system_type,
        efficiency_or_cop=efficiency
    )
    comfort_temp = TemperatureProfile(day_temp_c=temp_day, night_temp_c=temp_night)
    
    user_inputs = UserInputs(
        geometry=geometry,
        heating_system=heating_system,
        location=location,
        computation_mode=mode,
        comfort_temperature=comfort_temp,
        daily_energy=daily_energy_data,
        avg_indoor_temp_c=avg_indoor_temp
    )
    
    # 2. Stáhni počasí
    st.write("📡 Stahuji počasí...")
    dates = [d.date for d in daily_energy_data]
    min_date = min(dates)
    max_date = max(dates)
    
    weather_df = fetch_hourly_weather(location, min_date, max_date, api_key)
    weather_df = clean_weather_data(weather_df)
    
    # 3. Preprocessing
    st.write("🔧 Preprocessing dat...")
    daily_df = pd.DataFrame([d.model_dump() for d in daily_energy_data])
    daily_df, weather_df = align_daily_energy_to_hourly(daily_df, weather_df)
    
    indoor_temp_df = create_hourly_indoor_temp(avg_indoor_temp, weather_df)
    hourly_df = merge_hourly_data(weather_df, indoor_temp_df)
    
    warnings = validate_data_quality(daily_df, hourly_df)
    
    # 4. Baseline TUV
    st.write("💧 Odhaduji baseline TUV...")
    daily_df = split_heating_and_tuv(daily_df)
    baseline_tuv = daily_df['baseline_tuv_kwh'].iloc[0]
    
    # 5. Kalibrace
    st.write("🎯 Kalibruji model...")
    calibrated = calibrate_model_simple(
        daily_df,
        hourly_df,
        geometry.volume_m3,
        geometry.area_m2,
        avg_indoor_temp,
        baseline_tuv,
        mode=mode.value
    )
    
    # 6. Typický rok
    st.write("☀️ Vytvářím typický rok...")
    typical_year = create_typical_year_weather(location, api_key)
    
    # 7. Simulace roku
    st.write("📅 Simuluji roční potřebu...")
    annual_sim = simulate_annual_heating_demand(
        calibrated,
        typical_year,
        geometry.volume_m3,
        geometry.area_m2,
        comfort_temp
    )
    
    heating_demand_kwh = annual_sim['heating_demand_W'].sum() / 1000
    heating_per_m2 = heating_demand_kwh / area
    
    # 8. Primární energie
    eff_final = efficiency if efficiency else heating_system.get_default_efficiency()[0]
    primary = calculate_primary_energy(
        heating_demand_kwh,
        system_type.value,
        eff_final
    )
    primary_per_m2 = primary / area
    
    # 9. Klasifikace
    energy_class = classify_energy_label(heating_per_m2, primary_per_m2)
    
    # 10. Kvalita
    quality = assess_quality_level(mode, len(daily_df), calibrated, warnings)
    
    # 11. Nejistota
    lower, upper = estimate_uncertainty_bounds(calibrated, heating_per_m2, warnings)
    
    # 12. Disclaimery a návrhy
    disclaimers = generate_disclaimers(quality, mode, len(daily_df), warnings)
    suggestions = suggest_improvements(quality, mode, len(daily_df), calibrated)
    
    annual_results = AnnualResults(
        heating_demand_kwh_per_m2_year=heating_per_m2,
        primary_energy_kwh_per_m2_year=primary_per_m2,
        energy_class=energy_class,
        quality_level=quality,
        heating_demand_lower_bound=lower,
        heating_demand_upper_bound=upper,
        disclaimers=disclaimers
    )
    
    return {
        'annual_results': annual_results,
        'calibrated': calibrated,
        'user_inputs': user_inputs,
        'suggestions': suggestions,
        'warnings': warnings
    }


def display_results(results):
    """Zobrazí výsledky"""
    annual = results['annual_results']
    calibrated = results['calibrated']
    user_inputs = results['user_inputs']
    
    st.header("🎉 Výsledky")
    
    # Energetická třída
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        class_color = get_class_color(annual.energy_class)
        st.markdown(
            f"""
            <div style='text-align: center; padding: 40px; background: {class_color}; 
                        border-radius: 15px; color: white;'>
                <h1 style='font-size: 80px; margin: 0;'>Třída {annual.energy_class.value}</h1>
                <p style='font-size: 20px;'>{get_class_description(annual.energy_class)}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.divider()
    
    # Metriky
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        "Měrná potřeba tepla",
        f"{annual.heating_demand_kwh_per_m2_year:.1f}",
        help="kWh/(m²·rok)"
    )
    
    col2.metric(
        "Primární energie",
        f"{annual.primary_energy_kwh_per_m2_year:.1f}",
        help="kWh/(m²·rok) - orientačně"
    )
    
    col3.metric(
        "Spolehlivost",
        annual.quality_level.value.upper()
    )
    
    col4.metric(
        "MAPE kalibrace",
        f"{calibrated.mape_energy_pct:.1f}%"
    )
    
    # Grafy
    st.subheader("📊 Grafy")
    
    # TODO: Přidat grafy (pozorovaná vs. modelovaná teplota, spotřeba, atd.)
    st.info("Grafy budou doplněny v další iteraci")
    
    # Disclaimery
    st.subheader("⚠️ Upozornění")
    for disc in annual.disclaimers:
        st.warning(disc)
    
    # Návrhy
    if results['suggestions']:
        st.subheader("💡 Doporučení")
        for sug in results['suggestions']:
            st.info(sug)
    
    # Export
    st.divider()
    st.subheader("📄 Export reportu")
    
    if st.button("Vygenerovat HTML report"):
        html = generate_html_report(
            annual,
            calibrated,
            user_inputs,
            results['suggestions']
        )
        
        filename = f"energy_label_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = Path("reports") / filename
        filepath.parent.mkdir(exist_ok=True)
        
        save_html_report(html, str(filepath))
        
        st.success(f"✓ Report uložen: {filepath}")
        
        # Download button
        st.download_button(
            "📥 Stáhnout HTML",
            html,
            file_name=filename,
            mime="text/html"
        )


if __name__ == "__main__":
    main()
