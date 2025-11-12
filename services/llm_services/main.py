# services/llm_service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core.orchestrator import orchestrator

app = FastAPI(title="Cortex LLM Service")

class QueryIn(BaseModel):
    model: str | None = None
    prompt: str
    variables: dict | None = None

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/query")
async def query_endpoint(payload: QueryIn):
    try:
        result = await orchestrator.run_model(
            model=payload.model,
            prompt=payload.prompt,
            variables=payload.variables or {},
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
