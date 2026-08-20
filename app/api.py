"""
Thin FastAPI wrapper so the agent can be called over HTTP instead of just
from a script — this is what turns "a Python function" into "a service,"
which is the deployment-shaped skill most AI Engineer postings ask for.

Run with: uvicorn app.api:app --reload
Then: curl -X POST localhost:8000/ask -H 'Content-Type: application/json' -d '{"question": "..."}'
"""

import logging
import os

import anthropic
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

from app.agent import run_agent  # noqa: E402  (import after load_dotenv on purpose)

logger = logging.getLogger(__name__)

app = FastAPI(title="SecOps Copilot")

PERSIST_DIR = os.environ.get("CHROMA_DB_DIR", "./chroma_db")


class AskRequest(BaseModel):
    question: str


class ToolCallRecord(BaseModel):
    name: str
    input: dict
    result: dict


class AskResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCallRecord]
    steps_used: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    try:
        result = await run_agent(req.question, persist_dir=PERSIST_DIR)
    except (openai.APIError, anthropic.APIError) as e:
        logger.exception("Upstream LLM provider error while handling /ask")
        raise HTTPException(status_code=502, detail=f"LLM provider error: {e}")
    except Exception as e:
        logger.exception("Unexpected error while handling /ask")
        raise HTTPException(status_code=500, detail=f"Internal server error: {type(e).__name__}: {e}")

    return AskResponse(
        answer=result.answer,
        tool_calls=[ToolCallRecord(**tc) for tc in result.trace.tool_calls],
        steps_used=result.trace.steps_used,
    )
