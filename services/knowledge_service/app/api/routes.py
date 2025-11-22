# knowledge_service/app/api/routes.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List

from app.core.chunker import simple_chunk_text
from app.core.rag import (
    embed_texts,
    add_chunks_to_store,
    search_similar_chunks
)

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


# -----------------------------------------------------
# 1) Ingest file or raw text
# -----------------------------------------------------

@router.post("/ingest")
async def ingest_knowledge(
    source: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    if not file and not text:
        raise HTTPException(400, "Provide either a file or raw text")

    # ---- Read content ----
    if file:
        raw = await file.read()
        try:
            content = raw.decode("utf-8")
        except Exception:
            content = raw.decode("latin-1", errors="ignore")
        source_name = file.filename
    else:
        content = text
        source_name = source or "text_input"

    # ---- Chunk the document ----
    chunks = simple_chunk_text(content, chunk_size=800, overlap=100)

    # ---- Embed all chunks ----
    embeddings = await embed_texts(chunks)

    # ---- Format documents to store ----
    docs_to_save = []
    for chunk, emb in zip(chunks, embeddings):
        docs_to_save.append({
            "source": source_name,
            "text": chunk,
            "embedding": emb,
            "metadata": {"source": source_name}
        })

    saved = add_chunks_to_store(docs_to_save)

    return {"created": len(saved), "source": source_name}
    

# -----------------------------------------------------
# 2) Query knowledge store
# -----------------------------------------------------

@router.post("/query")
async def query_knowledge(query: str, top_k: int = 5):
    # ---- Embed user question ----
    embedded = await embed_texts([query])
    query_emb = embedded[0]

    # ---- Search in vector store ----
    results = search_similar_chunks(query_emb, top_k=top_k)

    out = []
    for doc, score in results:
        out.append({
            "score": score,
            "source": doc["source"],
            "text": doc["text"]
        })

    return {"results": out}
