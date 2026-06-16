from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, JSON, Column

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: str = "user" # admin, user, agent
    is_active: bool = True

class Mission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    intent: str
    status: str = "pending" # pending, working, success, failed
    result: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

class AgentState(SQLModel, table=True):
    id: Optional[str] = Field(primary_key=True)
    role: str
    status: str
    progress: int = 0
    energy: float = 100.0
    stamina: float = 100.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class SystemLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str
    message: str
    log_metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
