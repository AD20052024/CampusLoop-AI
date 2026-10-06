import os
from typing import Any, Dict, List, Optional
import httpx


class IBMGraniteAdapter:
    """
    Adapter for IBM Granite Foundation Models (via IBM watsonx.ai REST interface).
    
    Adheres strictly to CampusLoop AI Responsible AI principles:
    - Never generates numerical forecasts independently (all numbers come from ML/Rules).
    - Grounds recommendations in retrieved institutional RAG citations.
    - Provides transparent fallback when API credentials are not configured in environment.
    """

    def __init__(self):
        self.api_key = os.getenv("IBM_GRANITE_API_KEY", "")
        self.project_id = os.getenv("IBM_GRANITE_PROJECT_ID", "")
        self.endpoint_url = os.getenv(
            "IBM_GRANITE_URL",
            "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29",
        )
        self.model_id = os.getenv("IBM_GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2")

    @property
    def is_configured(self) -> bool:
        """Verify whether IBM Granite API credentials are provided in the environment."""
        return bool(self.api_key and self.project_id)

    def synthesize_intervention_briefing(
        self,
        predicted_waste: float,
        risk_level: str,
        action_type: str,
        recommendation: str,
        impact: Dict[str, Any],
        rag_citations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Synthesize an executive decision briefing grounding the ML forecast in
        institutional policy procedures and UN SDG 12 environmental rationale.
        """
        # Formulate grounded prompt payload
        citations_summary = "\n".join(
            [f"- [{c['source']} - {c['section']}]: {c['content'][:180]}..." for c in rag_citations]
        ) if rag_citations else "No specific institutional policy documents retrieved."

        # If IBM credentials are configured, execute live REST call to watsonx.ai
        if self.is_configured:
            try:
                prompt = (
                    f"You are CampusLoop AI's operational advisor aligned with UN SDG 12.\n"
                    f"Factual ML Predictions:\n"
                    f"- Forecasted Waste: {predicted_waste} kg\n"
                    f"- Risk Tier: {risk_level}\n"
                    f"- Operational Action: {action_type} ({recommendation})\n"
                    f"- Preventable CO2e: {impact.get('co2e_prevented_kg', 0)} kg\n"
                    f"- Salvaged Meals: {impact.get('meals_salvaged', 0)}\n\n"
                    f"Retrieved Campus SOP / Evidence:\n{citations_summary}\n\n"
                    f"Provide a concise, grounded 2-paragraph operational explanation for dining staff."
                )
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                }
                body = {
                    "model_id": self.model_id,
                    "input": prompt,
                    "parameters": {"max_new_tokens": 200, "temperature": 0.2},
                    "project_id": self.project_id,
                }
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(self.endpoint_url, json=body, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        generated_text = data["results"][0]["generated_text"]
                        return {
                            "provider": "IBM Granite (watsonx.ai)",
                            "model_id": self.model_id,
                            "executive_summary": generated_text.strip(),
                            "grounded_citations": [c["section"] for c in rag_citations],
                            "mode": "live_generation",
                        }
            except Exception:
                pass  # Fall through to deterministic synthesizer

        # Deterministic Grounded Synthesis (Offline / Testing / Development mode)
        executive_summary = (
            f"Based on the machine learning forecast of {predicted_waste} kg of food waste ({risk_level} Risk), "
            f"dining operations should execute '{recommendation}'. "
            f"Implementing this preventive adjustment is projected to avert {impact.get('co2e_prevented_kg', 0)} kg of CO₂e emissions "
            f"and preserve approximately {impact.get('meals_salvaged', 0)} meal portions in alignment with UN SDG 12."
        )

        return {
            "provider": "IBM Granite Grounded Synthesizer (Local Simulation Mode)",
            "model_id": self.model_id,
            "executive_summary": executive_summary,
            "grounded_citations": [c["section"] for c in rag_citations],
            "mode": "grounded_synthesis",
        }


# Global singleton adapter instance
_granite_adapter = None


def get_granite_adapter() -> IBMGraniteAdapter:
    global _granite_adapter
    if _granite_adapter is None:
        _granite_adapter = IBMGraniteAdapter()
    return _granite_adapter
