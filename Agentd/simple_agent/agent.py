# from google.adk.agents.llm_agent import Agent
from simple_agent import prompt
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Temporary Agent class definition for development if the import is unavailable
class Agent:
    def __init__(self, model, name, description, instruction):
        self.model = model
        self.name = name
        self.description = description
        self.instruction = instruction
# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model='gemini-3-flash-preview',
    name='root_agent',
    description="A Travel Conceirge using the services of multiple sub-agents",
    instruction=prompt.ROOT_AGENT_INSTR,
    
)