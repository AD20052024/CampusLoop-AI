# CampusLoop AI — System Architecture & Technical Specification

> **Tagline:** Predict. Prevent. Reuse. Recover.  
> **Primary Alignment:** UN SDG 12 — Responsible Consumption and Production  
> **Secondary Alignments:** UN SDG 11 (Sustainable Cities) & UN SDG 13 (Climate Action)

---

## 1. High-Level Closed-Loop Lifecycle

Campus dining operations require making food preparation decisions before actual attendance and consumption are known. Traditional systems stop at predictive modeling. CampusLoop AI implements a closed-loop decision intelligence platform connecting pre-service forecasting to post-service measured reality:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLOSED-LOOP CORE                               │
│                                                                             │
│   PREDICT  ───►  ASSESS  ───►  INTERVENE  ───►  MEASURE  ───►  LEARN        │
└──────┬─────────────┬──────────────┬───────────────┬──────────────┬──────────┘
       │             │              │               │              │
       ▼             ▼              ▼               ▼              ▼
 Operational     Waste Risk    Operational     Post-Service   Prediction Error
  ML Model         Engine        Guidance      Food Weighed   Model Retraining
 (Random Forest) (Rule Tiers)  (Human-in-Loop) (Actual Data)  (Feedback Loop)
```

---

## 2. Multi-Tier Modular Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION TIER                             │
│  FastAPI REST API (/api)  │  Interactive SPA Dashboard (/dashboard)     │
│  OpenAPI / Swagger (/docs) │  Human-in-the-Loop Approval UI              │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                           COORDINATION TIER                             │
│  CampusIntelligenceAgent                                                │
│  - Tool 1: predict_waste_tool                                           │
│  - Tool 2: calculate_risk_tool                                          │
│  - Tool 3: retrieve_policy_evidence_tool (RAG)                          │
│  - Tool 4: generate_intervention_tool                                   │
│  - Tool 5: calculate_impact_tool (UN SDG 12)                            │
│  - Tool 6: ibm_granite_synthesis_tool                                   │
│  - Tool 7: persist_record_tool                                          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                            INTELLIGENCE TIER                            │
│  ML Predictor            │ Risk Engine         │ Intervention Engine    │
│  (Scikit-Learn Pipeline) │ (Rule Thresholds)   │ (Action Directives)    │
│                          │                     │                        │
│  RAG Knowledge Engine    │ IBM Granite Adapter │ Impact Service         │
│  (TF-IDF / SOPs)         │ (watsonx.ai REST)   │ (CO2e, Water, Meals)   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                            PERSISTENCE TIER                             │
│  SQLAlchemy 2.0 ORM  │  SQLite (Dev) / PostgreSQL (Prod)                │
│  - predictions       │  - interventions                                 │
│  - outcomes          │  - model_versions                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Component Specifications

### 3.1 Preprocessing & ML Regressor (`app/ml/predictor.py`)
- **Algorithm:** Scikit-learn `Pipeline` pairing `ColumnTransformer` with `RandomForestRegressor(n_estimators=200, random_state=42)`.
- **Categorical Encoding:** `OneHotEncoder(handle_unknown='ignore')` for `meal`, `event_type`, and `weather_condition`.
- **Numerical Features:** Passthrough for `day_number`, `month`, `expected_attendance`, `holiday`, `exam_period`.
- **Portability:** Path derivation anchored in `app/config.py` via `pathlib.Path`; lazy model instantiation with thread-safe singleton caching.

### 3.2 Waste Risk Classification (`app/rules/waste_risk.py`)
- **Low Risk (< 10.0 kg):** Routine monitoring; standard operating kitchen procedure.
- **Medium Risk (10.0 – 24.99 kg):** Elevated risk; progressive batch cooking and close attendance tracking recommended.
- **High Risk (≥ 25.0 kg):** Critical risk; immediate batch reduction and mutual aid pantry donation standby required.

### 3.3 UN SDG 12 Impact Service (`app/services/impact.py`)
Calculates projected and measured benefits using evidence-grounded sustainability factors:
- **Avoided GHG Emissions:** $2.50\text{ kg CO}_2\text{e}$ per kg food waste prevented (FAO/EPA WARM).
- **Conserved Agricultural Water:** $850.0\text{ Liters}$ per kg food waste prevented.
- **Portion Equivalents Diverted:** $0.45\text{ kg}$ per standardized meal portion.
- **Estimated Economic Savings:** $\$3.50$ per kg food cost avoided.

### 3.4 Persistence & Feedback Engine (`app/database/`)
- Assigns persistent UUIDs (`prediction_id`) to every pre-service forecast.
- Links structured interventions with human manager approval states (`RECOMMENDED`, `APPROVED`, `EXECUTED`).
- Records post-service outcomes (`actual_attendance`, `actual_preparation`, `actual_consumption`, `actual_waste`).
- Computes prediction error ($\text{predicted} - \text{actual}$), absolute error, and percentage error (MAPE) to continuously measure model degradation.

### 3.5 RAG Knowledge Engine (`app/rag/knowledge_retriever.py`)
- Ingests institutional dining SOPs, Good Samaritan food recovery legal guidelines, and organics composting protocols from `data/rag/`.
- Chunks by structural header boundaries and indexes via TF-IDF cosine similarity.
- Supplies exact, verifiable citations for operational recommendations.

### 3.6 IBM Granite AI Adapter (`app/ai/granite_adapter.py`)
- Interfaces with IBM watsonx.ai REST endpoint for IBM Granite instruction-tuned models.
- **Strict Guardrail:** Granite does not calculate numerical predictions; it translates structured ML facts and RAG policy evidence into executive operational briefings.
- Graceful offline fallback generates deterministic grounded briefings when external credentials are absent.

### 3.7 Campus Intelligence Agent (`app/agents/campus_agent.py`)
- Orchestrates multi-step decision workflows across all components.
- Enforces human-in-the-loop oversight before high-impact interventions are marked executed.
- Emits an auditable execution trace detailing tool names, statuses, and outputs.
