# Hackathon_Project_Enigma_BE

Intelligent Support & Incident Co-Pilot - Collaborative Agent System Backend.

## Chunking Strategy (RAG)

- **Chunk Size: 1000** – Balances context window size with retrieval precision for support documentation. Larger chunks preserve more context; 1000 chars fits typical FAQ/runbook paragraphs.
- **Overlap: 200** – ~20% overlap preserves semantic continuity across boundaries, reducing split-sentence issues and improving retrieval quality.
- Configurable via env: `CHUNK_SIZE`, `CHUNK_OVERLAP`

## Quick Start

1. Install: `pip install -r requirements.txt`
2. Copy `env.example` to `.env`, set `OPENAI_API_KEY` (or use `TEST_MODE=true`)
3. Generate dataset: `python generate_all_files.py` (creates 100+ files: PDF, Word, TXT, PPTX, images)
4. Ingest docs: `python scripts/ingest_docs.py` or `POST /ingest` when server is running
5. Start: `python run_test_mode.py` (or `run_production_mode.py`)

## API Endpoints

- `POST /ticket` – Process ticket
- `POST /ingest` – Ingest documents for RAG
- `GET /sse/agent-stream` – Live agent events (optional `?task_id=`)
- `GET/PUT/DELETE /memory/episodic`, `/memory/semantic`, `/memory/working`
