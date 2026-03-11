# 📄 Lexora — Local RAG Document Chat System

Lexora is a fully local AI document assistant that allows users to upload PDFs and chat with them using a Retrieval-Augmented Generation (RAG) pipeline powered by Ollama + FAISS + FastAPI + React.

The system builds embeddings locally, stores vector indexes per document, and enables contextual question answering with streaming responses.

## 🚀 Features

- 📄 Upload PDF documents
- 🔎 Semantic search using FAISS vector database
- 🧠 Local LLM responses via Ollama (Mistral)
- ⚡ Batch embeddings using Ollama embedding API
- 📊 Financial document detection + revenue chart generation
- 💬 Chat memory per document
- 📡 Streaming AI responses
- 🧩 Multi-document comparison support
- 🟢 Fully local → No data leaves your machine

## 🧠 Architecture Overview

User Upload PDF
- Backend extracts text
- Text chunking
- Batch embedding via Ollama
- FAISS vector index creation
- Stored per document
- User asks question
- Relevant chunks retrieved
- Prompt built with context
- Ollama generates answer

## ⚙️ Tech Stack
### Backend

- FastAPI
- FAISS
- Ollama
- NumPy
- Rank-BM25
- PyPDF

### Frontend

- React / Next.js
- Fetch API
- Streaming UI

## 🧩 Key Concepts Used

- Retrieval Augmented Generation (RAG)
- Vector similarity search
- Batch embeddings optimization
- Prompt engineering
- Background task processing
- Streaming responses
- Local AI deployment

## 🏃 Setup Instructions
### 1️⃣ Clone Repository
git clone https://github.com/yourname/lexora.git
cd lexora
### 2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate
### 3️⃣ Install Dependencies
pip install -r requirements.txt
### 4️⃣ Install Ollama

Download from:

👉 https://ollama.com

Pull required models:

ollama pull mistral
ollama pull nomic-embed-text
### 5️⃣ Run Backend
cd backend
uvicorn main:app --reload
### 6️⃣ Run Frontend
cd frontend
npm install
npm run dev
### 7️⃣ Open Application
http://localhost:3000

## ⚡ Performance Optimizations

- Replaced HuggingFace embeddings → Ollama batch embeddings
- Reduced embedding calls from 200 → 1
- Added processing status polling API
- Implemented streaming LLM responses
- Limited chunk size for faster indexing
- Local FAISS storage per document

## 🔐 Privacy

All embeddings, vectors, prompts, and documents remain local on the machine.
No cloud inference unless explicitly integrated.

## 📈 Future Improvements

- GPU FAISS indexing
- Redis cache layer
- Multi-user authentication
- Document tagging
- Hybrid keyword + vector retrieval tuning

## 👨‍💻 System Architecture Explanation

The backend is divided into three main intelligence layers.

🔵 main.py — Entry Point

Handles:

- Upload API
- Chat API
- Document status API
- Background task scheduling

🟣 rag.py — Core Retrieval Pipeline (Most Important File)

Handles:

- Document chunking
- Embedding generation using Ollama
- FAISS index construction
- Retrieval of most relevant document chunks
- BM25 ranking
- Passing contextual information to the LLM

👉 This module acts as the retrieval intelligence layer.

🟡 brain.py — Generation Layer

Handles:

- Prompt construction
- Chat history injection
- Streaming response generation
- Running Ollama subprocess

This module generates the final AI response.

🟢 ChatPage.jsx — Frontend Interface

Handles:

- Upload button
- Chat interface
- Streaming response display
- Polling document processing status
- Sidebar document state

## 📁 Folder Structure
lexora/
│
├── backend/
│ ├── main.py  # FastAPI routes
│ ├── rag.py # Embedding + FAISS retrieval
│ ├── brain.py # LLM prompt + memory
│ ├── pdf_reader.py # PDF text extraction
│ ├── financial_detector.py # Detects financial documents
│ ├── financial_extractor.py # Extracts revenue/profit figures
│ ├── finance_api.py # Stock price via yfinance
│ ├── analytics/
│ │ └── chart_generator.py # Revenue trend charts
│ ├── vectorstore/ # Auto-created, gitignored
│ ├── chat_memory/ # Auto-created, gitignored
│ └── requirements.txt
│
└── frontend/
├── app/
│ └── chat/
│ └── page.js # Main chat UI
└── package.json



## 📌 Project Description

- AI Document Chat System (RAG Pipeline)
- Built a fully local Retrieval-Augmented Generation system enabling semantic question answering over uploaded PDFs using FAISS vector search and Ollama-based LLM inference.
- Implemented batch embedding optimization reducing indexing time by over 90%, streaming response generation, financial document analytics, and per-document conversational memory.
- Designed a scalable FastAPI backend and interactive React frontend supporting real-time document processing status tracking.
