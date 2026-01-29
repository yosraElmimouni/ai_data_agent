from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import engine, Base, get_db
from backend.utils import seed_db
from backend.agent import AIAgent
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Data Agent API")

# Seed database on startup
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    seed_db(db)

class QuestionRequest(BaseModel):
    question: str
    api_key: str

@app.get("/")
def read_root():
    return {"message": "AI Data Agent API is running"}

@app.post("/ask")
def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
    agent = AIAgent(api_key=request.api_key)
    try:
        response = agent.question(db, request.question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
