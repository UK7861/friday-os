# FRIDAY — DEPLOYMENT GUIDE

## Prerequisites
- Python 3.9+
- CrewAI
- FastAPI / Uvicorn
- Streamlit
- Pandas
- LangChain / LangChain-Community
- CrewAI Tools

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install crewai fastapi uvicorn streamlit pandas langchain-community crewai_tools
   ```

## Local Setup
1. **API Server**: Starts on port 8000. Manages global state and agent vitals.
2. **HUD Deck**: Hosted via Python HTTP server on port 8080.
3. **Streamlit**: Hosted on port 8501.

## One-Click Launch
Run the following command from the root directory:
```bash
python app/run_all.py
```

## Running Tests
Ensure the API server is running (or test will use TestClient), then execute:
```bash
PYTHONPATH=. pytest app/tests/test_agency.py
```

## Advanced Voice Control
Run the voice simulator to test English/Roman Urdu commands:
```bash
python app/voice_interface.py
```
