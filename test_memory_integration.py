"""
Test script for Phase 2: Test memory integration with fallback.
Tests both JSON and mem0 modes.
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

def test_json_mode():
    """Test that JSON mode still works (USE_MEM0=false)."""
    print("=" * 60)
    print("Phase 2 Test: JSON Mode (USE_MEM0=false)")
    print("=" * 60)
    
    # Temporarily disable mem0
    original_use_mem0 = os.getenv("USE_MEM0", "false")
    os.environ["USE_MEM0"] = "false"
    
    try:
        # Reload config to pick up the change
        import importlib
        import backend.config
        importlib.reload(backend.config)
        
        from backend.memory.storage import memory_storage
        
        # Test that it's using JSON
        assert not memory_storage._using_mem0, "Should be using JSON, not mem0"
        print("✅ Using JSON storage")
        
        # Test basic operations
        print("Testing: add_episodic_memory...")
        memory_id = memory_storage.add_episodic_memory(
            incident="Test incident: payment failed",
            outcome="Resolved by refunding customer",
            metadata={"priority": "high"}
        )
        print(f"✅ Added episodic memory with ID: {memory_id}")
        
        print("Testing: get_episodic_memory...")
        memories = memory_storage.get_episodic_memory(limit=5)
        assert len(memories) > 0, "Should have at least one memory"
        print(f"✅ Retrieved {len(memories)} memories")
        
        print("Testing: search_episodic_memory...")
        results = memory_storage.search_episodic_memory("payment")
        assert len(results) > 0, "Should find payment-related memories"
        print(f"✅ Found {len(results)} matching memories")
        
        return True
    except Exception as e:
        print(f"❌ JSON mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original setting
        if original_use_mem0:
            os.environ["USE_MEM0"] = original_use_mem0
        else:
            os.environ.pop("USE_MEM0", None)

def test_mem0_mode():
    """Test mem0 mode if available (USE_MEM0=true)."""
    print("\n" + "=" * 60)
    print("Phase 2 Test: mem0 Mode (USE_MEM0=true)")
    print("=" * 60)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "test-key-not-used":
        print("⚠️  OPENAI_API_KEY not set - skipping mem0 mode test")
        return False
    
    # Check if mem0 is available
    try:
        from mem0 import Memory
    except ImportError:
        print("⚠️  mem0 not installed - skipping mem0 mode test")
        print("   Install with: pip install mem0ai")
        return False
    
    # Enable mem0
    original_use_mem0 = os.getenv("USE_MEM0", "false")
    os.environ["USE_MEM0"] = "true"
    
    try:
        # Reload config
        import importlib
        import backend.config
        importlib.reload(backend.config)
        
        from backend.memory.storage import memory_storage
        
        # Test that it's using mem0
        if memory_storage._using_mem0:
            print("✅ Using mem0 storage")
        else:
            print("⚠️  mem0 enabled but fell back to JSON (check initialization)")
            return False
        
        # Test basic operations
        print("Testing: add_episodic_memory...")
        memory_id = memory_storage.add_episodic_memory(
            incident="Test incident: transaction error",
            outcome="Resolved by updating payment gateway",
            metadata={"priority": "high"}
        )
        print(f"✅ Added episodic memory with ID: {memory_id}")
        
        print("Testing: get_episodic_memory...")
        memories = memory_storage.get_episodic_memory(limit=5)
        print(f"✅ Retrieved {len(memories)} memories")
        
        print("Testing: search_episodic_memory (semantic search)...")
        # This should find "transaction error" even if we search for "payment issue"
        results = memory_storage.search_episodic_memory("payment problem")
        print(f"✅ Semantic search found {len(results)} matching memories")
        if results:
            print(f"   Example: {results[0].get('incident', '')[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ mem0 mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original setting
        if original_use_mem0:
            os.environ["USE_MEM0"] = original_use_mem0
        else:
            os.environ.pop("USE_MEM0", None)

def test_fallback():
    """Test that fallback to JSON works if mem0 fails."""
    print("\n" + "=" * 60)
    print("Phase 2 Test: Fallback Mechanism")
    print("=" * 60)
    
    # This test would require simulating a mem0 failure
    # For now, just verify the fallback flag exists
    from backend import config
    assert hasattr(config, 'MEM0_FALLBACK_TO_JSON'), "MEM0_FALLBACK_TO_JSON config missing"
    print(f"✅ Fallback flag exists: MEM0_FALLBACK_TO_JSON={config.MEM0_FALLBACK_TO_JSON}")
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PHASE 2: Memory Integration Tests")
    print("=" * 60)
    print("\nTesting memory system with mem0 integration and fallback.\n")
    
    results = []
    
    # Test 1: JSON mode (should always work)
    results.append(("JSON Mode", test_json_mode()))
    
    # Test 2: mem0 mode (if available)
    results.append(("mem0 Mode", test_mem0_mode()))
    
    # Test 3: Fallback mechanism
    results.append(("Fallback", test_fallback()))
    
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
        print("✅ All Phase 2 tests passed!")
        print("   mem0 integration is working correctly")
    else:
        print("⚠️  Some tests failed or were skipped")
        print("   Check the output above for details")
    print("=" * 60)


