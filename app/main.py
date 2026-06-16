from app.orchestration.graph_engine import build_friday_graph
from app.core.logging_config import logger
from app.db.postgres import get_session
from app.models.persistence import Mission
import asyncio

async def run_production_mission(user_intent: str):
    logger.info("FRIDAY MISSION INITIATED", intent=user_intent)
    
    # Initialize LangGraph workflow
    workflow = build_friday_graph()
    app = workflow.compile()
    
    # Initial State
    initial_state = {
        "task": user_intent,
        "plan": [],
        "results": [],
        "current_agent": "friday_ceo",
        "history": [],
        "status": "started"
    }
    
    # Execute Graph
    logger.info("Orchestrating multi-agent workflow via LangGraph")
    final_state = await app.ainvoke(initial_state)
    
    # Store results in the global system state (simulation)
    # In a real production system, this would update the DB and send a WS notification
    
    # Persistence
    # (Assuming we have a way to get session here or use a context manager)
    # This is a simplified production flow
    
    logger.info("MISSION COMPLETED", status=final_state.get("status"))
    return final_state

if __name__ == "__main__":
    # Test execution
    asyncio.run(run_production_mission("Synthesize a production-grade strategy for FRIDAY OS deployment."))
