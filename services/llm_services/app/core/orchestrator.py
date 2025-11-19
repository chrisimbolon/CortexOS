from openai import OpenAI
from app.core.costs import estimate_cost
from app.core.metrics_logger import save_metric
import time

client = OpenAI()

class Orchestrator:
    async def run_model(self, model: str, prompt: str, variables: dict):
        start = time.time()
        cached = False
        status = "success"

        try:
            # Build chat messages
            messages = [
                {"role": "user", "content": prompt}
            ]

            # New OpenAI API
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )

            text = response.choices[0].message.content

            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            cost = estimate_cost(model, total_tokens)

        except Exception as e:
            status = "error"
            text = str(e)
            input_tokens = output_tokens = total_tokens = 0
            cost = 0.0

        latency_ms = (time.time() - start) * 1000

        # Save to DB
        await save_metric(
            model_name=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
            status=status,
            prompt_preview=prompt[:200],
            cached=cached,
        )

        return {"text": text}

# Singleton
orchestrator = Orchestrator()






# # services/llm_services/app/core/orchestrator.py
# """
# CortexOrchestrator
# - async-friendly wrapper around a sync LLM call (OpenAI ChatCompletion)
# - uses redis.asyncio for caching (get/set)
# - logs metrics (tokens, latency, cost) through metrics_logger
# - provides an async run_model(...) used by FastAPI endpoints
# """

# from __future__ import annotations
# import time
# import hashlib
# import json
# import asyncio
# import os
# from typing import Any, Dict, Optional

# import openai
# import redis.asyncio as aioredis

# from app.core.metrics_logger import metrics_logger
# from app.core.costs import MODEL_COSTS

# # Load OpenAI key from env (or rely on your environment)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# openai.api_key = OPENAI_API_KEY

# REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
# DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o")  # change default if you want

# # Cache TTL seconds
# DEFAULT_CACHE_TTL = int(os.getenv("LLM_CACHE_TTL", "3600"))


# class CortexOrchestrator:
#     def __init__(self, redis_url: str = REDIS_URL, default_model: str = DEFAULT_MODEL):
#         self.default_model = default_model
#         self._redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)

#     def _generate_cache_key(self, model: str, prompt: str, variables: Optional[Dict[str, Any]] = None) -> str:
#         payload = {"model": model, "prompt": prompt, "vars": variables or {}}
#         raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
#         return "llm_cache:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

#     def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
#         info = MODEL_COSTS.get(model, {"input": 0.01, "output": 0.03})
#         input_cost = (prompt_tokens / 1000.0) * info["input"]
#         output_cost = (completion_tokens / 1000.0) * info["output"]
#         return round(input_cost + output_cost, 8)

#     def _call_openai_sync(self, model: str, messages: list, max_tokens: int = 512, temperature: float = 0.0):
#         """
#         Synchronous call to OpenAI ChatCompletion. Run inside a thread executor to avoid blocking.
#         Returns the raw response dict from openai.ChatCompletion.create
#         """
#         # NOTE: Using ChatCompletion for a stable usage 'usage' field.
#         resp = openai.ChatCompletion.create(
#             model=model,
#             messages=messages,
#             max_tokens=max_tokens,
#             temperature=temperature,
#         )
#         return resp

#     async def run_model(
#         self,
#         *, 
#         model: Optional[str] = None,
#         prompt: Optional[str] = None,
#         variables: Optional[Dict[str, Any]] = None,
#         messages: Optional[list] = None,
#         cache_ttl: int = DEFAULT_CACHE_TTL,
#         max_tokens: int = 512,
#         temperature: float = 0.0,
#     ) -> Dict[str, Any]:
#         """
#         Async-friendly wrapper to call an LLM.
#         - `prompt` OR `messages` must be provided. If prompt is provided, it will be wrapped in a system/user message.
#         - Checks Redis cache first; if hit returns cached output (and still logs a cache_hit).
#         - If miss: performs sync OpenAI call in thread, extracts usage, computes cost, logs metric, caches output.
#         """

#         model = model or self.default_model
#         if not (prompt or messages):
#             raise ValueError("Either `prompt` or `messages` must be provided")

#         # Build messages if only prompt provided
#         if messages is None:
#             messages = [
#                 {"role": "system", "content": "You are CortexOS: helpful assistant that cites sources when available."},
#                 {"role": "user", "content": prompt},
#             ]

#         # Compute cache key
#         cache_key = self._generate_cache_key(model, json.dumps(messages, ensure_ascii=False), variables)
#         # Check cache (async)
#         cached = await self._redis.get(cache_key)
#         if cached:
#             metrics_logger.log_cache_hit(model=model)
#             # cached stored as JSON of expected payload
#             return {"cached": True, "from_cache": json.loads(cached)}

#         # Not cached -> perform LLM call (sync in executor)
#         start = time.perf_counter()
#         loop = asyncio.get_running_loop()
#         try:
#             resp = await loop.run_in_executor(
#                 None,
#                 lambda: self._call_openai_sync(model=model, messages=messages, max_tokens=max_tokens, temperature=temperature)
#             )
#         except Exception as e:
#             latency_ms = (time.perf_counter() - start) * 1000.0
#             # Log error metric (tokens unknown)
#             await loop.run_in_executor(None, lambda: metrics_logger.log_request(
#                 model=model,
#                 latency_ms=latency_ms,
#                 prompt_tokens=0,
#                 completion_tokens=0,
#                 cost_usd=0.0,
#                 prompt=(prompt or str(messages))[:200],
#                 output="",
#                 cached=False,
#                 metadata={"error": str(e)},
#             ))
#             raise

#         latency_ms = (time.perf_counter() - start) * 1000.0

#         # Parse usage & output
#         # ChatCompletion response structure: resp["choices"][0]["message"]["content"], resp["usage"] keys
#         try:
#             output_text = resp["choices"][0]["message"]["content"]
#         except Exception:
#             output_text = str(resp)

#         usage = resp.get("usage", {}) or {}
#         prompt_tokens = usage.get("prompt_tokens", 0)
#         completion_tokens = usage.get("completion_tokens", 0)
#         total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

#         # compute cost
#         cost_usd = self._calculate_cost(model, prompt_tokens, completion_tokens)

#         # prepare payload to return (and cache)
#         payload = {
#             "cached": False,
#             "model": model,
#             "latency_ms": latency_ms,
#             "tokens": {"prompt": prompt_tokens, "completion": completion_tokens, "total": total_tokens},
#             "cost_usd": cost_usd,
#             "output": output_text,
#             "raw_response": resp,
#         }

#         # persist metric (sync DB commit via metrics_logger; call in executor)
#         await loop.run_in_executor(None, lambda: metrics_logger.log_request(
#             model=model,
#             latency_ms=latency_ms,
#             prompt_tokens=prompt_tokens,
#             completion_tokens=completion_tokens,
#             cost_usd=cost_usd,
#             prompt=(prompt or str(messages))[:2000],
#             output=output_text,
#             cached=False,
#             metadata={"variables": variables or {}},
#         ))

#         # cache the output JSON (store only the needed parts to limit size)
#         try:
#             await self._redis.set(cache_key, json.dumps(payload, ensure_ascii=False), ex=cache_ttl)
#         except Exception as e:
#             # cache failure should not break response
#             print("[orchestrator] Warning: failed to set cache:", e)

#         return payload


# # global instance to import from elsewhere
# orchestrator = CortexOrchestrator()








