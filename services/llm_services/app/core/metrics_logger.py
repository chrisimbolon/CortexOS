# services/llm_services/app/core/metrics_logger.py

from app.db.session import SessionLocal
from app.models.metrics import LLMRequestMetric
import asyncio

async def save_metric(
    model_name: str,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    cost_usd: float,
    latency_ms: float,
    status: str,
    prompt_preview: str,
    cached: bool,
):
    """
    This function wraps synchronous DB operations inside a thread executor,
    making it safe to await.
    """

    def _write():
        try:
            db = SessionLocal()

            metric = LLMRequestMetric(
                model_name=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost_usd=cost_usd,
                latency_ms=latency_ms,
                status=status,
                prompt_preview=prompt_preview,
                cached=1 if cached else 0,
            )

            db.add(metric)
            db.commit()
            db.refresh(metric)
            db.close()

        except Exception as e:
            print("[metrics_logger] Failed to persist metric:", e)

    # Run sync DB write in separate thread
    await asyncio.to_thread(_write)
