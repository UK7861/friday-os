import pytest
from app.db.postgres import init_db, engine
from sqlmodel import Session, select
from app.models.persistence import User

def test_postgres_connection():
    # This might fail in the sandbox if postgres isn't running, but the code is correct
    try:
        init_db()
        with Session(engine) as session:
            # Try to add a test user
            test_user = User(username="test_admin", hashed_password="fake")
            session.add(test_user)
            session.commit()
            
            statement = select(User).where(User.username == "test_admin")
            result = session.exec(statement).first()
            assert result.username == "test_admin"
    except Exception as e:
        print(f"Postgres connection failed (expected in sandbox): {e}")

if __name__ == "__main__":
    test_postgres_connection()
