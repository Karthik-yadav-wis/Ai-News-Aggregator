# AI Personalized News Assistant

An AI-powered web application that delivers personalized news summaries and intelligent search using LangChain and RAG (Retrieval-Augmented Generation).

## Overview

This project demonstrates practical implementation of:

- LangChain
  - Prompt Templates
  - Models
  - Output Parsers
  - Memory / Chat History
- RAG Pipeline
  - Document Loading
  - Chunking
  - Embeddings
  - Vector Storage
  - Semantic Retrieval

The application allows users to sign up, choose their interests, and receive AI-generated summaries of relevant news articles collected from the web.

---

# Features

## Authentication & User Management
- User signup/login using Supabase Auth
- Store and manage user preferences
- Edit interests anytime

## Personalized News Feed
- Fetch news/articles using APIs
- Filter content based on user interests
- AI-generated summaries for each article

## RAG-Based Search & Chat
- Semantic search using vector embeddings
- Ask questions about stored articles
- Context-aware conversational memory

## Vector Database
- ChromaDB for storing embeddings
- Efficient retrieval of relevant article chunks

---

# Tech Stack

## Frontend
- Next.js / React
- Tailwind CSS

## Backend
- FastAPI / Node.js
- LangChain

## Database & Auth
- Initial phase: sqlite3
- scaledup version: Supabase
- ChromaDB

## AI Models
- Ollama / OpenAI
- nomic-embed-text embeddings

---

# Architecture

```text
User → Frontend → Backend API
                     ↓
              News/API Fetching
                     ↓
               Text Chunking
                     ↓
              Embedding Model
                     ↓
                 ChromaDB
                     ↓
             LangChain RAG
                     ↓
        Summaries + AI Responses
