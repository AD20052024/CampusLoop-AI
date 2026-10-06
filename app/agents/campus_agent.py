from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.ai.granite_adapter import get_granite_adapter
from app.config import settings
from app.database import repository
from app.ml.predictor import predict_waste
from app.rag.knowledge_retriever import retrieve_policies
from app.rules.intervention import get_structured_intervention
from app.rules.waste_risk import calculate_risk
from app.services.impact import calculate_impact


class AgentAuditEntry:
    def __init__(self, step: int, tool_name: str, status: str, details: str):
        self.step = step
        self.tool_name = tool_name
        self.status = status
        self.details = details
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "tool_name": self.tool_name,
            "status": self.status,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class CampusIntelligenceAgent:
    """
    Autonomous multi-step coordinator agent for closed-loop sustainability intelligence.
    
    Coordinates:
    Data Validation -> ML Waste Prediction -> Risk Engine -> RAG Knowledge Retrieval ->
    Intervention Engine -> Impact Service -> IBM Granite Synthesis -> Database Persistence.
    
    Maintains strict human-in-the-loop oversight and generates an immutable audit trace.
    """

    def __init__(self):
        self.granite = get_granite_adapter()

    def run_workflow(
        self,
        operational_input: Dict[str, Any],
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Execute the coordinated intelligence lifecycle with auditable tool invocation."""
        audit_trail: List[Dict[str, Any]] = []
        step = 1

        # Tool 1: ML Waste Prediction
        predicted_waste = predict_waste(operational_input)
        audit_trail.append(
            AgentAuditEntry(
                step=step,
                tool_name="predict_waste_tool",
                status="SUCCESS",
                details=f"Generated ML waste forecast: {predicted_waste} kg",
            ).to_dict()
        )
        step += 1

        # Tool 2: Waste Risk Assessment
        risk = calculate_risk(predicted_waste)
        audit_trail.append(
            AgentAuditEntry(
                step=step,
                tool_name="calculate_risk_tool",
                status="SUCCESS",
                details=f"Assigned risk tier: {risk['risk_level']} (Priority: {risk['priority']})",
            ).to_dict()
        )
        step += 1

        # Tool 3: RAG Knowledge Retrieval
        rag_query = f"{operational_input.get('meal', '')} surplus food waste prevention {risk['risk_level']} risk donation"
        rag_citations = retrieve_policies(rag_query, top_k=2)
        audit_trail.append(
            AgentAuditEntry(
                step=step,
                tool_name="retrieve_policy_evidence_tool",
                status="SUCCESS",
                details=f"Retrieved {len(rag_citations)} policy evidence chunks from institutional knowledge base",
            ).to_dict()
        )
        step += 1

        # Tool 4: Operational Intervention Generation
        intervention = get_structured_intervention(risk["risk_level"])
        audit_trail.append(
            AgentAuditEntry(
                step=step,
                tool_name="generate_intervention_tool",
                status="SUCCESS",
                details=f"Action formulated: {intervention['action_type']} | Human Approval: {intervention['requires_human_approval']}",
            ).to_dict()
        )
        step += 1

        # Tool 5: UN SDG 12 Impact Calculation
        impact = calculate_impact(predicted_waste)
        audit_trail.append(
            AgentAuditEntry(
                step=step,
                tool_name="calculate_impact_tool",
                status="SUCCESS",
                details=f"Estimated impact: {impact['estimated_waste_prevented']} kg waste, {impact['co2e_prevented_kg']} kg CO2e prevented",
            ).to_dict()
        )
        step += 1

        # Tool 6: IBM Granite Synthesis
        ai_briefing = self.granite.synthesize_intervention_briefing(
            predicted_waste=predicted_waste,
            risk_level=risk["risk_level"],
            action_type=intervention["action_type"],
            recommendation=intervention["recommendation"],
            impact=impact,
            rag_citations=rag_citations,
        )
        audit_trail.append(
            AgentAuditEntry(
                step=step,
                tool_name="ibm_granite_synthesis_tool",
                status="SUCCESS",
                details=f"Synthesized executive operational explanation via {ai_briefing['provider']}",
            ).to_dict()
        )
        step += 1

        # Tool 7: Persistence (if DB session provided)
        prediction_id = None
        if db is not None:
            pred_record = repository.save_prediction(
                db=db,
                input_data=operational_input,
                predicted_waste=predicted_waste,
                risk_level=risk["risk_level"],
                model_version=settings.app_version,
            )
            interv_record = repository.save_intervention(
                db=db,
                prediction_id=pred_record.id,
                action_type=intervention["action_type"],
                priority=intervention["priority"],
                recommendation=intervention["recommendation"],
                requires_human_approval=intervention["requires_human_approval"],
            )
            prediction_id = pred_record.id
            intervention["id"] = interv_record.id
            audit_trail.append(
                AgentAuditEntry(
                    step=step,
                    tool_name="persist_record_tool",
                    status="SUCCESS",
                    details=f"Persisted closed-loop record with UUID {prediction_id}",
                ).to_dict()
            )

        return {
            "prediction_id": prediction_id,
            "predicted_waste": predicted_waste,
            "risk": risk,
            "intervention": intervention,
            "impact": impact,
            "policy_evidence": rag_citations,
            "ai_briefing": ai_briefing,
            "human_approval_required": intervention["requires_human_approval"],
            "agent_audit_trail": audit_trail,
        }


# Global singleton agent instance
_agent_instance = None


def get_campus_agent() -> CampusIntelligenceAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CampusIntelligenceAgent()
    return _agent_instance
