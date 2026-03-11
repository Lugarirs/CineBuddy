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
from .book_agent import book_agent

# --------------------------------------------------------------------------- #
#  Session services & Runners                                                 #
# --------------------------------------------------------------------------- #
movie_session_service = InMemorySessionService()
book_session_service = InMemorySessionService()

movie_runner = Runner(agent=root_agent, app_name="cinema_agent", session_service=movie_session_service)
book_runner = Runner(agent=book_agent, app_name="book_agent", session_service=book_session_service)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Cinema + Book Agent API started ✅")
    yield


app = FastAPI(title="CineMood API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    session_id: str
    response: str


# --------------------------------------------------------------------------- #
#  Shared runner helper                                                       #
# --------------------------------------------------------------------------- #
async def run_agent(runner, session_service, app_name, request: QueryRequest) -> QueryResponse:
    session_id = request.session_id or str(uuid.uuid4())
    user_id = "streamlit_user"

    try:
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id)
        if session is None:
            await session_service.create_session(
                app_name=app_name, user_id=user_id, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session error: {e}")

    message = types.Content(role="user", parts=[types.Part(text=request.query)])

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=message
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            final_response += part.text
                elif hasattr(event, "text") and event.text:
                    final_response = event.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    print(f"[DEBUG] app={app_name} session={session_id} response={final_response!r}")

    if not final_response:
        raise HTTPException(status_code=500, detail="Agent returned empty response.")

    return QueryResponse(session_id=session_id, response=final_response)


# --------------------------------------------------------------------------- #
#  Routes                                                                     #
# --------------------------------------------------------------------------- #
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=QueryResponse)
async def recommend_movies(request: QueryRequest):
    return await run_agent(movie_runner, movie_session_service, "cinema_agent", request)


@app.post("/recommend-books", response_model=QueryResponse)
async def recommend_books(request: QueryRequest):
    return await run_agent(book_runner, book_session_service, "book_agent", request)