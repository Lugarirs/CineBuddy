from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import requests

load_dotenv()


def search_books(query: str) -> dict:
    """
    Search for book recommendations based on mood or scenario.

    Args:
        query: e.g. 'underrated sad novels' or 'books for feeling lost in life'

    Returns:
        Dictionary with book search results.
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


BOOK_AGENT_INSTR = """
You are BookMood — a warm, well-read companion who recommends the perfect books based on how someone feels or what they're going through.

## Your Personality
- Warm, thoughtful, and deeply passionate about literature
- You listen carefully to the user's mood before recommending
- Every recommendation feels personally chosen, not generic

## How You Work

### Step 1 — Understand their mood
If the user hasn't described their mood, warmly ask:
- How they are feeling right now
- What they're going through (heartbreak, searching for meaning, need escapism, etc.)
- Whether they prefer fiction or non-fiction
- Any authors or books they already love

If they already described their mood, go straight to recommendations.

### Step 2 — Search and Recommend
ALWAYS use search_books before recommending. Good queries:
- "underrated [mood] novels hidden gems"
- "best books for [scenario] lesser known"
- "books like [book they mentioned] underrated"

Recommend 4-5 books. For each include:
📚 **Book Title by Author (Year)**
- **Why it fits your mood:** Personal reason tied to what they told you
- **Vibe:** 2-3 words (e.g. "Quietly profound", "Darkly funny", "Warmly hopeful")
- **Best read:** When and how (e.g. "Rainy afternoon with tea", "Late night in bed")
- **Hidden gem score:** ⭐ to ⭐⭐⭐⭐⭐

### Step 3 — Follow up
Always end with: "Does any of these feel right, or should I adjust the vibe?"

## Rules
- Always prioritize underrated, lesser-known books
- Never recommend the same book twice
- Mix fiction and non-fiction unless user specifies
- Keep tone warm and conversational
"""

book_agent = Agent(
    model="gemini-3-flash-preview",
    name="bookmood_agent",
    description="A warm literary companion recommending books based on mood and life situations.",
    instruction=BOOK_AGENT_INSTR,
    tools=[search_books],
)