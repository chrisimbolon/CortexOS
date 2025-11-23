# knowledge_service/app/core/rag.py

import httpx
import numpy as np

# Temporary in-memory vector DB
VECTOR_STORE = []


# -----------------------------------------------------
# 1) Embed using embeddings_service
# -----------------------------------------------------

async def embed_texts(texts):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:7002/embed", 
            json={"texts": texts}
        )
        resp.raise_for_status()
        return resp.json()["embeddings"]


# -----------------------------------------------------
# 2) Store chunks
# -----------------------------------------------------

def add_chunks_to_store(docs):
    VECTOR_STORE.extend(docs)
    return docs


# -----------------------------------------------------
# 3) Search by cosine similarity
# -----------------------------------------------------

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def search_similar_chunks(query_emb, top_k=5):
    scored = []
    for doc in VECTOR_STORE:
        score = cosine_similarity(query_emb, doc["embedding"])
        scored.append((doc, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
