"""
Run the server in PRODUCTION MODE.
Requires OPENAI_API_KEY in .env file.
"""
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Project root: this folder (contains backend/ package)
script_dir = Path(__file__).parent
project_root = script_dir

# Load .env file from backend directory
env_path = script_dir / ".env"
load_dotenv(env_path)

# Check for OpenAI key
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("=" * 60)
    print("  ❌ PRODUCTION MODE - OpenAI Key Required")
    print("=" * 60)
    print("\nPlease set OPENAI_API_KEY in .env file at project root")
    print("\nSteps:")
    print("  1. Copy env.example to .env")
    print("  2. Add: OPENAI_API_KEY=sk-your-key-here")
    print("  3. Get key from: https://platform.openai.com/api-keys")
    print()
    sys.exit(1)

# Ensure test mode is off
if "TEST_MODE" in os.environ:
    del os.environ["TEST_MODE"]

# Change to project root so imports work
os.chdir(project_root)

# Add project root to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("=" * 60)
print("  STARTING SERVER IN PRODUCTION MODE")
print("=" * 60)
print("✅ Production mode enabled")
print("✅ Using OpenAI embeddings")
print("✅ Full RAG functionality")
print("=" * 60)
print()

# Start uvicorn from project root
try:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"],
        cwd=project_root,
        env=env
    )
except KeyboardInterrupt:
    print("\n\nServer stopped.")

