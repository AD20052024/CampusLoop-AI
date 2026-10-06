# CampusLoop AI

### An AI-Powered Closed-Loop Resource Intelligence and Food-Waste Prevention Platform for Sustainable Campuses

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg?logo=scikitlearn)](https://scikit-learn.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00.svg)](https://www.sqlalchemy.org/)
[![UN SDG 12](https://img.shields.io/badge/UN%20SDG-12%20Responsible%20Consumption-007A3D.svg)](https://sdgs.un.org/goals/goal12)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Tagline:** Predict. Prevent. Reuse. Recover.  
> **Primary Alignment:** UN Sustainable Development Goal 12 (Target 12.3 — Halve per capita food waste by 2030)  
> **Secondary Alignments:** UN SDG 11 (Sustainable Cities) & UN SDG 13 (Climate Action)

---

## 1. Executive Summary & Problem Context

University dining operations face an asymmetric information dilemma daily: kitchen preparation decisions must be finalized **before** actual diner attendance and consumption numbers are known. This structural uncertainty leads to routine kitchen overproduction, avoidable plate waste, unnecessary carbon emissions, and financial losses.

Traditional campus approaches either rely on static headcounts or stop at disconnected predictive analytics. **CampusLoop AI** bridges this gap by establishing an integrated, closed-loop decision intelligence platform that connects operational forecasting to human-in-the-loop intervention and empirical post-service outcome feedback:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THE CLOSED-LOOP LIFECYCLE                          │
│                                                                             │
│   PREDICT  ───►  ASSESS  ───►  INTERVENE  ───►  MEASURE  ───►  LEARN        │
└──────┬─────────────┬──────────────┬───────────────┬──────────────┬──────────┘
       │             │              │               │              │
       ▼             ▼              ▼               ▼              ▼
 Operational     Waste Risk    Actionable      Post-Service   Prediction Error
  ML Model         Engine      Guidance        Food Weighed   Model Retraining
 (Random Forest) (Rule Tiers)  (Human-in-Loop) (Actual Data)  (Feedback Loop)
```

---

## 2. Core Differentiator: Beyond Waste Prediction

Predicting food waste alone is not novel. CampusLoop AI's innovation lies in its **closed-loop decision support architecture**:

1. **Prediction:** *What did we expect?* (ML Random Forest regression on pre-service operational variables).
2. **Assessment:** *What is the risk level and why?* (Deterministic, explainable risk tier classification).
3. **Intervention:** *What operational action is recommended?* (Structured actions: progressive batching, mutual aid donation standby, attendance reviews).
4. **Evidence (RAG):** *What institutional policy supports this?* (Retrieval-Augmented Generation citing dining hall SOPs and the Bill Emerson Food Donation Act).
5. **AI Synthesis (IBM Granite):** *What is the executive rationale?* (Grounded linguistic briefing without numerical hallucination).
6. **Outcome:** *What actually happened?* (Post-service physical weigh-ins logged by staff).
7. **Feedback:** *How accurate was the prediction, and what should be improved?* (Continuous tracking of MAE, MAPE, and intervention efficacy).

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION TIER                             │
│  FastAPI REST API (/api)  │  Interactive SPA Dashboard (/dashboard)     │
│  OpenAPI / Swagger (/docs) │  Human-in-the-Loop Decision UI              │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                           COORDINATION TIER                             │
│  CampusIntelligenceAgent                                                │
│  - Tool 1: predict_waste_tool        - Tool 5: calculate_impact_tool    │
│  - Tool 2: calculate_risk_tool       - Tool 6: ibm_granite_tool        │
│  - Tool 3: retrieve_policy_tool (RAG)- Tool 7: persist_record_tool      │
│  - Tool 4: generate_intervention_tool                                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                            INTELLIGENCE TIER                            │
│  ML Predictor (Scikit-Learn) │ Waste Risk Engine (Rule Tiers)           │
│  RAG Knowledge Retriever     │ IBM Granite LLM Adapter (watsonx.ai)     │
│  Intervention Engine         │ UN SDG 12 Impact Service                 │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                            PERSISTENCE TIER                             │
│  SQLAlchemy 2.0 ORM  │  SQLite (Local Dev) / PostgreSQL (Production)    │
│  - predictions       │  - interventions                                 │
│  - outcomes          │  - model_versions                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Machine Learning & Chronological Evaluation

### The Chronological Evaluation Principle
Unlike standard tabular datasets, campus operational data is sequential and seasonal. Random train-test splitting introduces **severe temporal data leakage** (training on future months to predict past months). CampusLoop AI implements a **chronological holdout split**:
- **Training Set (Earliest 80%):** 876 records spanning January through mid-October.
- **Testing Set (Latest 20%):** 219 records spanning mid-October through December.

### Benchmark Comparison: ML vs. Naive Baseline
A predictive model must prove superiority over simple operational heuristics. CampusLoop AI benchmarks its Random Forest pipeline against a **Meal-Specific Historical Average**:

| Model / Strategy | MAE (Mean Absolute Error) | RMSE | $R^2$ Score | Performance vs. Baseline |
| :--- | :---: | :---: | :---: | :---: |
| **Historical Meal Average (Baseline)** | **2.84 kg** | **3.65 kg** | **0.18** | Benchmark |
| **CampusLoop AI (Random Forest Pipeline)** | **1.42 kg** | **1.89 kg** | **0.78** | **+50.0% Error Reduction** |

### Preprocessing Pipeline & Feature Set
- **Categorical Columns (`OneHotEncoder(handle_unknown='ignore')`):** `meal` (Breakfast, Lunch, Dinner), `event_type` (Normal, Event, Festival), `weather_condition` (Clear, Cloudy, Rainy).
- **Numerical Columns (`passthrough`):** `day_number` (0-6), `month` (1-12), `expected_attendance`, `holiday` (0/1), `exam_period` (0/1).
- **Artifact & Metadata:** Fitted pipeline serialized to `waste_prediction_model.pkl` with full evaluation lineage recorded in `waste_prediction_model_metadata.json`.

---

## 5. UN SDG 12 Grounded Impact Quantification

Rather than arbitrary estimates, CampusLoop AI computes sustainability impact using peer-reviewed, authoritative environmental conversion factors:

- **Avoided Carbon Emissions:** $2.50\text{ kg CO}_2\text{e}$ per kg food waste prevented (FAO Food Wastage Footprint / EPA WARM).
- **Conserved Agricultural Water:** $850.0\text{ Liters}$ per kg food waste prevented.
- **Portion Equivalents Diverted:** $0.45\text{ kg}$ per standardized meal portion (~1 lb).
- **Economic Value Saved:** $\$3.50$ per kg food cost avoided.

---

## 6. Generative AI (IBM Granite) & Knowledge Retrieval (RAG)

### Retrieval-Augmented Generation (RAG)
Institutional food recovery requires strict adherence to food safety standards and donation liability laws. CampusLoop AI includes a local RAG engine (`app/rag/knowledge_retriever.py`) that chunks and indexes campus dining SOPs, composting guidelines, and the **Bill Emerson Good Samaritan Food Donation Act**. Recommendations are backed by verifiable citations.

### IBM Granite Foundation Model Integration
- **Strict Guardrail:** IBM Granite does **not** compute numerical predictions. All numbers are derived deterministically from the ML model, risk engine, and impact service.
- **Role:** Granite translates structured facts and RAG policy evidence into concise executive briefings for dining managers.
- **Resilient Fallback:** When live watsonx.ai credentials are not present in `.env`, the system executes deterministic grounded template synthesis with zero hallucination.

---

## 7. Interactive Single-Page Dashboard

CampusLoop AI includes a responsive HTML/CSS/JavaScript dashboard served by FastAPI at `/` (also available at `/dashboard/`):

1. **Meal forecast:** Estimate leftover food from service details, expected attendance, and optional campus conditions.
2. **Risk and guidance:** Display a deterministic risk tier and an operational recommendation for staff review.
3. **Potential impact:** Show clearly labeled scenario estimates using the configured reduction assumption.
4. **Staff follow-up:** Record action approval or completion with the staff member's name.
5. **Outcome tracking:** Save actual attendance, preparation, consumption, and waste, then compare the result with the forecast.
6. **Recent history:** Review and select saved predictions for post-service outcome entry.

---

## 8. Responsible AI & Ethical Framework

- **Human-in-the-Loop:** High and Medium risk interventions require manual confirmation by dining supervisors. The AI serves as an advisory system, never an autonomous kitchen controller.
- **Privacy & Data Minimization:** The platform processes exclusively aggregate operational counts (diners, meal types, weather). Zero student PII or meal-card tracking is collected or stored.
- **Academic & Prototype Transparency:** Development data is derived from a 1,095-row synthetic dataset modeled after university cafeteria operations. It is labeled as a research prototype and never fabricated as a live commercial deployment.

---

## 9. Quickstart & Installation

### Prerequisites
- Python 3.11+ (CI checks Python 3.11, 3.12, and 3.13)
- Git

### 1. Open & Set Up the Project
```bash
cd CampusLoop-AI

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements-dev.txt
```

### 3. Start the Platform
```bash
uvicorn app.main:app --reload
```
Once started, access:
- **Dashboard:** `http://localhost:8000/`
- **Alternate dashboard URL:** `http://localhost:8000/dashboard/`
- **Interactive API Documentation:** `http://localhost:8000/docs`
- **System Health Probe:** `http://localhost:8000/health`

### 4. Run the Test Suite
```bash
python -m pytest -q
```

### Container

Build and run the single-instance demo container with a persistent SQLite data volume:

```bash
docker build -t campusloop-ai .
docker run --rm -p 8000:8000 -v campusloop-data:/app/data campusloop-ai
```

Open `http://localhost:8000/`. For a public multi-instance deployment, configure a managed PostgreSQL database and persistent storage; SQLite is intended for local use and single-instance demos. The prediction data is synthetic, so do not use the prototype for real kitchen decisions without local validation and operational review.

### Publish the source on GitHub

In VS Code, open **Source Control**, review the changed files, stage the files you intend to publish, and make a commit using your own Git identity. Then choose **Publish Branch** and select public or private visibility. GitHub Pages cannot host this FastAPI application; the included workflow runs tests and builds the container on GitHub Actions.

---

## 10. Repository Structure

```
CampusLoop-AI/
├── app/
│   ├── __init__.py               # Package marker
│   ├── config.py                 # Centralized settings & absolute path resolution
│   ├── main.py                   # FastAPI app, CORS, lifespan DB init, static dashboard
│   ├── api/
│   │   ├── __init__.py           # API package marker
│   │   ├── routes.py             # Closed-loop REST routes (predict, interventions, outcomes)
│   │   └── schemas.py            # Typed Pydantic schemas, enums, response contracts
│   ├── database/
│   │   ├── __init__.py           # Database package marker
│   │   ├── session.py            # SQLAlchemy engine, sessionmaker, init_db
│   │   ├── models.py             # ORM models (PredictionRecord, InterventionRecord, OutcomeRecord)
│   │   └── repository.py         # Data access functions & closed-loop analytics
│   ├── ml/
│   │   ├── __init__.py           # ML package marker
│   │   └── predictor.py          # Lazy-loading singleton predictor & custom exceptions
│   ├── rules/
│   │   ├── __init__.py           # Rules package marker
│   │   ├── waste_risk.py         # Deterministic waste risk classification & threshold rules
│   │   └── intervention.py       # Structured intervention directives & human approval tags
│   ├── services/
│   │   ├── __init__.py           # Services package marker
│   │   └── impact.py             # UN SDG 12 environmental & economic impact calculator
│   ├── rag/
│   │   ├── __init__.py           # RAG package marker
│   │   └── knowledge_retriever.py# TF-IDF policy ingestion, chunking, and citation engine
│   ├── ai/
│   │   ├── __init__.py           # AI package marker
│   │   └── granite_adapter.py    # IBM Granite watsonx.ai adapter with grounded synthesis
│   └── agents/
│       ├── __init__.py           # Agents package marker
│       └── campus_agent.py       # Autonomous agent coordinator with tool audit trail
├── data/
│   ├── rag/                      # Institutional SOPs & food recovery policy knowledge base
│   │   ├── campus_dining_waste_sop.md
│   │   ├── food_recovery_and_donation_guidelines.md
│   │   └── composting_and_organics_diversion.md
│   ├── sample/                   # Synthetic development dataset
│   │   └── campus_resource_data.csv
│   └── processed/                # Cleaned datasets, trained model, and metadata
│       ├── campus_resource_data_clean.csv
│       ├── ml_dataset.csv
│       ├── waste_prediction_model.pkl
│       └── waste_prediction_model_metadata.json
├── frontend/                     # Responsive dining planning dashboard
│   ├── dashboard.html            # Forecast and service follow-up interface
│   ├── dashboard.css             # Dashboard layout and responsive styles
│   └── dashboard.js              # Prediction, review, and outcome workflows
├── scripts/                      # Data engineering & evaluation pipeline scripts
│   ├── generate_sample_data.py   # Synthetic data generator (free of target leakage)
│   ├── clean_data.py             # Non-negative validation & data cleaning
│   ├── prepare_ml_data.py        # Feature engineering & temporal extraction
│   └── train_model.py            # Chronological holdout training & baseline evaluation
├── tests/                        # Comprehensive automated test suite
│   ├── __init__.py               # Test package marker
│   ├── conftest.py               # Shared fixtures & FastAPI TestClient
│   ├── test_waste_risk.py        # Boundary tests for risk thresholds
│   ├── test_impact.py            # Unit tests for UN SDG 12 conversion factors
│   ├── test_predictor.py         # Lazy loading, inference, and exception handling tests
│   ├── test_api.py               # Integration tests for health, predict, and 422 validations
│   ├── test_database_and_feedback.py # End-to-end closed-loop workflow integration tests
│   └── test_agent_and_rag.py     # RAG citation, Granite synthesis, and agent workflow tests
├── docs/                         # In-depth technical documentation
│   ├── architecture.md           # System architecture & component specifications
│   ├── api.md                    # Complete REST API reference with payload schemas
│   ├── evaluation.md             # ML methodology, chronological holdout, and baseline comparison
│   └── responsible_ai.md         # Ethical standards, privacy, and hallucination controls
├── .gitignore                    # Version control hygiene
├── .env.example                  # Environment configuration template
└── requirements.txt              # Production dependency declarations
```

---

## 11. Technical Resume & Interview Talking Points

When presenting CampusLoop AI in technical interviews or portfolio reviews, emphasize these architectural design decisions:

- **Why a closed-loop architecture instead of just ML prediction?**  
  *Prediction in isolation does not change operational outcomes. By linking prediction to human-approved interventions and empirical post-service weigh-ins, the system calculates real prediction error and measures whether interventions actually prevented waste.*
- **Why Random Forest over Deep Learning?**  
  *Tabular operational data (1,095 records) with mixed categorical (meal, weather, events) and numerical features is well-suited for tree-based ensemble methods. Random Forest provides high interpretability, low latency inference (<10ms), and robustness against overfitting on smaller tabular sets.*
- **Why chronological train/test splitting instead of random shuffling?**  
  *Sequential time-series data suffers from bidirectional temporal leakage under random shuffling (training on future dates to predict past dates). Chronological holdout (80% train / 20% test) mirrors real deployment.*
- **Why are risk rules deterministic rather than LLM-generated?**  
  *Operational kitchen risk thresholds require strict, reproducible safety guarantees. Allowing an LLM to assign risk categories risks hallucination and non-deterministic behavior. LLMs are used for language synthesis, not numerical categorization.*
- **How are LLM hallucinations controlled?**  
  *IBM Granite is constrained by prompt boundaries and architectural contracts: it receives verified numerical outputs from the ML model and rule engines, translating them into human-readable briefings with citations.*
- **How is privacy protected?**  
  *The system relies on aggregate operational diner numbers. No student PII, card swipe numbers, or personal identifying information is ever collected or stored.*

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
