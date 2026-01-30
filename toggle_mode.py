"""
Toggle between TEST MODE and PRODUCTION MODE.
"""
import os
import sys

def get_current_mode():
    """Get current mode from environment."""
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    has_openai_key = bool(os.getenv("OPENAI_API_KEY"))
    
    if test_mode:
        return "TEST"
    elif has_openai_key:
        return "PRODUCTION"
    else:
        return "TEST (no OpenAI key found)"

def set_mode(mode: str):
    """Set the mode."""
    if mode.upper() == "TEST":
        os.environ["TEST_MODE"] = "true"
        print("✅ Switched to TEST MODE")
        print("   - Uses mock embeddings")
        print("   - No OpenAI key required")
    elif mode.upper() == "PRODUCTION":
        if "TEST_MODE" in os.environ:
            del os.environ["TEST_MODE"]
        print("✅ Switched to PRODUCTION MODE")
        print("   - Uses OpenAI embeddings")
        print("   - Requires OPENAI_API_KEY in .env")
    else:
        print(f"❌ Unknown mode: {mode}")
        print("   Use: TEST or PRODUCTION")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        set_mode(mode)
    else:
        print(f"Current mode: {get_current_mode()}")
        print("\nUsage:")
        print("  python backend/toggle_mode.py TEST       # Switch to test mode")
        print("  python backend/toggle_mode.py PRODUCTION # Switch to production mode")
        print("\nOr set environment variable:")
        print("  set TEST_MODE=true        # Windows")
        print("  export TEST_MODE=true     # Linux/Mac")

