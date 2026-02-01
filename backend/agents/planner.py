"""
Planner agent for task planning and orchestration.
Uses OpenAI LLM for intelligent strategy planning with rule-based fallback.
"""
import logging
from typing import Optional
from backend import config
from backend.observability import observability

logger = logging.getLogger("agent_system")


def plan_with_llm(ticket: str, task_id: Optional[str] = None) -> dict:
    """Use OpenAI LLM to plan execution strategy."""
    try:
        from backend.observability import create_observable_llm
        from langchain_core.prompts import ChatPromptTemplate
        
        llm = create_observable_llm(
            agent_name="PlannerAgent",
            operation="execution_planning",
            task_id=task_id,
            model="gpt-3.5-turbo",
            temperature=0
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a support system planner. Analyze the ticket and plan the execution strategy.

Respond with ONLY a JSON object (no markdown):

{{
    "mode": "parallel" or "serial",
    "priority": "HIGH" or "LOW",
    "complexity": "simple" or "moderate" or "complex",
    "domain": category like "financial", "technical", "billing", "general",
    "requires_reasoning": true/false (needs deep analysis?),
    "requires_memory": true/false (needs historical context?),
    "requires_retrieval": true/false (needs knowledge base search?),
    "reasoning": "brief explanation of your planning decision"
}}

Guidelines:
- Use "parallel" for most tickets (faster)
- Use "serial" only for very complex multi-step issues
- HIGH priority: errors, failures, financial issues, data mismatches, urgent requests
- complex: needs correlation with history, root cause analysis
- moderate: needs some context lookup
- simple: straightforward question/request"""),
            ("human", "{ticket}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"ticket": ticket})
        
        import json
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content)
        
        return {
            "mode": result.get("mode", "parallel"),
            "priority": result.get("priority", "LOW"),
            "complexity": result.get("complexity", "moderate"),
            "domain": result.get("domain", "general"),
            "requires_reasoning": result.get("requires_reasoning", True),
            "requires_memory": result.get("requires_memory", True),
            "requires_retrieval": result.get("requires_retrieval", True),
            "reasoning": result.get("reasoning", "LLM planning"),
            "method": "LLM"
        }
    except Exception as e:
        logger.warning(f"[LLM_FAILURE] PlannerAgent: LLM planning failed - {type(e).__name__}: {e}", exc_info=True)
        return None


def plan_with_rules(ticket: str) -> dict:
    """Fallback rule-based planning."""
    ticket_lower = ticket.lower()
    
    # Payment service and financial tickets are high priority
    payment_keywords = ["payment", "transaction", "gateway", "billing", "invoice", "refund", "charge"]
    is_payment_related = any(keyword in ticket_lower for keyword in payment_keywords)
    
    # Determine priority
    high_priority_indicators = ["fail", "error", "urgent", "down", "critical", "broken", "500", "400", "mismatch"]
    is_high_priority = any(ind in ticket_lower for ind in high_priority_indicators) or is_payment_related
    
    # Determine complexity
    complex_indicators = ["correlate", "compare", "analyze", "history", "pattern", "why", "root cause"]
    is_complex = any(ind in ticket_lower for ind in complex_indicators)
    
    # Determine domain
    domain = "general"
    if is_payment_related:
        domain = "financial"
    elif any(kw in ticket_lower for kw in ["api", "database", "server", "code", "bug"]):
        domain = "technical"
    elif any(kw in ticket_lower for kw in ["account", "login", "password", "user"]):
        domain = "account"
    
    return {
        "mode": "parallel",
        "priority": "HIGH" if is_high_priority else "LOW",
        "complexity": "complex" if is_complex else "moderate",
        "domain": domain,
        "requires_reasoning": True,
        "requires_memory": True,
        "requires_retrieval": True,
        "reasoning": f"Rule-based: {'high priority' if is_high_priority else 'standard'} {domain} ticket",
        "method": "rules"
    }


def plan(state):
    """Plan execution strategy using LLM (with rule-based fallback)."""
    ticket = state.get("ticket", "")
    tool_call = observability.log_tool_call("execution_planning", "PlannerAgent", {"ticket": ticket[:100]}, state.get("task_id"))
    
    # Try LLM planning first (if not in test mode)
    result = None
    if not config.TEST_MODE and config.OPENAI_API_KEY and config.OPENAI_API_KEY != "test-key-not-used":
        result = plan_with_llm(ticket, task_id=state.get("task_id"))
    
    # Fallback to rules if LLM failed or in test mode
    if not result:
        if not config.TEST_MODE:
            logger.info("[LLM_FALLBACK] PlannerAgent: Using rule-based planning (LLM failed or unavailable)")
        result = plan_with_rules(ticket)
    
    # Build strategy object
    strategy = {
        "mode": result["mode"],
        "priority": result["priority"],
        "complexity": result["complexity"],
        "domain": result["domain"],
        "agents": ["intent", "memory", "retrieve"],
        "async_agents": ["observability", "learning"],
        "requires_reasoning": result["requires_reasoning"],
        "requires_memory": result["requires_memory"],
        "requires_retrieval": result["requires_retrieval"],
        "reasoning": result["reasoning"],
        "method": result["method"]
    }
    
    if result["domain"] == "financial":
        strategy["requires_fast_response"] = True
    
    state["execution_strategy"] = strategy
    state["plan"] = f"Mode: {strategy['mode']}, Priority: {strategy['priority']}, Complexity: {strategy['complexity']}"
    
    observability.log_tool_result(tool_call, {"strategy": strategy, "method": result["method"]})
    observability.log_decision("PlannerAgent", f"strategy_{strategy['mode']}_{strategy['complexity']}", 
                              f"{result['reasoning']} (via {result['method']})",
                              {"strategy": strategy}, state.get("task_id"))
    observability.log_agent_execution("PlannerAgent", state, "strategy_planned")
    
    print(f"[PlannerAgent] Strategy: {strategy['mode']}, Priority: {strategy['priority']}, Complexity: {strategy['complexity']} (via {result['method']})")
    return state

