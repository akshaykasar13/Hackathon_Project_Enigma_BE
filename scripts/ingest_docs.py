#!/usr/bin/env python3
"""CLI to ingest documents for RAG. Run after adding docs to data/docs."""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.rag.vector_store import ingest_docs

if __name__ == "__main__":
    result = ingest_docs()
    print(f"\nIngest complete: {result.get('chunks_created', 0)} chunks, {result.get('files_processed', 0)} files")
    if result.get("errors"):
        print("Errors:", result["errors"])
