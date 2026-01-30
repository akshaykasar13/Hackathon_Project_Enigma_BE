"""
Ingestion agent for processing and ingesting documents.
"""
from backend.observability import observability

def ingest(state):
    """Process and ingest documents."""
    tool_call = observability.log_tool_call("ticket_ingestion", "IngestionAgent", {"input": state.get("input", "")[:100]}, state.get("task_id"))
    
    # Simple ingestion: extract text from input
    if "input" in state:
        state["ticket"] = state.get("input", "")
    
    observability.log_tool_result(tool_call, {"ticket": state.get("ticket", "")[:50]})
    observability.log_agent_execution("IngestionAgent", state, "ticket_ingested", reasoning="Normalized input as ticket for downstream processing")
    print("[IngestionAgent] Processed input")
    return state

