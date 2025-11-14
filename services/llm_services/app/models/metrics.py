# services/llm_services/app/models/metrics.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from app.db.session import Base

class LLMRequestMetric(Base):
    __tablename__ = "llm_request_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(128), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    status = Column(String(32), default="success")
    metadata = Column(JSON, nullable=True)
    prompt_preview = Column(Text, nullable=True)
    cached = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
