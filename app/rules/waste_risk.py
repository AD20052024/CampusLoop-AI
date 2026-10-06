from typing import Any, Dict

LOW_RISK_THRESHOLD = 10.0
MEDIUM_RISK_THRESHOLD = 25.0


def calculate_risk(predicted_waste: float) -> Dict[str, Any]:
    """
    Categorize predicted waste into operational risk tiers.

    Threshold logic:
    - Low: < 10.0 kg (routine monitoring)
    - Medium: 10.0 kg to 24.99 kg (heightened monitoring and kitchen adjustments)
    - High: >= 25.0 kg (critical intervention required: batch reduction / redistribution)
    """
    predicted_val = round(max(float(predicted_waste), 0.0), 2)

    if predicted_val < LOW_RISK_THRESHOLD:
        level = "Low"
        priority = "Standard"
        reason = f"Projected waste of {predicted_val} kg is within standard operating tolerance (< {LOW_RISK_THRESHOLD} kg)."
    elif predicted_val < MEDIUM_RISK_THRESHOLD:
        level = "Medium"
        priority = "Elevated"
        reason = f"Projected waste of {predicted_val} kg exceeds baseline threshold ({LOW_RISK_THRESHOLD} kg) but remains under critical threshold ({MEDIUM_RISK_THRESHOLD} kg)."
    else:
        level = "High"
        priority = "Critical"
        reason = f"Projected waste of {predicted_val} kg exceeds critical threshold (>= {MEDIUM_RISK_THRESHOLD} kg). Immediate operational adjustment warranted."

    return {
        "predicted_waste": predicted_val,
        "risk_level": level,
        "priority": priority,
        "reason": reason,
    }