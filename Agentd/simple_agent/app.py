import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import root_agent

# --------------------------------------------------------------------------- #
#  Session service & Runner — created once at startup                         #
# --------------------------------------------------------------------------- #
session_service = InMemorySessionService()
APP_NAME = "cinema_agent"

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


# --------------------------------------------------------------------------- #
#  Lifespan                                                                   #
# --------------------------------------------------------------------------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Cinema Agent API started ✅")
    yield
    print("Cinema Agent API shutting down...")


# --------------------------------------------------------------------------- #
#  App                                                                        #
# --------------------------------------------------------------------------- #
app = FastAPI(
    title="Cinema Agent API",
    description="Underrated movie recommendations powered by Gemini via Google ADK",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
#  Schemas                                                                    #
# --------------------------------------------------------------------------- #
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None   # pass back the same id for multi-turn


class QueryResponse(BaseModel):
    session_id: str
    response: str


# --------------------------------------------------------------------------- #
#  Routes                                                                     #
# --------------------------------------------------------------------------- #
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=QueryResponse)
async def recommend_movies(request: QueryRequest):
    """
    Send a message to the cinema agent and get movie recommendations.
    Pass `session_id` from a previous response to continue the conversation.
    """
    # Reuse or create a session
    session_id = request.session_id or str(uuid.uuid4())
    user_id = "streamlit_user"

    try:
        # Ensure session exists
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        if session is None:
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session error: {e}")

    # Build the ADK message
    message = types.Content(
        role="user",
        parts=[types.Part(text=request.query)],
    )

    # Run the agent and collect the final text reply
    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    if not final_response:
        raise HTTPException(status_code=500, detail="Agent returned an empty response.")

    return QueryResponse(session_id=session_id, response=final_response)