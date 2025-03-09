import json
import os
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

class DocumentEmbedder:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the document embedder with a sentence transformer model."""
        self.model = SentenceTransformer(model_name)
    
    def create_document_chunks(
        self,
        document: Dict[str, Any],
        chunk_size: int = 500,  # Smaller chunks
        overlap: int = 100
    ) -> List[Dict[str, Any]]:
        """Split document into overlapping chunks for processing."""
        if not document.get("full_text"):
            print(f"Warning: No text found in document {document.get('filename')}")
            return []
            
        text = document["full_text"]
        chunks = []
        
        # Split text into paragraphs first
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        
        current_chunk = []
        current_text = ""
        
        for para in paragraphs:
            # Split long paragraphs into sentences
            if len(para) > chunk_size:
                sentences = [s.strip() + "." for s in para.split(".") if s.strip()]
                for sentence in sentences:
                    if len(current_text + " " + sentence) > chunk_size and current_chunk:
                        # Store current chunk
                        chunk_text = " ".join(current_chunk)
                        chunks.append({
                            "id": f"{document['filename']}-chunk-{len(chunks)}",
                            "text": chunk_text,
                            "source": document['filename'],
                            "section_type": self._determine_section_type(chunk_text, document)
                        })
                        
                        # Start new chunk with overlap
                        if len(current_chunk) > 1:
                            current_chunk = current_chunk[-1:] + [sentence]
                            current_text = " ".join(current_chunk)
                        else:
                            current_chunk = [sentence]
                            current_text = sentence
                    else:
                        current_chunk.append(sentence)
                        current_text = current_text + " " + sentence if current_text else sentence
            else:
                # Handle regular paragraphs
                if len(current_text + " " + para) > chunk_size and current_chunk:
                    # Store current chunk
                    chunk_text = " ".join(current_chunk)
                    chunks.append({
                        "id": f"{document['filename']}-chunk-{len(chunks)}",
                        "text": chunk_text,
                        "source": document['filename'],
                        "section_type": self._determine_section_type(chunk_text, document)
                    })
                    
                    # Start new chunk with overlap
                    if len(current_chunk) > 1:
                        current_chunk = current_chunk[-1:] + [para]
                        current_text = " ".join(current_chunk)
                    else:
                        current_chunk = [para]
                        current_text = para
                else:
                    current_chunk.append(para)
                    current_text = current_text + " " + para if current_text else para
        
        # Add final chunk if it exists
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "id": f"{document['filename']}-chunk-{len(chunks)}",
                "text": chunk_text,
                "source": document['filename'],
                "section_type": self._determine_section_type(chunk_text, document)
            })
        
        print(f"Created {len(chunks)} chunks from {document['filename']}")
        return chunks
    
    def _determine_section_type(self, chunk_text: str, document: Dict[str, Any]) -> str:
        """Determine which section of the document this chunk belongs to."""
        chunk_text = chunk_text.upper()
        sections = document.get("sections", {})
        
        # Check if chunk belongs to a specific section
        if sections.get("header") and chunk_text.startswith(sections["header"][:100].upper()):
            return "header"
        elif sections.get("syllabus") and chunk_text in sections["syllabus"].upper():
            return "syllabus"
        elif sections.get("dispositive") and chunk_text in sections["dispositive"].upper():
            return "dispositive"
        else:
            return "decision"
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate embeddings for document chunks."""
        if not chunks:
            return []
            
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings in batches
        embeddings = []
        batch_size = 32
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(batch_texts)
            embeddings.extend(batch_embeddings.tolist())
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i]
        
        return chunks

def process_documents(processed_dir: str = None, embeddings_dir: str = None) -> None:
    """Process all documents and generate embeddings."""
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if processed_dir is None:
        processed_dir = os.path.join(os.path.dirname(script_dir), 'processed')
    if embeddings_dir is None:
        embeddings_dir = os.path.join(os.path.dirname(script_dir), 'embeddings')
    
    # Ensure processed directory exists
    if not os.path.exists(processed_dir):
        print(f"Processed directory not found at: {processed_dir}")
        return
    
    # Create embeddings directory
    os.makedirs(embeddings_dir, exist_ok=True)
    
    # Initialize embedder
    embedder = DocumentEmbedder()
    
    # Process all JSON files
    all_chunks = []
    json_files = [f for f in os.listdir(processed_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in: {processed_dir}")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    for json_file in tqdm(json_files, desc="Processing documents"):
        try:
            # Load processed document
            with open(os.path.join(processed_dir, json_file), 'r', encoding='utf-8') as f:
                document = json.load(f)
            
            # Create chunks
            chunks = embedder.create_document_chunks(document)
            
            if chunks:
                # Generate embeddings
                chunks_with_embeddings = embedder.generate_embeddings(chunks)
                
                # Add to collection
                all_chunks.extend(chunks_with_embeddings)
            else:
                print(f"Warning: No chunks created for {json_file}")
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
            continue
    
    if not all_chunks:
        print("No chunks were created from any documents")
        return
    
    # Save all chunks with embeddings
    output_file = os.path.join(embeddings_dir, "document_chunks.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {len(json_files)} documents into {len(all_chunks)} chunks")
    print(f"Saved embeddings to: {output_file}")

if __name__ == "__main__":
    process_documents() 