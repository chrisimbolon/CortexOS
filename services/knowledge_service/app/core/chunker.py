# knowledge_service/app/core/chunker.py

# knowledge_service/app/core/chunker.py

from typing import List
from app.core.config import settings


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text (str): The raw text to chunk.
        chunk_size (int, optional): Size of each chunk. Defaults to settings.CHUNK_SIZE.
        overlap (int, optional): Number of characters overlapping between chunks.
                                 Defaults to settings.CHUNK_OVERLAP.

    Returns:
        List[str]: A list of text chunks.
    """
    # Use defaults from settings if not provided
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if overlap is None:
        overlap = settings.CHUNK_OVERLAP

    if chunk_size <= overlap:
        raise ValueError("chunk_size must be larger than overlap")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks
