from fastapi import status
from app.rag.knowledge_retriever import retrieve_policies
from app.ai.granite_adapter import get_granite_adapter
from app.agents.campus_agent import get_campus_agent


def test_rag_policy_retrieval():
    citations = retrieve_policies("donation surplus pantry", top_k=2)
    assert len(citations) > 0
    first = citations[0]
    assert "source" in first
    assert "section" in first
    assert "content" in first
    assert first["relevance_score"] > 0.0


def test_ibm_granite_grounded_synthesis():
    adapter = get_granite_adapter()
    rag_citations = retrieve_policies("donation", top_k=1)

    impact = {"co2e_prevented_kg": 15.0, "meals_salvaged": 20.0}
    briefing = adapter.synthesize_intervention_briefing(
        predicted_waste=12.5,
        risk_level="Medium",
        action_type="MONITOR",
        recommendation="Monitor preparation quantity and attendance",
        impact=impact,
        rag_citations=rag_citations,
    )

    assert "executive_summary" in briefing
    assert "12.5" in briefing["executive_summary"]
    assert "Medium" in briefing["executive_summary"]
    assert len(briefing["grounded_citations"]) > 0


def test_agent_workflow_execution(valid_prediction_payload):
    agent = get_campus_agent()
    result = agent.run_workflow(valid_prediction_payload)

    assert "predicted_waste" in result
    assert "risk" in result
    assert "intervention" in result
    assert "impact" in result
    assert "policy_evidence" in result
    assert "ai_briefing" in result
    assert "agent_audit_trail" in result

    # Check audit trail steps
    trail = result["agent_audit_trail"]
    assert len(trail) >= 5
    tool_names = [t["tool_name"] for t in trail]
    assert "predict_waste_tool" in tool_names
    assert "calculate_risk_tool" in tool_names
    assert "retrieve_policy_evidence_tool" in tool_names


def test_agent_api_endpoint(client, valid_prediction_payload):
    response = client.post("/api/agent/run", json=valid_prediction_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "agent_audit_trail" in data
    assert "ai_briefing" in data
    assert "policy_evidence" in data
    assert data["predicted_waste"] >= 0.0


def test_rag_policies_api_endpoint(client):
    response = client.get("/api/rag/policies?query=composting&top_k=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["query"] == "composting"
    assert "citations" in data
