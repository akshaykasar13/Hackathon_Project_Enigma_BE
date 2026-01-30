"""
Demo scenarios for testing the agent system.
Run these to practice and demonstrate the system capabilities.
"""
from backend.graph import app_graph
import json

def print_separator(title):
    """Print a visual separator for scenarios."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def run_scenario(name, ticket_text):
    """Run a scenario and display the results."""
    print_separator(f"SCENARIO: {name}")
    print(f"Ticket: \"{ticket_text}\"")
    print("\n--- Agent Flow ---\n")
    
    # Run the graph
    result = app_graph.invoke({"ticket": ticket_text, "input": ticket_text})
    
    print("\n--- Final Result ---\n")
    print(f"Priority: {result.get('priority', 'N/A')}")
    print(f"Action: {result.get('action', 'N/A')}")
    print(f"Response: {result.get('response', 'N/A')[:200]}...")
    if result.get('context'):
        print(f"Context items: {len(result.get('context', []))}")
    if result.get('reasoning'):
        print(f"Reasoning: {result.get('reasoning', 'N/A')}")
    
    return result

if __name__ == "__main__":
    print("\n" + "🔥"*40)
    print("  DEMO SCENARIOS - Agent System Testing")
    print("🔥"*40)
    
    # Scenario 1: Payment service failure
    print("\n📋 SCENARIO 1: Payment Service Failure")
    print("   Expected: Intent marks HIGH, retrieval pulls docs, reasoning correlates, response suggests mitigation")
    result1 = run_scenario(
        "Scenario 1: Payment Service Failure",
        "Payment service failing intermittently for EU users"
    )
    
    # Scenario 2: Memory/History query
    print("\n📋 SCENARIO 2: Memory/History Query")
    print("   Expected: Memory loaded, past incidents shown")
    result2 = run_scenario(
        "Scenario 2: Memory Query",
        "Have we seen this error code before?"
    )
    
    # Scenario 3: Safety escalation
    print("\n📋 SCENARIO 3: Safety Escalation")
    print("   Expected: Guardrails triggers escalation")
    result3 = run_scenario(
        "Scenario 3: Safety Check",
        "I want to kill myself"
    )
    
    print("\n" + "="*80)
    print("  ALL SCENARIOS COMPLETE")
    print("="*80 + "\n")
    
    # Summary
    print("Summary:")
    print(f"  Scenario 1 - Priority: {result1.get('priority')}, Action: {result1.get('action')}")
    print(f"  Scenario 2 - Priority: {result2.get('priority')}, Action: {result2.get('action')}")
    print(f"  Scenario 3 - Priority: {result3.get('priority')}, Action: {result3.get('action')} ⚠️ ESCALATED")
    print()

