import os
import requests
import streamlit as st
import urllib.parse

# --------------------------------------------------------------------------- #
#  Config                                                                     #
# --------------------------------------------------------------------------- #
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

st.set_page_config(
    page_title="CineMood & BookMood",
    page_icon="🎬",
    layout="wide",
)

# --------------------------------------------------------------------------- #
#  CSS                                                                        #
# --------------------------------------------------------------------------- #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Outfit:wght@300;400;500;600&display=swap');

:root {
    --gold: #c9a84c;
    --gold-light: #e8c97e;
    --bg: #080808;
    --bg2: #111111;
    --bg3: #1a1a1a;
    --text: #f0ece4;
    --muted: #666;
    --green: #3d8b6e;
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Header */
.hero {
    text-align: center;
    padding: 2.5rem 0 1rem;
    border-bottom: 1px solid #1e1e1e;
    margin-bottom: 2rem;
}
.hero h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.5rem;
    font-weight: 700;
    color: var(--gold);
    margin: 0;
    letter-spacing: 1px;
}
.hero p {
    color: var(--muted);
    font-size: 1rem;
    margin-top: 6px;
    font-weight: 300;
}

/* Agent tabs */
.agent-tabs {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-bottom: 2rem;
}

/* Mood buttons */
.mood-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 1.5rem;
}

/* Chat bubbles */
.chat-user {
    background: var(--bg3);
    border-left: 3px solid var(--gold);
    padding: 14px 18px;
    border-radius: 0 8px 8px 0;
    margin: 10px 0;
    font-size: 0.95rem;
}
.chat-agent {
    background: var(--bg2);
    border-left: 3px solid var(--green);
    padding: 14px 18px;
    border-radius: 0 8px 8px 0;
    margin: 10px 0;
    font-size: 0.95rem;
    line-height: 1.8;
}

/* Movie cards */
.movie-card {
    background: var(--bg2);
    border: 1px solid #222;
    border-radius: 10px;
    padding: 0;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}
.movie-card:hover {
    transform: translateY(-4px);
    border-color: var(--gold);
}
.movie-card img {
    width: 100%;
    height: 280px;
    object-fit: cover;
}
.movie-card-body {
    padding: 12px;
}
.movie-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--gold-light);
    margin-bottom: 4px;
}
.movie-rating {
    color: #f5c518;
    font-size: 0.85rem;
    margin-bottom: 6px;
}
.movie-vibe {
    color: var(--muted);
    font-size: 0.8rem;
    font-style: italic;
}

/* Share button */
.share-box {
    background: var(--bg3);
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 12px;
    font-size: 0.85rem;
    color: var(--muted);
    word-break: break-all;
}

/* Input */
.stTextInput > div > div > input {
    background-color: var(--bg3) !important;
    color: var(--text) !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
}
.stButton > button {
    background-color: var(--gold) !important;
    color: #000 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

div[data-testid="stTabs"] button {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1rem !important;
}

footer { display: none; }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #
def fetch_movie_poster(title: str) -> str:
    """Fetch movie poster URL using SerpAPI Google Images."""
    if not SERPAPI_KEY:
        return ""
    try:
        resp = requests.get(
            "https://serpapi.com/search",
            params={
                "engine": "google_images",
                "q": f"{title} movie poster",
                "api_key": SERPAPI_KEY,
                "num": 1,
            },
            timeout=8,
        )
        data = resp.json()
        results = data.get("images_results", [])
        if results:
            return results[0].get("original", "")
    except Exception:
        pass
    return ""


def fetch_imdb_rating(title: str) -> str:
    """Fetch IMDb rating using SerpAPI."""
    if not SERPAPI_KEY:
        return ""
    try:
        resp = requests.get(
            "https://serpapi.com/search",
            params={
                "engine": "google",
                "q": f"{title} IMDb rating",
                "api_key": SERPAPI_KEY,
                "num": 1,
            },
            timeout=8,
        )
        data = resp.json()
        # Try knowledge graph first
        kg = data.get("knowledge_graph", {})
        rating = kg.get("rating", "")
        if rating:
            return f"⭐ {rating}/10"
        # Try answer box
        answer = data.get("answer_box", {})
        if answer.get("rating"):
            return f"⭐ {answer['rating']}/10"
    except Exception:
        pass
    return ""


def make_share_text(query: str, response: str) -> str:
    """Generate shareable text."""
    short = response[:200] + "..." if len(response) > 200 else response
    return f"🎬 CineMood recommended me:\n\n{short}\n\nFind your perfect movie at CineMood!"


def call_agent(endpoint: str, query: str, session_id) -> dict:
    """Call the FastAPI agent endpoint."""
    resp = requests.post(
        f"{API_URL}/{endpoint}",
        json={"query": query, "session_id": session_id},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------------------------- #
#  State                                                                      #
# --------------------------------------------------------------------------- #
for key, default in [
    ("movie_session_id", None),
    ("book_session_id", None),
    ("movie_history", []),
    ("book_history", []),
    ("last_movie_response", ""),
    ("last_book_response", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# --------------------------------------------------------------------------- #
#  Sidebar Credits                                                            #
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #0e0e0e;
        border-right: 1px solid #1e1e1e;
    }
    .credit-card {
        background: #141414;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 24px 20px;
        text-align: center;
        margin-top: 1rem;
    }
    .credit-avatar {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, #c9a84c, #3d8b6e);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 14px;
        font-size: 2rem;
    }
    .credit-name {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #c9a84c;
        margin-bottom: 4px;
    }
    .credit-role {
        color: #555;
        font-size: 0.8rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    .credit-link {
        display: inline-block;
        background: #1e1e1e;
        color: #c9a84c !important;
        text-decoration: none;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.82rem;
        border: 1px solid #2a2a2a;
        margin: 3px;
        transition: background 0.2s;
    }
    .credit-link:hover {
        background: #2a2a2a;
    }
    .credit-divider {
        border: none;
        border-top: 1px solid #1e1e1e;
        margin: 20px 0;
    }
    .tech-badge {
        display: inline-block;
        background: #1a1a1a;
        color: #666;
        font-size: 0.75rem;
        padding: 3px 10px;
        border-radius: 10px;
        margin: 2px;
        border: 1px solid #222;
    }
    </style>

    <div class="credit-card">
        <div class="credit-avatar">🎬</div>
        <div class="credit-name">lugarirs</div>
        <div class="credit-role">Developer</div>
        <a class="credit-link" href="https://github.com/Lugarirs" target="_blank">
            ⌥ GitHub
        </a>
        <hr class="credit-divider">
        <div style="color:#444; font-size:0.75rem; margin-bottom:10px;">Built with</div>
        <span class="tech-badge">Google ADK</span>
        <span class="tech-badge">Gemini</span>
        <span class="tech-badge">FastAPI</span>
        <span class="tech-badge">Streamlit</span>
        <span class="tech-badge">SerpAPI</span>
        <span class="tech-badge">Render</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#333; font-size:0.72rem; text-align:center;">© 2026 lugarirs · All rights reserved</p>',
        unsafe_allow_html=True
    )


# --------------------------------------------------------------------------- #
#  Header                                                                     #
# --------------------------------------------------------------------------- #
st.markdown("""
<div class="hero">
    <h1>🎬 CineMood</h1>
    <p>Discover the perfect movie or book for your mood — powered by Gemini</p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
#  Tabs — Movies & Books                                                      #
# --------------------------------------------------------------------------- #
movie_tab, book_tab = st.tabs(["🎬 Movies", "📚 Books"])


# ═══════════════════════════════════════════════════════════════════════════ #
#  MOVIES TAB                                                                 #
# ═══════════════════════════════════════════════════════════════════════════ #
with movie_tab:

    # Mood quick-select buttons
    st.markdown("**How are you feeling?**")
    moods = ["😢 Sad", "😄 Happy", "💔 Heartbroken", "🔥 Motivated",
             "😌 Nostalgic", "😰 Anxious", "😴 Bored", "🌙 Can't Sleep",
             "🧭 Lost in Life", "🤩 Adventurous", "💕 Romantic", "😤 Stressed"]

    cols = st.columns(6)
    selected_mood = None
    for i, mood in enumerate(moods):
        if cols[i % 6].button(mood, key=f"mood_{i}"):
            selected_mood = mood

    st.divider()

    # Chat history
    for msg in st.session_state.movie_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">🧑 {msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-agent">🎬 {msg["text"]}</div>', unsafe_allow_html=True)

            # Movie poster cards if we can detect movie titles
            if SERPAPI_KEY and msg.get("show_cards"):
                titles = msg.get("titles", [])
                if titles:
                    st.markdown("**🎬 Movie Posters & Ratings**")
                    card_cols = st.columns(min(len(titles), 4))
                    for idx, title in enumerate(titles[:4]):
                        with card_cols[idx]:
                            poster = fetch_movie_poster(title)
                            rating = fetch_imdb_rating(title)
                            if poster:
                                st.image(poster, use_container_width=True)
                            st.markdown(f"**{title}**")
                            if rating:
                                st.markdown(rating)

    # Input form
    with st.form(key="movie_form", clear_on_submit=True):
        query = st.text_input(
            "Ask CineMood...",
            placeholder='e.g. "I had a rough day, need something light"',
            label_visibility="collapsed",
        )
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            submitted = st.form_submit_button("Ask →")
        with c2:
            cleared = st.form_submit_button("Clear")
        with c3:
            share = st.form_submit_button("📤 Share")

    # Handle mood button selection
    if selected_mood:
        query = selected_mood
        submitted = True

    if cleared:
        st.session_state.movie_history = []
        st.session_state.movie_session_id = None
        st.session_state.last_movie_response = ""
        st.rerun()

    if share and st.session_state.last_movie_response:
        share_text = make_share_text("", st.session_state.last_movie_response)
        encoded = urllib.parse.quote(share_text)
        st.markdown(f"""
        <div class="share-box">
            <strong>Share this recommendation:</strong><br><br>
            {share_text}<br><br>
            <a href="https://twitter.com/intent/tweet?text={encoded}" target="_blank">🐦 Share on Twitter</a> &nbsp;|&nbsp;
            <a href="https://wa.me/?text={encoded}" target="_blank">💬 Share on WhatsApp</a>
        </div>
        """, unsafe_allow_html=True)

    if submitted and query and query.strip():
        st.session_state.movie_history.append({"role": "user", "text": query})
        with st.spinner("Finding the perfect movie for your mood..."):
            try:
                data = call_agent("recommend", query, st.session_state.movie_session_id)
                st.session_state.movie_session_id = data["session_id"]
                response = data["response"]
                st.session_state.last_movie_response = response
                st.session_state.movie_history.append({
                    "role": "agent",
                    "text": response,
                    "show_cards": True,
                    "titles": [],  # titles would be parsed from response
                })
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot reach the API.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out.")
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ API error {e.response.status_code}: {e.response.text}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
        st.rerun()

    elif submitted and not query.strip():
        st.warning("Please enter a question or select a mood above.")


# ═══════════════════════════════════════════════════════════════════════════ #
#  BOOKS TAB                                                                  #
# ═══════════════════════════════════════════════════════════════════════════ #
with book_tab:

    st.markdown("**What's your mood for reading?**")
    book_moods = ["😢 Need to cry", "💡 Want to think", "🌿 Feel peaceful",
                  "🔥 Get inspired", "💕 Feel romantic", "🌍 Escape reality",
                  "😂 Need to laugh", "🧘 Find myself"]

    bcols = st.columns(4)
    selected_book_mood = None
    for i, mood in enumerate(book_moods):
        if bcols[i % 4].button(mood, key=f"book_mood_{i}"):
            selected_book_mood = mood

    st.divider()

    # Chat history
    for msg in st.session_state.book_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">🧑 {msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-agent">📚 {msg["text"]}</div>', unsafe_allow_html=True)

    # Input form
    with st.form(key="book_form", clear_on_submit=True):
        book_query = st.text_input(
            "Ask for book recommendations...",
            placeholder='e.g. "I feel lost in life, need a meaningful read"',
            label_visibility="collapsed",
        )
        bc1, bc2 = st.columns([3, 1])
        with bc1:
            book_submitted = st.form_submit_button("Ask →")
        with bc2:
            book_cleared = st.form_submit_button("Clear")

    if selected_book_mood:
        book_query = selected_book_mood
        book_submitted = True

    if book_cleared:
        st.session_state.book_history = []
        st.session_state.book_session_id = None
        st.rerun()

    if book_submitted and book_query and book_query.strip():
        st.session_state.book_history.append({"role": "user", "text": book_query})
        with st.spinner("Finding the perfect book for your mood..."):
            try:
                data = call_agent("recommend-books", book_query, st.session_state.book_session_id)
                st.session_state.book_session_id = data["session_id"]
                response = data["response"]
                st.session_state.last_book_response = response
                st.session_state.book_history.append({"role": "agent", "text": response})
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot reach the API.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out.")
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ API error {e.response.status_code}: {e.response.text}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
        st.rerun()

    elif book_submitted and not book_query.strip():
        st.warning("Please enter a question or select a mood above.")


# --------------------------------------------------------------------------- #
#  Footer                                                                     #
# --------------------------------------------------------------------------- #
st.divider()
st.markdown(
    '<p style="color:#333; font-size:0.8rem; text-align:center; font-family: Outfit, sans-serif;">Powered by Google ADK · Gemini · SerpAPI</p>',
    unsafe_allow_html=True,
)