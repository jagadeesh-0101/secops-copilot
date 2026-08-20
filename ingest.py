"""
Run this once (and again any time sample_docs/ changes) to build the local
vector store before asking the agent anything.

    python ingest.py
"""

import os

from dotenv import load_dotenv

from app.retriever import ingest_directory

load_dotenv()

if __name__ == "__main__":
    persist_dir = os.environ.get("CHROMA_DB_DIR", "./chroma_db")
    n = ingest_directory("sample_docs", persist_dir)
    print(f"Indexed {n} chunks into {persist_dir}")
