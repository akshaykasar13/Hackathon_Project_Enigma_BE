"""
Test script for Phase 1: Verify mem0 can be initialized separately.
This is a standalone test that doesn't affect the main system.
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

def test_mem0_import():
    """Test if mem0 can be imported."""
    print("=" * 60)
    print("Phase 1 Test: mem0 Import")
    print("=" * 60)
    try:
        from mem0 import Memory
        print("✅ mem0 imported successfully")
        return True
    except ImportError as e:
        print(f"❌ mem0 import failed: {e}")
        print("   Install with: pip install mem0ai")
        return False

def test_mem0_initialization():
    """Test if mem0 can be initialized with OpenAI."""
    print("\n" + "=" * 60)
    print("Phase 1 Test: mem0 Initialization")
    print("=" * 60)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "test-key-not-used":
        print("⚠️  OPENAI_API_KEY not set - skipping initialization test")
        print("   Set OPENAI_API_KEY in .env to test initialization")
        return False
    
    try:
        from mem0 import Memory
        
        # Try to initialize mem0
        memory = Memory.from_config({
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "test_memories",
                    "path": str(project_root / "data" / "test_mem0_db")
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
        })
        
        print("✅ mem0 initialized successfully")
        print(f"   Vector store: Chroma")
        print(f"   Embedder: OpenAI (text-embedding-3-small)")
        return True
    except Exception as e:
        print(f"❌ mem0 initialization failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_mem0_basic_operations():
    """Test basic mem0 operations."""
    print("\n" + "=" * 60)
    print("Phase 1 Test: mem0 Basic Operations")
    print("=" * 60)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "test-key-not-used":
        print("⚠️  OPENAI_API_KEY not set - skipping operations test")
        return False
    
    try:
        from mem0 import Memory
        
        memory = Memory.from_config({
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "test_memories",
                    "path": str(project_root / "data" / "test_mem0_db")
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
        })
        
        # Test adding a memory
        print("Testing: add memory...")
        result = memory.add(
            messages=[{"role": "user", "content": "Test memory: payment failed for user"}],
            user_id="test_user",
            metadata={"type": "test", "timestamp": "2024-01-01"}
        )
        print("✅ Memory added successfully")
        
        # Test searching
        print("Testing: search memory...")
        results = memory.search(query="payment issue", user_id="test_user", limit=5)
        print(f"✅ Search completed - found {len(results)} results")
        
        return True
    except Exception as e:
        print(f"❌ mem0 operations failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PHASE 1: mem0 Preparation Tests")
    print("=" * 60)
    print("\nThese tests verify mem0 can be used before integration.")
    print("No changes to main system - safe to run.\n")
    
    results = []
    
    # Test 1: Import
    results.append(("Import", test_mem0_import()))
    
    # Test 2: Initialization (only if import succeeded)
    if results[0][1]:
        results.append(("Initialization", test_mem0_initialization()))
        
        # Test 3: Basic operations (only if initialization succeeded)
        if results[1][1]:
            results.append(("Basic Operations", test_mem0_basic_operations()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All Phase 1 tests passed!")
        print("   Ready to proceed to Phase 2 (integration)")
    else:
        print("⚠️  Some tests failed")
        print("   Fix issues before proceeding to Phase 2")
    print("=" * 60)


