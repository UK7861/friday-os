from sqlmodel import Session, text
from app.db.postgres import engine

class SQLMasterTool:
    @staticmethod
    def execute_query(query: str):
        with Session(engine) as session:
            try:
                result = session.exec(text(query))
                if "SELECT" in query.upper():
                    return [dict(row) for row in result.mappings()]
                session.commit()
                return "Execution Successful"
            except Exception as e:
                return f"SQL Error: {str(e)}"

    @staticmethod
    def reflect_schema():
        # Production schema reflection logic
        with Session(engine) as session:
            result = session.exec(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            return [row[0] for row in result]

sql_master = SQLMasterTool()
