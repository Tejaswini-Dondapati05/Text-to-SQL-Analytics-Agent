
"""
FastAPI backend for LangGraph Text-to-SQL Agent.

Run:
uvicorn api:app --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent import ask_question
from db import init_db


app = FastAPI(
    title="Text-to-SQL Analytics Agent",
    description="Gemini + LangGraph + SQLite + FastAPI",
    version="1.0.0"
)


# Initialize database
@app.on_event("startup")
def startup():
    init_db()


# Request schema
class Question(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Ask a question about your database"
    )


# Health check
@app.get("/")
def health():
    return {
        "status": "ok",
        "message": "Text-to-SQL Agent API is running"
    }


# Ask question
@app.post("/ask")
def ask(q: Question):

    question = q.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        result = ask_question(question)

        if result.get("error"):
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
