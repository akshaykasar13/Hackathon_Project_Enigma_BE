# Chunking & Overlap Strategy – Justification

## Requirement Summary

- Knowledge bases must be chunked
- Overlap must be used to preserve semantic continuity
- Teams should justify: chunk size, overlap size

---

## Implementation

| Parameter      | Value | Configurable |
|----------------|-------|--------------|
| **Chunk Size** | 1000 characters | `CHUNK_SIZE` (env) |
| **Overlap**    | 200 characters  | `CHUNK_OVERLAP` (env) |
| **Splitter**   | `RecursiveCharacterTextSplitter` | - |
| **Separators** | `\n\n`, `\n`, ` `, `` (in order of preference) | - |

**Location:** `backend/rag/vector_store.py`, `backend/config.py`

---

## Justification: Chunk Size = 1000

### Rationale

1. **Support documentation structure**
   - FAQs, runbooks, and technical docs often fit in 500–1500 characters per idea
   - 1000 chars keeps a full idea or procedure in one chunk
   - Reduces mid-sentence or mid-paragraph splits

2. **Embedding model limits**
   - Typical embedding models handle 512–8192 tokens
   - 1000 characters ≈ 250–300 tokens
   - Leaves room for query + multiple chunks without hitting limits

3. **Retrieval quality**
   - Larger chunks → more context per hit, but more noise
   - Smaller chunks → more granular but less context
   - 1000 chars is a practical balance for support-style content

4. **Domain**
   - Payment, billing, and incident docs have clear sections and bullet points
   - 1000 chars usually contains one procedure or one FAQ entry

### Trade-offs

- Smaller (e.g. 500): more granular matches, but more fragments
- Larger (e.g. 2000): more context, but weaker semantic matching

---

## Justification: Overlap = 200

### Rationale

1. **Semantic continuity**
   - Adjacent chunks share 200 characters at boundaries
   - Reduces loss of context at split points (e.g. half of a sentence)

2. **Overlap proportion**
   - 200 / 1000 ≈ 20% overlap
   - Common practice for RAG: 10–25% overlap
   - Gives 800 new characters per chunk, 200 carried over

3. **Split quality**
   - Recursive splitter uses `\n\n`, `\n`, then space
   - Overlap covers cases where splits still cut across sentences
   - Helps retrieval when the answer spans a chunk boundary

4. **Deduplication**
   - 200 chars is short enough that similar chunks are still distinguishable
   - Embeddings + retrieval normally handle near-duplicates

### Trade-offs

- Smaller (e.g. 50): less context continuity, more boundary cuts
- Larger (e.g. 400): stronger continuity, more redundancy and storage

---

## Summary

| Parameter    | Value | Justification                                              |
|-------------|-------|------------------------------------------------------------|
| **Chunk Size** | 1000 | Aligned with support docs, embeddings, and retrieval needs |
| **Overlap**    | 200  | ~20% overlap for semantic continuity at chunk boundaries   |

Both values are configurable via environment variables for experimentation and tuning.
