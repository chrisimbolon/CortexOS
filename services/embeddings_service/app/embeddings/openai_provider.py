from openai import OpenAI
from app.core.config import settings
from app.core.logger import logger

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_embedding(text: str) -> list[float]:
    try:
        response = client.embeddings.create(
            model=settings.MODEL_NAME,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise
