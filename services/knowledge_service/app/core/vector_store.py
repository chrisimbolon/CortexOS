# services/knowledge_service/app/core/vector_store.py
"""
Flexible Vector Store:
- If pgvector + Postgres is available (DATABASE_URL points to Postgres && pgvector installed),
  use SQLAlchemy + pgvector for efficient search (recommended for production).
- Otherwise fall back to a lightweight SQLite file-based store that stores vectors as CSV blobs
  and computes cosine similarity in Python (OK for development / small corpora).
"""

import os
import json
import math
from typing import List, Tuple, Optional

# Try to detect if we can use pgvector with SQLAlchemy
USE_PGVECTOR = False
try:
    from sqlalchemy import create_engine, Column, Integer, String, Text, select
    from sqlalchemy.orm import declarative_base, sessionmaker
    from pgvector.sqlalchemy import Vector
    USE_PGVECTOR = True
except Exception:
    USE_PGVECTOR = False

# local sqlite fallback imports
import sqlite3

from app.core.config import settings

# ---------- PGVECTOR implementation ----------
if USE_PGVECTOR:
    Base = declarative_base()

    class ChunkRow(Base):
        __tablename__ = "chunks"
        id = Column(Integer, primary_key=True, index=True)
        source = Column(String(255), nullable=True)
        text = Column(Text, nullable=False)
        metadata = Column(Text, nullable=True)  # store JSON string
        embedding = Column(Vector(dimensions=1536), nullable=False)  # adjust dims if needed

    class PGVectorStore:
        def __init__(self, database_url: str):
            self.engine = create_engine(database_url, pool_pre_ping=True)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            Base.metadata.create_all(bind=self.engine)

        def add(self, source: str, texts: List[str], embeddings: List[List[float]], metadatas: Optional[List[dict]] = None):
            db = self.SessionLocal()
            try:
                objs = []
                for i, (t, e) in enumerate(zip(texts, embeddings)):
                    m = metadatas[i] if metadatas and i < len(metadatas) else {}
                    obj = ChunkRow(source=source, text=t, metadata=json.dumps(m), embedding=e)
                    db.add(obj)
                    objs.append(obj)
                db.commit()
                for o in objs:
                    db.refresh(o)
                return objs
            finally:
                db.close()

        def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[dict, float]]:
            # Use pgvector distance operator "<->" (small distance is better)
            db = self.SessionLocal()
            try:
                # SQLAlchemy text approach for vector distance
                stmt = select(ChunkRow).order_by(ChunkRow.embedding.distance(query_embedding)).limit(top_k)
                res = db.execute(stmt).scalars().all()
                out = []
                for r in res:
                    # Convert distance to similarity-like score using reciprocal
                    # Note: pgvector distance is Euclidean by default; for ranking it's fine.
                    out.append(({
                        "id": r.id,
                        "source": r.source,
                        "text": r.text,
                        "metadata": json.loads(r.metadata) if r.metadata else {},
                    }, 1.0))  # we don't have direct distance here; ranking is order-based
                return out
            finally:
                db.close()

# ---------- SQLITE fallback implementation ----------
class SQLiteVectorStore:
    def __init__(self, path: str):
        self.path = path
        init = not os.path.exists(self.path)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        if init:
            self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            text TEXT NOT NULL,
            metadata TEXT,
            embedding TEXT NOT NULL
        );
        """)
        self.conn.commit()

    def _encode(self, v: List[float]) -> str:
        # store as JSON string
        return json.dumps(v)

    def _decode(self, s: str) -> List[float]:
        return json.loads(s)

    def add(self, source: str, texts: List[str], embeddings: List[List[float]], metadatas: Optional[List[dict]] = None):
        cur = self.conn.cursor()
        for i, (t, e) in enumerate(zip(texts, embeddings)):
            m = metadatas[i] if metadatas and i < len(metadatas) else {}
            cur.execute(
                "INSERT INTO chunks (source, text, metadata, embedding) VALUES (?, ?, ?, ?)",
                (source, t, json.dumps(m), self._encode(e))
            )
        self.conn.commit()

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[dict, float]]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, source, text, metadata, embedding FROM chunks")
        rows = cur.fetchall()
        scored = []
        for r in rows:
            emb = self._decode(r[4])
            score = self._cosine_similarity(query_embedding, emb)
            scored.append(({
                "id": r[0],
                "source": r[1],
                "text": r[2],
                "metadata": json.loads(r[3]) if r[3] else {},
            }, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x*y for x,y in zip(a,b))
        na = math.sqrt(sum(x*x for x in a))
        nb = math.sqrt(sum(x*x for x in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na*nb)

# ---------- Factory ----------
class VectorStore:
    def __init__(self):
        if USE_PGVECTOR:
            db_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
            # If DATABASE_URL looks like Postgres, use PG backend
            if db_url and db_url.startswith("postgres"):
                self._impl = PGVectorStore(db_url)
            else:
                # fallback to sqlite
                self._impl = SQLiteVectorStore(os.getenv("VECTOR_DB_PATH", settings.VECTOR_DB_PATH))
        else:
            self._impl = SQLiteVectorStore(os.getenv("VECTOR_DB_PATH", settings.VECTOR_DB_PATH))

    def add(self, *args, **kwargs):
        return self._impl.add(*args, **kwargs)

    def search(self, *args, **kwargs):
        return self._impl.search(*args, **kwargs)
