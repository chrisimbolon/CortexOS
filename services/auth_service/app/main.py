from fastapi import FastAPI

app = FastAPI(title="CortexOS Auth Service")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "auth_service"}
