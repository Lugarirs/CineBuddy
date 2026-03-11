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
    page_title="CineMood",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------------- #
#  Language                                                                   #
# --------------------------------------------------------------------------- #
query_params = st.query_params
detected_lang = query_params.get("lang", "en")
if detected_lang not in ["en", "ta", "hi"]:
    detected_lang = "en"

LANG_STRINGS = {
    "en": {
        "title": "CineMood",
        "subtitle": "Your mood. Your perfect watch, read & listen.",
        "movies": "🎬 Movies", "books": "📚 Books", "music": "🎵 Music",
        "mood_label": "How are you feeling right now?",
        "ph_movie": "Describe your mood or situation...",
        "ph_book": "What are you going through?",
        "ph_music": "What kind of songs do you need?",
        "ask": "Find →", "clear": "Clear", "share": "Share",
        "spin_movie": "Finding your perfect movie...",
        "spin_book": "Finding your perfect book...",
        "spin_music": "Finding your perfect songs...",
        "powered": "Powered by Google ADK · Gemini · SerpAPI",
    },
    "ta": {
        "title": "சினிமூட்",
        "subtitle": "உங்கள் மனநிலை. உங்கள் சரியான திரைப்படம், புத்தகம் & இசை.",
        "movies": "🎬 திரைப்படம்", "books": "📚 புத்தகம்", "music": "🎵 இசை",
        "mood_label": "இப்போது எப்படி உணர்கிறீர்கள்?",
        "ph_movie": "உங்கள் மனநிலையை விவரிக்கவும்...",
        "ph_book": "நீங்கள் என்ன கடந்து செல்கிறீர்கள்?",
        "ph_music": "என்ன மாதிரி பாடல்கள் வேண்டும்?",
        "ask": "கண்டுபிடி →", "clear": "அழி", "share": "பகிர்",
        "spin_movie": "சரியான திரைப்படம் தேடுகிறோம்...",
        "spin_book": "சரியான புத்தகம் தேடுகிறோம்...",
        "spin_music": "சரியான பாடல்கள் தேடுகிறோம்...",
        "powered": "Google ADK · Gemini · SerpAPI ஆல் இயக்கப்படுகிறது",
    },
    "hi": {
        "title": "सिनेमूड",
        "subtitle": "आपका मूड। आपकी परफेक्ट फिल्म, किताब और गाना।",
        "movies": "🎬 फ़िल्में", "books": "📚 किताबें", "music": "🎵 संगीत",
        "mood_label": "अभी आप कैसा महसूस कर रहे हैं?",
        "ph_movie": "अपना मूड बताएं...",
        "ph_book": "आप क्या महसूस कर रहे हैं?",
        "ph_music": "कौन से गाने चाहिए?",
        "ask": "खोजें →", "clear": "साफ़", "share": "शेयर",
        "spin_movie": "सही फिल्म ढूंढ रहे हैं...",
        "spin_book": "सही किताब ढूंढ रहे हैं...",
        "spin_music": "सही गाने ढूंढ रहे हैं...",
        "powered": "Google ADK · Gemini · SerpAPI द्वारा संचालित",
    },
}
L = LANG_STRINGS[detected_lang]

# --------------------------------------------------------------------------- #
#  CSS — Cinematic Dark Luxury                                                #
# --------------------------------------------------------------------------- #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Crimson+Pro:ital,wght@0,300;0,400;1,300&family=Syne:wght@400;600;700&display=swap');

:root {
    --gold: #c8a951;
    --gold2: #f0d080;
    --red: #c0392b;
    --bg: #050507;
    --bg2: #0d0d12;
    --bg3: #13131a;
    --bg4: #1a1a24;
    --text: #e8e0d0;
    --muted: #555566;
    --teal: #2a7a6a;
    --purple: #6a3d9a;
    --border: #1e1e2e;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.block-container {
    max-width: 740px !important;
    padding: 0 1rem 2rem !important;
}

/* ── Hero Banner ── */
.hero-banner {
    position: relative;
    width: calc(100% + 2rem);
    margin-left: -1rem;
    height: 340px;
    overflow: hidden;
    margin-bottom: 2rem;
}
.hero-banner img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: brightness(0.35) saturate(0.8);
}
.hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        to bottom,
        transparent 0%,
        rgba(5,5,7,0.6) 60%,
        rgba(5,5,7,1) 100%
    );
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    padding-bottom: 2rem;
    text-align: center;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(3.5rem, 12vw, 6rem);
    color: var(--gold);
    letter-spacing: 6px;
    line-height: 1;
    text-shadow: 0 0 40px rgba(200,169,81,0.4);
    margin: 0;
}
.hero-sub {
    font-family: 'Crimson Pro', serif;
    font-style: italic;
    font-size: clamp(0.9rem, 3vw, 1.1rem);
    color: rgba(232,224,208,0.6);
    margin-top: 6px;
    letter-spacing: 1px;
}
.lang-badge {
    display: inline-block;
    background: rgba(200,169,81,0.15);
    border: 1px solid rgba(200,169,81,0.3);
    color: var(--gold);
    font-size: 0.72rem;
    padding: 3px 12px;
    border-radius: 20px;
    margin-top: 10px;
    letter-spacing: 1px;
}

/* ── Mood Buttons ── */
.mood-section-label {
    font-family: 'Crimson Pro', serif;
    font-style: italic;
    color: var(--muted);
    font-size: 0.9rem;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
}
.stButton > button {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.78rem !important;
    padding: 6px 4px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--bg4) !important;
    border-color: var(--gold) !important;
    color: var(--gold) !important;
}

/* ── Ask button override ── */
.ask-btn > button {
    background: linear-gradient(135deg, #c8a951, #a07830) !important;
    color: #000 !important;
    font-weight: 700 !important;
    border: none !important;
    font-size: 0.9rem !important;
    letter-spacing: 1px !important;
}

/* ── Chat bubbles ── */
.chat-wrap { margin: 6px 0; }
.chat-user {
    background: var(--bg3);
    border-left: 3px solid var(--gold);
    padding: 12px 16px;
    border-radius: 0 10px 10px 0;
    font-size: 0.9rem;
    color: var(--text);
    margin-bottom: 4px;
}
.chat-agent {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--teal);
    padding: 14px 18px;
    border-radius: 0 10px 10px 0;
    font-size: 0.9rem;
    line-height: 1.85;
    color: var(--text);
}
.chat-music { border-left-color: var(--purple) !important; }
.chat-book  { border-left-color: #2a6a9a !important; }

/* ── Image card grid ── */
.img-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 10px;
    margin: 14px 0;
}
.img-card {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--border);
    background: var(--bg3);
    transition: transform 0.2s, border-color 0.2s;
}
.img-card:hover {
    transform: translateY(-3px);
    border-color: var(--gold);
}
.img-card img {
    width: 100%;
    height: 180px;
    object-fit: cover;
    display: block;
}
.img-card-label {
    padding: 8px 10px;
    font-size: 0.75rem;
    color: var(--gold2);
    font-family: 'Crimson Pro', serif;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ── Section divider ── */
.section-line {
    border: none;
    border-top: 1px solid var(--border);
    margin: 16px 0;
}

/* ── Input ── */
.stTextInput > div > div > input {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 1px rgba(200,169,81,0.3) !important;
}

/* ── Tabs ── */
div[data-testid="stTabs"] button {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.5px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom-color: var(--gold) !important;
}

/* ── Share box ── */
.share-box {
    background: var(--bg3);
    border: 1px dashed var(--border);
    border-radius: 8px;
    padding: 14px 16px;
    font-size: 0.82rem;
    color: var(--muted);
    line-height: 1.7;
    margin-top: 10px;
}
.share-box a { color: var(--gold); text-decoration: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #080810; border-right: 1px solid var(--border); }
.credit-wrap { text-align: center; padding: 20px 12px; }
.credit-avatar {
    width: 64px; height: 64px; border-radius: 50%;
    background: linear-gradient(135deg, var(--gold), var(--teal));
    margin: 0 auto 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem;
}
.credit-name {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem; color: var(--gold); letter-spacing: 3px;
}
.credit-role { color: var(--muted); font-size: 0.72rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 14px; }
.credit-gh {
    display: inline-block;
    background: var(--bg3); color: var(--gold) !important;
    border: 1px solid var(--border); border-radius: 20px;
    padding: 5px 18px; font-size: 0.8rem; text-decoration: none;
}
.tech-row { margin-top: 16px; }
.tech-badge {
    display: inline-block; background: var(--bg4); color: var(--muted);
    font-size: 0.68rem; padding: 3px 8px; border-radius: 8px; margin: 2px;
    border: 1px solid var(--border);
}

/* ── Tab images ── */
.tab-hero {
    width: 100%; height: 140px; object-fit: cover;
    border-radius: 10px; margin-bottom: 16px;
    filter: brightness(0.7) saturate(0.9);
}

footer, #MainMenu { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #
def fetch_image(query: str, num: int = 1) -> list:
    """Fetch images from SerpAPI Google Images."""
    if not SERPAPI_KEY:
        return []
    try:
        resp = requests.get(
            "https://serpapi.com/search",
            params={"engine": "google_images", "q": query, "api_key": SERPAPI_KEY, "num": num},
            timeout=8,
        )
        results = resp.json().get("images_results", [])
        return [r.get("original", "") for r in results[:num] if r.get("original")]
    except Exception:
        return []


def call_agent(endpoint: str, query: str, session_id, lang: str) -> dict:
    resp = requests.post(
        f"{API_URL}/{endpoint}",
        json={"query": query, "session_id": session_id, "language": lang},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def make_share(response: str) -> str:
    short = response[:200] + "..." if len(response) > 200 else response
    return f"🎬 CineMood says:\n\n{short}\n\nFind yours at CineMood!"


# --------------------------------------------------------------------------- #
#  State                                                                      #
# --------------------------------------------------------------------------- #
defaults = {
    "movie_session_id": None, "book_session_id": None, "music_session_id": None,
    "movie_history": [], "book_history": [], "music_history": [],
    "last_movie_resp": "", "last_music_resp": "",
    "hero_img": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --------------------------------------------------------------------------- #
#  Sidebar                                                                    #
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown(f"""
    <div class="credit-wrap">
        <div class="credit-avatar">🎬</div>
        <div class="credit-name">LUGARIRS</div>
        <div class="credit-role">Developer</div>
        <a class="credit-gh" href="https://github.com/Lugarirs" target="_blank">⌥ GitHub</a>
        <div class="tech-row">
            <div style="color:#333; font-size:0.68rem; margin-bottom:6px;">BUILT WITH</div>
            <span class="tech-badge">Google ADK</span>
            <span class="tech-badge">Gemini</span>
            <span class="tech-badge">FastAPI</span>
            <span class="tech-badge">Streamlit</span>
            <span class="tech-badge">SerpAPI</span>
            <span class="tech-badge">Render</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    lang_choice = st.selectbox(L["powered"][:8], ["Auto", "English", "தமிழ்", "हिंदी"], index=0, label_visibility="collapsed")
    if lang_choice == "English":   detected_lang = "en"; L = LANG_STRINGS["en"]
    elif lang_choice == "தமிழ்": detected_lang = "ta"; L = LANG_STRINGS["ta"]
    elif lang_choice == "हिंदी": detected_lang = "hi"; L = LANG_STRINGS["hi"]
    st.markdown(f'<p style="color:#222; font-size:0.65rem; text-align:center; margin-top:20px;">© 2026 lugarirs</p>', unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
#  Hero Banner — fetch once                                                   #
# --------------------------------------------------------------------------- #
if st.session_state.hero_img is None:
    imgs = fetch_image("cinematic film noir dark dramatic movie still", 1)
    st.session_state.hero_img = imgs[0] if imgs else "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=80"

lang_display = {"en": "🇬🇧 English", "ta": "🇮🇳 தமிழ்", "hi": "🇮🇳 हिंदी"}

st.markdown(f"""
<div class="hero-banner">
    <img src="{st.session_state.hero_img}" alt="Cinema">
    <div class="hero-overlay">
        <div class="hero-title">{L['title']}</div>
        <div class="hero-sub">{L['subtitle']}</div>
        <span class="lang-badge">{lang_display.get(detected_lang, '🌍 English')}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
#  Tabs                                                                       #
# --------------------------------------------------------------------------- #
movie_tab, book_tab, music_tab = st.tabs([L["movies"], L["books"], L["music"]])

# ═══════════════════════ MOVIES ════════════════════════════════════════════ #
with movie_tab:

    # Tab hero image
    movie_tab_imgs = fetch_image("vintage cinema movie theater seats dark", 1)
    if movie_tab_imgs:
        st.markdown(f'<img src="{movie_tab_imgs[0]}" class="tab-hero" alt="Movies">', unsafe_allow_html=True)

    st.markdown(f'<div class="mood-section-label">{L["mood_label"]}</div>', unsafe_allow_html=True)

    movie_moods = {
        "en": ["😢 Sad","😄 Happy","💔 Heartbroken","🔥 Motivated","😌 Nostalgic","😰 Anxious","😴 Bored","🌙 Can't Sleep","🧭 Lost","🤩 Adventure","💕 Romantic","😤 Stressed"],
        "ta": ["😢 சோகம்","😄 மகிழ்ச்சி","💔 மனம் உடைந்து","🔥 உத்வேகம்","😌 கடந்தகாலம்","😰 கவலை","😴 சலிப்பு","🌙 தூக்கமின்மை","🧭 தொலைந்து","🤩 சாகசம்","💕 காதல்","😤 மன அழுத்தம்"],
        "hi": ["😢 उदास","😄 खुश","💔 दिल टूटा","🔥 प्रेरित","😌 पुरानी यादें","😰 चिंतित","😴 बोर","🌙 नींद नहीं","🧭 खोया हुआ","🤩 साहसी","💕 रोमांटिक","😤 तनाव"],
    }
    moods = movie_moods.get(detected_lang, movie_moods["en"])
    selected_mood = None
    cols = st.columns(4)
    for i, m in enumerate(moods):
        if cols[i % 4].button(m, key=f"mm{i}"):
            selected_mood = m

    st.markdown('<hr class="section-line">', unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.movie_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">🧑 {msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-agent">🎬 {msg["text"]}</div>', unsafe_allow_html=True)
            # Show image cards if available
            if msg.get("images"):
                img_html = '<div class="img-grid">'
                for img in msg["images"]:
                    img_html += f'<div class="img-card"><img src="{img["url"]}" alt="{img["label"]}"><div class="img-card-label">{img["label"]}</div></div>'
                img_html += '</div>'
                st.markdown(img_html, unsafe_allow_html=True)

    with st.form("movie_form", clear_on_submit=True):
        query = st.text_input("q", placeholder=L["ph_movie"], label_visibility="collapsed")
        c1, c2, c3 = st.columns([4, 1, 1])
        submitted = c1.form_submit_button(L["ask"])
        cleared   = c2.form_submit_button(L["clear"])
        shared    = c3.form_submit_button(L["share"])

    if selected_mood: query = selected_mood; submitted = True

    if cleared:
        st.session_state.movie_history = []; st.session_state.movie_session_id = None
        st.session_state.last_movie_resp = ""; st.rerun()

    if shared and st.session_state.last_movie_resp:
        text = make_share(st.session_state.last_movie_resp)
        enc = urllib.parse.quote(text)
        st.markdown(f'<div class="share-box">{text}<br><br><a href="https://twitter.com/intent/tweet?text={enc}" target="_blank">🐦 Twitter</a> &nbsp;·&nbsp; <a href="https://wa.me/?text={enc}" target="_blank">💬 WhatsApp</a></div>', unsafe_allow_html=True)

    if submitted and query and query.strip():
        st.session_state.movie_history.append({"role": "user", "text": query})
        with st.spinner(L["spin_movie"]):
            try:
                data = call_agent("recommend", query, st.session_state.movie_session_id, detected_lang)
                st.session_state.movie_session_id = data["session_id"]
                response = data["response"]
                st.session_state.last_movie_resp = response

                # Fetch poster images for first 3 movie-like words in response
                images = []
                if SERPAPI_KEY:
                    lines = [l.strip() for l in response.split('\n') if '**' in l and '(' in l][:3]
                    for line in lines:
                        import re
                        match = re.search(r'\*\*(.*?)\*\*', line)
                        if match:
                            title = match.group(1).strip()
                            imgs = fetch_image(f"{title} official movie poster", 1)
                            if imgs:
                                images.append({"url": imgs[0], "label": title[:25]})

                st.session_state.movie_history.append({
                    "role": "agent", "text": response, "images": images
                })
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot reach the API.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out.")
            except Exception as e:
                st.error(f"Error: {e}")
        st.rerun()


# ═══════════════════════ BOOKS ═════════════════════════════════════════════ #
with book_tab:

    book_tab_imgs = fetch_image("cozy bookshelf warm library reading nook dark", 1)
    if book_tab_imgs:
        st.markdown(f'<img src="{book_tab_imgs[0]}" class="tab-hero" alt="Books">', unsafe_allow_html=True)

    st.markdown(f'<div class="mood-section-label">{L["mood_label"]}</div>', unsafe_allow_html=True)

    book_moods = {
        "en": ["😢 Need to cry","💡 Deep thoughts","🌿 Feel peaceful","🔥 Get inspired","💕 Romantic","🌍 Escape","😂 Laugh","🧘 Find myself"],
        "ta": ["😢 அழ வேண்டும்","💡 ஆழமான சிந்தனை","🌿 அமைதி","🔥 உத்வேகம்","💕 காதல்","🌍 தப்பிக்க","😂 சிரிக்க","🧘 என்னை கண்டுபிடிக்க"],
        "hi": ["😢 रोना है","💡 गहरी सोच","🌿 शांति","🔥 प्रेरणा","💕 रोमांटिक","🌍 पलायन","😂 हंसना","🧘 खुद को ढूंढना"],
    }
    bmoods = book_moods.get(detected_lang, book_moods["en"])
    sel_book = None
    bcols = st.columns(4)
    for i, m in enumerate(bmoods):
        if bcols[i % 4].button(m, key=f"bm{i}"): sel_book = m

    st.markdown('<hr class="section-line">', unsafe_allow_html=True)

    for msg in st.session_state.book_history:
        css = "chat-user" if msg["role"] == "user" else "chat-agent chat-book"
        icon = "🧑" if msg["role"] == "user" else "📚"
        st.markdown(f'<div class="{css}">{icon} {msg["text"]}</div>', unsafe_allow_html=True)

    with st.form("book_form", clear_on_submit=True):
        bq = st.text_input("bq", placeholder=L["ph_book"], label_visibility="collapsed")
        bc1, bc2 = st.columns([4, 1])
        b_sub = bc1.form_submit_button(L["ask"])
        b_clr = bc2.form_submit_button(L["clear"])

    if sel_book: bq = sel_book; b_sub = True

    if b_clr:
        st.session_state.book_history = []; st.session_state.book_session_id = None; st.rerun()

    if b_sub and bq and bq.strip():
        st.session_state.book_history.append({"role": "user", "text": bq})
        with st.spinner(L["spin_book"]):
            try:
                data = call_agent("recommend-books", bq, st.session_state.book_session_id, detected_lang)
                st.session_state.book_session_id = data["session_id"]
                st.session_state.book_history.append({"role": "agent", "text": data["response"]})
            except Exception as e:
                st.error(f"Error: {e}")
        st.rerun()


# ═══════════════════════ MUSIC ═════════════════════════════════════════════ #
with music_tab:

    music_tab_imgs = fetch_image("concert stage dramatic lighting music neon dark", 1)
    if music_tab_imgs:
        st.markdown(f'<img src="{music_tab_imgs[0]}" class="tab-hero" alt="Music">', unsafe_allow_html=True)

    st.markdown(f'<div class="mood-section-label">{L["mood_label"]}</div>', unsafe_allow_html=True)

    music_moods = {
        "en": ["😢 Heartbroken","🔥 Pump up","😌 Chill","💕 Romantic","🌧️ Rainy day","🌙 Late night","🥳 Party","🧘 Meditate"],
        "ta": ["😢 மனம் உடைந்து","🔥 உற்சாகம்","😌 அமைதி","💕 காதல்","🌧️ மழை நாள்","🌙 இரவு","🥳 கொண்டாட்டம்","🧘 தியானம்"],
        "hi": ["😢 दिल टूटा","🔥 जोश","😌 सुकून","💕 प्यार","🌧️ बारिश","🌙 रात","🥳 पार्टी","🧘 ध्यान"],
    }
    mmoods = music_moods.get(detected_lang, music_moods["en"])
    sel_music = None
    mcols = st.columns(4)
    for i, m in enumerate(mmoods):
        if mcols[i % 4].button(m, key=f"mus{i}"): sel_music = m

    st.markdown('<hr class="section-line">', unsafe_allow_html=True)

    for msg in st.session_state.music_history:
        css = "chat-user" if msg["role"] == "user" else "chat-agent chat-music"
        icon = "🧑" if msg["role"] == "user" else "🎵"
        st.markdown(f'<div class="{css}">{icon} {msg["text"]}</div>', unsafe_allow_html=True)

    with st.form("music_form", clear_on_submit=True):
        mq = st.text_input("mq", placeholder=L["ph_music"], label_visibility="collapsed")
        mc1, mc2, mc3 = st.columns([4, 1, 1])
        m_sub = mc1.form_submit_button(L["ask"])
        m_clr = mc2.form_submit_button(L["clear"])
        m_shr = mc3.form_submit_button(L["share"])

    if sel_music: mq = sel_music; m_sub = True

    if m_clr:
        st.session_state.music_history = []; st.session_state.music_session_id = None; st.rerun()

    if m_shr and st.session_state.last_music_resp:
        text = make_share(st.session_state.last_music_resp)
        enc = urllib.parse.quote(text)
        st.markdown(f'<div class="share-box">{text}<br><br><a href="https://twitter.com/intent/tweet?text={enc}" target="_blank">🐦 Twitter</a> &nbsp;·&nbsp; <a href="https://wa.me/?text={enc}" target="_blank">💬 WhatsApp</a></div>', unsafe_allow_html=True)

    if m_sub and mq and mq.strip():
        st.session_state.music_history.append({"role": "user", "text": mq})
        with st.spinner(L["spin_music"]):
            try:
                data = call_agent("recommend-music", mq, st.session_state.music_session_id, detected_lang)
                st.session_state.music_session_id = data["session_id"]
                st.session_state.last_music_resp = data["response"]
                st.session_state.music_history.append({"role": "agent", "text": data["response"]})
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot reach the API.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out.")
            except Exception as e:
                st.error(f"Error: {e}")
        st.rerun()

# --------------------------------------------------------------------------- #
#  Footer                                                                     #
# --------------------------------------------------------------------------- #
st.markdown(f'<p style="color:#1a1a2a; font-size:0.7rem; text-align:center; margin-top:2rem; font-family:Syne,sans-serif; letter-spacing:1px;">{L["powered"].upper()}</p>', unsafe_allow_html=True)