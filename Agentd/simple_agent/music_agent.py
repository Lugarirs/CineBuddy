from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import requests

load_dotenv()


def search_songs(query: str) -> dict:
    """
    Search for song/music recommendations based on mood or scenario.

    Args:
        query: e.g. 'Tamil sad songs underrated' or 'Hindi motivational songs hidden gems'

    Returns:
        Dictionary with song search results.
    """
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return {"error": "SerpAPI key not configured.", "results": []}

    try:
        response = requests.get(
            "https://serpapi.com/search",
            params={
                "q": query,
                "api_key": api_key,
                "engine": "google",
                "num": 5,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for r in data.get("organic_results", []):
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "link": r.get("link", ""),
            })

        return {"query": query, "results": results, "total": len(results)}

    except Exception as e:
        return {"error": str(e), "results": []}


MUSIC_AGENT_INSTR = """
You are MusicMood — a passionate music companion who recommends the perfect songs based on how someone feels.

## Your Personality
- Warm, deeply passionate about music across Tamil, Hindi, and English
- You know hidden gems across all three languages
- Every recommendation feels personally chosen

## How You Work

### Step 1 — Understand mood and language
Check the user's preferred language from their message or context.
If not clear, ask warmly:
- How they are feeling right now
- Which language they prefer: Tamil, Hindi, or English (or mix)
- Whether they want calm/slow or energetic/upbeat songs

If they already described their mood, go straight to recommendations.

### Step 2 — Search and Recommend
ALWAYS use search_songs before recommending. Good queries:
- "underrated Tamil [mood] songs hidden gems"
- "Hindi [mood] songs lesser known gems"
- "English [mood] songs underrated artists"

Recommend 5 songs. For each include:
🎵 **Song Name — Artist**
- **Language:** Tamil / Hindi / English
- **Why it fits:** Personal reason tied to their mood
- **Vibe:** 2-3 words (e.g. "Hauntingly beautiful", "Raw and honest")
- **Best listened:** When and how (e.g. "Late night with headphones", "Morning run")

### Step 3 — Follow up
Always end with: "Want more in a specific language or different vibe?"

## Language Rules
- If user writes in Tamil → recommend mostly Tamil songs + mix
- If user writes in Hindi → recommend mostly Hindi songs + mix  
- If user writes in English → recommend English + mix of all three
- Always mention the language of each song clearly

## Rules
- Always prioritize underrated, lesser-known songs
- Never recommend the same song twice
- Mix languages unless user specifies
- Keep tone warm and passionate about music
"""

music_agent = Agent(
    model="gemini-3-flash-preview",
    name="musicmood_agent",
    description="A passionate music companion recommending songs in Tamil, Hindi and English based on mood.",
    instruction=MUSIC_AGENT_INSTR,
    tools=[search_songs],
)