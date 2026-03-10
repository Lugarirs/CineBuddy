from fastapi import FastAPI
from pydantic import BaseModel
from Agentd.simple_agent.agent import root_agent

app = FastAPI()

class Query(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Agent running successfully"}


@app.get("/agent")
def agent_info():
    return {
        "name": root_agent.name,
        "description": root_agent.description
    }


@app.post("/chat")
def chat(query: Query):

    user_question = query.question

    response = f"""
Hello! I am {root_agent.name}.

You asked: {user_question}

I can help with:
• Travel planning
• Destination suggestions
• Trip itineraries
• Travel tips
"""

    return {
        "agent": root_agent.name,
        "question": user_question,
        "response": response
    }