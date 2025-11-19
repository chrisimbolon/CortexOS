# services/llm_services/app/core/orchestrator.py

from groq import Groq
from app.core.costs import estimate_cost
from app.core.metrics_logger import save_metric
import time
import os

# Load Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Orchestrator:
    async def run_model(self, model: str, prompt: str, variables: dict):
        start = time.monotonic()

        try:
            # --- Call sync OpenAI API inside async function ---
            # The trick is: run sync code directly in async (it's allowed)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.choices[0].message.content
            usage = response.usage

            latency = (time.monotonic() - start) * 1000

            # Save metrics
            await save_metric(
                model_name=model,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                cost_usd=estimate_cost(model, usage.total_tokens),
                latency_ms=latency,
                status="success",
                prompt_preview=prompt[:200],
                cached=False,
            )

            return {"response": text}

        except Exception as e:
            latency = (time.monotonic() - start) * 1000

            await save_metric(
                model_name=model,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                cost_usd=0,
                latency_ms=latency,
                status="error",
                prompt_preview=prompt[:200],
                cached=False,
            )

            raise e


orchestrator = Orchestrator()
