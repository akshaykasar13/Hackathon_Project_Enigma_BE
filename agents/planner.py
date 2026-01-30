"""
Planner agent for task planning and orchestration.
Decides execution strategy: serial, parallel, or async.
"""
from backend.observability import observability

def plan(state):
    """Plan execution strategy based on ticket characteristics."""
    ticket = state.get("ticket", "").lower()
    tool_call = observability.log_tool_call("execution_planning", "PlannerAgent", {"ticket": ticket[:100]})
    
    # Determine execution strategy
    strategy = {
        "mode": "parallel",  # Default to parallel for speed
        "agents": ["intent", "memory", "retrieve"],
        "async_agents": ["observability", "learning"]
    }
    
    # Payment service and financial tickets are high priority
    payment_keywords = ["payment", "transaction", "gateway", "billing", "invoice", "refund", "charge"]
    is_payment_related = any(keyword in ticket for keyword in payment_keywords)
    
    # High priority tickets need faster processing (parallel execution)
    if "fail" in ticket or "error" in ticket or "urgent" in ticket or is_payment_related:
        strategy["mode"] = "parallel"
        strategy["priority"] = "HIGH"
        if is_payment_related:
            strategy["domain"] = "financial_services"
            strategy["requires_fast_response"] = True
    else:
        strategy["mode"] = "parallel"  # Default to parallel for all tickets (as per requirements)
        strategy["priority"] = "LOW"
    
    # Complex queries may need sequential reasoning (but still use parallel for initial steps)
    if "correlate" in ticket or "compare" in ticket or "analyze" in ticket:
        strategy["requires_reasoning"] = True
    
    state["execution_strategy"] = strategy
    state["plan"] = f"Mode: {strategy['mode']}, Priority: {strategy.get('priority', 'NORMAL')}"
    
    observability.log_tool_result(tool_call, strategy)
    observability.log_decision("PlannerAgent", f"strategy_{strategy['mode']}", 
                              f"Selected {strategy['mode']} execution for ticket characteristics",
                              {"strategy": strategy})
    observability.log_agent_execution("PlannerAgent", state, "strategy_planned")
    
    print(f"[PlannerAgent] Strategy: {strategy['mode']}, Agents: {len(strategy['agents'])}")
    return state

