# services/llm_services/app/main.py
from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title="Cortex LLM Service")

# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# Mount API routes
app.include_router(api_router, prefix="/api")
