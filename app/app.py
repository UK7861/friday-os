import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Friday Management Control Room", layout="wide", page_icon="🚀")

API_URL = "http://localhost:8000"

st.title("🚀 Friday — Management Control Room")
st.markdown("### Powered by JARVIS-Core v4.0 (Humanoid Intelligence)")

col1, col2 = st.columns([1, 2])

def get_state():
    try:
        response = requests.get(f"{API_URL}/state", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

state = get_state()

with col1:
    st.header("Global State")
    if state:
        if state.get("approval_pending"):
            st.warning(f"⚠️ APPROVAL REQUIRED: {state.get('pending_action', '')}")
            if st.button("CONFIRM ACTION"):
                requests.post(f"{API_URL}/approve")
                st.success("Action confirmed.")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Health", state.get("status", "UNKNOWN"))
        m2.metric("Missions", state.get("mission_count", 0))
        m3.metric("Intel Level", state.get("intelligence_level", 1000))
        m4.metric("Core", state.get("core_version", "OS-1.0"))
    else:
        st.error("⚠️ Connection to Friday Core lost. Is the API server running?")

    st.subheader("Command Interface")
    voice_input = st.text_input("Enter Command (English/Roman Urdu) 🎤")
    if st.button("Transmit Command"):
        if voice_input:
            try:
                r = requests.post(
                    f"{API_URL}/command",
                    json={"command": voice_input},
                    timeout=10
                )
                if r.status_code == 200:
                    st.success(f"✅ Command '{voice_input}' transmitted to Friday CEO.")
                else:
                    st.error(f"Command failed: {r.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

    st.subheader("Agent Factory")
    new_agent_role = st.text_input("New agent role (e.g. 'Sentiment Analyst')")
    if st.button("Synthesize New Agent"):
        if new_agent_role:
            try:
                r = requests.post(
                    f"{API_URL}/command",
                    json={"command": f"Create a new agent with role: {new_agent_role}"},
                    timeout=10
                )
                st.info(f"✅ Agent synthesis initiated for: {new_agent_role}")
                requests.post(f"{API_URL}/log", json={"message": f"Manual Agent Synthesis: {new_agent_role}", "level": "WARNING"})
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a role name.")

with col2:
    st.header("Dynamic Agent Intelligence")
    if state:
        vitals = state.get("agent_vitals", {})
        if vitals:
            for agent_role, data in vitals.items():
                with st.expander(f"🤖 {agent_role} — {data['status']}"):
                    progress_val = min(max(float(data.get("progress", 0)), 0.0), 1.0)
                    st.progress(progress_val)
                    st.write(f"Energy: {data.get('energy', 100)}% | Status: {data['status']}")
                    if data.get("alerts", 0) > 0:
                        st.warning(f"Self-Healing active: {data['alerts']} alerts resolved.")
        else:
            st.info("All agents in Standby Mode.")
    else:
        st.warning("Real-time telemetry unavailable.")

    st.header("Unified Mission Logs")
    if state:
        logs = state.get("logs", [])
        if logs:
            log_df = pd.DataFrame(logs)
            st.dataframe(log_df.tail(20), use_container_width=True)
        else:
            st.info("No logs yet. Run a mission to see activity.")
    else:
        st.write("Log buffer inaccessible.")

st.sidebar.image("https://img.icons8.com/nolan/256/iron-man.png", width=100)
st.sidebar.header("Operational Mode")
auto_expand = st.sidebar.toggle("Autonomous Expansion", value=True)
self_healing = st.sidebar.toggle("Self-Healing Protocols", value=True)
scout_global = st.sidebar.toggle("Scout Global Mode", value=True)

if st.sidebar.button("System Reboot"):
    st.warning("Rebooting Friday sub-systems...")
    try:
        requests.post(f"{API_URL}/log", json={"message": "System Reboot Initiated.", "level": "ERROR"})
        st.success("Reboot signal sent.")
    except Exception:
        st.error("Could not reach API.")

if st.sidebar.button("🔄 Refresh State"):
    st.rerun()
