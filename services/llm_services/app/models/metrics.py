from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class LLMRequestMetric(Base):
    __tablename__ = "llm_request_metrics"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    model_name = Column(String, index=True)
    agent_name = Column(String, nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    error_message = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
