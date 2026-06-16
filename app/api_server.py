from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta, datetime
from typing import List, Optional
from pydantic import BaseModel

from app.db.postgres import init_db, get_session, engine
from app.db.redis_bus import redis_cache
from app.memory.graph import graph_memory
from app.core.ws_manager import ws_manager
from app.core.logging_config import setup_logging, logger
from app.core.security import verify_password, get_password_hash, create_access_token, ALGORITHM, SECRET_KEY
from app.models.persistence import User, Mission, AgentState, SystemLog
from app.orchestration.graph_engine import build_friday_graph
from jose import JWTError, jwt

app = FastAPI(title="FRIDAY OS - Production Intelligence Core")
setup_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------- PYDANTIC MODELS ----------
class LogRequest(BaseModel):
    message: str
    level: str = "INFO"

class AgentUpdateRequest(BaseModel):
    name: str
    status: str
    progress: int = 0

class MissionRequest(BaseModel):
    intent: str

class CommandRequest(BaseModel):
    command: str

# ---------- AUTH ----------
async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(hours=24))
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/register")
def register_user(user: User, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user.hashed_password = get_password_hash(user.hashed_password)
    session.add(user)
    session.commit()
    return {"status": "User created"}

# ---------- MISSION CONTROL ----------
from app.main import run_production_mission
import asyncio

@app.post("/missions/execute")
async def execute_mission(req: MissionRequest, session: Session = Depends(get_session)):
    mission = Mission(intent=req.intent, status="working")
    session.add(mission)
    session.commit()
    session.refresh(mission)
    logger.info("Mission Started", mission_id=mission.id, intent=req.intent)
    asyncio.create_task(run_production_mission(req.intent))
    # Increment mission count in Redis
    count = int(redis_cache.get_state("mission_count") or 0)
    redis_cache.set_state("mission_count", str(count + 1))
    return {"mission_id": mission.id, "status": "running"}

@app.post("/command")
async def receive_command(req: CommandRequest, session: Session = Depends(get_session)):
    """Receive a command from the HUD frontend or voice interface."""
    log = SystemLog(level="INFO", message=f"COMMAND: {req.command}", log_metadata={})
    session.add(log)
    session.commit()
    # Broadcast to HUD via WebSocket
    await ws_manager.broadcast({"type": "COMMAND_RECEIVED", "payload": req.command})
    # Kick off a mission
    asyncio.create_task(run_production_mission(req.command))
    count = int(redis_cache.get_state("mission_count") or 0)
    redis_cache.set_state("mission_count", str(count + 1))
    return {"status": "Command received", "command": req.command}

# ---------- LOGGING ENDPOINT (used by autopilot + scout) ----------
@app.post("/log")
async def receive_log(req: LogRequest, session: Session = Depends(get_session)):
    log = SystemLog(level=req.level.upper(), message=req.message, log_metadata={})
    session.add(log)
    session.commit()
    # Broadcast log to HUD
    await ws_manager.broadcast({
        "type": "LOG",
        "payload": {"level": req.level, "message": req.message, "timestamp": datetime.utcnow().isoformat()}
    })
    return {"status": "logged"}

# ---------- AGENT STATE ENDPOINT ----------
@app.post("/update_agent")
async def update_agent(session: Session = Depends(get_session), name: str = "", status: str = "IDLE", progress: int = 0):
    agent_id = name.replace(" ", "_").lower()
    agent = session.exec(select(AgentState).where(AgentState.id == agent_id)).first()
    if agent:
        agent.status = status
        agent.progress = progress
        agent.last_updated = datetime.utcnow()
        session.add(agent)
        session.commit()
    # Broadcast update
    await ws_manager.broadcast({
        "type": "AGENT_UPDATE",
        "payload": {"name": name, "status": status, "progress": progress}
    })
    return {"status": "updated", "agent": name}

# ---------- APPROVE ENDPOINT ----------
@app.post("/approve")
async def approve_action(session: Session = Depends(get_session)):
    redis_cache.set_state("approval_pending", "false")
    log = SystemLog(level="INFO", message="Manual approval granted by operator.", log_metadata={})
    session.add(log)
    session.commit()
    await ws_manager.broadcast({"type": "APPROVAL_GRANTED", "payload": {}})
    return {"status": "approved"}

# ---------- UPGRADE CORE ----------
@app.post("/upgrade_core")
async def upgrade_core(session: Session = Depends(get_session)):
    current_intel = int(redis_cache.get_state("intel_level") or 1000)
    new_intel = current_intel + 50
    redis_cache.set_state("intel_level", str(new_intel))
    log = SystemLog(level="INFO", message=f"Core upgraded. Intel level: {new_intel}", log_metadata={})
    session.add(log)
    session.commit()
    await ws_manager.broadcast({"type": "CORE_UPGRADE", "payload": {"intel_level": new_intel}})
    return {"status": "upgraded", "intel_level": new_intel}

# ---------- MAIN STATE ENDPOINT (fixed shape for Streamlit + HUD) ----------
@app.get("/state")
async def get_system_state(session: Session = Depends(get_session)):
    agents = session.exec(select(AgentState)).all()
    logs = session.exec(select(SystemLog).order_by(SystemLog.timestamp.desc()).limit(20)).all()

    # Build agent_vitals dict for Streamlit
    agent_vitals = {}
    for a in agents:
        agent_vitals[a.role] = {
            "status": a.status,
            "progress": a.progress / 100.0,  # Streamlit st.progress expects 0.0-1.0
            "energy": a.energy,
            "alerts": 0
        }

    # Try graph memory — graceful fallback if Neo4j offline
    try:
        graph = graph_memory.get_graph()
    except Exception:
        graph = {"nodes": [], "links": []}

    intel_level = int(redis_cache.get_state("intel_level") or 1000)
    mission_count = int(redis_cache.get_state("mission_count") or 0)
    approval_pending = (redis_cache.get_state("approval_pending") or "false") == "true"

    return {
        # Streamlit-expected fields
        "approval_pending": approval_pending,
        "pending_action": redis_cache.get_state("pending_action") or "",
        "status": "ONLINE",
        "mission_count": mission_count,
        "intelligence_level": intel_level,
        "core_version": "OS-1.0-ALIVE",
        "agent_vitals": agent_vitals,
        # HUD + raw fields
        "agents": [a.dict() for a in agents],
        "logs": [{"timestamp": l.timestamp.isoformat(), "level": l.level, "message": l.message} for l in logs],
        "knowledge_graph": graph,
        "intel_level": intel_level,
        "uptime": 3600,
        # Nested core block (for tests)
        "core": {
            "status": "ONLINE",
            "version": "OS-1.0-ALIVE",
            "intel_level": intel_level
        }
    }

# ---------- WEBSOCKET HUD ----------
@app.websocket("/ws/hud")
async def hud_websocket(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial state on connect
        agents = []
        try:
            with Session(engine) as s:
                agents = [a.dict() for a in s.exec(select(AgentState)).all()]
        except Exception:
            pass
        await websocket.send_text(__import__("json").dumps({
            "type": "INIT",
            "payload": {"agents": agents, "intel_level": int(redis_cache.get_state("intel_level") or 1000)}
        }))
        while True:
            data = await websocket.receive_text()
            # Forward commands as missions
            import json
            try:
                msg = json.loads(data)
                if msg.get("type") == "COMMAND":
                    asyncio.create_task(run_production_mission(msg.get("payload", "")))
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# ---------- STARTUP ----------
@app.on_event("startup")
def startup():
    try:
        init_db()
    except Exception as e:
        logger.error("DB init failed — running without persistence", error=str(e))
        return

    from app.agents.all_agents import get_all_agents
    with Session(engine) as session:
        try:
            existing = session.exec(select(AgentState)).first()
            if not existing:
                workforce = get_all_agents()
                for agent in workforce["all_list"]:
                    state = AgentState(
                        id=agent.role.replace(" ", "_").lower(),
                        role=agent.role,
                        status="STANDBY",
                        progress=0,
                        energy=100.0,
                        stamina=100.0
                    )
                    session.add(state)
                session.commit()
                logger.info(f"Seeded {len(workforce['all_list'])} agents.")
        except Exception as e:
            logger.error("Agent seeding failed", error=str(e))

    logger.info("FRIDAY Production OS Initialized")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
