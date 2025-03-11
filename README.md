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

![Philippine Legal Assistant](https://github.com/user-attachments/assets/87fd1629-2949-4ebc-95f3-b5bcdbdf0478)
