from fastapi import FastAPI
from app.routes import auth_proxy, knowledge_proxy, embeddings_proxy

app = FastAPI(title="CortexOS Gateway")

app.include_router(auth_proxy.router, prefix="/auth", tags=["Auth"])
app.include_router(knowledge_proxy.router, prefix="/knowledge", tags=["Knowledge"])
app.include_router(embeddings_proxy.router, prefix="/embeddings", tags=["Embeddings"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "gateway"}
