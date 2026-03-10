from google.adk.agents.llm_agent import Agent
from dotenv import load_dotenv
from . import prompt
load_dotenv()  # Load environment variables from .env file
# Mock tool implementation
def get_underrated_movies(query=None):
    # This is a mock implementation. Replace with actual logic as needed.
    return [
        "The Fall (2006)",
        "Moon (2009)",
        "Coherence (2013)",
        "The Man from Earth (2007)",
        "Hunt for the Wilderpeople (2016)"
    ]

root_agent = Agent(
    model='gemini-3-flash-preview',
    name='root_agent',
    description="Youre a cinema agent that you will give the underrated best movies",
    instruction=prompt.ROOT_AGENT_INSTR,
    tools=[get_underrated_movies],
)