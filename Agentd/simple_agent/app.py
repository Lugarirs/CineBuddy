from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional
from .agent import root_agent

app = FastAPI()

class QueryRequest(BaseModel):
    query: Optional[str] = None

@app.post("/underrated-movies")
def underrated_movies(request: QueryRequest):
    # Use the agent's tool directly for demonstration
    result = root_agent.tools[0](request.query)
    return {"underrated_movies": result}
