from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os
from pathlib import Path
from api.qa_service import QAService
from api.document_service import DocumentService

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

# Initialize services
qa_service = QAService()
document_service = DocumentService()

# For backward compatibility
qa_system = LegalQASystem()

class QuestionRequest(BaseModel):
    question: str
    user_id: str
    document_id: Optional[str] = None
    top_k: Optional[int] = 3
    threshold: Optional[float] = 0.5

class ChunkInfo(BaseModel):
    text: str
    source: str
    similarity: float

class AnswerResponse(BaseModel):
    answer: str
    confidence: Optional[float] = None
    source: Optional[str] = None
    relevant_chunks: List[ChunkInfo] = []

class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    metadata: Dict[str, Any] = {}

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Philippine Legal Assistant API is running"}

@app.post("/api/query", response_model=AnswerResponse)
async def query(request: QuestionRequest):
    """
    Get an answer for a legal question based on user-uploaded documents.
    
    Args:
        request: QuestionRequest object containing the question and user information
        
    Returns:
        AnswerResponse object containing the answer and related information
    """
    try:
        # Get document chunks for the user
        chunks = document_service.get_document_chunks(
            user_id=request.user_id,
            document_id=request.document_id
        )
        
        if not chunks:
            return AnswerResponse(
                answer="No documents found. Please upload documents first.",
                confidence=0.0,
                source=None,
                relevant_chunks=[]
            )
        
        # Get answer using QA service
        try:
            result = qa_service.answer_question(
                question=request.question,
                chunks=chunks,
                top_k=request.top_k
            )
        except Exception as qa_error:
            print(f"Error in QA service: {str(qa_error)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing question: {str(qa_error)}"
            )
        
        # Transform chunks into response format
        formatted_chunks = [
            ChunkInfo(
                text=chunk["text"],
                source=chunk["source"],
                similarity=chunk["similarity"]
            )
            for chunk in result.get("relevant_chunks", [])
        ]
        
        # Return formatted response
        return AnswerResponse(
            answer=result["answer"],
            confidence=0.0,  # Not provided by the new service
            source=result.get("sources", [None])[0] if result.get("sources") else None,
            relevant_chunks=formatted_chunks
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in query endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    """
    Upload a document for processing.
    
    Args:
        file: The PDF file to upload
        user_id: The ID of the user uploading the document
        
    Returns:
        DocumentResponse object with document information
    """
    try:
        result = await document_service.upload_document(file, user_id)
        return DocumentResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{user_id}", response_model=DocumentListResponse)
async def get_user_documents(user_id: str):
    """
    Get a list of documents for a user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        DocumentListResponse object with a list of documents
    """
    try:
        documents = document_service.get_user_documents(user_id)
        return DocumentListResponse(
            documents=[DocumentResponse(**doc) for doc in documents]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sources/{user_id}")
async def get_user_sources(user_id: str):
    """Get list of all available document sources for a user."""
    chunks = document_service.get_document_chunks(user_id)
    return qa_service.get_sources(chunks)

@app.delete("/api/documents/{user_id}/{document_id}")
async def delete_document(user_id: str, document_id: str):
    """
    Delete a document.
    
    Args:
        user_id: The ID of the user
        document_id: The ID of the document to delete
        
    Returns:
        Success message or error
    """
    try:
        success = document_service.delete_document(user_id, document_id)
        if success:
            return {"status": "success", "message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

# Legacy endpoint for backward compatibility
@app.post("/api/legacy/query", response_model=AnswerResponse)
async def legacy_query(request: QuestionRequest):
    """
    Legacy endpoint for querying the system with pre-loaded documents.
    
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