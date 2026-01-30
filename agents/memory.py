"""
Memory agent for managing conversation and context memory.
Manages Working, Episodic, and Semantic memory types.
"""
from backend.memory.storage import memory_storage
from backend.context import window_context
from backend.observability import observability


def load_memory(state):
    """Load all memory types: Working, Episodic, and Semantic."""
    # Log tool call
    tool_call = observability.log_tool_call("memory_load", "MemoryAgent", {"task_id": state.get("task_id")})
    
    try:
        ticket = state.get("ticket", "")
        task_id = state.get("task_id", "default")
        
        # Working Memory - Current task context
        working = memory_storage.get_working_memory(task_id)
        state["working_memory"] = working
        
        # Episodic Memory - Past incidents and conversations
        episodic = memory_storage.get_episodic_memory(limit=10)
        state["episodic_memory"] = episodic
        state["past_incidents"] = [e.get("incident", "") for e in episodic]
        
        # Semantic Memory - Search for relevant documents/FAQs
        if ticket:
            semantic_results = memory_storage.search_semantic_memory(ticket)
            state["semantic_memory"] = semantic_results[:5]  # Top 5 results
        
        # Add current task to working memory
        memory_storage.add_working_memory(task_id, {
            "ticket": ticket,
            "timestamp": state.get("timestamp")
        })
        
        # Apply context windowing to prevent unbounded growth
        state = window_context(state)
        
        # Log success
        observability.log_tool_result(tool_call, {
            "working_count": len(working),
            "episodic_count": len(episodic),
            "semantic_count": len(state.get('semantic_memory', []))
        })
        
        observability.log_agent_execution("MemoryAgent", state, "memory_loaded")
        print(f"[MemoryAgent] Loaded: {len(working)} working, {len(episodic)} episodic, {len(state.get('semantic_memory', []))} semantic")
    except Exception as e:
        observability.log_tool_result(tool_call, None, str(e))
        raise
    
    return state


def save_memory(state):
    """Save to episodic memory after conversation."""
    from backend.observability import observability
    
    ticket = state.get("ticket", "")
    response = state.get("response", "")
    action = state.get("action", "AUTO_RESPOND")
    priority = state.get("priority", "LOW")
    
    tool_call = observability.log_tool_call("memory_save", "MemoryAgent", {"ticket": ticket[:100]})
    
    if ticket and response:
        # Save as episodic memory
        memory_id = memory_storage.add_episodic_memory(
            incident=ticket,
            outcome=response,
            metadata={
                "action": action,
                "priority": priority,
                "confidence": state.get("confidence", 0.0)
            }
        )
        observability.log_tool_result(tool_call, {"memory_id": memory_id, "saved": True})
        observability.log_agent_execution("MemoryAgent", state, "memory_saved")
        print(f"[MemoryAgent] Saved episodic memory: {ticket[:50]}...")
    else:
        observability.log_tool_result(tool_call, {"saved": False, "reason": "missing_ticket_or_response"})
    
    return state

