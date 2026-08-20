"""
Owns the local vector store: ingesting runbooks into it, and running
semantic search against it at query time.

Deliberately uses Chroma's bundled local embedding model (all-MiniLM-L6-v2
via onnxruntime) instead of an API embedding call, so the whole
ingest-and-retrieve pipeline runs offline with zero API cost and zero API
key — you can develop and test retrieval quality for free, and only spend
API calls on the generation step once retrieval is already working.
That's a real cost/latency tradeoff worth being able to explain: local
embeddings are free and fast but generally lower quality than something
like OpenAI's text-embedding-3, which is a reasonable upgrade path once
this is past the prototype stage.
"""

import glob
import os

import chromadb

from app.chunking import chunk_document

COLLECTION_NAME = "secops_runbooks"


def get_client(persist_dir: str) -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=persist_dir)


def get_collection(persist_dir: str):
    client = get_client(persist_dir)
    return client.get_or_create_collection(COLLECTION_NAME)


def ingest_directory(docs_dir: str, persist_dir: str) -> int:
    """Chunk and embed every .md file in docs_dir. Returns number of chunks indexed."""
    collection = get_collection(persist_dir)

    # Wipe and rebuild rather than trying to diff — simple and correct for
    # a corpus this size. At real scale you'd track content hashes per file
    # and only re-embed what changed, since embedding calls cost money.
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    ids, texts, metadatas = [], [], []
    for path in sorted(glob.glob(os.path.join(docs_dir, "*.md"))):
        source = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        for chunk in chunk_document(raw, source=source):
            ids.append(f"{source}::{chunk.chunk_index}")
            texts.append(chunk.text)
            metadatas.append({"source": chunk.source, "heading": chunk.heading})

    if not ids:
        return 0

    collection.add(ids=ids, documents=texts, metadatas=metadatas)
    return len(ids)


def search(query: str, persist_dir: str, top_k: int = 4) -> list[dict]:
    collection = get_collection(persist_dir)
    results = collection.query(query_texts=[query], n_results=top_k)

    hits = []
    for text, meta, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append(
            {
                "text": text,
                "source": meta["source"],
                "heading": meta["heading"],
                # Chroma returns a distance (lower = more similar); expose a
                # 0-1 "similarity" score too since that's more intuitive to
                # read in logs and eval output.
                "distance": distance,
                "similarity": round(1 / (1 + distance), 4),
            }
        )
    return hits
