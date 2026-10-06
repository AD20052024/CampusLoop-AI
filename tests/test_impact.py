import pytest
from app.services.impact import (
    calculate_impact,
    CO2E_PER_KG_FOOD,
    WATER_LITERS_PER_KG_FOOD,
    KG_PER_MEAL_PORTION,
    ESTIMATED_COST_PER_KG,
)


def test_standard_impact_calculation():
    predicted_waste = 20.0
    impact = calculate_impact(predicted_waste, reduction_rate=0.20)

    expected_prevented = 4.0
    assert impact["predicted_waste"] == 20.0
    assert impact["estimated_waste_prevented"] == expected_prevented
    assert impact["estimated_remaining_waste"] == 16.0
    assert impact["estimated_reduction_percent"] == 20.0

    # SDG 12 Environmental Metrics
    assert impact["co2e_prevented_kg"] == round(expected_prevented * CO2E_PER_KG_FOOD, 2)
    assert impact["water_saved_liters"] == round(expected_prevented * WATER_LITERS_PER_KG_FOOD, 2)
    assert impact["meals_salvaged"] == round(expected_prevented / KG_PER_MEAL_PORTION, 1)
    assert impact["financial_savings_estimated"] == round(expected_prevented * ESTIMATED_COST_PER_KG, 2)


def test_zero_waste_impact():
    impact = calculate_impact(0.0)
    assert impact["estimated_waste_prevented"] == 0.0
    assert impact["co2e_prevented_kg"] == 0.0
    assert impact["water_saved_liters"] == 0.0
    assert impact["meals_salvaged"] == 0.0
    assert impact["financial_savings_estimated"] == 0.0


def test_negative_waste_clamped_to_zero():
    impact = calculate_impact(-10.0)
    assert impact["predicted_waste"] == 0.0
    assert impact["estimated_waste_prevented"] == 0.0


def test_reduction_rate_bounds():
    # Rate > 1.0 clamped to 1.0
    impact = calculate_impact(10.0, reduction_rate=1.5)
    assert impact["estimated_reduction_percent"] == 100.0
    assert impact["estimated_waste_prevented"] == 10.0
