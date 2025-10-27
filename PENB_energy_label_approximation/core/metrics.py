"""
Klasifikace do energetických tříd a výpočet metrik
"""
from core.data_models import EnergyClass


def classify_energy_label(
    heating_demand_kwh_per_m2_year: float,
    primary_energy_kwh_per_m2_year: float,
    use_primary: bool = True
) -> EnergyClass:
    """
    Přiřadí orientační energetickou třídu.
    
    Poznámka: Toto jsou ZJEDNODUŠENÉ hranice pro ilustraci!
    Skutečný PENB používá složitější metodiku podle TNI 73 0329/Z1.
    
    Args:
        heating_demand_kwh_per_m2_year: měrná potřeba tepla
        primary_energy_kwh_per_m2_year: primární energie
        use_primary: použít primární energii (True) nebo potřebu tepla (False)
    
    Returns:
        EnergyClass
    """
    value = primary_energy_kwh_per_m2_year if use_primary else heating_demand_kwh_per_m2_year
    
    # Orientační hranice (pro bytové domy, zjednodušené)
    if use_primary:
        # Primární energie
        if value < 50:
            return EnergyClass.A
        elif value < 75:
            return EnergyClass.B
        elif value < 110:
            return EnergyClass.C
        elif value < 150:
            return EnergyClass.D
        elif value < 200:
            return EnergyClass.E
        elif value < 270:
            return EnergyClass.F
        else:
            return EnergyClass.G
    else:
        # Potřeba tepla
        if value < 30:
            return EnergyClass.A
        elif value < 50:
            return EnergyClass.B
        elif value < 75:
            return EnergyClass.C
        elif value < 100:
            return EnergyClass.D
        elif value < 130:
            return EnergyClass.E
        elif value < 180:
            return EnergyClass.F
        else:
            return EnergyClass.G


def get_class_description(energy_class: EnergyClass) -> str:
    """Vrátí popisek třídy"""
    descriptions = {
        EnergyClass.A: "Mimořádně úsporná",
        EnergyClass.B: "Velmi úsporná",
        EnergyClass.C: "Úsporná",
        EnergyClass.D: "Méně úsporná",
        EnergyClass.E: "Nehospodárná",
        EnergyClass.F: "Velmi nehospodárná",
        EnergyClass.G: "Mimořádně nehospodárná"
    }
    return descriptions.get(energy_class, "Neznámá")


def get_class_color(energy_class: EnergyClass) -> str:
    """Vrátí barvu pro vizualizaci"""
    colors = {
        EnergyClass.A: "#00A651",  # zelená
        EnergyClass.B: "#4AB849",
        EnergyClass.C: "#C5D82F",  # žlutozelená
        EnergyClass.D: "#FFF200",  # žlutá
        EnergyClass.E: "#FDB913",  # oranžová
        EnergyClass.F: "#F37021",
        EnergyClass.G: "#ED1C24"   # červená
    }
    return colors.get(energy_class, "#CCCCCC")
