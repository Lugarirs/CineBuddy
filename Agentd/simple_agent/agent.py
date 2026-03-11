from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import requests
from . import prompt

load_dotenv()

def search_movies(query: str) -> dict:
    """
    Search the web for movie recommendations based on mood, scenario, or any query.

    Args:
        query: e.g. 'underrated sad movies' or 'hidden gem films for heartbreak'

    Returns:
        Dictionary with movie search results.
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

        return {
            "query": query,
            "results": results,
            "total": len(results),
        }

    except requests.exceptions.Timeout:
        return {"error": "Search timed out.", "results": []}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Search failed: {str(e)}", "results": []}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "results": []}


root_agent = Agent(
    model="gemini-2.5-flash",
    name="cinemood_agent",
    description="A warm cinema companion recommending underrated movies based on mood and life situations.",
    instruction=prompt.ROOT_AGENT_INSTR,
    tools=[search_movies]
)