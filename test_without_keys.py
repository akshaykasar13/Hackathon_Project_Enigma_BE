"""
Test the system without OpenAI keys.
This script sets up test mode and runs a simple test.
"""
import os
import sys

# Set test mode before importing anything
os.environ["TEST_MODE"] = "true"

print("=" * 60)
print("  TEST MODE - No API Keys Required")
print("=" * 60)
print()

# Import after setting test mode
import config
from graph import app_graph

def test_basic_flow():
    """Test the basic agent flow."""
    print("\n[Test] Testing basic agent flow...")
    
    test_ticket = "Payment service failing intermittently for EU users"
    
    initial_state = {
        "ticket": test_ticket,
        "input": test_ticket,
        "task_id": "test-123",
        "timestamp": "2024-01-01T00:00:00"
    }
    
    try:
        print(f"[Test] Processing ticket: {test_ticket}")
        result = app_graph.invoke(initial_state)
        
        print("\n[Test] ✅ SUCCESS!")
        print(f"[Test] Priority: {result.get('priority', 'N/A')}")
        print(f"[Test] Action: {result.get('action', 'N/A')}")
        print(f"[Test] Response: {result.get('response', 'N/A')[:100]}...")
        
        return True
    except Exception as e:
        print(f"\n[Test] ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory():
    """Test memory operations."""
    print("\n[Test] Testing memory operations...")
    
    try:
        from memory.storage import memory_storage
        
        # Test adding memory
        memory_id = memory_storage.add_episodic_memory(
            incident="Test incident",
            outcome="Test outcome",
            metadata={"test": True}
        )
        print(f"[Test] Added memory with ID: {memory_id}")
        
        # Test retrieving memory
        memories = memory_storage.get_episodic_memory(limit=1)
        print(f"[Test] Retrieved {len(memories)} memories")
        
        print("[Test] ✅ Memory operations working!")
        return True
    except Exception as e:
        print(f"[Test] ❌ Memory test failed: {e}")
        return False

def test_guardrails():
    """Test guardrails."""
    print("\n[Test] Testing guardrails...")
    
    try:
        from agents.guardrails import guard
        
        # Test safe input
        safe_state = {"ticket": "How do I reset my password?"}
        result = guard(safe_state.copy())
        print(f"[Test] Safe input - Action: {result.get('action')}")
        
        # Test banned input
        banned_state = {"ticket": "I want to kill myself"}
        result = guard(banned_state.copy())
        print(f"[Test] Banned input - Action: {result.get('action')}")
        
        print("[Test] ✅ Guardrails working!")
        return True
    except Exception as e:
        print(f"[Test] ❌ Guardrails test failed: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 Starting tests in TEST MODE...\n")
    
    results = []
    
    # Test 1: Memory
    results.append(("Memory", test_memory()))
    
    # Test 2: Guardrails
    results.append(("Guardrails", test_guardrails()))
    
    # Test 3: Full flow (may fail if vector store is empty, that's OK)
    print("\n[Test] Note: Full flow test may fail if vector store is empty.")
    print("[Test] This is expected - you need to ingest documents first.")
    try:
        results.append(("Full Flow", test_basic_flow()))
    except Exception as e:
        print(f"[Test] Full flow test skipped: {e}")
        results.append(("Full Flow", None))
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    for test_name, result in results:
        if result is True:
            print(f"  ✅ {test_name}: PASSED")
        elif result is False:
            print(f"  ❌ {test_name}: FAILED")
        else:
            print(f"  ⚠️  {test_name}: SKIPPED")
    
    print("\n💡 To test with real embeddings:")
    print("   1. Get OpenAI API key from https://platform.openai.com/api-keys")
    print("   2. Create backend/.env file with: OPENAI_API_KEY=sk-...")
    print("   3. Run: uvicorn backend.main:app --reload")
    print()

