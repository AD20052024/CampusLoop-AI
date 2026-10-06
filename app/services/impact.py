from typing import Any, Dict

# Sustainability Conversion Factors (UN SDG 12 Alignment)
# Source References: FAO Food Wastage Footprint, EPA WARM, and USDA meal equivalence benchmarks
CO2E_PER_KG_FOOD = 2.50         # kg CO2e greenhouse gas emissions per kg food waste
WATER_LITERS_PER_KG_FOOD = 850.0 # Liters of embedded agricultural water per kg food
KG_PER_MEAL_PORTION = 0.45      # kg per standardized diverted meal portion (~1 lb)
ESTIMATED_COST_PER_KG = 3.50    # Estimated procurement/preparation cost in USD per kg food


def calculate_impact(
    predicted_waste: float,
    reduction_rate: float = 0.20,
) -> Dict[str, Any]:
    """
    Compute projected environmental and economic benefits resulting from
    waste-prevention interventions aligned primarily with UN SDG 12.

    Parameters:
    - predicted_waste: Baseline predicted food waste in kg.
    - reduction_rate: Assumed operational intervention efficiency (default: 20%).
    """
    waste = max(float(predicted_waste), 0.0)
    rate = max(min(float(reduction_rate), 1.0), 0.0)

    estimated_reduction = waste * rate
    remaining_waste = waste - estimated_reduction

    co2e_prevented = estimated_reduction * CO2E_PER_KG_FOOD
    water_saved = estimated_reduction * WATER_LITERS_PER_KG_FOOD
    meals_salvaged = estimated_reduction / KG_PER_MEAL_PORTION if KG_PER_MEAL_PORTION > 0 else 0.0
    financial_savings = estimated_reduction * ESTIMATED_COST_PER_KG

    return {
        "predicted_waste": round(waste, 2),
        "estimated_waste_prevented": round(estimated_reduction, 2),
        "estimated_remaining_waste": round(remaining_waste, 2),
        "estimated_reduction_percent": round(rate * 100, 2),
        "co2e_prevented_kg": round(co2e_prevented, 2),
        "water_saved_liters": round(water_saved, 2),
        "meals_salvaged": round(meals_salvaged, 1),
        "financial_savings_estimated": round(financial_savings, 2),
    }