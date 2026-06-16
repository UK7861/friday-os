from app.orchestration.graph_engine import build_friday_graph
from langchain_core.messages import HumanMessage
import asyncio
import pytest

@pytest.mark.asyncio
async def test_langgraph_flow():
    app = build_friday_graph()
    
    inputs = {
        "messages": [HumanMessage(content="Scout Upwork for data engineering projects and generate a proposal.")],
        "context": {},
        "mission_id": 1
    }
    
    async for output in app.astream(inputs):
        for key, value in output.items():
            print(f"Node '{key}':")
            print(f"  Next: {value.get('next_node')}")
            print(f"  Log: {value['messages'][-1].content}")
            
if __name__ == "__main__":
    asyncio.run(test_langgraph_flow())
