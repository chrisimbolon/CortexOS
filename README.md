🌐 CortexOS — Modular AI Microservices Platform

CortexOS is a high-performance AI orchestration platform built with a modern microservices architecture.
It provides a clean, scalable way to run LLMs, embeddings, RAG pipelines, metrics logging, and API integrations — all fully containerized and production-ready.

This project is designed for real-world deployment, expandability, and developer ergonomics, making it perfect for:

AI/ML backend engineering

RAG-powered applications

LangChain-style LLM orchestration without the bloat

FastAPI microservice architecture

Portfolio-level demonstration of AI system design

Core Features
🧠 1. LLM Orchestration Service

Modular orchestration layer for any LLM provider (OpenAI, Groq, Anthropic, local models).

Built-in support for:

ChatCompletion abstraction

Model switching

Token usage tracking

Automatic cost estimation

Latency measurement

Pluggable backends for hybrid routing (OpenAI + Groq + Local inference).


📚 2. Knowledge / RAG Service

Document ingestion (file upload or raw text)

Automatic text chunking

Embeddings generation via Embeddings Service

Vector search via:

pgvector (preferred)

JSON fallback for local dev

Top-K retrieval API

Extensible metadata support

Forms the foundation of a full RAG pipeline.

🔤 3. Embeddings Service

Unified API for generating embeddings

Provider-agnostic (OpenAI, Groq, HuggingFace, etc)

Handles batching, retries, throttling

Clean FastAPI microservice ready for horizontal scaling

📊 4. Metrics Service (LLM Telemetry)

Captures structured metrics for every LLM call:

Latency

Input/Output token counts

Cost (provider-aware)

Cached / non-cached calls

Prompt preview

Status tracking (success/error)

Perfect for:

Observability

Cost dashboards

Usage analytics

Optimization

🏗️ Architecture Overview

cortexOS/
│
├── services/
│   ├── llm_services/          # Orchestrator + metrics
│   ├── embeddings_service/    # Embeddings API
│   ├── knowledge_service/     # RAG ingest + vector search
│   └── api_gateway/ (optional)
│
├── shared/
│   ├── utils/
│   ├── costs/
│   └── core/
│
└── docker/
    ├── docker-compose.yml
    ├── caddy/
    └── postgres/ (with pgvector)

Each service is fully self-contained with:

its own FastAPI app

its own database layer

its own Dockerfile

clean separation of concerns

This is textbook production microservice architecture, perfect for scaling or portfolio demonstration.

⚙️ Tech Stack
Backend

FastAPI (high-performance async APIs)

SQLAlchemy

PostgreSQL + pgvector

Uvicorn / Gunicorn

Docker + Docker Compose

AI Integrations

OpenAI API

Groq API

HuggingFace embeddings

Extensible provider architecture

DevOps

Caddy (reverse proxy + TLS)

Makefile shortcuts

Local + production .env separation

🔌 Endpoints Overview
LLM Service (/api/query)

POST /api/query
{
  "prompt": "Hello from CortexOS",
  "model": "llama-3.1-8b-instant"
}

Response:
{
  "response": "Hello from the other side…"
}

Knowledge Service
Ingest:
POST /api/ingest
Multipart:
- file=@document.pdf
- source=doc1

Search:
POST /api/query
{
  "query": "Explain pgvector installation",
  "top_k": 5
}

### 🧩 RAG Pipeline (High-Level)

Ingest data

Chunk → Embed → Store in pgvector

User query

Embed → Vector search top-K chunks

Context assembly

Merges retrieved chunks + user prompt

LLM orchestration

Route to Groq/OpenAI

Log metrics

Return final answer

This pipeline mirrors real production RAG systems used at modern AI startups.

🛠️ Local Development
1. Clone & install

git clone <repo>
cd cortexOS

2. Start all services
docker compose up --build

3. Run a single service locally (example: llm_services)
cd services/llm_services
uvicorn app.main:app --reload --port 8000

🔐 Environment Variables

Create a .env per service:

LLM_SERVICE .env
OPENAI_API_KEY=...
GROQ_API_KEY=...
DATABASE_URL=postgresql://cortex_user:cortex_pass@postgres:5432/cortex_llm

KNOWLEDGE_SERVICE .env
DATABASE_URL=postgresql://cortex_user:cortex_pass@postgres:5432/cortex_llm
EMBEDDINGS_SERVICE_URL=http://embeddings_service:8001

## 📦 Production Deployment

CortexOS is built to be deployed via:

DigitalOcean Droplets

AWS ECS

Google Cloud Run

Render

Railway

Reverse proxy handled by Caddy:

Automatic HTTPS

Zero config domain routing

Hot reload support

This is ideal for solo-dev deployments and client projects.

📝 Why This Project Matters

This project demonstrates senior-level software engineering ability, including:

Microservices architecture

Advanced AI systems (RAG, embeddings, aggregation)

Observability + metrics

Dockerized deployment

Clean, scalable abstractions

Production-grade LLM integration

This is portfolio gold and can be shown confidently to:

Recruiters

CTOs

Engineering managers

Startup founders

Author

Christyan Simbolon
Fullstack Engineer — Python • FastAPI • Next.js • Docker
AI/RAG & LLM Engineering • Systems Architecture

LinkedIn: (add your link here)