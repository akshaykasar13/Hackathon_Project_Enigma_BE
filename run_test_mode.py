"""
Run the server in TEST MODE.
Equivalent to: set TEST_MODE=true && uvicorn backend.main:app --reload
"""
import os
import sys
import subprocess
from pathlib import Path

# Set test mode
os.environ["TEST_MODE"] = "true"

# Project root: this folder (contains backend/ package)
script_dir = Path(__file__).parent
project_root = script_dir

# Add project root to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
os.chdir(project_root)

print("=" * 60)
print("  STARTING SERVER IN TEST MODE")
print("=" * 60)
print("✅ Test mode enabled - No OpenAI key required")
print("✅ Using mock embeddings")
print("✅ All features work except real semantic search")
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

