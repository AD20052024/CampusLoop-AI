# CampusLoop AI — REST API Reference Guide

All endpoints are hosted by default at `http://localhost:8000` with interactive OpenAPI documentation available at `http://localhost:8000/docs`.

---

## Core Operations Endpoints

### 1. Execute Waste Prediction & Assessment
- **Method:** `POST`
- **Path:** `/api/predict`
- **Description:** Consumes pre-service dining variables, generates Random Forest food waste forecast (kg), calculates risk tier, formulates structured intervention guidance, computes UN SDG 12 impact, and persists record to SQLite.

#### Request Body
```json
{
  "day_number": 1,
  "month": 10,
  "meal": "Lunch",
  "expected_attendance": 260,
  "event_type": "Normal",
  "holiday": 0,
  "exam_period": 0,
  "weather_condition": "Clear"
}
```

#### Response (`200 OK`)
```json
{
  "prediction_id": "98a123f4-c28b-4a57-b06f-71b3dc921850",
  "predicted_waste": 6.85,
  "risk_level": "Low",
  "risk": {
    "predicted_waste": 6.85,
    "risk_level": "Low",
    "priority": "Standard",
    "reason": "Projected waste of 6.85 kg is within standard operating tolerance (< 10.0 kg)."
  },
  "recommended_action": "Continue normal preparation and monitoring",
  "intervention": {
    "id": "e83b0f74-32aa-4921-9988-cb941eef5912",
    "action_type": "STANDARD_OPERATION",
    "priority": "Standard",
    "recommendation": "Continue normal preparation and monitoring",
    "requires_human_approval": false,
    "status": "RECOMMENDED"
  },
  "impact": {
    "predicted_waste": 6.85,
    "estimated_waste_prevented": 1.37,
    "estimated_remaining_waste": 5.48,
    "estimated_reduction_percent": 20.0,
    "co2e_prevented_kg": 3.42,
    "water_saved_liters": 1164.5,
    "meals_salvaged": 3.0,
    "financial_savings_estimated": 4.80
  },
  "model_version": "0.1.0"
}
```

Prediction inputs constrain `day_number` to 0–6, `month` to 1–12, and `expected_attendance` to 1–10,000. Categorical values must match the options shown in the request example. Each prediction and its intervention are persisted to the configured database.

---

### 2. Autonomous Agent Decision Workflow
- **Method:** `POST`
- **Path:** `/api/agent/run`
- **Description:** Invokes `CampusIntelligenceAgent` to autonomously coordinate prediction, risk assessment, RAG policy retrieval, UN SDG 12 quantification, and IBM Granite synthesis with a complete step-by-step audit trail.

#### Response (`200 OK`)
```json
{
  "prediction_id": "98a123f4-c28b-4a57-b06f-71b3dc921850",
  "predicted_waste": 6.85,
  "risk": { ... },
  "intervention": { ... },
  "impact": { ... },
  "policy_evidence": [
    {
      "source": "campus_dining_waste_sop.md",
      "section": "Campus Dining Waste Sop — Pre-Service Attendance Forecasting",
      "content": "Head chefs and dining supervisors must consult...",
      "relevance_score": 0.428
    }
  ],
  "ai_briefing": {
    "provider": "IBM Granite Grounded Synthesizer",
    "executive_summary": "Based on the machine learning forecast...",
    "grounded_citations": ["Campus Dining Waste Sop — Pre-Service Attendance Forecasting"]
  },
  "human_approval_required": false,
  "agent_audit_trail": [
    { "step": 1, "tool_name": "predict_waste_tool", "status": "SUCCESS" },
    { "step": 2, "tool_name": "calculate_risk_tool", "status": "SUCCESS" },
    { "step": 3, "tool_name": "retrieve_policy_evidence_tool", "status": "SUCCESS" },
    { "step": 4, "tool_name": "generate_intervention_tool", "status": "SUCCESS" },
    { "step": 5, "tool_name": "calculate_impact_tool", "status": "SUCCESS" },
    { "step": 6, "tool_name": "ibm_granite_synthesis_tool", "status": "SUCCESS" },
    { "step": 7, "tool_name": "persist_record_tool", "status": "SUCCESS" }
  ]
}
```

---

## Closed-Loop Feedback & Outcome Endpoints

### 3. Record Post-Service Measured Outcome
- **Method:** `POST`
- **Path:** `/api/predictions/{prediction_id}/outcomes`
- **Description:** Closes the loop after meal service by logging actual metrics, calculating forecast error ($\text{predicted} - \text{actual}$), and computing waste reduction achieved.

#### Request Body
```json
{
  "actual_attendance": 252,
  "actual_preparation": 95.0,
  "actual_consumption": 89.2,
  "actual_waste": 5.1
}
```

#### Response (`201 Created`)
```json
{
  "prediction_id": "98a123f4-c28b-4a57-b06f-71b3dc921850",
  "actual_attendance": 252,
  "actual_preparation": 95.0,
  "actual_consumption": 89.2,
  "actual_surplus": 5.8,
  "actual_waste": 5.1,
  "prediction_error": 1.75,
  "absolute_error": 1.75,
  "percent_error": 34.31,
  "waste_reduction_achieved": 1.75
}
```

---

### 4. Human Intervention Approval
- **Method:** `POST`
- **Path:** `/api/predictions/{prediction_id}/interventions/{intervention_id}`
- **Description:** Allows cafeteria staff or managers to approve, reject, or mark operational interventions executed.

#### Request Body
```json
{
  "status": "APPROVED",
  "approved_by": "Chef Marcus (Dining Manager)"
}
```

---

### 5. Aggregated Closed-Loop Feedback Analytics
- **Method:** `GET`
- **Path:** `/api/feedback/analytics`
- **Description:** Returns cumulative metrics, historical Mean Absolute Error (MAE), Mean Absolute Percentage Error (MAPE), total SDG 12 savings, and time-series history for dashboard visualization.

---

### 6. Institutional Policy Knowledge Retrieval (RAG)
- **Method:** `GET`
- **Path:** `/api/rag/policies?query=donation&top_k=3`
- **Description:** Queries campus dining SOPs, food safety protocols, and donation guidelines, returning exact citation chunks.

---

### 7. Prediction History and Detail
- **Method:** `GET`
- **Paths:** `/api/predictions?limit=50&offset=0` and `/api/predictions/{prediction_id}`
- **Description:** Lists recent forecasts or returns a forecast with its interventions and, if entered, its measured outcome.

Model evaluation details are in `data/processed/waste_prediction_model_metadata.json`; there is no `/api/model-info` endpoint.

## Access Control

This prototype does not authenticate API callers. Use synthetic data only unless the deployment adds platform access control or application authentication.
