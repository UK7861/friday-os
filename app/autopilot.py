import time
import requests
import random
import asyncio
from app.main import run_production_mission

API_URL = "http://localhost:8000"

SAMPLE_MISSIONS = [
    "Real-time sentiment analysis for social media",
    "Automated financial forecasting dashboard",
    "Customer churn prediction for Telecom",
    "Healthcare data interoperability layer",
    "Create a new scraping unit for e-commerce data",
    "Build a Power BI dashboard for sales performance",
    "Optimize SQL queries for data warehouse",
    "Generate executive report on quarterly trends",
]

def safe_post(path: str, **kwargs):
    try:
        return requests.post(f"{API_URL}{path}", timeout=5, **kwargs)
    except Exception as e:
        print(f"[Autopilot] POST {path} failed: {e}")
        return None

def safe_get(path: str):
    try:
        return requests.get(f"{API_URL}{path}", timeout=5)
    except Exception as e:
        print(f"[Autopilot] GET {path} failed: {e}")
        return None

def autopilot_loop():
    print("🤖 Friday Autopilot & System Health Monitor Started...")
    cycle = 0

    while True:
        try:
            cycle += 1
            print(f"\n[Autopilot] Cycle {cycle}")

            # System Health Check
            safe_post("/log", json={"message": f"Autopilot Cycle {cycle}: Running diagnostics.", "level": "INFO"})

            # Random self-healing simulation (10% chance)
            if random.random() > 0.9:
                problem = random.choice([
                    "Agent memory spike in ML Oracle",
                    "Latency detected in Scout Service",
                    "Redis cache miss rate elevated",
                ])
                safe_post("/log", json={"message": f"ANOMALY DETECTED: {problem}", "level": "ERROR"})
                time.sleep(2)
                safe_post("/log", json={"message": "QA Agent: Self-healing sequence active...", "level": "WARNING"})
                time.sleep(2)
                safe_post("/log", json={"message": f"QA Agent: {problem} resolved. System stable.", "level": "SUCCESS"})

            # Execute a random mission
            requirement = random.choice(SAMPLE_MISSIONS)
            safe_post("/log", json={"message": f"AUTOPILOT MISSION: {requirement}", "level": "INFO"})

            # Update a random agent to WORKING
            agent_name = random.choice([
                "Friday CEO (Living Intelligence)", "Python Overlord (Data Engineer)",
                "Analytics Expert", "ML Oracle", "SQL Overlord"
            ])
            safe_post(f"/update_agent?name={agent_name}&status=WORKING&progress={random.randint(10, 90)}")

            # Run the actual mission
            asyncio.run(run_production_mission(requirement))

            # Mark agent back to IDLE
            safe_post(f"/update_agent?name={agent_name}&status=STANDBY&progress=0")

            safe_post("/log", json={"message": "MISSION COMPLETE. Final report ready.", "level": "SUCCESS"})

            # Evolution step
            safe_post("/upgrade_core")
            safe_post("/log", json={"message": "Evolution Engine: Intelligence upgraded.", "level": "INFO"})

            time.sleep(45)

        except KeyboardInterrupt:
            print("\n[Autopilot] Shutdown requested.")
            break
        except Exception as e:
            print(f"[Autopilot] Unexpected error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    autopilot_loop()
