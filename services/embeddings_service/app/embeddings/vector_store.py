import numpy as np
from app.core.logger import logger

class InMemoryVectorStore:
    def __init__(self):
        self.store = []
        logger.info("Initialized in-memory vector store")

    def add_vector(self, text: str, vector: list[float]):
        self.store.append({"text": text, "vector": np.array(vector)})
        logger.info(f"Added vector for text: {text[:30]}...")

    def search(self, query_vector: list[float], top_k: int = 3):
        if not self.store:
            return []

        query_np = np.array(query_vector)
        similarities = []

        for item in self.store:
            sim = np.dot(item["vector"], query_np) / (
                np.linalg.norm(item["vector"]) * np.linalg.norm(query_np)
            )
            similarities.append((item["text"], sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def reset(self):
        self.store.clear()
        logger.info("Vector store cleared")
