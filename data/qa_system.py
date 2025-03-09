import json
import os
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
import torch
from tqdm import tqdm

class LegalQASystem:
    def __init__(
        self,
        embeddings_path: str = None,
        qa_model_name: str = "deepset/roberta-base-squad2",
        embedding_model_name: str = "all-MiniLM-L6-v2"
    ):
        """Initialize the QA system with necessary models and data."""
        # Set up paths
        if embeddings_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            embeddings_dir = os.path.join(os.path.dirname(script_dir), 'embeddings')
            embeddings_path = os.path.join(embeddings_dir, 'document_chunks.json')
        
        if not os.path.exists(embeddings_path):
            raise FileNotFoundError(f"Embeddings file not found at: {embeddings_path}")
        
        # Load models
        self.qa_pipeline = pipeline(
            "question-answering",
            model=qa_model_name,
            tokenizer=qa_model_name,
            device=0 if torch.cuda.is_available() else -1
        )
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # Load document chunks
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        
        # Convert embeddings to numpy array for faster processing
        self.embeddings = np.array([chunk["embedding"] for chunk in self.chunks])
        
        print(f"Loaded {len(self.chunks)} document chunks from: {embeddings_path}")
    
    def find_relevant_chunks(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Find the most relevant document chunks for a given query."""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Calculate cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top k results above threshold
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        relevant_chunks = []
        
        for idx in top_indices:
            similarity = float(similarities[idx])
            if similarity >= threshold:
                chunk = self.chunks[idx].copy()
                chunk["similarity"] = similarity
                relevant_chunks.append(chunk)
        
        # Sort by similarity
        relevant_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return relevant_chunks
    
    def answer_question(
        self,
        question: str,
        top_k: int = 5,
        threshold: float = 0.3
    ) -> Dict[str, Any]:
        """Answer a question using the relevant document chunks."""
        # Find relevant chunks
        relevant_chunks = self.find_relevant_chunks(question, top_k, threshold)
        
        if not relevant_chunks:
            return {
                "answer": "I could not find any relevant information to answer this question.",
                "confidence": 0.0,
                "context": None,
                "source": None,
                "relevant_chunks": []
            }
        
        # Sort chunks by similarity and combine into context
        chunks_text = []
        total_length = 0
        max_length = 2000  # Maximum context length
        
        for chunk in relevant_chunks:
            chunk_text = chunk["text"]
            if total_length + len(chunk_text) <= max_length:
                chunks_text.append(chunk_text)
                total_length += len(chunk_text)
            else:
                break
        
        context = "\n\n".join(chunks_text)
        
        # Get answer from QA model
        try:
            qa_result = self.qa_pipeline(
                question=question,
                context=context,
                handle_impossible_answer=True,
                max_answer_len=200  # Increased max answer length
            )
            
            # Find source chunk for the answer
            source_chunk = None
            for chunk in relevant_chunks:
                if qa_result["answer"] in chunk["text"]:
                    source_chunk = chunk
                    break
            
            # Format the response
            return {
                "answer": qa_result["answer"],
                "confidence": float(qa_result["score"]),
                "source": source_chunk["source"] if source_chunk else relevant_chunks[0]["source"],
                "relevant_chunks": [
                    {
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "similarity": chunk["similarity"]
                    }
                    for chunk in relevant_chunks[:3]  # Return top 3 most relevant chunks
                ]
            }
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            # Return most relevant text as fallback
            return {
                "answer": relevant_chunks[0]["text"][:500] + "...",
                "confidence": relevant_chunks[0]["similarity"],
                "source": relevant_chunks[0]["source"],
                "relevant_chunks": [
                    {
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "similarity": chunk["similarity"]
                    }
                    for chunk in relevant_chunks[:3]
                ]
            }

def setup_qa_system() -> None:
    """Download necessary models and set up the QA system."""
    # Download models
    model_name = "deepset/roberta-base-squad2"
    
    print("Downloading QA model...")
    AutoTokenizer.from_pretrained(model_name)
    AutoModelForQuestionAnswering.from_pretrained(model_name)
    
    print("Downloading embedding model...")
    SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Setup complete!")

if __name__ == "__main__":
    # Set up the system
    setup_qa_system()
    
    # Create QA system
    qa_system = LegalQASystem()
    
    # Example usage
    question = "What are the main points of the case?"
    result = qa_system.answer_question(question)
    
    print(f"\nQ: {question}")
    print(f"A: {result['answer']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Source: {result['source']}")
    
    if result.get('relevant_chunks'):
        print("\nRelevant document sections:")
        for chunk in result['relevant_chunks']:
            print(f"- {chunk['source']} - Similarity: {chunk['similarity']:.2f}")
    else:
        print("\nNo relevant document sections found.") 