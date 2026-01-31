"""
Graph module for managing the agent workflow graph.
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

from backend.agents.ingestion import ingest
from backend.agents.planner import plan
from backend.agents.intent import classify
from backend.agents.retrieval import retrieve
from backend.agents.memory import load_memory
from backend.agents.reasoning import reason
from backend.agents.response import respond
from backend.agents.guardrails import guard

# Reducer functions for concurrent state updates
def replace_state(left: any, right: any) -> any:
    """Replace left with right (last write wins), but don't replace with empty/None."""
    # For strings, don't replace with empty strings
    if isinstance(right, str) and right == "":
        return left if left else right
    # For floats/numbers, always use right if it's not None
    if isinstance(right, (int, float)) and right is not None:
        return right
    # For other types, replace if right is not None
    return right if right is not None else left

def extend_list(left: list, right: list) -> list:
    """Extend list with new items, avoiding duplicates."""
    if not isinstance(left, list):
        left = []
    if not isinstance(right, list):
        right = []
    # Combine and remove duplicates while preserving order
    combined = left + right
    seen = set()
    result = []
    for item in combined:
        # Use tuple for hashable items, string representation for others
        key = item if isinstance(item, (str, int, float, tuple)) else str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

class State(TypedDict, total=False):
    ticket: Annotated[str, replace_state]  # Can be updated by ingestion
    input: Annotated[str, replace_state]
    task_id: Annotated[str, replace_state]
    timestamp: Annotated[str, replace_state]
    priority: Annotated[str, replace_state]  # Can be updated concurrently
    action: Annotated[str, replace_state]
    response: Annotated[str, replace_state]
    confidence: Annotated[float, replace_state]
    retrieved_docs: Annotated[list, extend_list]  # Can be extended concurrently
    context: Annotated[list, extend_list]  # Can be extended concurrently
    past_incidents: Annotated[list, replace_state]  # Memory agent sets the full list
    correlation: Annotated[list, replace_state]  # Reasoning agent sets the full list
    reasoning: Annotated[str, replace_state]
    escalation_reason: Annotated[str, replace_state]
    working_memory: Annotated[list, replace_state]
    episodic_memory: Annotated[list, replace_state]
    semantic_memory: Annotated[list, replace_state]
    execution_strategy: Annotated[str, replace_state]
    conversation_history: Annotated[list, replace_state]

graph = StateGraph(State)

graph.add_node("ingest", ingest)
graph.add_node("planner", plan)
graph.add_node("memory", load_memory)
graph.add_node("intent", classify)
graph.add_node("retrieve", retrieve)
graph.add_node("reason", reason)
graph.add_node("respond", respond)
graph.add_node("guard", guard)

# According to requirements diagram: Planner → (Intent, Memory, Retrieval in parallel) → Reasoning
# LangGraph supports parallel execution by having multiple edges from the same node
# All three agents (Intent, Memory, Retrieval) can run in parallel from Planner

graph.set_entry_point("ingest")

graph.add_edge("ingest", "planner")

# PARALLEL EXECUTION: Intent, Memory, and Retrieval all run simultaneously from Planner
# This matches the requirements diagram exactly
graph.add_edge("planner", "intent")
graph.add_edge("planner", "memory")   # Runs in parallel with intent
graph.add_edge("planner", "retrieve") # Runs in parallel with intent and memory

# All three parallel agents converge at Reasoning
# Reasoning waits for all three to complete (LangGraph handles this automatically)
graph.add_edge("intent", "reason")
graph.add_edge("memory", "reason")
graph.add_edge("retrieve", "reason")

# Reason goes to respond
graph.add_edge("reason", "respond")

# Respond goes to guard
graph.add_edge("respond", "guard")

# Guard goes to END (save_memory runs async in main.py BackgroundTasks)
graph.add_edge("guard", END)

app_graph = graph.compile()

