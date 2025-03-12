import os
import uuid
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import tempfile
from fastapi import UploadFile

# Import document processing modules
from data.document_parser import DocumentParser
from data.document_embeddings import DocumentEmbedder

class DocumentService:
    def __init__(self):
        """Initialize the document service."""
        self.parser = DocumentParser()
        self.embedder = DocumentEmbedder()
        
        # Set up directories
        self.base_dir = Path(__file__).parent.parent
        self.user_data_dir = self.base_dir / "user_data"
        self.user_data_dir.mkdir(exist_ok=True)
    
    def get_user_dir(self, user_id: str) -> Path:
        """Get or create user-specific directory."""
        user_dir = self.user_data_dir / user_id
        user_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (user_dir / "raw").mkdir(exist_ok=True)
        (user_dir / "processed").mkdir(exist_ok=True)
        (user_dir / "embeddings").mkdir(exist_ok=True)
        
        return user_dir
    
    async def upload_document(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """Upload and process a document."""
        # Create user directory
        user_dir = self.get_user_dir(user_id)
        
        # Generate a unique filename
        original_filename = file.filename or "document.pdf"
        file_extension = original_filename.split(".")[-1].lower()
        
        if file_extension != "pdf":
            raise ValueError("Only PDF files are supported")
        
        # Create a unique filename
        unique_id = str(uuid.uuid4())
        unique_filename = f"{unique_id}.pdf"
        
        # Save the uploaded file
        file_path = user_dir / "raw" / unique_filename
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Read the uploaded file in chunks and write to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Move the temporary file to the destination
        shutil.move(temp_file_path, file_path)
        
        # Process the document
        processed_data = self.process_document(str(file_path), user_id, original_filename)
        
        if not processed_data:
            raise ValueError("Failed to process document")
        
        return {
            "id": unique_id,
            "filename": original_filename,
            "status": "processed",
            "metadata": processed_data.get("metadata", {})
        }
    
    def process_document(self, pdf_path: str, user_id: str, original_filename: str) -> Optional[Dict[str, Any]]:
        """Process a document and generate embeddings."""
        user_dir = self.get_user_dir(user_id)
        
        # Extract the document ID from the filename
        doc_id = os.path.basename(pdf_path).split(".")[0]
        
        # Process the document
        processed_path = user_dir / "processed" / f"{doc_id}.json"
        
        # Extract text and metadata
        text = self.parser.extract_text_from_pdf(pdf_path)
        if not text:
            return None
        
        # Clean the text
        text = self.parser.clean_legal_text(text)
        
        # Extract sections
        sections = self.parser.extract_sections(text)
        
        # Create document metadata
        metadata = {
            "id": doc_id,
            "filename": original_filename,
            "sections": {k: len(v) for k, v in sections.items()},
            "total_length": len(text)
        }
        
        # Create document object
        document = {
            "id": doc_id,
            "filename": original_filename,
            "full_text": text,
            "sections": sections,
            "metadata": metadata
        }
        
        # Save processed document
        with open(processed_path, "w", encoding="utf-8") as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
        
        # Create chunks and embeddings
        chunks = self.embedder.create_document_chunks(document)
        chunks_with_embeddings = self.embedder.generate_embeddings(chunks)
        
        # Save embeddings
        embeddings_path = user_dir / "embeddings" / f"{doc_id}.json"
        with open(embeddings_path, "w", encoding="utf-8") as f:
            json.dump(chunks_with_embeddings, f, ensure_ascii=False, indent=2)
        
        # Update user's document catalog
        self.update_user_catalog(user_id, document)
        
        return document
    
    def update_user_catalog(self, user_id: str, document: Dict[str, Any]) -> None:
        """Update the user's document catalog."""
        user_dir = self.get_user_dir(user_id)
        catalog_path = user_dir / "catalog.json"
        
        # Create or load existing catalog
        if catalog_path.exists():
            with open(catalog_path, "r", encoding="utf-8") as f:
                catalog = json.load(f)
        else:
            catalog = {"documents": []}
        
        # Add or update document in catalog
        doc_entry = {
            "id": document["id"],
            "filename": document["filename"],
            "status": "processed",
            "metadata": document["metadata"]
        }
        
        # Check if document already exists
        for i, existing_doc in enumerate(catalog["documents"]):
            if existing_doc["id"] == document["id"]:
                catalog["documents"][i] = doc_entry
                break
        else:
            catalog["documents"].append(doc_entry)
        
        # Save updated catalog
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
    
    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get a list of documents for a user."""
        user_dir = self.get_user_dir(user_id)
        catalog_path = user_dir / "catalog.json"
        
        if not catalog_path.exists():
            return []
        
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        
        # Add status field to each document
        documents = catalog["documents"]
        for doc in documents:
            # Add status field if it doesn't exist
            if "status" not in doc:
                doc["status"] = "processed"
        
        return documents
    
    def get_document_chunks(self, user_id: str, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get document chunks for a user, optionally filtered by document ID."""
        user_dir = self.get_user_dir(user_id)
        embeddings_dir = user_dir / "embeddings"
        
        all_chunks = []
        
        # If document_id is provided, only load that document
        if document_id:
            embedding_path = embeddings_dir / f"{document_id}.json"
            if embedding_path.exists():
                with open(embedding_path, "r", encoding="utf-8") as f:
                    chunks = json.load(f)
                all_chunks.extend(chunks)
        else:
            # Load all documents
            for embedding_file in embeddings_dir.glob("*.json"):
                with open(embedding_file, "r", encoding="utf-8") as f:
                    chunks = json.load(f)
                all_chunks.extend(chunks)
        
        return all_chunks 