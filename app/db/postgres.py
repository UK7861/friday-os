import os
from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://friday_user:friday_password@localhost:5432/friday_db")

engine = create_engine(DATABASE_URL)

def init_db():
    from app.models.persistence import User, Mission, AgentState, SystemLog
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
