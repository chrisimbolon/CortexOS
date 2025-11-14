# app/main.py
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="LLM Microservice")
app.include_router(router, prefix="/api")
