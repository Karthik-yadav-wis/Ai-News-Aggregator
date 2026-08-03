# The Dispatch — AI Personalized News Assistant

An AI-powered web application that delivers personalized news summaries using LangChain and RAG (Retrieval-Augmented Generation). Users sign up, choose their interests, and get AI-generated summaries built from real news articles collected from the web.

## Overview

This project demonstrates a practical, end-to-end implementation of:

- **LangChain**
  - Prompt Templates
  - Chat Models (Gemini)
  - Output Parsers
  - Memory / Chat History 
- **RAG Pipeline**
  - Document loading (multi-source news APIs)
  - Chunking
  - Embeddings
  - Vector storage
  - Semantic retrieval

## Features

**Authentication & User Management**
- Signup/login with JWT access tokens and Argon2 password hashing
- Store, edit, and retrieve saved interests per user

**Personalized News Feed**
- Fetches articles from three news APIs per interest (Currents, FreeNews, NewsData.io), deduplicated by URL
- Chunks and embeds articles into a per-topic-searchable vector store
- Generates a grouped, per-topic AI summary on demand

**Interest Images**
- Each saved interest is automatically matched to a real photo via the Wikipedia REST API, cached per topic so it's only fetched once

## Tech Stack

**Frontend**
- Vite + React
- Custom design system 

**Backend**
- FastAPI
- SQLAlchemy + SQLite
- LangChain

**Vector Store**
- FAISS

**AI Models**
- Google Gemini — `gemini-3.6-flash` for summarization, `gemini-embedding-001` for embeddings
- *(Originally built on local Ollama models — `llama3.2` and `nomic-embed-text` — since migrated to Gemini for speed and easier deployment)*

## Architecture

```
User → Frontend (React) → Backend API (FastAPI)
                               ↓
                     News APIs (fetch + dedupe)
                               ↓
                        Text Chunking
                               ↓
                    Gemini Embeddings
                               ↓
                            FAISS
                               ↓
                 LangChain Retrieval + Prompt
                               ↓
                     Gemini Summarization
                               ↓
                  Per-topic AI Summaries
```

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create `backend/.env`:
```
CURRENT_NEWS_API_KEY=your_key
FREE_NEWS_API_KEY=your_key
NEWS_DATA_API_KEY=your_key
GEMINI_API_KEY=your_key
```

Run it:
```bash
uvicorn main:app --reload
```
Backend runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Frontend runs at `http://localhost:5173`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/signup` | Create a new user |
| POST | `/login` | Authenticate, returns a JWT |
| GET | `/user/interests` | Get the current user's saved interests + images |
| POST | `/user/interests` | Save/update the current user's interests |
| POST | `/fetch-news` | Fetch, chunk, and embed news for the user's interests |
| GET | `/summary` | Retrieve and summarize stored articles per interest |

All routes except `/signup` and `/login` require `Authorization: Bearer <token>`.

## Roadmap

- [ ] RAG chat/search endpoint with conversational memory
- [ ] Deduplicate against already-ingested articles before re-embedding
- [ ] Deploy backend to a persistent host (Render/Railway) and frontend to Vercel

## Contributors

- [Karthik-yadav-22](https://github.com/Karthik-yadav-22)
- [hrudyagali](https://github.com/hrudyagali)
