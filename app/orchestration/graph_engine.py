import os
from typing import TypedDict, List, Annotated, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.agents.all_agents import get_all_agents
from app.core.llm_provider import LLMFactory
from crewai import Crew, Process, Task
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_node: str
    context: Dict[str, Any]
    mission_id: int

# Build LLM — tries OpenAI, falls back to Ollama (local), then mock
def _build_llm():
    if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here":
        try:
            return LLMFactory.get_llm("openai", "gpt-4o-mini")
        except Exception:
            pass
    if os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here":
        try:
            return LLMFactory.get_llm("google")
        except Exception:
            pass
    try:
        return LLMFactory.get_llm("ollama", "llama3")
    except Exception:
        return None  # agents will use mock responses

LLM = _build_llm()
WORKFORCE = get_all_agents(llm=LLM)

def _run_crew(agents: list, task_desc: str) -> str:
    """Run a CrewAI crew — if LLM is None, return a structured mock response."""
    if LLM is None:
        return f"[MOCK] Task completed: {task_desc}"
    try:
        task = Task(
            description=task_desc,
            agent=agents[0],
            expected_output="A detailed professional analysis and result."
        )
        crew = Crew(agents=agents, tasks=[task], process=Process.sequential, verbose=False)
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        return f"[Agent execution note: {str(e)[:120]}]"

def planner_node(state: AgentState):
    task_desc = state["messages"][0].content
    ceo = WORKFORCE["leadership"][0]
    result = _run_crew(
        [ceo],
        f"You are the Friday CEO. Decompose this mission into a clear execution plan: '{task_desc}'. "
        f"List the key steps and which specialist agents should handle each step."
    )
    plan = ["Scouting", "Data Analysis", "Documentation", "QA Audit"]
    return {
        "messages": [AIMessage(content=f"Friday CEO: {result}")],
        "context": {"plan": plan, "current_step": 0, "task": task_desc},
        "next_node": "scout_agent"
    }

def scout_node(state: AgentState):
    scout = WORKFORCE["leadership"][1]
    task_desc = state["context"].get("task", "")
    result = _run_crew(
        [scout],
        f"Scout for relevant project opportunities and client needs related to: '{task_desc}'. "
        f"Identify the key stakeholders, platforms, and approach for engagement."
    )
    return {
        "messages": [AIMessage(content=f"JARVIS Scout: {result}")],
        "context": {**state["context"], "current_step": 1},
        "next_node": "data_agent"
    }

def data_node(state: AgentState):
    task_desc = state["context"].get("task", "")
    # Select relevant specialists based on keywords
    specialists = WORKFORCE["specialists"]
    keyword_map = {
        "sql": "SQL Overlord", "database": "SQL Overlord",
        "excel": "Excel Master", "spreadsheet": "Excel Master",
        "ml": "Machine Learning Oracle (Data Scientist)", "predict": "Machine Learning Oracle (Data Scientist)",
        "deep learning": "Deep Learning Strategist", "neural": "Deep Learning Strategist",
        "power bi": "Power BI Commander", "tableau": "Tableau Viz Architect",
        "big data": "Big Data Architect", "spark": "Big Data Architect",
        "report": "Executive Document Architect", "invoice": "Executive Document Architect",
        "analytics": "Analytics Expert", "dashboard": "Analytics Expert",
    }
    chosen_role = "Python Overlord (Data Engineer)"
    task_lower = task_desc.lower()
    for kw, role in keyword_map.items():
        if kw in task_lower:
            chosen_role = role
            break
    active_agent = next((a for a in specialists if a.role == chosen_role), specialists[0])
    result = _run_crew(
        [active_agent],
        f"Execute this data task with full professional precision: '{task_desc}'. "
        f"Provide a complete, structured analysis, solution, and any code/outputs required."
    )
    return {
        "messages": [AIMessage(content=f"{active_agent.role}: {result}")],
        "context": {**state["context"], "current_step": 2, "specialist_output": result},
        "next_node": "qa_node"
    }

def qa_node(state: AgentState):
    qa = WORKFORCE["gatekeeper"]
    specialist_output = state["context"].get("specialist_output", "")
    result = _run_crew(
        [qa],
        f"Audit this output for quality, accuracy, and completeness: '{specialist_output[:500]}'. "
        f"Report any issues found and confirm whether it meets production standards."
    )
    return {
        "messages": [AIMessage(content=f"QA Agent: {result}")],
        "context": {**state["context"], "current_step": 3},
        "next_node": "finalizer"
    }

def finalizer_node(state: AgentState):
    doc_arch = next(
        (s for s in WORKFORCE["specialists"] if s.role == "Executive Document Architect"),
        WORKFORCE["specialists"][-1]
    )
    all_outputs = " | ".join([m.content for m in state["messages"]])
    result = _run_crew(
        [doc_arch],
        f"Synthesize all agent outputs into a final professional mission report. "
        f"Outputs: {all_outputs[:600]}. Generate an executive summary with key findings and next steps."
    )
    return {
        "messages": [AIMessage(content=f"Executive Document Architect: {result}")],
        "context": {**state["context"], "current_step": 4},
        "status": "completed",
        "next_node": END
    }

def build_friday_graph():
    builder = StateGraph(AgentState)
    builder.add_node("planner", planner_node)
    builder.add_node("scout_agent", scout_node)
    builder.add_node("data_agent", data_node)
    builder.add_node("qa_node", qa_node)
    builder.add_node("finalizer", finalizer_node)
    builder.set_entry_point("planner")
    builder.add_edge("planner", "scout_agent")
    builder.add_edge("scout_agent", "data_agent")
    builder.add_edge("data_agent", "qa_node")
    builder.add_edge("qa_node", "finalizer")
    builder.add_edge("finalizer", END)
    return builder.compile()
