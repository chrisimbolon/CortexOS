from fastapi import FastAPI
from app.routes import query, ingest

app = FastAPI(title="CortexOS Knowledge Service")

app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "knowledge_service"}
