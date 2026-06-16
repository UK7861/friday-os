import requests
import time

API_URL = "http://localhost:8000"

def simulate_tts(text: str):
    """Simulates Friday's voice output."""
    print(f'\n[FRIDAY]: "{text}"')

def process_voice_command(voice_command: str):
    print(f"[USER]: {voice_command}")
    requests.post(f"{API_URL}/log", json={"message": f"VOICE: {voice_command}", "level": "INFO"}, timeout=5)

    cmd_lower = voice_command.lower()

    if any(w in cmd_lower for w in ["approve", "theek hai", "confirm"]):
        requests.post(f"{API_URL}/approve", timeout=5)
        resp = "Thank you, Boss. Proceeding with the delivery as ordered."

    elif any(w in cmd_lower for w in ["status", "status kya hai", "how are you", "kaise ho"]):
        try:
            state = requests.get(f"{API_URL}/state", timeout=5).json()
            intel = state.get("intelligence_level", "unknown")
            missions = state.get("mission_count", 0)
            resp = (f"All systems operational, Boss. Intel level: {intel}. "
                    f"Missions completed: {missions}. The workforce is standing by.")
        except Exception:
            resp = "Boss, I cannot reach the core right now. Please check the API server."

    elif "reboot" in cmd_lower or "restart" in cmd_lower:
        requests.post(f"{API_URL}/log", json={"message": "Reboot command via voice.", "level": "WARNING"}, timeout=5)
        resp = "Reboot signal acknowledged, Boss. Initiating graceful restart sequence."

    elif any(w in cmd_lower for w in ["shukriya", "thank you", "thanks"]):
        resp = "Aapka shukriya, Boss. Main hamesha aapki khidmat mein hoon."

    else:
        # Forward as a mission
        try:
            requests.post(f"{API_URL}/command", json={"command": voice_command}, timeout=10)
            resp = f"Command logged and mission initiated, Boss. I'm on it."
        except Exception:
            resp = f"I've noted that, Boss. However, the core is unreachable at the moment."

    simulate_tts(resp)
    requests.post(f"{API_URL}/log", json={"message": f"FRIDAY: {resp}", "level": "SUCCESS"}, timeout=5)

if __name__ == "__main__":
    print("Friday Voice Interface — Type commands (or 'exit' to quit)")
    print("Supports English and Roman Urdu commands.\n")
    while True:
        try:
            cmd = input("[YOU]: ").strip()
            if cmd.lower() in ["exit", "quit", "bye"]:
                print("[FRIDAY]: Goodbye, Boss. Systems remain on standby.")
                break
            if cmd:
                process_voice_command(cmd)
        except KeyboardInterrupt:
            break
