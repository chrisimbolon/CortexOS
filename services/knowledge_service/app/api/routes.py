# services/knowledge_service/app/api/routes.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import json
from app.embeddings_client import get_embeddings
from app.utils import simple_chunk_text
from app.crud import add_chunks, search_similar_chunks

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/api/ingest")
async def ingest_file(source: Optional[str] = Form(None), file: Optional[UploadFile] = File(None), text: Optional[str] = Form(None)):
    """
    Ingest either uploaded file or raw text. If file is provided, read as text (simple).
    Returns number of chunks created.
    """
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide file or text")

    if file:
        # read binary then decode heuristically
        raw = await file.read()
        try:
            content = raw.decode("utf-8")
        except Exception:
            content = raw.decode("latin-1", errors="ignore")
        source_name = file.filename
    else:
        content = text
        source_name = source or "text_input"

    # chunk the content
    chunks = simple_chunk_text(content, chunk_size=800, overlap=100)

    # call embeddings service for all chunks
    embeddings = await get_embeddings(chunks)  # returns list of vectors

    # build payload for DB
    to_save = []
    for c, emb in zip(chunks, embeddings):
        to_save.append({
            "source": source_name,
            "text": c,
            "embedding": emb,
            "metadata": {"source": source_name}
        })

    saved = add_chunks(to_save)
    return {"created": len(saved)}

@router.post("/api/query")
async def query_knowledge(query: str, top_k: int = 5):
    """
    Given a query string, compute embedding (call embeddings_service), search similar chunks,
    and return the top_k chunks (text + metadata + score).
    """
    # compute query embedding
    embeddings = await get_embeddings([query])
    q_emb = embeddings[0]
    results = search_similar_chunks(q_emb, top_k=top_k)
    out = []
    for chunk, score in results:
        out.append({
            "id": chunk.id,
            "source": chunk.source,
            "text": chunk.text,
            "metadata": chunk.metadata,
            "score": score
        })
    return {"results": out}
