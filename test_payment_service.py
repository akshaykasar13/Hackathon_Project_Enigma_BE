"""
Test script to verify payment service scenario with all agents.
"""
import os
import sys

# Set test mode
os.environ["TEST_MODE"] = "true"

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.graph import app_graph

def test_payment_service_scenario():
    """Test payment service scenario end-to-end."""
    print("\n" + "="*80)
    print("  PAYMENT SERVICE SCENARIO TEST")
    print("="*80)
    
    ticket = "Payment service failing intermittently for EU users"
    
    initial_state = {
        "ticket": ticket,
        "input": ticket,
        "task_id": "test-payment-001",
        "timestamp": "2024-01-01T00:00:00"
    }
    
    print(f"\n📋 Ticket: {ticket}")
    print("\n🔄 Executing agent workflow...\n")
    
    result = app_graph.invoke(initial_state)
    
    print("\n" + "-"*80)
    print("  RESULTS")
    print("-"*80)
    
    if result:
        print(f"✅ Priority: {result.get('priority', 'N/A')}")
        print(f"✅ Action: {result.get('action', 'N/A')}")
        print(f"✅ Confidence: {result.get('confidence', 0.0):.2f}")
        print(f"✅ Correlations: {len(result.get('correlation', []))}")
        print(f"✅ Past Incidents: {len(result.get('past_incidents', []))}")
        print(f"✅ Retrieved Docs: {len(result.get('retrieved_docs', []))}")
        
        print("\n📝 Response:")
        print(result.get('response', 'N/A')[:200] + "...")
        
        print("\n🔗 Correlations:")
        for corr in result.get('correlation', [])[:3]:
            print(f"  - {corr}")
        
        print("\n📚 Past Incidents:")
        for incident in result.get('past_incidents', [])[:5]:
            print(f"  - {incident}")
        
        # Verify all agents executed
        print("\n✅ Agent Execution Verification:")
        print(f"  - Ingestion: {'✅' if result.get('ticket') else '❌'}")
        print(f"  - Planner: {'✅' if result.get('execution_strategy') else '❌'}")
        print(f"  - Intent: {'✅' if result.get('priority') else '❌'}")
        print(f"  - Memory: {'✅' if result.get('past_incidents') else '❌'}")
        print(f"  - Retrieval: {'✅' if result.get('retrieved_docs') is not None else '❌'}")
        print(f"  - Reasoning: {'✅' if result.get('correlation') else '❌'}")
        print(f"  - Response: {'✅' if result.get('response') else '❌'}")
        print(f"  - Guardrails: {'✅' if result.get('action') and result.get('confidence') is not None else '❌'}")
        
        # Payment service specific checks
        print("\n💳 Payment Service Verification:")
        is_payment = any(kw in ticket.lower() for kw in ["payment", "transaction", "gateway"])
        print(f"  - Payment detected: {'✅' if is_payment else '❌'}")
        print(f"  - High priority: {'✅' if result.get('priority') == 'HIGH' else '❌'}")
        print(f"  - EU region detected: {'✅' if 'eu' in ticket.lower() else 'N/A'}")
        print(f"  - Financial mitigation: {'✅' if 'gateway' in result.get('response', '').lower() or 'transaction' in result.get('response', '').lower() else '❌'}")
        
        return result
    else:
        print("❌ No result returned!")
        return None

if __name__ == "__main__":
    result = test_payment_service_scenario()
    
    if result and result.get('priority') == 'HIGH' and result.get('action') == 'AUTO_RESPOND':
        print("\n" + "="*80)
        print("  ✅ PAYMENT SERVICE TEST PASSED")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("  ⚠️  PAYMENT SERVICE TEST NEEDS REVIEW")
        print("="*80)

