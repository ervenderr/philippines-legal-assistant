from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
from pathlib import Path

# Add the parent directory to Python path to import the QA system
sys.path.append(str(Path(__file__).parent.parent))
from data.qa_system import LegalQASystem

app = FastAPI(
    title="Philippine Legal Assistant API",
    description="API for analyzing Philippine legal documents and answering questions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize QA system
qa_system = LegalQASystem()

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3
    threshold: Optional[float] = 0.5

class ChunkInfo(BaseModel):
    text: str
    source: str
    similarity: float

class AnswerResponse(BaseModel):
    answer: str
    confidence: float
    source: Optional[str] = None
    relevant_chunks: List[ChunkInfo] = []

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Philippine Legal Assistant API is running"}

@app.post("/api/query", response_model=AnswerResponse)
async def query(request: QuestionRequest):
    """
    Get an answer for a legal question.
    
    Args:
        request: QuestionRequest object containing the question and optional parameters
        
    Returns:
        AnswerResponse object containing the answer and related information
    """
    try:
        # Get relevant chunks first
        relevant_chunks = qa_system.find_relevant_chunks(
            request.question,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        # Get answer using QA system
        result = qa_system.answer_question(
            request.question,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        # Transform chunks into response format
        formatted_chunks = [
            ChunkInfo(
                text=chunk["text"],
                source=chunk["source"],
                similarity=chunk["similarity"]
            )
            for chunk in relevant_chunks
        ]
        
        # Return formatted response
        return AnswerResponse(
            answer=result["answer"],
            confidence=result.get("confidence", 0.0),
            source=result.get("source"),
            relevant_chunks=formatted_chunks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 