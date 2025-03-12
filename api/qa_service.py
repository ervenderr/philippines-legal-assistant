from typing import List, Dict, Any, Optional
import openai
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
import os
import json
from pathlib import Path

load_dotenv()

class QAService:
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        openai.api_key = api_key
        
        # Initialize embedding model for document retrieval
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

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
        """Answer a question using GPT-4 with retrieved context."""
        # Get relevant chunks
        try:
            relevant_chunks = self._get_relevant_chunks(question, chunks, top_k)
            
            if not relevant_chunks:
                return {
                    "answer": "I don't have enough information to answer this question. Please upload relevant documents first.",
                    "sources": [],
                    "context": "",
                    "relevant_chunks": []
                }
                
            context = self._format_context(relevant_chunks)
            
            # Construct the prompt
            system_prompt = """You are a legal assistant specialized in Philippine law. 
            Answer questions based on the provided legal document excerpts.
            Always cite your sources and be precise in your answers.
            If you're not confident about an answer or if the context doesn't contain relevant information, say so.
            Format your response in markdown."""

            user_prompt = f"""Context from legal documents:
            {context}

            Question: {question}

            Please provide a detailed answer with:
            1. Direct answer to the question
            2. Relevant citations from the provided context
            3. Any important caveats or limitations"""

            # Get response from GPT-4
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,  # Lower temperature for more focused answers
                    max_tokens=1000
                )
            except Exception as openai_error:
                print(f"OpenAI API error: {str(openai_error)}")
                # Fallback to a simple response
                return {
                    "answer": f"I encountered an error while processing your question. Error: {str(openai_error)}",
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

            # Extract sources
            sources = [chunk["source"] for chunk in relevant_chunks]
            
            return {
                "answer": response.choices[0].message["content"],
                "sources": sources,
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