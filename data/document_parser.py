import pdfplumber
import re
import json
import os
from typing import Dict, List, Optional
import spacy
from tqdm import tqdm

class DocumentParser:
    def __init__(self):
        """Initialize the document parser with spaCy model."""
        self.nlp = spacy.load("en_core_web_sm")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF while preserving basic structure."""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                print(f"Processing {pdf_path}: {len(pdf.pages)} pages")
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                print(f"Extracted {len(text)} characters")
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {str(e)}")
            return ""
        return text

    def clean_legal_text(self, text: str) -> str:
        """Clean and structure legal text."""
        if not text.strip():
            return ""
            
        # Remove page numbers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Fix paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = re.sub(r'([A-Za-z]),([A-Za-z])', r'\1, \2', text)
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Split document into logical sections based on headings."""
        if not text.strip():
            return {
                "header": "",
                "syllabus": "",
                "decision": "",
                "dispositive": ""
            }
        
        sections = {
            "header": "",
            "syllabus": "",
            "decision": "",
            "dispositive": ""
        }
        
        # Split into paragraphs
        paragraphs = text.split("\n\n")
        
        # Extract header (first few paragraphs)
        header_end = min(3, len(paragraphs))
        sections["header"] = "\n\n".join(paragraphs[:header_end])
        
        # Look for syllabus section
        for i, para in enumerate(paragraphs):
            if any(keyword in para.upper() for keyword in ["SYLLABUS", "SYNOPSIS", "SUMMARY"]):
                sections["syllabus"] = para
                break
        
        # Look for dispositive portion (from the end)
        for i, para in enumerate(reversed(paragraphs)):
            if any(keyword in para.upper() for keyword in ["WHEREFORE", "SO ORDERED"]):
                sections["dispositive"] = para
                break
        
        # The rest is considered the decision
        sections["decision"] = text
        
        return sections

    def process_document(self, pdf_path: str, output_dir: str) -> Optional[Dict]:
        """Process a single document and save the results."""
        print(f"\nProcessing document: {pdf_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print(f"No text extracted from {pdf_path}")
            return None
        
        # Clean text
        cleaned_text = self.clean_legal_text(text)
        if not cleaned_text:
            print(f"No text after cleaning {pdf_path}")
            return None
        
        print(f"Cleaned text length: {len(cleaned_text)} characters")
        
        # Extract sections
        sections = self.extract_sections(cleaned_text)
        
        # Process with spaCy for additional analysis
        doc = self.nlp(cleaned_text[:1000000])  # Limit to 1M chars to avoid memory issues
        
        # Extract entities
        entities = [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            for ent in doc.ents
        ]
        
        # Create output structure
        output = {
            "filename": os.path.basename(pdf_path),
            "full_text": cleaned_text,
            "sections": sections,
            "entities": entities,
            "metadata": {
                "num_tokens": len(doc),
                "num_sentences": len(list(doc.sents)),
                "num_entities": len(entities)
            }
        }
        
        # Save to JSON
        output_path = os.path.join(
            output_dir,
            os.path.basename(pdf_path).replace(".pdf", ".json")
        )
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"Saved processed document to: {output_path}")
        return output

def process_all_documents(raw_dir: str = None, processed_dir: str = None) -> None:
    """Process all PDF documents in the raw directory."""
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if raw_dir is None:
        raw_dir = os.path.join(script_dir, 'raw')
    if processed_dir is None:
        processed_dir = os.path.join(os.path.dirname(script_dir), 'processed')
    
    # Ensure directories exist
    if not os.path.exists(raw_dir):
        print(f"Raw directory not found at: {raw_dir}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(processed_dir, exist_ok=True)
    
    # Initialize parser
    parser = DocumentParser()
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(raw_dir) if f.endswith(".pdf")]
    
    if not pdf_files:
        print(f"No PDF files found in: {raw_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each document
    for pdf_file in tqdm(pdf_files, desc="Processing documents"):
        pdf_path = os.path.join(raw_dir, pdf_file)
        parser.process_document(pdf_path, processed_dir)
    
    print(f"Processed documents saved to: {processed_dir}")

if __name__ == "__main__":
    # Download spaCy model if not already installed
    os.system("python -m spacy download en_core_web_sm")
    
    # Process all documents
    process_all_documents() 