from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class QAService:
    def __init__(self):
        # Initialize embedding model for document retrieval
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize a local question-answering pipeline
        try:
            # This will use a smaller model suitable for question answering
            self.qa_pipeline = pipeline(
                "question-answering",
                model="distilbert-base-cased-distilled-squad",
                tokenizer="distilbert-base-cased-distilled-squad"
            )
            print("Initialized local QA model successfully")
        except Exception as e:
            print(f"Error initializing QA pipeline: {str(e)}")
            self.qa_pipeline = None

    def _get_relevant_chunks(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve most relevant document chunks for the query."""
        if not chunks:
            return []
            
        # Extract embeddings from chunks
        chunk_embeddings = np.array([chunk["embedding"] for chunk in chunks])
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Calculate similarities
        similarities = np.dot(chunk_embeddings, query_embedding) / (
            np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        result_chunks = []
        for i in top_indices:
            chunk = chunks[i].copy()
            chunk["similarity"] = float(similarities[i])
            result_chunks.append(chunk)
            
        return result_chunks

    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Format chunks into context string."""
        context = "\n\n".join([
            f"Source: {chunk['source']}\n{chunk['text']}"
            for chunk in chunks
        ])
        return context

    def answer_question(self, question: str, chunks: List[Dict[str, Any]], top_k: int = 5) -> Dict[str, Any]:
        """Answer a question using a local model with retrieved context."""
        try:
            # Get relevant chunks
            relevant_chunks = self._get_relevant_chunks(question, chunks, top_k)
            
            if not relevant_chunks:
                return {
                    "answer": "I don't have enough information to answer this question. Please upload relevant documents first.",
                    "sources": [],
                    "context": "",
                    "relevant_chunks": []
                }
                
            # Format context
            context = self._format_context(relevant_chunks)
            
            # If QA pipeline is not available, return a simple response
            if self.qa_pipeline is None:
                return {
                    "answer": "I'm unable to process your question because the QA model is not available. Please check the server logs for more information.",
                    "sources": [chunk["source"] for chunk in relevant_chunks],
                    "context": context,
                    "relevant_chunks": [
                        {
                            "text": chunk["text"],
                            "source": chunk["source"],
                            "similarity": chunk["similarity"]
                        }
                        for chunk in relevant_chunks
                    ]
                }
            
            # Use the local QA pipeline to get an answer
            try:
                # Combine all relevant chunks into a single context
                combined_text = "\n\n".join([chunk["text"] for chunk in relevant_chunks])
                
                # Get answer from QA pipeline
                result = self.qa_pipeline(
                    question=question,
                    context=combined_text,
                )
                
                # Format the answer
                answer = result["answer"]
                confidence = result["score"]
                
                # Find the source chunk that contains the answer
                source_chunk = None
                for chunk in relevant_chunks:
                    if answer in chunk["text"]:
                        source_chunk = chunk
                        break
                
                source = source_chunk["source"] if source_chunk else relevant_chunks[0]["source"]
                
                # Create a more comprehensive answer
                comprehensive_answer = f"""
Based on the provided documents, the answer is:

{answer}

This information comes from: {source}

Confidence: {confidence:.2f}
                """
                
                return {
                    "answer": comprehensive_answer.strip(),
                    "sources": [chunk["source"] for chunk in relevant_chunks],
                    "context": context,
                    "relevant_chunks": [
                        {
                            "text": chunk["text"],
                            "source": chunk["source"],
                            "similarity": chunk["similarity"]
                        }
                        for chunk in relevant_chunks
                    ]
                }
            except Exception as model_error:
                print(f"Model error: {str(model_error)}")
                # Fallback to a simple response
                return {
                    "answer": f"I encountered an error while processing your question with the local model. Error: {str(model_error)}",
                    "sources": [chunk["source"] for chunk in relevant_chunks],
                    "context": context,
                    "relevant_chunks": [
                        {
                            "text": chunk["text"],
                            "source": chunk["source"],
                            "similarity": chunk["similarity"]
                        }
                        for chunk in relevant_chunks
                    ]
                }
        except Exception as e:
            print(f"Error in answer_question: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def get_sources(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Get list of all available document sources."""
        return list(set(chunk["source"] for chunk in chunks)) 