"""
Hodnocení kvality a spolehlivosti výsledků
"""
from core.data_models import QualityLevel, CalibratedParameters, ComputationMode


def assess_quality_level(
    computation_mode: ComputationMode,
    n_days_data: int,
    calibrated_params: CalibratedParameters,
    data_warnings: list
) -> QualityLevel:
    """
    Vyhodnotí úroveň spolehlivosti výsledků.
    
    Args:
        computation_mode: použitý režim výpočtu
        n_days_data: počet dní dat
        calibrated_params: parametry kalibrace
        data_warnings: seznam varování z validace
    
    Returns:
        QualityLevel
    """
    # Skóre kvality (čím vyšší, tím lepší)
    score = 0
    
    # 1. Režim výpočtu
    if computation_mode == ComputationMode.ADVANCED:
        score += 30
    elif computation_mode == ComputationMode.STANDARD:
        score += 20
    else:  # BASIC
        score += 5
    
    # 2. Délka dat
    if n_days_data >= 28:
        score += 30
    elif n_days_data >= 14:
        score += 20
    elif n_days_data >= 7:
        score += 10
    else:
        score += 2
    
    # 3. Kvalita kalibrace (RMSE teploty)
    if calibrated_params.rmse_temperature_c < 0.5:
        score += 20
    elif calibrated_params.rmse_temperature_c < 1.0:
        score += 15
    elif calibrated_params.rmse_temperature_c < 2.0:
        score += 10
    else:
        score += 2
    
    # 4. Kvalita kalibrace (MAPE energie)
    if calibrated_params.mape_energy_pct < 5:
        score += 20
    elif calibrated_params.mape_energy_pct < 10:
        score += 15
    elif calibrated_params.mape_energy_pct < 20:
        score += 10
    else:
        score += 2
    
    # 5. Penalizace za varování
    score -= len(data_warnings) * 5
    
    score = max(0, score)  # minimálně 0
    
    # Rozhodni podle skóre
    if score >= 70:
        quality = QualityLevel.HIGH
    elif score >= 40:
        quality = QualityLevel.MEDIUM
    else:
        quality = QualityLevel.LOW
    
    return quality


def generate_disclaimers(
    quality_level: QualityLevel,
    computation_mode: ComputationMode,
    n_days_data: int,
    data_warnings: list
) -> list[str]:
    """
    Generuje upozornění a disclaimery k výsledkům.
    
    Returns:
        Seznam textů
    """
    disclaimers = []
    
    # Základní disclaimer
    disclaimers.append(
        "⚠ Toto NENÍ oficiální Průkaz energetické náročnosti budovy (PENB). "
        "Jedná se o orientační odhad na základě provozních dat."
    )
    
    # Podle kvality
    if quality_level == QualityLevel.LOW:
        disclaimers.append(
            "⚠ NÍZKÁ spolehlivost výsledků. Doporučujeme doplnit více dat nebo "
            "použít vyšší režim výpočtu."
        )
    elif quality_level == QualityLevel.MEDIUM:
        disclaimers.append(
            "✓ STŘEDNÍ spolehlivost výsledků. Výsledky jsou orientační."
        )
    else:  # HIGH
        disclaimers.append(
            "✓ VYSOKÁ spolehlivost výsledků v rámci možností provozních dat."
        )
    
    # Podle režimu
    if computation_mode == ComputationMode.BASIC:
        disclaimers.append(
            "Použit režim BASIC - pouze hrubý lineární odhad bez dynamické simulace."
        )
    
    # Délka dat
    if n_days_data < 14:
        disclaimers.append(
            f"Málo dat ({n_days_data} dní). Doporučeno alespoň 14-28 dní pro lepší odhad."
        )
    
    # Varování z dat
    if len(data_warnings) > 0:
        disclaimers.append(
            f"Zjištěno {len(data_warnings)} varování v kvalitě dat. "
            "Viz detailní zpráva."
        )
    
    # Metodika
    disclaimers.append(
        "Výpočet používá zjednodušený 1R1C tepelný model kalibrovaný "
        "na provozní data. Nezohledňuje všechny faktory jako oficiální PENB."
    )
    
    return disclaimers


def suggest_improvements(
    quality_level: QualityLevel,
    computation_mode: ComputationMode,
    n_days_data: int,
    calibrated_params: CalibratedParameters
) -> list[str]:
    """
    Navrhne zlepšení pro lepší výsledky.
    
    Returns:
        Seznam návrhů
    """
    suggestions = []
    
    if computation_mode == ComputationMode.BASIC:
        suggestions.append(
            "📈 Použijte režim STANDARD nebo ADVANCED pro přesnější výsledky"
        )
    
    if n_days_data < 28:
        suggestions.append(
            f"📅 Doplňte více dat - máte {n_days_data} dní, doporučeno 28+ dní"
        )
    
    if calibrated_params.rmse_temperature_c > 2.0:
        suggestions.append(
            "🌡️ Vysoká odchylka vnitřní teploty - zkontrolujte, zda jste zadali "
            "správnou průměrnou teplotu nebo poskytněte hodinová měření"
        )
    
    if calibrated_params.mape_energy_pct > 20:
        suggestions.append(
            "⚡ Vysoká odchylka energie - zkontrolujte správnost odečtů spotřeby, "
            "případně označte dny s extrémním chováním (velké větrání, výpadky, ...)"
        )
    
    # Fyzikální návrhy
    H_total = calibrated_params.H_env_W_per_K + (
        1.2 * 1005 * calibrated_params.infiltration_rate_per_h / 3600
    )
    
    if calibrated_params.infiltration_rate_per_h > 0.8:
        suggestions.append(
            "🪟 Vysoká infiltrace (únik vzduchu). Zvažte výměnu oken nebo "
            "těsnění pro úsporu energie."
        )
    
    if calibrated_params.H_env_W_per_K > 200:
        suggestions.append(
            "🏠 Vysoké tepelné ztráty obálkou. Zvažte zateplení stěn/střechy."
        )
    
    if quality_level == QualityLevel.HIGH:
        suggestions.append(
            "✓ Kvalita výsledků je dobrá. Pro oficiální PENB kontaktujte "
            "oprávněnou osobu."
        )
    
    return suggestions
