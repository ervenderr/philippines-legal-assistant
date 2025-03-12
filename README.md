# Philippine Legal Assistant

A comprehensive legal research tool that combines natural language processing and machine learning to analyze Philippine legal documents. The system provides intelligent search capabilities and can answer questions about user-uploaded legal documents with relevant citations.

## 🌟 Features

### Document Management

- 📄 PDF text extraction and processing
- 📤 User-specific document upload and storage
- 🗑️ Document deletion functionality
- 🔍 Automatic document sectioning (header, syllabus, decision, dispositive)
- 📊 Document metadata extraction and cataloging

### Search and Analysis

- 🔎 Semantic search across uploaded documents
- ❓ Question-answering capabilities
- 📑 Document chunking and embedding
- 💡 Context-aware responses
- 📌 Source citations and relevant passages
- 🧠 Local model processing (no API costs)

### User Interface

- 🎨 Modern, responsive web interface
- 🌙 Dark mode support
- ⚡ Real-time search results
- 📱 Mobile-friendly design
- 🔄 Document management interface

## 🏗️ Architecture

The project consists of two main components:

### Backend (Python/FastAPI)

- Document processing pipeline
- User-specific document storage
- Machine learning models for text analysis
- REST API endpoints
- Local question-answering model

### Frontend (Next.js)

- Modern web interface
- Real-time search
- Document upload and management
- Responsive design

## 📁 Project Structure

```
philippines-legal-assistant/
├── api/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── qa_service.py      # Question answering service
│   └── document_service.py # Document management service
├── data/                  # Data processing modules
│   ├── document_parser.py # PDF processing
│   ├── document_embeddings.py # Text embedding
│   └── qa_system.py      # Question answering
├── user_data/             # User-specific document storage
│   └── [user_id]/         # Individual user directories
│       ├── raw/           # Raw PDF documents
│       ├── processed/     # Processed JSON files
│       ├── embeddings/    # Document embeddings
│       └── catalog.json   # User document catalog
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
- Hugging Face transformers for question answering
- Local DistilBERT model for answering questions

> **Note:** The current local model (DistilBERT) has relatively low confidence levels compared to OpenAI models. This is a trade-off for having a free, locally-running solution without API costs.

### Frontend Development

The frontend is built with:

- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Shadcn UI components
- next-themes for dark mode

## 🚀 Usage

1. **Upload Documents**: Upload your Philippine legal documents (Supreme Court decisions, laws, regulations)
2. **Ask Questions**: Query your uploaded documents with natural language questions
3. **Get Answers**: Receive answers with relevant citations and supporting evidence
4. **Manage Documents**: Delete documents you no longer need

## 📚 Documentation

- Backend API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Frontend documentation: See [frontend/README.md](frontend/README.md)

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

![ph-legal-assistance-ui](https://github.com/user-attachments/assets/c3a69d6c-7d71-4d51-bf36-5d9f32bacc4b)

_Note: This is a placeholder image. Please replace it with an actual screenshot of your application._
