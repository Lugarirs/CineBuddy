from fastapi import FastAPI
from Agentd.simple_agent.agent import root_agent

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Agent is running"}

@app.get("/agent")
def run_agent():
    return {
        "name": root_agent.name,
        "description": root_agent.description
    }