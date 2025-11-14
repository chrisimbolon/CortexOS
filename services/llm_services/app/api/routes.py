from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.orchestrator import orchestrator

router = APIRouter()

class QueryIn(BaseModel):
    model: str | None = None
    prompt: str
    variables: dict | None = None

@router.post("/query")
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
