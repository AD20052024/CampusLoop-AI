from typing import Any, Dict


def get_intervention(risk_level: str) -> str:
    """Return summary recommendation text for cafeteria staff based on risk level."""
    if risk_level == "High":
        return "Reduce preparation and consider redistribution or donation"
    elif risk_level == "Medium":
        return "Monitor preparation quantity and attendance"
    return "Continue normal preparation and monitoring"


def get_structured_intervention(risk_level: str) -> Dict[str, Any]:
    """
    Return a comprehensive operational intervention structure with action codes,
    priority levels, and human-in-the-loop oversight tags.
    """
    if risk_level == "High":
        return {
            "action_type": "REDUCE_PREPARATION",
            "priority": "Critical",
            "recommendation": "Reduce preparation and consider redistribution or donation",
            "requires_human_approval": True,
        }
    elif risk_level == "Medium":
        return {
            "action_type": "MONITOR",
            "priority": "Elevated",
            "recommendation": "Monitor preparation quantity and attendance",
            "requires_human_approval": False,
        }
    else:
        return {
            "action_type": "STANDARD_OPERATION",
            "priority": "Standard",
            "recommendation": "Continue normal preparation and monitoring",
            "requires_human_approval": False,
        }
    return 'Continue normal preparation and monitoring'