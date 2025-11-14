import uuid
import time
from sqlalchemy.orm import Session
from app.models.metrics import LLMRequestMetric
from .deps import get_db

def log_llm_request(
    db: Session,
    model_name: str,
    agent_name: str,
    prompt_tokens: int,
    completion_tokens: int,
    cost_usd: float,
    start_time: float,
    success: bool = True,
    error_message: str = None,
    metadata: dict = None,
):
    latency_ms = (time.time() - start_time) * 1000
    total_tokens = prompt_tokens + completion_tokens

    metric = LLMRequestMetric(
        request_id=str(uuid.uuid4()),
        model_name=model_name,
        agent_name=agent_name,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        success=success,
        error_message=error_message,
        metadata=metadata,
    )
    db.add(metric)
    db.commit()
