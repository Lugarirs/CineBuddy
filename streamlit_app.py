import os
import requests
import streamlit as st

# --------------------------------------------------------------------------- #
#  Config                                                                     #
# --------------------------------------------------------------------------- #
# ✅ Single source of truth — set API_URL env var on Render, leave blank for local
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="🎬 Cinema Agent",
    page_icon="🎬",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0e0e0e;
    color: #f0ece4;
}
h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem !important;
    color: #e8c97e;
    letter-spacing: -0.5px;
}
.subtitle { color: #888; font-size: 1rem; margin-top: -12px; margin-bottom: 24px; }
.chat-user {
    background: #1c1c1c; border-left: 3px solid #e8c97e;
    padding: 12px 16px; border-radius: 4px; margin: 8px 0; font-size: 0.95rem;
}
.chat-agent {
    background: #161616; border-left: 3px solid #4a9e7f;
    padding: 12px 16px; border-radius: 4px; margin: 8px 0;
    font-size: 0.95rem; line-height: 1.7;
}
.stTextInput > div > div > input {
    background-color: #1a1a1a !important; color: #f0ece4 !important;
    border: 1px solid #333 !important; border-radius: 6px !important;
}
.stButton > button {
    background-color: #e8c97e !important; color: #0e0e0e !important;
    font-weight: 600 !important; border: none !important;
    border-radius: 6px !important; padding: 0.5rem 1.5rem !important;
}
</style>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "history" not in st.session_state:
    st.session_state.history = []

st.markdown("<h1>🎬 Cinema Agent</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover hidden gems & underrated films — powered by Gemini</p>', unsafe_allow_html=True)
st.divider()

for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-user">🧑 {msg["text"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-agent">🎬 {msg["text"]}</div>', unsafe_allow_html=True)

with st.form(key="query_form", clear_on_submit=True):
    query = st.text_input(
        "Ask the cinema agent…",
        placeholder='e.g. "Recommend underrated sci-fi films from the 90s"',
        label_visibility="collapsed",
    )
    col1, col2 = st.columns([3, 1])
    with col1:
        submitted = st.form_submit_button("Ask →")
    with col2:
        cleared = st.form_submit_button("Clear chat", type="secondary")

if cleared:
    st.session_state.history = []
    st.session_state.session_id = None
    st.rerun()

if submitted and query.strip():
    st.session_state.history.append({"role": "user", "text": query})
    with st.spinner("Thinking…"):
        try:
            payload = {"query": query, "session_id": st.session_state.session_id}
            # ✅ API_URL is the base URL only — /recommend appended exactly once
            resp = requests.post(f"{API_URL}/recommend", json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.history.append({"role": "agent", "text": data["response"]})
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot reach the API. Is the FastAPI server running?")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The agent might be busy.")
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
    st.rerun()

elif submitted and not query.strip():
    st.warning("Please enter a question first.")

st.divider()
st.markdown('<p style="color:#444; font-size:0.8rem; text-align:center;">Powered by Google ADK · Gemini 2.0 Flash</p>', unsafe_allow_html=True)