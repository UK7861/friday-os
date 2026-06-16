import pytest
import json
from app.agents.all_agents import get_all_agents
from app.tools.data_tools import data_cleaning_tool

def test_agent_counts():
    agents = get_all_agents()
    assert len(agents["all_list"]) == 16
    specialists = agents["specialists"]
    assert any(a.role == 'Executive Document Architect' for a in specialists)
    assert any(a.role == 'Deep Tajziya Analyst' for a in specialists)
    assert any(a.role == 'Analytics Expert' for a in specialists)
    leadership = agents["leadership"]
    assert any("Friday CEO" in a.role for a in leadership)
    assert any(a.role == 'JARVIS Scout & Liaison' for a in leadership)
    assert agents["gatekeeper"].role == 'QA Agent (Auditor)'
    assert agents["liaison"][0].role == 'Live Data Collector'

def test_data_cleaning_tool():
    raw_data = json.dumps([
        {"id": 1, "name": "Alice"},
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": None}
    ])
    cleaned_json = data_cleaning_tool.run(raw_data)
    cleaned_data = json.loads(cleaned_json)
    assert len(cleaned_data) == 1
    assert cleaned_data[0]["name"] == "Alice"

def test_api_server_state_shape():
    """Test that /state returns all required fields for both Streamlit and HUD."""
    from fastapi.testclient import TestClient
    from app.api_server import app

    client = TestClient(app)
    response = client.get("/state")
    assert response.status_code == 200
    data = response.json()

    # Core block (for test_production.py compatibility)
    assert "core" in data
    assert "status" in data["core"]

    # Streamlit-required fields
    assert "approval_pending" in data
    assert "mission_count" in data
    assert "intelligence_level" in data
    assert "core_version" in data
    assert "agent_vitals" in data

    # HUD-required fields
    assert "agents" in data
    assert "logs" in data
    assert "knowledge_graph" in data

def test_log_endpoint():
    from fastapi.testclient import TestClient
    from app.api_server import app

    client = TestClient(app)
    response = client.post("/log", json={"message": "Test log entry", "level": "INFO"})
    assert response.status_code == 200
    assert response.json()["status"] == "logged"

def test_command_endpoint():
    from fastapi.testclient import TestClient
    from app.api_server import app

    client = TestClient(app)
    response = client.post("/command", json={"command": "Test command from pytest"})
    assert response.status_code == 200
    assert "status" in response.json()
