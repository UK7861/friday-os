import pytest
from app.orchestration.graph_engine import build_friday_graph

def test_graph_initialization():
    workflow = build_friday_graph()
    assert workflow is not None

def test_llm_factory():
    from app.core.llm_provider import llm_manager
    # In sandbox we might not have keys, but we check if it handles wrong providers
    with pytest.raises(ValueError):
        llm_manager.get_llm(provider="invalid")

def test_sandbox_execution():
    from app.tools.sandbox.python_executor import sandbox
    code = "print('Hello Production')"
    result = sandbox.execute(code)
    assert "Hello Production" in result
