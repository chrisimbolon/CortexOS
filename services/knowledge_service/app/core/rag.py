# knowledge_service/app/core/rag.py

# services/knowledge_service/app/core/rag.py
from typing import List, Dict, Any
import uuid
import os
from app.core.chunker import chunk_text
from app.core.embeddings_client import get_embedding, get_embeddings
from app.core.vector_store import VectorStore
from app.core.config import settings
import httpx

vector_store = VectorStore()

def ingest_text(text: str, source: str = None, metadata: Dict[str, Any] | None = None) -> str:
    """
    Ingest raw text:
    - chunk text
    - call embeddings service
    - store chunks + embeddings in vector store
    Returns generated doc_id
    """
    doc_id = str(uuid.uuid4())
    source_name = source or doc_id
    # chunk
    chunks = chunk_text(text)
    # get embeddings (batch)
    # embeddings_client expects full URL configured in settings
    embeddings = None
    # since get_embeddings is async, we call it synchronously via httpx here to keep
    # this function sync (fast fallback). If you want purely async, refactor accordingly.
    # For now call embeddings service directly (POST).
    emb_url = os.getenv("EMBEDDING_SERVICE_URL", settings.EMBEDDING_SERVICE_URL)
    # assume embeddings endpoint is /api/embeddings
    endpoint = emb_url.rstrip("/") + "/api/embeddings"
    resp = httpx.post(endpoint, json={"texts": chunks}, timeout=30.0)
    resp.raise_for_status()
    data = resp.json()
    embeddings = data.get("embeddings", [])
    if not embeddings or len(embeddings) != len(chunks):
        raise RuntimeError("Embeddings service returned invalid response")

    # optional metadatas list
    metadatas = [{"source": source_name} for _ in chunks]

    vector_store.add(source_name, chunks, embeddings, metadatas)

    return doc_id


def semantic_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Return top_k chunks (with score & metadata) for a query string.
    """
    emb_url = os.getenv("EMBEDDING_SERVICE_URL", settings.EMBEDDING_SERVICE_URL)
    endpoint = emb_url.rstrip("/") + "/api/embeddings"
    resp = httpx.post(endpoint, json={"texts": [query]}, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()
    query_emb = data.get("embeddings", [])[0]

    results = vector_store.search(query_emb, top_k=top_k)
    # results are list of (docdict, score)
    out = []
    for docdict, score in results:
        out.append({
            "id": docdict.get("id"),
            "source": docdict.get("source"),
            "text": docdict.get("text"),
            "metadata": docdict.get("metadata", {}),
            "score": score,
        })
    return out


def build_prompt(query: str, contexts: List[Dict[str, Any]], instruction: str | None = None, max_context_tokens: int = 1500) -> str:
    """
    Build a prompt that concatenates the top contexts and the user query.
    Keep it simple: include contexts at the top and a short instruction.
    """
    header = instruction or "You are a helpful assistant. Use the context below to answer the question as best as possible.\n\nContext:\n"
    context_texts = []
    total_len = 0
    for c in contexts:
        snippet = c.get("text", "")
        total_len += len(snippet)
        if total_len > max_context_tokens:
            break
        context_texts.append(f"- {snippet}")

    context_blob = "\n".join(context_texts)
    prompt = f"{header}{context_blob}\n\nUser question: {query}\n\nAnswer:"
    return prompt


# import httpx
# import numpy as np

# # Temporary in-memory vector DB
# VECTOR_STORE = []


# # -----------------------------------------------------
# # 1) Embed using embeddings_service
# # -----------------------------------------------------

# async def embed_texts(texts):
#     async with httpx.AsyncClient() as client:
#         resp = await client.post(
#             "http://localhost:7002/embed", 
#             json={"texts": texts}
#         )
#         resp.raise_for_status()
#         return resp.json()["embeddings"]


# # -----------------------------------------------------
# # 2) Store chunks
# # -----------------------------------------------------

# def add_chunks_to_store(docs):
#     VECTOR_STORE.extend(docs)
#     return docs


# # -----------------------------------------------------
# # 3) Search by cosine similarity
# # -----------------------------------------------------

# def cosine_similarity(a, b):
#     a = np.array(a)
#     b = np.array(b)
#     return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# def search_similar_chunks(query_emb, top_k=5):
#     scored = []
#     for doc in VECTOR_STORE:
#         score = cosine_similarity(query_emb, doc["embedding"])
#         scored.append((doc, score))

#     scored.sort(key=lambda x: x[1], reverse=True)
#     return scored[:top_k]
