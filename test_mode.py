"""
Test mode configuration - allows testing without OpenAI API keys.
Uses mock embeddings and simplified functionality.
"""
import os
os.environ["TEST_MODE"] = "true"

print("[TestMode] Running in TEST MODE - No OpenAI key required")
print("[TestMode] Using mock embeddings and simplified functionality")

