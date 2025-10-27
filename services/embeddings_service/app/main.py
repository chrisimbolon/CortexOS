from fastapi import FastAPI

app = FastAPI(title="CortexOS Embeddings Service")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "embeddings_service"}
