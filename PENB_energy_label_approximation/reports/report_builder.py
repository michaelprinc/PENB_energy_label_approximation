"""
Generátor HTML reportů
"""
from datetime import datetime
from jinja2 import Template
import pandas as pd
from core.data_models import (
    AnnualResults, CalibratedParameters, UserInputs,
    EnergyClass, QualityLevel
)
from core.metrics import get_class_description, get_class_color


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Orientační Energetický Štítek - {{ location }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 30px;
        }
        .energy-class {
            font-size: 72px;
            font-weight: bold;
            text-align: center;
            padding: 30px;
            color: white;
            border-radius: 10px;
            margin: 20px 0;
            background-color: {{ class_color }};
        }
        .metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        .metric {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }
        .metric-label {
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .disclaimer {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }
        .suggestion {
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin: 10px 0;
        }
        .quality-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }
        .quality-high { background: #28a745; }
        .quality-medium { background: #ffc107; color: #333; }
        .quality-low { background: #dc3545; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f9f9f9;
            font-weight: bold;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Orientační Energetický Štítek</h1>
        
        <p><strong>Lokalita:</strong> {{ location }}</p>
        <p><strong>Datum výpočtu:</strong> {{ computation_date }}</p>
        <p><strong>Spolehlivost:</strong> 
            <span class="quality-badge quality-{{ quality_level }}">{{ quality_label }}</span>
        </p>
        
        <div class="energy-class">
            Třída {{ energy_class }}
        </div>
        
        <p style="text-align: center; color: #666;">
            {{ class_description }}
        </p>
        
        <h2>📈 Výsledky</h2>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Měrná potřeba tepla</div>
                <div class="metric-value">{{ heating_demand }} kWh/(m²·rok)</div>
            </div>
            
            <div class="metric">
                <div class="metric-label">Primární energie (orientačně)</div>
                <div class="metric-value">{{ primary_energy }} kWh/(m²·rok)</div>
            </div>
            
            <div class="metric">
                <div class="metric-label">Plocha bytu</div>
                <div class="metric-value">{{ area }} m²</div>
            </div>
            
            <div class="metric">
                <div class="metric-label">Celková roční spotřeba</div>
                <div class="metric-value">{{ total_annual }} kWh/rok</div>
            </div>
        </div>
        
        {% if uncertainty_lower and uncertainty_upper %}
        <p style="color: #666; font-size: 14px;">
            <em>Interval spolehlivosti: {{ uncertainty_lower }} - {{ uncertainty_upper }} kWh/(m²·rok)</em>
        </p>
        {% endif %}
        
        <h2>🏠 Parametry bytu</h2>
        
        <table>
            <tr>
                <th>Parametr</th>
                <th>Hodnota</th>
            </tr>
            <tr>
                <td>Plocha</td>
                <td>{{ area }} m²</td>
            </tr>
            <tr>
                <td>Výška stropu</td>
                <td>{{ height }} m</td>
            </tr>
            <tr>
                <td>Objem</td>
                <td>{{ volume }} m³</td>
            </tr>
            <tr>
                <td>Systém vytápění</td>
                <td>{{ heating_system }}</td>
            </tr>
            <tr>
                <td>Účinnost/COP</td>
                <td>{{ efficiency }}</td>
            </tr>
        </table>
        
        <h2>🔧 Kalibrované parametry modelu</h2>
        
        <table>
            <tr>
                <th>Parametr</th>
                <th>Hodnota</th>
            </tr>
            <tr>
                <td>Tepelné ztráty obálkou (H_env)</td>
                <td>{{ h_env }} W/K</td>
            </tr>
            <tr>
                <td>Intenzita infiltrace</td>
                <td>{{ infiltration }} 1/h</td>
            </tr>
            <tr>
                <td>Tepelná kapacita</td>
                <td>{{ c_th }} MJ/K</td>
            </tr>
            <tr>
                <td>Baseline TUV</td>
                <td>{{ baseline_tuv }} kWh/den</td>
            </tr>
            <tr>
                <td>RMSE teploty</td>
                <td>{{ rmse_temp }} °C</td>
            </tr>
            <tr>
                <td>MAPE energie</td>
                <td>{{ mape_energy }} %</td>
            </tr>
        </table>
        
        <h2>⚠️ Upozornění</h2>
        
        {% for disclaimer in disclaimers %}
        <div class="disclaimer">
            {{ disclaimer }}
        </div>
        {% endfor %}
        
        {% if suggestions %}
        <h2>💡 Doporučení</h2>
        
        {% for suggestion in suggestions %}
        <div class="suggestion">
            {{ suggestion }}
        </div>
        {% endfor %}
        {% endif %}
        
        <div class="footer">
            <p>Vygenerováno aplikací pro orientační odhad energetické náročnosti</p>
            <p>NENÍ oficiální PENB podle vyhlášky č. 264/2020 Sb.</p>
        </div>
    </div>
</body>
</html>
"""


def generate_html_report(
    annual_results: AnnualResults,
    calibrated_params: CalibratedParameters,
    user_inputs: UserInputs,
    suggestions: list[str]
) -> str:
    """
    Vygeneruje HTML report.
    
    Returns:
        HTML string
    """
    # Připrav data pro šablonu
    template = Template(HTML_TEMPLATE)
    
    # Mapování quality level
    quality_map = {
        QualityLevel.HIGH: ("VYSOKÁ", "high"),
        QualityLevel.MEDIUM: ("STŘEDNÍ", "medium"),
        QualityLevel.LOW: ("NÍZKÁ", "low")
    }
    
    quality_label, quality_css = quality_map[annual_results.quality_level]
    
    # Rendering
    html = template.render(
        location=user_inputs.location,
        computation_date=annual_results.computation_date.strftime("%d.%m.%Y %H:%M"),
        energy_class=annual_results.energy_class.value,
        class_description=get_class_description(annual_results.energy_class),
        class_color=get_class_color(annual_results.energy_class),
        quality_level=quality_css,
        quality_label=quality_label,
        heating_demand=f"{annual_results.heating_demand_kwh_per_m2_year:.1f}",
        primary_energy=f"{annual_results.primary_energy_kwh_per_m2_year:.1f}",
        area=f"{user_inputs.geometry.area_m2:.1f}",
        height=f"{user_inputs.geometry.height_m:.2f}",
        volume=f"{user_inputs.geometry.volume_m3:.1f}",
        total_annual=f"{annual_results.heating_demand_kwh_per_m2_year * user_inputs.geometry.area_m2:.0f}",
        heating_system=user_inputs.heating_system.system_type.value.replace('_', ' ').title(),
        efficiency=f"{user_inputs.heating_system.efficiency_or_cop:.2f}" if user_inputs.heating_system.efficiency_or_cop else "Výchozí",
        h_env=f"{calibrated_params.H_env_W_per_K:.1f}",
        infiltration=f"{calibrated_params.infiltration_rate_per_h:.3f}",
        c_th=f"{calibrated_params.C_th_J_per_K / 1e6:.1f}",
        baseline_tuv=f"{calibrated_params.baseline_TUV_kwh_per_day:.2f}",
        rmse_temp=f"{calibrated_params.rmse_temperature_c:.2f}",
        mape_energy=f"{calibrated_params.mape_energy_pct:.1f}",
        disclaimers=annual_results.disclaimers,
        suggestions=suggestions,
        uncertainty_lower=f"{annual_results.heating_demand_lower_bound:.1f}" if annual_results.heating_demand_lower_bound else None,
        uncertainty_upper=f"{annual_results.heating_demand_upper_bound:.1f}" if annual_results.heating_demand_upper_bound else None
    )
    
    return html


def save_html_report(html: str, filepath: str):
    """Uloží HTML report do souboru"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Report uložen: {filepath}")
