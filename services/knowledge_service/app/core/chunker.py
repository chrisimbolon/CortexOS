# app/core/chunker.py

from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 100
) -> List[str]:
    """
    Splits text into overlapping chunks.

    Args:
        text (str): Raw text to split.
        chunk_size (int): Max characters per chunk.
        overlap (int): How many characters adjacent chunks share.

    Returns:
        List[str]: List of text chunks.
    """

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

        # Move forward with overlap
        start += chunk_size - overlap

    return chunks
