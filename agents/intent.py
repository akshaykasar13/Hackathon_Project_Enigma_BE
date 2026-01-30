"""
Intent agent for understanding user intent.
"""
from backend.observability import observability

def classify(state):
    """Classify user intent."""
    tool_call = observability.log_tool_call("intent_classification", "IntentAgent", {"ticket": state.get("ticket", "")[:100]})
    
    try:
        text = state.get("ticket", "").lower()
        
        # Financial service priority detection
        payment_keywords = ["payment", "transaction", "gateway", "billing", "invoice", "refund", "charge", "financial"]
        is_payment_related = any(keyword in text for keyword in payment_keywords)
        
        # High priority indicators
        high_priority_indicators = ["fail", "error", "down", "broken", "urgent", "critical", "outage"]
        is_high_priority = any(indicator in text for indicator in high_priority_indicators)
        
        # Payment service issues are always high priority
        if is_payment_related and (is_high_priority or "intermittent" in text or "slow" in text):
            priority = "HIGH"
        elif is_high_priority:
            priority = "HIGH"
        else:
            priority = "LOW"
        
        state["priority"] = priority
        
        observability.log_tool_result(tool_call, {"priority": priority})
        observability.log_decision("IntentAgent", f"Classified as {priority}", 
                                  f"Keywords detected: {'fail/error' if priority == 'HIGH' else 'none'}", 
                                  {"ticket_text": text[:50]})
        observability.log_agent_execution("IntentAgent", state, f"classified_{priority.lower()}")
        print("[IntentAgent]", priority)
    except Exception as e:
        observability.log_tool_result(tool_call, None, str(e))
        raise
    
    return state

