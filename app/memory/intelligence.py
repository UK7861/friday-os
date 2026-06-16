from app.memory.graph import graph_memory
from app.db.redis_bus import redis_cache
from app.core.logging_config import logger

class LongTermMemory:
    @staticmethod
    def store_experience(mission_id: int, intent: str, result: str):
        # Store in Neo4j as a relationship
        graph_memory.add_knowledge("Mission", f"COMPLETED_{mission_id}", intent)
        # Store metadata in Redis for quick access
        redis_cache.set_state(f"mission:{mission_id}:result", result)
        logger.info("Experience Stored", mission_id=mission_id)

    @staticmethod
    def retrieve_context(query: str):
        # Semantic search or graph traversal logic
        return graph_memory.get_graph()

class AgentLearner:
    @staticmethod
    def update_agent_strategy(agent_role: str, performance_score: float):
        # Logic to evolve agent prompts or tools based on mission success
        logger.info("Agent Learning Strategy Updated", role=agent_role, score=performance_score)
        # Increment global intel level in Redis
        current_intel = int(redis_cache.get_state("intel_level") or 1000)
        redis_cache.set_state("intel_level", str(current_intel + int(performance_score * 10)))

memory_engine = LongTermMemory()
learner_engine = AgentLearner()
