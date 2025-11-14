# services/llm_services/app/core/metrics_logger.py
"""
Simple synchronous metrics logger that writes LLM call records to Postgres via SQLAlchemy.
Used by orchestrator via run_in_executor so it doesn't block the event loop.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.metrics import LLMRequestMetric  # ensure this model exists in app/models/metrics.py

class MetricsLogger:
    def __init__(self):
        # using SessionLocal factory from app.db.session
        self._session_factory = SessionLocal

    def log_request(
        self,
        *,
        model: str,
        latency_ms: float,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        prompt: str,
        output: str,
        cached: bool = False,
        metadata: dict | None = None,
    ):
        db: Session = self._session_factory()
        try:
            metric = LLMRequestMetric(
                model_name=model,
                input_tokens=prompt_tokens,
                output_tokens=completion_tokens,
                total_tokens=(prompt_tokens + completion_tokens),
                cost_usd=cost_usd,
                latency_ms=latency_ms,
                status="success" if not metadata or "error" not in (metadata or {}) else "error",
                metadata=metadata or {},
                prompt_preview=(prompt[:1000] if prompt else None),
                created_at=datetime.utcnow(),
                cached=cached,
            )
            db.add(metric)
            db.commit()
        except Exception as exc:
            db.rollback()
            # Avoid crashing the orchestrator for metrics failures
            print("[metrics_logger] Failed to persist metric:", exc)
        finally:
            db.close()

    def log_cache_hit(self, model: str):
        # For now we just log a small message and we could persist a special metric row if needed
        print(f"[metrics_logger] Cache hit for model={model}")


metrics_logger = MetricsLogger()
