# services/knowledge_service/app/api/routes.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.core.rag import ingest_text, semantic_search, build_prompt
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/api/ingest")
async def ingest_endpoint(source: Optional[str] = Form(None), file: Optional[UploadFile] = File(None), text: Optional[str] = Form(None)):
    """
    Ingest raw text or uploaded file.
    Returns a doc_id.
    """
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide file or text")

    if file:
        raw = await file.read()
        try:
            content = raw.decode("utf-8")
        except Exception:
            content = raw.decode("latin-1", errors="ignore")
        src = source or file.filename
    else:
        content = text
        src = source or "text_input"

    try:
        doc_id = ingest_text(content, source=src)
        return {"status": "ok", "doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/query")
async def query_endpoint(query: str = Form(...), top_k: int = Form(5), instruction: Optional[str] = Form(None)):
    """
    Run semantic search and return contexts.
    """
    try:
        results = semantic_search(query, top_k=top_k)
        # build a simple prompt to be passed to an LLM later
        prompt = build_prompt(query, results, instruction=instruction)
        return {"results": results, "prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/answer")
async def answer_endpoint(query: str = Form(...), top_k: int = Form(5), model: Optional[str] = Form(None)):
    """
    Optional convenience endpoint:
    - runs semantic search
    - builds prompt
    - forwards prompt to the LLM orchestrator service (if ORCHESTRATOR_URL set)
    - returns LLM response plus contexts
    """
    try:
        # search + prompt
        results = semantic_search(query, top_k=top_k)
        prompt = build_prompt(query, results)

        orchestrator_url = os.getenv("ORCHESTRATOR_URL", None)
        if not orchestrator_url:
            # orchestrator not configured — return prompt & contexts only
            return {"results": results, "prompt": prompt, "llm_response": None}

        # call orchestrator
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                orchestrator_url.rstrip("/") + "/api/query",
                json={"prompt": prompt, "model": model}
            )
            resp.raise_for_status()
            data = resp.json()
        return {"results": results, "prompt": prompt, "llm_response": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
