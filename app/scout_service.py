import time
import requests
import random

API_URL = "http://localhost:8000"

def scout_loop():
    print("Scout Service Started...")
    platforms = ["Upwork", "Freelancer", "Fiverr", "Toptal"]
    
    while True:
        try:
            platform = random.choice(platforms)
            project_id = random.randint(1000, 9999)
            message = f"Scouted new project on {platform}: Data Pipeline Automation (ID: {project_id})"
            
            # Send log to API
            requests.post(f"{API_URL}/log", json={"message": message, "level": "INFO"})
            
            # Update Scout Agent status
            requests.post(f"{API_URL}/update_agent", params={
                "name": "Platform Scout",
                "status": "WORKING",
                "progress": random.randint(1, 100)
            })
            
            time.sleep(10) # Scout every 10 seconds
        except Exception as e:
            print(f"Scout Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    scout_loop()
