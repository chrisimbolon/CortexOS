# app/embeddings_client.py

from typing import List, Optional
import asyncio
import os
import httpx
from app.core.config import settings

EMBEDDINGS_PATH = "/api/embeddings"  # endpoint at embeddings service expected
EMBEDDINGS_URL = os.getenv("EMBEDDINGS_SERVICE_URL", settings.EMBEDDINGS_SERVICE_URL)
DEFAULT_TIMEOUT = 30.0
BATCH_SIZE = int(os.getenv("EMBEDDINGS_BATCH_SIZE", 32))


async def _post_embeddings(client: httpx.AsyncClient, texts: List[str]) -> List[List[float]]:
    """
    Internal helper to call the embeddings service with a batch of texts.
    Expects response: {"embeddings": [[...], [...]]}
    """
    url = f"{EMBEDDINGS_URL}{EMBEDDINGS_PATH}"
    r = await client.post(url, json={"texts": texts}, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    # support both {"embeddings": [...]} and {"embedding": ...} patterns
    return data.get("embeddings") or data.get("embedding")


async def get_embeddings(texts: List[str], batch_size: int = BATCH_SIZE) -> List[List[float]]:
    """
    Batch-safe embeddings fetcher. Returns embeddings in the same order as texts.
    """
    if not texts:
        return []

    embeddings: List[List[float]] = []
    async with httpx.AsyncClient() as client:
        # chunk texts into batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                batch_emb = await _post_embeddings(client, batch)
            except httpx.HTTPError as e:
                # raise a clear runtime error for upstream handling
                raise RuntimeError(f"Embeddings service failed: {e}") from e
            embeddings.extend(batch_emb)
            # small sleep to avoid bursting if many batches (adjust if needed)
            await asyncio.sleep(0.01)
    return embeddings


async def get_embedding(text: str) -> List[float]:
    """Convenience wrapper for a single text -> vector call."""
    res = await get_embeddings([text], batch_size=1)
    return res[0]
