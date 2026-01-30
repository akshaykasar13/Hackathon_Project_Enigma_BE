"""
Configuration management for the agent system.
Loads environment variables and provides configuration.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Test mode check
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY and not TEST_MODE:
    raise ValueError(
        "OPENAI_API_KEY is required. Please set it in your .env file.\n"
        "Get your API key from: https://platform.openai.com/api-keys\n"
        "Or run in test mode: python -c 'import test_mode; from backend.main import app'"
    )

if TEST_MODE:
    print("[Config] Running in TEST MODE - OpenAI key not required")
    print("[Config]    Using mock embeddings for testing")
    OPENAI_API_KEY = "test-key-not-used"
else:
    print("[Config] Running in PRODUCTION MODE - Using OpenAI embeddings")

# LangSmith Configuration (Optional - for observability)
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "agent-system-hackathon")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

# Set LangSmith environment variables if configured
if LANGCHAIN_API_KEY and LANGCHAIN_TRACING_V2:
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
    print(f"[Config] LangSmith tracing enabled for project: {LANGCHAIN_PROJECT}")
else:
    print("[Config] LangSmith tracing disabled (set LANGCHAIN_API_KEY and LANGCHAIN_TRACING_V2=true to enable)")

# Application Configuration
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Vector Store Configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "backend/data/chroma")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Memory Configuration
MEMORY_DIR = os.getenv("MEMORY_DIR", "backend/data/memory")

