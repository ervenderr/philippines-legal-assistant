import os
import json
import pandas as pd
from datetime import datetime
import pdfplumber

def extract_metadata(pdf_path):
    """Extract basic metadata from PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Get first page text for title extraction
            first_page = pdf.pages[0].extract_text()
            
            # Basic title extraction - first line of text
            title = first_page.split('\n')[0].strip()
            
            # Get file stats
            file_stats = os.stat(pdf_path)
            size_kb = file_stats.st_size / 1024
            modified_date = datetime.fromtimestamp(file_stats.st_mtime)
            
            return {
                'Title': title,
                'File Name': os.path.basename(pdf_path),
                'Date Modified': modified_date.strftime('%Y-%m-%d'),
                'Size (KB)': round(size_kb, 2),
                'Type': 'Supreme Court Decision' if not '-' in os.path.basename(pdf_path) else 'Separate Opinion',
                'Source URL': 'https://sc.judiciary.gov.ph/jurisprudence/'
            }
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return None

def create_catalog(raw_dir=None):
    """Create a catalog of all PDF documents in the raw directory."""
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if raw_dir is None:
        raw_dir = os.path.join(script_dir, 'raw')
    
    processed_dir = os.path.join(os.path.dirname(script_dir), 'processed')
    
    # Ensure raw directory exists
    if not os.path.exists(raw_dir):
        print(f"Raw directory not found at: {raw_dir}")
        return None
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(raw_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in: {raw_dir}")
        return None
    
    # Extract metadata for each file
    metadata_list = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(raw_dir, pdf_file)
        metadata = extract_metadata(pdf_path)
        if metadata:
            metadata_list.append(metadata)
    
    if not metadata_list:
        print("No metadata could be extracted from the PDF files")
        return None
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(metadata_list)
    
    # Add Document ID (simple incremental)
    df.insert(0, 'Document ID', range(1, len(df) + 1))
    
    # Save to CSV
    os.makedirs(processed_dir, exist_ok=True)
    csv_path = os.path.join(processed_dir, 'document_catalog.csv')
    df.to_csv(csv_path, index=False)
    
    print(f"Catalog created with {len(df)} documents")
    print(f"Saved to: {csv_path}")
    return df

if __name__ == "__main__":
    create_catalog() 