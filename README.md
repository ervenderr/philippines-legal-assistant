# Philippine Legal Assistant

A comprehensive legal research tool that combines natural language processing and machine learning to analyze Philippine Supreme Court decisions. The system provides intelligent search capabilities and can answer questions about legal documents with relevant citations.

## 🌟 Features

### Document Processing

- 📄 PDF text extraction and processing
- 🔍 Automatic document sectioning (header, syllabus, decision, dispositive)
- 🏷️ Named entity recognition for legal entities
- 📊 Document metadata extraction and cataloging

### Search and Analysis

- 🔎 Semantic search across documents
- ❓ Question-answering capabilities
- 📑 Document chunking and embedding
- 💡 Context-aware responses
- 📌 Source citations and relevant passages

### User Interface

- 🎨 Modern, responsive web interface
- 🌙 Dark mode support
- ⚡ Real-time search results
- 📱 Mobile-friendly design

## 🏗️ Architecture

The project consists of two main components:

### Backend (Python/FastAPI)

- Document processing pipeline
- Machine learning models for text analysis
- REST API endpoints
- Database management

### Frontend (Next.js)

- Modern web interface
- Real-time search
- Responsive design
- Dark mode support

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- GPU recommended for better performance

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd philippines-legal-assistant
```

2. Set up the backend:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download required models
python -m spacy download en_core_web_sm
python data/qa_system.py
```

3. Set up the frontend:

```bash
cd frontend
npm install
```

### Running the Application

1. Start the backend server:

```bash
cd api
uvicorn main:app --reload
```

2. Start the frontend development server:

```bash
cd frontend
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📁 Project Structure

```
philippines-legal-assistant/
├── api/                    # FastAPI backend
│   └── main.py            # API endpoints
├── data/                  # Data processing modules
│   ├── raw/               # Raw PDF documents
│   ├── processed/         # Processed JSON files
│   ├── embeddings/        # Document embeddings
│   ├── create_catalog.py  # Document cataloging
│   ├── document_parser.py # PDF processing
│   ├── document_embeddings.py # Text embedding
│   └── qa_system.py      # Question answering
├── frontend/             # Next.js frontend
│   ├── src/             # Source code
│   └── public/          # Static files
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🛠️ Development

### Backend Development

The backend is built with FastAPI and uses several machine learning models:

- Sentence transformers for text embeddings
- Spacy for NLP tasks
- Hugging Face transformers for question answering

### Frontend Development

The frontend is built with:

- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Shadcn UI components
- next-themes for dark mode

## 📚 Documentation

- Backend API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Frontend documentation: See [frontend/README.md](frontend/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Sentence Transformers](https://www.sbert.net/)
- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [Spacy](https://spacy.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [Shadcn UI](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
