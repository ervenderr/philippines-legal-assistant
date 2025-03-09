# Personal Project: Building a Legal Document Analysis Tool for Philippine Law

## Project Overview
This personal project aims to create a simple but effective tool that can analyze Philippine legal documents, extract key information, and answer specific questions about their content. It's designed as a learning experience that will strengthen your ML/NLP skills while creating something potentially useful.

## Phase 1: Setting Up Your Project (Week 1)

### Day 1-2: Environment and Resource Setup
1. **Create a project directory**:
   ```
   mkdir philippines-legal-assistant
   cd philippines-legal-assistant
   ```

2. **Set up a virtual environment**:
   ```
   python -m venv legal_env
   source legal_env/bin/activate  # On Windows: legal_env\Scripts\activate
   ```

3. **Install necessary libraries**:
   ```
   pip install transformers datasets torch pandas numpy spacy gensim sentence-transformers
   pip install flask python-dotenv pdfplumber
   ```

4. **Create a GitHub repository** for tracking your progress

### Day 3-5: Data Collection
1. **Download a small set of legal documents**:
   - 10-15 Supreme Court decisions from [SC Judiciary](https://sc.judiciary.gov.ph/jurisprudence/)
   - 5-10 Philippine laws or regulations from [Official Gazette](https://www.officialgazette.gov.ph/)
   - Store in a `data/raw` folder

2. **Create a simple data catalog**:
   - Make a spreadsheet listing your documents with metadata:
     - Document ID
     - Title
     - Date
     - Type (court decision, law, contract, etc.)
     - Source URL

## Phase 2: Document Processing (Week 2)

### Day 6-8: Document Parsing
1. **Create a document parser**:
   ```python
   # document_parser.py
   import pdfplumber
   import re
   
   def extract_text_from_pdf(pdf_path):
       """Extract text from PDF while preserving basic structure."""
       text = ""
       with pdfplumber.open(pdf_path) as pdf:
           for page in pdf.pages:
               text += page.extract_text() + "\n\n"
       return text
   
   def clean_legal_text(text):
       """Clean and structure legal text."""
       # Remove page numbers
       text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
       # Fix paragraph breaks
       text = re.sub(r'\n\s*\n', '\n\n', text)
       return text
   
   def extract_sections(text):
       """Split document into logical sections based on headings."""
       # Implement basic section detection based on patterns in your documents
       # This will be specific to Philippine legal document formats
       return sections
   ```

2. **Process your documents**:
   ```python
   # process_documents.py
   import os
   import json
   from document_parser import extract_text_from_pdf, clean_legal_text, extract_sections
   
   raw_dir = "data/raw"
   processed_dir = "data/processed"
   
   os.makedirs(processed_dir, exist_ok=True)
   
   for filename in os.listdir(raw_dir):
       if filename.endswith(".pdf"):
           pdf_path = os.path.join(raw_dir, filename)
           text = extract_text_from_pdf(pdf_path)
           cleaned_text = clean_legal_text(text)
           sections = extract_sections(cleaned_text)
           
           # Save processed document
           output_file = os.path.join(processed_dir, filename.replace(".pdf", ".json"))
           with open(output_file, "w") as f:
               json.dump({
                   "filename": filename,
                   "full_text": cleaned_text,
                   "sections": sections
               }, f, indent=2)
   ```

### Day 9-10: Document Chunking and Analysis
1. **Create functions to split documents into manageable chunks**:
   ```python
   def create_document_chunks(document, chunk_size=500, overlap=100):
       """Split document into overlapping chunks for processing."""
       text = document["full_text"]
       chunks = []
       
       # Create overlapping chunks
       for i in range(0, len(text), chunk_size - overlap):
           chunk = text[i:i + chunk_size]
           chunks.append({
               "id": f"{document['filename']}-chunk-{len(chunks)}",
               "text": chunk,
               "source": document['filename']
           })
       
       return chunks
   ```

2. **Analyze document structure**:
   ```python
   import spacy
   
   nlp = spacy.load("en_core_web_sm")
   
   def analyze_document_structure(document):
       """Extract key entities and structure from document."""
       doc = nlp(document["full_text"])
       
       # Extract entities
       entities = [{"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
                  for ent in doc.ents]
       
       # Extract sentence boundaries
       sentences = [{"text": sent.text, "start": sent.start_char, "end": sent.end_char}
                   for sent in doc.sents]
       
       return {
           "filename": document["filename"],
           "entities": entities,
           "sentences": sentences
       }
   ```

## Phase 3: Building the Retrieval System (Week 3)

### Day 11-13: Document Embeddings
1. **Generate embeddings for your document chunks**:
   ```python
   from sentence_transformers import SentenceTransformer
   
   # Use a generic model first (later you can fine-tune)
   model = SentenceTransformer('all-MiniLM-L6-v2')
   
   def generate_embeddings(chunks):
       """Generate embeddings for document chunks."""
       texts = [chunk["text"] for chunk in chunks]
       embeddings = model.encode(texts)
       
       for i, chunk in enumerate(chunks):
           chunk["embedding"] = embeddings[i].tolist()
       
       return chunks
   ```

2. **Save embeddings**:
   ```python
   import json
   
   def save_embeddings(chunks, output_file):
       """Save document chunks with embeddings."""
       with open(output_file, "w") as f:
           json.dump(chunks, f)
   
   # Process all documents
   all_chunks = []
   for filename in os.listdir("data/processed"):
       if filename.endswith(".json"):
           with open(os.path.join("data/processed", filename)) as f:
               document = json.load(f)
           
           chunks = create_document_chunks(document)
           chunks_with_embeddings = generate_embeddings(chunks)
           all_chunks.extend(chunks_with_embeddings)
   
   save_embeddings(all_chunks, "data/embeddings/document_chunks.json")
   ```

### Day 14-16: Building a Simple Retrieval System
1. **Create a basic vector search function**:
   ```python
   import numpy as np
   from sentence_transformers import SentenceTransformer
   
   model = SentenceTransformer('all-MiniLM-L6-v2')
   
   def load_document_chunks(embeddings_file):
       """Load document chunks with embeddings."""
       with open(embeddings_file) as f:
           return json.load(f)
   
   def search_documents(query, chunks, top_k=5):
       """Search for relevant document chunks."""
       query_embedding = model.encode(query)
       
       # Convert list embeddings to numpy for faster processing
       chunk_embeddings = np.array([chunk["embedding"] for chunk in chunks])
       
       # Calculate cosine similarity
       similarities = np.dot(chunk_embeddings, query_embedding) / (
           np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(query_embedding)
       )
       
       # Get top k results
       top_indices = np.argsort(similarities)[-top_k:][::-1]
       
       results = []
       for idx in top_indices:
           results.append({
               "chunk": chunks[idx],
               "similarity": float(similarities[idx])
           })
       
       return results
   ```

## Phase 4: Building the Question-Answering System (Week 4)

### Day 17-19: Setting Up the Model
1. **Download a pre-trained model**:
   ```python
   from transformers import AutoTokenizer, AutoModelForQuestionAnswering
   
   # For this small project, we'll use a generic QA model first
   tokenizer = AutoTokenizer.from_pretrained("deepset/roberta-base-squad2")
   model = AutoModelForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2")
   
   # Save the model locally
   tokenizer.save_pretrained("models/qa_model")
   model.save_pretrained("models/qa_model")
   ```

2. **Create a QA function**:
   ```python
   from transformers import pipeline
   
   qa_pipeline = pipeline("question-answering", model="models/qa_model", tokenizer="models/qa_model")
   
   def answer_question(question, contexts):
       """Answer a question based on retrieved contexts."""
       # Concatenate contexts
       context = " ".join([result["chunk"]["text"] for result in contexts])
       
       # Truncate if too long
       max_length = 512
       if len(context) > max_length:
           context = context[:max_length]
       
       # Get answer
       result = qa_pipeline(question=question, context=context)
       
       return {
           "answer": result["answer"],
           "confidence": result["score"],
           "context": context
       }
   ```

### Day 20-21: Creating a Simple API
1. **Set up a Flask API**:
   ```python
   # app.py
   from flask import Flask, request, jsonify
   import json
   from search import load_document_chunks, search_documents
   from qa import answer_question
   
   app = Flask(__name__)
   
   # Load documents
   chunks = load_document_chunks("data/embeddings/document_chunks.json")
   
   @app.route('/api/query', methods=['POST'])
   def query():
       data = request.json
       question = data.get('question')
       
       if not question:
           return jsonify({"error": "Question is required"}), 400
       
       # Search for relevant chunks
       relevant_chunks = search_documents(question, chunks)
       
       # Answer the question
       answer = answer_question(question, relevant_chunks)
       
       # Add sources to the response
       answer["sources"] = [chunk["chunk"]["source"] for chunk in relevant_chunks]
       
       return jsonify(answer)
   
   if __name__ == '__main__':
       app.run(debug=True)
   ```

## Phase 5: Building a Simple UI (Week 5)

### Day 22-25: Creating a Basic Web Interface
1. **Create HTML templates**:
   ```html
   <!-- templates/index.html -->
   <!DOCTYPE html>
   <html>
   <head>
       <title>Philippine Legal Assistant</title>
       <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
   </head>
   <body>
       <div class="container">
           <h1>Philippine Legal Document Assistant</h1>
           <form id="queryForm">
               <input type="text" id="question" placeholder="Ask a question about your legal documents...">
               <button type="submit">Search</button>
           </form>
           <div id="results">
               <!-- Results will be displayed here -->
           </div>
       </div>
       <script src="{{ url_for('static', filename='script.js') }}"></script>
   </body>
   </html>
   ```

2. **Create JavaScript for the interface**:
   ```javascript
   // static/script.js
   document.getElementById('queryForm').addEventListener('submit', async function(e) {
       e.preventDefault();
       
       const question = document.getElementById('question').value;
       const resultsDiv = document.getElementById('results');
       
       resultsDiv.innerHTML = '<p>Searching...</p>';
       
       try {
           const response = await fetch('/api/query', {
               method: 'POST',
               headers: {
                   'Content-Type': 'application/json'
               },
               body: JSON.stringify({ question })
           });
           
           const data = await response.json();
           
           let html = `
               <div class="answer">
                   <h2>Answer:</h2>
                   <p>${data.answer}</p>
                   <p class="confidence">Confidence: ${Math.round(data.confidence * 100)}%</p>
                   <h3>Sources:</h3>
                   <ul>
           `;
           
           data.sources.forEach(source => {
               html += `<li>${source}</li>`;
           });
           
           html += `
                   </ul>
               </div>
           `;
           
           resultsDiv.innerHTML = html;
       } catch (error) {
           resultsDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
       }
   });
   ```

3. **Update Flask to serve the UI**:
   ```python
   # app.py (updated)
   from flask import Flask, request, jsonify, render_template
   
   # ... existing code ...
   
   @app.route('/')
   def index():
       return render_template('index.html')
   
   # ... rest of the existing code ...
   ```

## Phase 6: Testing and Improvements (Week 6)

### Day 26-28: Testing and Debugging
1. **Create test cases**:
   ```python
   # tests.py
   import requests
   import json
   
   BASE_URL = "http://localhost:5000"
   
   test_questions = [
       "What is the punishment for libel in the Philippines?",
       "How is property divided in divorce cases?",
       "What constitutes cybercrime under Philippine law?",
       # Add more test questions
   ]
   
   def test_api():
       """Test the query API with sample questions."""
       results = []
       
       for question in test_questions:
           response = requests.post(
               f"{BASE_URL}/api/query",
               json={"question": question}
           )
           
           results.append({
               "question": question,
               "response": response.json(),
               "status_code": response.status_code
           })
       
       # Save results
       with open("test_results.json", "w") as f:
           json.dump(results, f, indent=2)
   
   if __name__ == "__main__":
       test_api()
   ```

2. **Manually review results and fix issues**

### Day 29-30: Adding Improvements
1. **Improve citation extraction**:
   ```python
   def extract_citations(text):
       """Extract legal citations from text."""
       # Philippine citation patterns
       patterns = [
           r'G\.R\. No\. \d+',
           r'Republic Act No\. \d+',
           # Add more patterns
       ]
       
       citations = []
       for pattern in patterns:
           matches = re.findall(pattern, text)
           citations.extend(matches)
       
       return citations
   ```

2. **Add citation to the API response**:
   ```python
   # Update the query function
   @app.route('/api/query', methods=['POST'])
   def query():
       # ... existing code ...
       
       # Extract citations
       citations = extract_citations(answer["context"])
       answer["citations"] = citations
       
       return jsonify(answer)
   ```

## Phase 7: Documentation and Reflection (Week 7)

### Day 31-32: Documentation
1. **Create a README.md file**:
   ```markdown
   # Philippine Legal Document Assistant

   A personal project to explore and analyze Philippine legal documents using NLP.

   ## Features
   - Document processing for Philippine legal texts
   - Semantic search across legal documents
   - Question answering based on legal document context
   - Extraction of legal citations

   ## Setup
   1. Clone this repository
   2. Create a virtual environment: `python -m venv legal_env`
   3. Activate the environment: `source legal_env/bin/activate`
   4. Install dependencies: `pip install -r requirements.txt`
   5. Run the application: `python app.py`

   ## Usage
   - Access the web interface at http://localhost:5000
   - Ask questions about Philippine law in natural language
   - View answers with source attribution

   ## Limitations
   - Limited document corpus
   - Not a substitute for professional legal advice
   - Experimental project for learning purposes
   ```

2. **Document your code with comments**

### Day 33-35: Future Improvements Planning
1. **Create a list of potential improvements**:
   - Fine-tuning with Philippine legal texts
   - Adding more document types
   - Improving entity recognition for Philippine legal entities
   - Building a document upload interface

## Learning Outcomes

By completing this personal project, you'll gain:

1. **Practical NLP skills** with real-world legal documents
2. **End-to-end ML pipeline experience** from data collection to deployment
3. **Domain-specific knowledge** about Philippine legal documents
4. **Project portfolio piece** demonstrating your abilities

## Resource Requirements

This project is designed to be completed on a standard laptop with:
- 8GB+ RAM
- Python 3.7+
- Internet connection for downloading models
- No special GPU required (though it would speed up processing)

The total disk space needed is approximately 2-3GB, primarily for models and document storage.
